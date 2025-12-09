#!/usr/bin/env python3
"""
Extract universities from MGP everything.json (nested structure) and geocode them.
Saves progress every 100 universities.
Caches NOT-FOUND universities in a separate file.
Resumes automatically using checkpoint file.
"""

import json
import time
import requests
import os
import sys
from collections import defaultdict

CHECKPOINT_FILE = "university_coordinates_partial.json"
OUTPUT_JS = "university_coordinates.js"
NOT_FOUND_JSON = "universities_not_found.json"
NOT_FOUND_JS = "universities_not_found.js"


# -----------------------------------------------------------
# Load MGP master JSON
# -----------------------------------------------------------
def load_data(json_file):
    print(f"Loading {json_file}...")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"✓ Loaded {len(data)} records")
    return data


# -----------------------------------------------------------
# Extract all unique universities from nested MGP structure
# -----------------------------------------------------------
def extract_universities(data):
    universities = set()
    counts = defaultdict(int)

    for _, person in data.items():
        mgp = person.get("MGP_academic", {})
        student = mgp.get("student_data", {})
        degrees = student.get("degrees", [])

        for degree in degrees:
            schools = degree.get("schools", [])
            if isinstance(schools, list):
                for school in schools:
                    if school and school.lower() not in ["unknown", "", "none"]:
                        universities.add(school)
                        counts[school] += 1

    universities = sorted(universities, key=lambda u: counts[u], reverse=True)

    print(f"✓ Found {len(universities)} unique universities")
    return universities


# -----------------------------------------------------------
# Geocode via Nominatim API
# -----------------------------------------------------------
def geocode(university_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": university_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "MGP-Geocoder/1.0 (contact: example@example.com)"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None
    except Exception:
        return None


# -----------------------------------------------------------
# Save checkpoint of FOUND + NOT FOUND universities
# -----------------------------------------------------------
def save_checkpoint(found, not_found):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(found, f, indent=2)
    print(f"💾 Saved checkpoint ({len(found)} found entries)")

    with open(NOT_FOUND_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted(list(not_found)), f, indent=2)
    print(f"💾 Saved NOT-FOUND list ({len(not_found)} universities)")


# -----------------------------------------------------------
# Write final JS file for FOUND universities
# -----------------------------------------------------------
def write_js(found):
    valid_count = sum(1 for v in found.values() if v)

    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write("// Auto-generated university coordinates\n")
        f.write(f"// Contains {valid_count} universities with valid coordinates\n\n")
        f.write("const UNIVERSITY_COORDS = {\n")

        for name, coords in sorted(found.items()):
            if coords is None:
                continue
            safe = name.replace("'", "\\'")
            f.write(f"  '{safe}': [{coords[0]}, {coords[1]}],\n")

        f.write("};\n\nexport default UNIVERSITY_COORDS;\n")

    print(f"\n🎉 Saved final JS file: {OUTPUT_JS}")


# -----------------------------------------------------------
# Write NOT FOUND as a JS module as well
# -----------------------------------------------------------
def write_not_found_js(not_found):
    with open(NOT_FOUND_JS, "w", encoding="utf-8") as f:
        f.write("// Universities that could NOT be geocoded\n")
        f.write(f"// Count: {len(not_found)}\n\n")
        f.write("export const UNIVERSITIES_NOT_FOUND = [\n")
        for name in sorted(not_found):
            safe = name.replace("'", "\\'")
            f.write(f"  '{safe}',\n")
        f.write("];\n")

    print(f"📄 Saved NOT FOUND JS file: {NOT_FOUND_JS}")


# -----------------------------------------------------------
# MAIN SCRIPT
# -----------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_and_geocode_mgp.py everything.json")
        return

    json_path = sys.argv[1]

    # Load everything.json
    data = load_data(json_path)

    # Extract university list
    universities = extract_universities(data)

    # Load checkpoint if exists
    found = {}
    not_found = set()

    if os.path.exists(CHECKPOINT_FILE):
        print(f"🔄 Loading checkpoint: {CHECKPOINT_FILE}")
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            found = json.load(f)

    if os.path.exists(NOT_FOUND_JSON):
        print(f"🔄 Loading NOT-FOUND record: {NOT_FOUND_JSON}")
        with open(NOT_FOUND_JSON, "r", encoding="utf-8") as f:
            not_found = set(json.load(f))

    # Determine remaining universities
    remaining = [
        u for u in universities
        if u not in found and u not in not_found
    ]

    print(f"\n→ Need to geocode {len(remaining)} universities\n")

    # Loop through remaining universities
    for i, uni in enumerate(remaining, 1):
        print(f"[{i}/{len(remaining)}] {uni[:60]}...", end=" ")

        coords = geocode(uni)

        if coords:
            print(f"✓ {coords}")
            found[uni] = coords
        else:
            print("✗ Not found")
            not_found.add(uni)

        # Save every 100 entries
        if i % 100 == 0:
            save_checkpoint(found, not_found)

        time.sleep(1.1)

    # Final save
    save_checkpoint(found, not_found)
    write_js(found)
    write_not_found_js(not_found)

    print("\n✨ DONE: All possible universities processed!")


if __name__ == "__main__":
    main()
