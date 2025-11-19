#!/usr/bin/env python3

import json
import os

def check_missing_ids(backup_file="mgp_cache/all_academics_merged.json"):
    """
    Check how many IDs are missing in the backup file.
    """
    print(f"Analyzing: {os.path.basename(backup_file)}")
    
    if not os.path.exists(backup_file):
        print(f"File not found: {backup_file}")
        return
    
    # Load the data
    print("Loading file:")
    with open(backup_file, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data):,} academics\n")
    
    # Get all IDs
    existing_ids = sorted([int(id) for id in data.keys()])
    
    min_id = existing_ids[0]
    max_id = existing_ids[-1]
    total_range = max_id - min_id + 1
    
    print(f"ID Range: {min_id:,} to {max_id:,}")
    print(f"Total possible IDs in range: {total_range:,}")
    print(f"IDs present: {len(existing_ids):,}")
    print(f"IDs missing: {total_range - len(existing_ids):,}")
    print(f"Coverage: {100 * len(existing_ids) / total_range:.2f}%")
    
    # Find all missing IDs
    all_possible_ids = set(range(min_id, max_id + 1))
    existing_id_set = set(existing_ids)
    missing_ids = sorted(all_possible_ids - existing_id_set)
    
    if missing_ids:
        print(f"Missing IDs")
        print(f"Total missing: {len(missing_ids):,}\n")
        
        # Group consecutive missing IDs into ranges
        gaps = []
        if missing_ids:
            gap_start = missing_ids[0]
            gap_end = missing_ids[0]
            
            for i in range(1, len(missing_ids)):
                if missing_ids[i] == gap_end + 1:
                    # Consecutive, extend the gap
                    gap_end = missing_ids[i]
                else:
                    # Gap ended, save it
                    gaps.append((gap_start, gap_end))
                    gap_start = missing_ids[i]
                    gap_end = missing_ids[i]
            
            # Don't forget the last gap
            gaps.append((gap_start, gap_end))
        
        print(f"Number of gaps: {len(gaps)}\n")
        
        # Show all gaps
        if len(gaps) <= 50:
            print("All gaps:")
            for gap_start, gap_end in gaps:
                if gap_start == gap_end:
                    print(f"  Missing ID: {gap_start:,}")
                else:
                    gap_size = gap_end - gap_start + 1
                    print(f"  Missing IDs: {gap_start:,} to {gap_end:,} ({gap_size:,} IDs)")
        else:
            print("First 30 gaps:")
            for gap_start, gap_end in gaps[:30]:
                if gap_start == gap_end:
                    print(f"  Missing ID: {gap_start:,}")
                else:
                    gap_size = gap_end - gap_start + 1
                    print(f"  Missing IDs: {gap_start:,} to {gap_end:,} ({gap_size:,} IDs)")
            print(f"  ... and {len(gaps)-30} more gaps")
        
        # Save missing IDs to file
        output_file = backup_file.replace('.json', '_missing_ids.json')
        with open(output_file, 'w') as f:
            json.dump({
                "total_missing": len(missing_ids),
                "gaps": [
                    {
                        "start": gap_start,
                        "end": gap_end,
                        "size": gap_end - gap_start + 1
                    }
                    for gap_start, gap_end in gaps
                ],
                "missing_ids": missing_ids
            }, f, indent=2)
        
        print(f"Detailed missing IDs saved to: {os.path.basename(output_file)}")
        
        # Show largest gaps
        large_gaps = sorted([(start, end, end-start+1) for start, end in gaps], 
                          key=lambda x: x[2], reverse=True)
        
        if large_gaps[0][2] > 1:
            print(f"\nLargest gaps:")
            for gap_start, gap_end, gap_size in large_gaps[:5]:
                print(f"  {gap_start:,} to {gap_end:,} ({gap_size:,} IDs)")
    else:
        print("No missing IDs! Perfect coverage")
    
    # File size
    file_size = os.path.getsize(backup_file) / (1024 * 1024)
    print(f"\nFile size: {file_size:.2f} MB")

if __name__ == '__main__':
    check_missing_ids("mgp_cache/all_academics_merged.json")