#!/usr/bin/env python3

import json
import os
import glob
from pathlib import Path

def merge_checkpoints(cache_dir="mgp_cache", output_file="all_academics_merged.json"):
    """
    Merge all checkpoint files, removing duplicates.
    Uses ID as the key, so duplicates are automatically removed.
    """
    
    print(f"\nMerging Checkpoint Files:")
    print(f"Looking in: {cache_dir}/\n")
    
    # Find all checkpoint files
    checkpoint_pattern = os.path.join(cache_dir, "checkpoint_*.json")
    checkpoint_files = sorted(glob.glob(checkpoint_pattern))
    
    if not checkpoint_files:
        print(" No checkpoint files found!")
        return
    
    print(f"Found {len(checkpoint_files)} checkpoint files:")
    for f in checkpoint_files:
        file_size = os.path.getsize(f) / (1024 * 1024)  # Size in MB
        print(f"  - {os.path.basename(f)} ({file_size:.2f} MB)")
    
    # Dictionary to store all unique academics (ID is the key)
    all_academics = {}
    
    print(f"\nMerging files...")
    
    # Process each checkpoint file
    for i, checkpoint_file in enumerate(checkpoint_files, 1):
        try:
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            
            # Count academics before merging
            before_count = len(all_academics)
            
            # Merge the data (dict keys ensure no duplicates)
            if isinstance(data, dict):
                all_academics.update(data)
            
            # Count how many new ones were added
            new_count = len(all_academics) - before_count
            
            filename = os.path.basename(checkpoint_file)
            print(f"  [{i}/{len(checkpoint_files)}] {filename}: "
                  f"{len(data)} records → {new_count} new, "
                  f"{len(data) - new_count} duplicates")
            
        except Exception as e:
            print(f"Error reading {checkpoint_file}: {e}")
            continue
    
    # Also merge all_academics.json if it exists
    all_academics_file = os.path.join(cache_dir, "all_academics.json")
    if os.path.exists(all_academics_file):
        print(f"\nMerging existing all_academics.json...")
        try:
            with open(all_academics_file, 'r') as f:
                existing_data = json.load(f)
            before_count = len(all_academics)
            all_academics.update(existing_data)
            new_count = len(all_academics) - before_count
            print(f"  Added {new_count} additional records from all_academics.json")
        except Exception as e:
            print(f"   Error reading all_academics.json: {e}")
    
    # Save merged result
    output_path = os.path.join(cache_dir, output_file)
    print(f"\nSaving merged data to: {output_file}")
    
    with open(output_path, 'w') as f:
        json.dump(all_academics, f, indent=2)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    
    # Statistics
    print(f"\nMerge Complete:")
    print(f"Total unique academics: {len(all_academics)}")
    print(f"Output file: {output_path}")
    print(f"File size: {file_size:.2f} MB")
    
    # Find ID range
    if all_academics:
        ids = [int(id) for id in all_academics.keys()]
        print(f"ID range: {min(ids)} to {max(ids)}")
        print(f"Coverage: {len(ids)} IDs out of {max(ids) - min(ids) + 1} possible "
              f"({100 * len(ids) / (max(ids) - min(ids) + 1):.1f}%)")
    
    return all_academics

def find_gaps(cache_dir="mgp_cache"):
    """
    Find missing ID ranges in your cached data.
    """
    all_academics_file = os.path.join(cache_dir, "all_academics_merged.json")
    
    if not os.path.exists(all_academics_file):
        print("Run merge_checkpoints() first!")
        return
    
    with open(all_academics_file, 'r') as f:
        data = json.load(f)
    
    ids = sorted([int(id) for id in data.keys()])
    
    print(f"\n=== Finding Gaps ===")
    print(f"Analyzing {len(ids)} IDs from {ids[0]} to {ids[-1]}")
    
    # Find gaps
    gaps = []
    for i in range(len(ids) - 1):
        if ids[i+1] - ids[i] > 1:
            gap_start = ids[i] + 1
            gap_end = ids[i+1] - 1
            gap_size = gap_end - gap_start + 1
            gaps.append((gap_start, gap_end, gap_size))
    
    if gaps:
        print(f"\nFound {len(gaps)} gaps:")
        for gap_start, gap_end, gap_size in gaps[:20]:  # Show first 20
            if gap_size == 1:
                print(f"  Missing ID: {gap_start}")
            else:
                print(f"  Missing IDs: {gap_start}-{gap_end} ({gap_size} IDs)")
        
        if len(gaps) > 20:
            print(f"  ... and {len(gaps) - 20} more gaps")
        
        total_missing = sum(gap[2] for gap in gaps)
        print(f"\nTotal missing IDs: {total_missing}")
    else:
        print("\nNo gaps found! Complete sequential coverage.")

if __name__ == '__main__':
    # Merge all checkpoints
    merged_data = merge_checkpoints(cache_dir="mgp_cache")
    
    # Find any gaps in the data
    if merged_data:
        find_gaps(cache_dir="mgp_cache")