#!/usr/bin/env python3

import json
import os
import glob

def concat_all_backups(cache_dir="mgp_cache", output_file="all_academics_merged_complete.json"):
    """
    Concatenate all backup files (backup1, backup2, backup3, etc.) into one file.
    Automatically removes duplicates.
    """
    
    print(f"\n=== Concatenating All Backup Files ===\n")
    
    # Find all backup files
    backup_pattern = os.path.join(cache_dir, "all_academics_merged_backup*.json")
    backup_files = sorted(glob.glob(backup_pattern))
    
    # Filter out .zip files and only keep .json
    backup_files = [f for f in backup_files if f.endswith('.json')]
    
    if not backup_files:
        print("❌ No backup files found!")
        return
    
    print(f"Found {len(backup_files)} backup files:")
    for bf in backup_files:
        print(f"  - {os.path.basename(bf)}")
    print()
    
    # Combine all backups
    all_data = {}
    
    for i, backup_file in enumerate(backup_files, 1):
        print(f"Loading {os.path.basename(backup_file)}...", end=" ")
        
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            before_count = len(all_data)
            all_data.update(backup_data)
            new_count = len(all_data) - before_count
            duplicate_count = len(backup_data) - new_count
            
            # Get ID range
            ids = sorted([int(id) for id in backup_data.keys()])
            
            print(f"✓")
            print(f"  Records: {len(backup_data):,}")
            print(f"  ID range: {min(ids):,} to {max(ids):,}")
            print(f"  New: {new_count:,}, Duplicates: {duplicate_count:,}")
            print()
            
        except Exception as e:
            print(f"✗ Error: {e}\n")
    
    # Save combined file
    output_path = os.path.join(cache_dir, output_file)
    print(f"Saving combined file to {output_file}...")
    
    with open(output_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    
    # Statistics
    print(f"\n=== Concatenation Complete ===")
    print(f"Total unique academics: {len(all_data):,}")
    print(f"File: {output_path}")
    print(f"File size: {file_size:.2f} MB")
    
    if all_data:
        ids = sorted([int(id) for id in all_data.keys()])
        print(f"ID range: {min(ids):,} to {max(ids):,}")
        print(f"Coverage: {len(ids):,} IDs out of {max(ids) - min(ids) + 1:,} possible "
              f"({100 * len(ids) / (max(ids) - min(ids) + 1):.1f}%)")
        
        # Find gaps
        gaps = []
        for i in range(len(ids) - 1):
            if ids[i+1] - ids[i] > 1:
                gap_start = ids[i] + 1
                gap_end = ids[i+1] - 1
                gap_size = gap_end - gap_start + 1
                if gap_size > 100:  # Only show large gaps
                    gaps.append((gap_start, gap_end, gap_size))
        
        if gaps:
            print(f"\nLarge gaps found (>100 IDs):")
            for gap_start, gap_end, gap_size in gaps[:5]:
                print(f"  Missing: {gap_start:,} to {gap_end:,} ({gap_size:,} IDs)")
            if len(gaps) > 5:
                print(f"  ... and {len(gaps)-5} more gaps")
        else:
            print("\n✓ No large gaps!")
    
    print(f"\n✓ All backups combined into: {output_file}")

if __name__ == '__main__':
    concat_all_backups(
        cache_dir="mgp_cache",
        output_file="all_academics_merged_complete.json"
    )