#!/usr/bin/env python3
"""
Analyze tourist overlay coverage by metro line
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from data.metro_loader import normalize_station_id

def main():
    base_dir = Path(__file__).parent.parent
    metro_path = base_dir / "data" / "barcelona_metro_lines_stations.json"
    tourist_path = base_dir / "data" / "tourist_ca.json"
    
    # Load data
    with open(metro_path, 'r', encoding='utf-8') as f:
        metro_data = json.load(f)
    
    with open(tourist_path, 'r', encoding='utf-8') as f:
        tourist_data = json.load(f)
    
    tourist_keys = set(tourist_data['stations'].keys())
    
    print("=" * 70)
    print("TOURIST OVERLAY COVERAGE BY LINE")
    print("=" * 70)
    print()
    
    for line in metro_data['lines']:
        line_id = line['id']
        line_name = line['name']
        
        # Extract station names
        station_names = []
        for station_data in line['stations']:
            if isinstance(station_data, str):
                station_names.append(station_data)
            elif isinstance(station_data, dict):
                name = station_data.get('name', '')
                if name:
                    station_names.append(name)
        
        # Check which are in tourist overlay
        covered_stations = []
        for name in station_names:
            station_id = normalize_station_id(name)
            if station_id in tourist_keys:
                covered_stations.append(name)
        
        coverage_pct = (len(covered_stations) / len(station_names) * 100) if station_names else 0
        
        print(f"{line_id:6s} - {line_name:20s} | {len(covered_stations):2d}/{len(station_names):2d} stations ({coverage_pct:.0f}%)")
        if covered_stations:
            for station in covered_stations:
                print(f"         • {station}")
        print()

if __name__ == "__main__":
    main()
