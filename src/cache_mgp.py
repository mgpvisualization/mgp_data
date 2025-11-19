#!/usr/bin/env python3

import requests
import json
import os
import time
from pathlib import Path

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiI0ZjU4MDJiMi1hN2ZiLTRmNjMtOGE1NS0wOTJjYzIzNDg0ODYiLCJyb2xlIjoidXNlciIsImV4cCI6MTc2MjkwMDkwMn0.JmeD1OnXBgtTlnrlrOH6LvyXfZYD9GcyZzdrt1pVAsM"
PROTOCOL = "https"
HOSTNAME = "mathgenealogy.org"
PORT = "8000"

def doquery(endpoint, params, timeout=60):
    """Query the MGP API."""
    headers = {'x-access-token': TOKEN}
    url = f"{PROTOCOL}://{HOSTNAME}:{PORT}{endpoint}"
    
    r = requests.get(url, headers=headers, params=params, timeout=timeout)
    if r.ok:
        result = r.text
        r.close()
        return result
    else:
        r.close()
        raise RuntimeError(f"Error executing query: {r.status_code}")

def cache_all_academics(start_id=1, max_id=30000, batch_size=10, output_dir="mgp_cache"):
    """
    Download all academic data using small batches of 10 (proven to work).
    
    Args:
        start_id: Starting ID (default 1)
        max_id: Maximum ID to check (default 300000)
        batch_size: Number of IDs per request (10 is reliable)
        output_dir: Directory to save data
    """
    Path(output_dir).mkdir(exist_ok=True)
    
    progress_file = os.path.join(output_dir, "cache_progress.json")
    
    # Load existing progress
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            last_completed = progress.get('last_completed_range', start_id - 1)
            start_id = last_completed + 1
        print(f"Resuming from ID {start_id}")
    
    print(f"Starting MGP Database Cache")
    print(f"ID Range: {start_id} to {max_id}")
    print(f"Batch Size: {batch_size} (small batches that work reliably)")
    print(f"Rate Limiting: 1 second between batches")
    total_batches = (max_id - start_id) // batch_size
    print(f"Total Batches: {total_batches}")
    
    current_id = start_id
    batch_num = 1
    total_downloaded = 0
    all_data = {}
    
    while current_id <= max_id:
        range_start = current_id
        range_stop = min(current_id + batch_size, max_id + 1)
        
        try:
            print(f"Batch {batch_num}: IDs {range_start}-{range_stop-1}...", end=" ", flush=True)
            
            endpoint = '/api/v2/MGP/acad/range'
            params = {
                'start': range_start,
                'stop': range_stop,
                'step': 1
            }
            
            result = doquery(endpoint, params, timeout=60)
            batch_data = json.loads(result)
            
            # Add to all_data
            if isinstance(batch_data, list) and len(batch_data) > 0:
                # If it's a list of academics
                for acad in batch_data:
                    if 'MGP_academic' in acad and 'ID' in acad['MGP_academic']:
                        acad_id = str(acad['MGP_academic']['ID'])
                        all_data[acad_id] = acad
            elif isinstance(batch_data, dict):
                # If it's already a dict
                all_data.update(batch_data)
            
            count = len(batch_data) if isinstance(batch_data, (dict, list)) else 0
            total_downloaded += count
            print(f"{count} records (Total: {total_downloaded})")
            
            # Save progress every 10 batches
            if batch_num % 10 == 0:
                with open(progress_file, 'w') as f:
                    json.dump({
                        'last_completed_range': range_stop - 1,
                        'total_downloaded': total_downloaded,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }, f, indent=2)
                
                # Save data checkpoint
                checkpoint_file = os.path.join(output_dir, f"checkpoint_{range_stop}.json")
                with open(checkpoint_file, 'w') as f:
                    json.dump(all_data, f, indent=2)
                print(f"  → Checkpoint saved: {total_downloaded} records")
            
            current_id = range_stop
            batch_num += 1
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ Error: {e}")
            
            if "401" in str(e):
                print("Token expired! Get a new token and restart.")
                break
            
            # Wait and continue to next batch
            print("  Waiting 5 seconds...")
            time.sleep(5)
            current_id = range_stop  # Skip this batch and continue
            continue
    
    # Save final complete dataset
    final_file = os.path.join(output_dir, "all_academics.json")
    with open(final_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    with open(progress_file, 'w') as f:
        json.dump({
            'last_completed_range': max_id,
            'total_downloaded': total_downloaded,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'complete': True
        }, f, indent=2)
    
    print(f"Cache Complete")
    print(f"Total academics downloaded: {total_downloaded}")
    print(f"Saved to: {final_file}")
    print(f"Location: {os.path.abspath(output_dir)}")

if __name__ == '__main__':
    cache_all_academics(
        start_id=20260, 
        max_id=350000,       
        batch_size=10,
        output_dir="mgp_cache"
    )