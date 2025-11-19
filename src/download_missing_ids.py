#!/usr/bin/env python3

import requests
import json
import os
import time

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiI0ZjU4MDJiMi1hN2ZiLTRmNjMtOGE1NS0wOTJjYzIzNDg0ODYiLCJyb2xlIjoidXNlciIsImV4cCI6MTc2MjY1MjM3N30.JMB2_fkVGTr3R1ef0PWtp4-iO7K3st_FCaFl5pSfAUc"

PROTOCOL = "https"
HOSTNAME = "mathgenealogy.org"
PORT = "8000"

def find_missing_ids(merged_file="mgp_cache/all_academics_merged.json"):
    """Find all missing IDs from the merged data."""
    print("Loading merged data...")
    
    with open(merged_file, 'r') as f:
        data = json.load(f)
    
    existing_ids = set(int(id) for id in data.keys())
    min_id = min(existing_ids)
    max_id = max(existing_ids)
    
    print(f"Found {len(existing_ids)} existing IDs (range: {min_id} to {max_id})")
    
    # Find all missing IDs in the range
    all_ids = set(range(min_id, max_id + 1))
    missing_ids = sorted(all_ids - existing_ids)
    
    print(f"Missing {len(missing_ids)} IDs\n")
    
    return missing_ids

def download_missing_ids(cache_dir="mgp_cache"):
    """
    Download only the missing IDs one at a time (most reliable for gaps).
    """
    merged_file = os.path.join(cache_dir, "all_academics_merged.json")
    
    if not os.path.exists(merged_file):
        print("all_academics_merged.json not found!")
        print("Run merge_checkpoints.py first!")
        return
    
    # Find missing IDs
    missing_ids = find_missing_ids(merged_file)
    
    if not missing_ids:
        print("No missing IDs! Your dataset is complete")
        return
    
    print(f"Downloading {len(missing_ids)} Missing IDs")
    print(f"Querying one ID at a time (most reliable for scattered IDs)")
    
    # Load existing data
    with open(merged_file, 'r') as f:
        all_data = json.load(f)
    
    headers = {'x-access-token': TOKEN}
    
    # Process each ID individually
    newly_found = 0
    not_found = []
    
    for i, acad_id in enumerate(missing_ids, 1):
        try:
            # Query single academic
            url = f"{PROTOCOL}://{HOSTNAME}:{PORT}/api/v2/MGP/acad"
            params = {'id': acad_id}
            
            r = requests.get(url, headers=headers, params=params, timeout=30)
            
            if r.ok:
                data = json.loads(r.text)
                r.close()
                
                # Add to dataset
                all_data[str(acad_id)] = data
                newly_found += 1
                
                if i % 10 == 0:
                    print(f"Progress: {i}/{len(missing_ids)} - Found {newly_found} (ID {acad_id} ✓)", end="\r")
            elif r.status_code == 404:
                # ID doesn't exist in database
                r.close()
                not_found.append(acad_id)
                if i % 10 == 0:
                    print(f"Progress: {i}/{len(missing_ids)} - Found {newly_found} (ID {acad_id} not in DB)", end="\r")
            else:
                r.close()
                print(f"Error {r.status_code} for ID {acad_id}")
                not_found.append(acad_id)
            
            # Rate limiting
            time.sleep(0.2)
            
            # Save progress every 50 IDs
            if i % 50 == 0:
                with open(merged_file, 'w') as f:
                    json.dump(all_data, f, indent=2)
                print(f"\nProgress saved: {newly_found} new records added")
            
        except Exception as e:
            print(f"Error for ID {acad_id}: {e}")
            
            if "401" in str(e):
                print("oken expired! Get a new token and restart")
                # Save before stopping
                with open(merged_file, 'w') as f:
                    json.dump(all_data, f, indent=2)
                break
            
            not_found.append(acad_id)
            time.sleep(2)
            continue
    
    # Final save
    print(f"\nSaving final data...")
    with open(merged_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    # Save list of IDs that truly don't exist
    if not_found:
        not_found_file = os.path.join(cache_dir, "ids_not_found.json")
        with open(not_found_file, 'w') as f:
            json.dump(sorted(not_found), f, indent=2)
    
    print(f"Complete")
    print(f"Successfully added: {newly_found} records")
    print(f"IDs not found (don't exist in database): {len(not_found)}")
    print(f"Total academics now: {len(all_data)}")
    
    if not_found:
        print(f"\nList of non-existent IDs saved to: ids_not_found.json")
        print(f"First few non-existent IDs: {sorted(not_found)[:10]}")

if __name__ == '__main__':
    download_missing_ids(cache_dir="mgp_cache")