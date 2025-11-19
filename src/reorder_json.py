#!/usr/bin/env python3

import json
import os
from collections import OrderedDict

def reorder_json_by_id(input_file="mgp_cache/all_academics_merged.json"):
    """
    Reorder JSON file so IDs are in numerical order from smallest to largest.
    """
    
    print(f"\n=== Reordering {os.path.basename(input_file)} ===\n")
    
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    # Load the file
    print("Loading file...")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    original_size = os.path.getsize(input_file) / (1024 * 1024)
    
    print(f"  Loaded {len(data):,} records")
    print(f"  Original file size: {original_size:.2f} MB")
    
    # Get ID range before reordering
    ids = [int(id) for id in data.keys()]
    first_key_before = list(data.keys())[0]
    
    print(f"\nBefore reordering:")
    print(f"  First ID in file: {first_key_before}")
    print(f"  Actual smallest ID: {min(ids):,}")
    print(f"  Actual largest ID: {max(ids):,}")
    
    # Sort IDs numerically
    print(f"\nSorting {len(ids):,} IDs numerically...")
    sorted_ids = sorted(ids)
    
    # Create new ordered dictionary
    print("Creating reordered dictionary...")
    ordered_data = OrderedDict()
    
    for i, id_num in enumerate(sorted_ids):
        ordered_data[str(id_num)] = data[str(id_num)]
        
        # Progress indicator
        if (i + 1) % 10000 == 0:
            print(f"  Processed {i+1:,}/{len(sorted_ids):,} records...")
    
    # Save reordered file
    print(f"\nSaving reordered file...")
    
    # Create backup first
    backup_file = input_file.replace('.json', '_unordered_backup.json')
    print(f"  Creating backup: {os.path.basename(backup_file)}")
    os.rename(input_file, backup_file)
    
    # Save ordered version
    with open(input_file, 'w') as f:
        json.dump(ordered_data, f, indent=2)
    
    new_size = os.path.getsize(input_file) / (1024 * 1024)
    
    # Verify
    with open(input_file, 'r') as f:
        verify_data = json.load(f)
    
    first_key_after = list(verify_data.keys())[0]
    last_key_after = list(verify_data.keys())[-1]
    
    print(f"\nReordering Complete")
    print(f"After reordering:")
    print(f"  First ID in file: {first_key_after}")
    print(f"  Last ID in file: {last_key_after}")
    print(f"  Total records: {len(verify_data):,}")
    print(f"  File size: {new_size:.2f} MB")
    
    print(f"\n Original file backed up to: {os.path.basename(backup_file)}")
    print(f"Reordered file saved to: {os.path.basename(input_file)}")

if __name__ == '__main__':
    # Reorder all_academics_merged.json
    reorder_json_by_id("mgp_cache/all_academics_merged.json")
    
    # You can also reorder other files:
    # reorder_json_by_id("mgp_cache/all_academics_checkpoints.json")