#!/usr/bin/env python3
"""
Tourist Overlay Checker
Validates that all keys in tourist_ca.json match actual station names
"""
import json
import sys
from pathlib import Path

# Add parent directory to path to import from data module
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.metro_loader import normalize_station_id


def load_metro_stations(metro_path):
    """Load all station names from metro dataset"""
    with open(metro_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    station_names = []
    for line in data.get("lines", []):
        for station_data in line.get("stations", []):
            if isinstance(station_data, str):
                station_names.append(station_data)
            elif isinstance(station_data, dict):
                name = station_data.get("name", "")
                if name:
                    station_names.append(name)
    
    return station_names


def load_tourist_overlay(tourist_path):
    """Load tourist overlay keys"""
    if not tourist_path.exists():
        return {}
    
    with open(tourist_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get("stations", {}) if isinstance(data, dict) else {}


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    metro_path = base_dir / "data" / "barcelona_metro_lines_stations.json"
    tourist_path = base_dir / "data" / "tourist_ca.json"
    
    print("=" * 70)
    print("TOURIST OVERLAY VALIDATION")
    print("=" * 70)
    print(f"\nMetro dataset: {metro_path}")
    print(f"Tourist overlay: {tourist_path}")
    
    # Load data
    try:
        station_names = load_metro_stations(metro_path)
        tourist_data = load_tourist_overlay(tourist_path)
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        return 1
    
    # Get unique station names and normalize
    unique_station_names = sorted(set(station_names))
    station_id_to_name = {}
    for name in unique_station_names:
        station_id = normalize_station_id(name)
        station_id_to_name[station_id] = name
    
    print(f"\nTotal unique stations in metro dataset: {len(unique_station_names)}")
    print(f"Total keys in tourist overlay: {len(tourist_data)}")
    
    # Find matches
    matched_keys = []
    unmatched_overlay_keys = []
    
    for overlay_key in sorted(tourist_data.keys()):
        if overlay_key in station_id_to_name:
            matched_keys.append(overlay_key)
        else:
            unmatched_overlay_keys.append(overlay_key)
    
    # Find stations without overlay
    stations_without_overlay = []
    for name in unique_station_names:
        station_id = normalize_station_id(name)
        if station_id not in tourist_data:
            stations_without_overlay.append(name)
    
    # Report results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\n✓ Matched keys: {len(matched_keys)}")
    if matched_keys:
        print("  Overlay keys that matched stations:")
        for key in matched_keys:
            station_name = station_id_to_name[key]
            print(f"    - {key:30s} → {station_name}")
    
    print(f"\n{'❌' if unmatched_overlay_keys else '✓'} Unmatched overlay keys: {len(unmatched_overlay_keys)}")
    if unmatched_overlay_keys:
        print("  Keys in tourist_ca.json that don't match any station:")
        for key in unmatched_overlay_keys:
            print(f"    - {key}")
    
    print(f"\n⚠ Stations without overlay entry: {len(stations_without_overlay)}")
    if stations_without_overlay:
        print(f"  Showing first 20 of {len(stations_without_overlay)}:")
        for name in stations_without_overlay[:20]:
            station_id = normalize_station_id(name)
            print(f"    - {name:35s} (normalized: {station_id})")
    
    # Summary
    print("\n" + "=" * 70)
    if unmatched_overlay_keys:
        print("❌ VALIDATION FAILED: Found unmatched overlay keys")
        print("=" * 70)
        return 1
    else:
        print("✅ VALIDATION PASSED: All overlay keys match stations")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    sys.exit(main())
