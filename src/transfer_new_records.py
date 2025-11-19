#!/usr/bin/env python3

import json
import os

def transfer_new_records(
    source_file="mgp_cache/all_academics_merged.json",
    target_file="mgp_cache/all_academics_checkpoints.json"
):
    """
    Transfer newly found records from merged file to checkpoints file.
    Only adds records that don't already exist in checkpoints.
    """
    
    print(f"\n=== Transferring New Records ===\n")
    
    # Check if files exist
    if not os.path.exists(source_file):
        print(f"❌ Source file not found: {source_file}")
        return
    
    if not os.path.exists(target_file):
        print(f"❌ Target file not found: {target_file}")
        return
    
    # Load source file (all_academics_merged.json)
    print(f"Loading {os.path.basename(source_file)}...")
    with open(source_file, 'r') as f:
        merged_data = json.load(f)
    
    merged_ids = set(merged_data.keys())
    print(f"  ✓ Loaded {len(merged_data):,} records")
    
    # Load target file (all_academics_checkpoints.json)
    print(f"Loading {os.path.basename(target_file)}...")
    with open(target_file, 'r') as f:
        checkpoints_data = json.load(f)
    
    checkpoints_ids = set(checkpoints_data.keys())
    print(f"  ✓ Loaded {len(checkpoints_data):,} records\n")
    
    # Find new IDs (in merged but not in checkpoints)
    new_ids = merged_ids - checkpoints_ids
    
    if not new_ids:
        print("✓ No new records to transfer! Files are already in sync.")
        return
    
    print(f"Found {len(new_ids):,} new records to transfer")
    print(f"First few new IDs: {sorted([int(id) for id in list(new_ids)[:10]])}\n")
    
    # Add new records to checkpoints
    print("Transferring new records...")
    for acad_id in new_ids:
        checkpoints_data[acad_id] = merged_data[acad_id]
    
    # Save updated checkpoints file
    print(f"Saving updated {os.path.basename(target_file)}...")
    with open(target_file, 'w') as f:
        json.dump(checkpoints_data, f, indent=2)
    
    file_size = os.path.getsize(target_file) / (1024 * 1024)
    
    print(f"\n=== Transfer Complete ===")
    print(f"Total records in checkpoints file: {len(checkpoints_data):,}")
    print(f"New records added: {len(new_ids):,}")
    print(f"File size: {file_size:.2f} MB")
    
    # Show ID range
    all_ids = sorted([int(id) for id in checkpoints_data.keys()])
    print(f"ID range: {min(all_ids):,} to {max(all_ids):,}")
    
    # Show what was added
    new_ids_sorted = sorted([int(id) for id in new_ids])
    print(f"\nNew IDs added range: {min(new_ids_sorted):,} to {max(new_ids_sorted):,}")
    
    print(f"\n✓ Successfully updated {target_file}")

if __name__ == '__main__':
    transfer_new_records(
        source_file="mgp_cache/all_academics_merged.json",
        target_file="mgp_cache/all_academics_checkpoints.json"
    )