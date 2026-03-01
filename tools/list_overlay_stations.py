#!/usr/bin/env python3
"""List all stations in the tourist overlay"""
import json
from pathlib import Path

base_dir = Path(__file__).parent.parent
tourist_path = base_dir / "data" / "tourist_ca.json"

with open(tourist_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

stations = data['stations']

print(f"Total stations in overlay: {len(stations)}\n")
print("All station IDs (normalized keys):")
print("=" * 70)

for i, key in enumerate(sorted(stations.keys()), 1):
    station = stations[key]
    priority = station['priority']
    highlight = '*' if station.get('highlight', False) else ' '
    print(f"{i:2d}. [{highlight}] P{priority} | {key}")
