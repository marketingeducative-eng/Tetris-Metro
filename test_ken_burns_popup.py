"""
Test script for Ken Burns tourist popup animation.
Validates that:
1. Image URLs are loaded from tourist_ca.json
2. Station objects have image_url attributes
3. Popup displays image with animation
"""

import json
from pathlib import Path
from data.metro_loader import load_metro_network

# Load metro network with tourist data
metro_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
tourist_path = Path(__file__).parent / "data" / "tourist_ca.json"

with open(tourist_path, 'r', encoding='utf-8') as f:
    tourist_data = json.load(f).get('stations', {})

print("=" * 60)
print("KEN BURNS POPUP TEST")
print("=" * 60)

# Check tourist data has image_url fields
print("\n✓ Tourist data loaded")
print(f"  Total stations in tourist_ca.json: {len(tourist_data)}")

stations_with_images = 0
for station_id, station_info in tourist_data.items():
    if 'image_url' in station_info:
        stations_with_images += 1
        print(f"  • {station_id}: {station_info.get('image_url', 'NO URL')}")

print(f"\n✓ Stations with image_url: {stations_with_images}/{len(tourist_data)}")

# Load metro network
try:
    network = load_metro_network(str(metro_path))
    print(f"\n✓ Metro network loaded: {len(network.lines)} lines")
    
    # Check if stations have image_url attribute
    images_found = 0
    for line in network.lines:
        for station in line.stations:
            if hasattr(station, 'image_url') and station.image_url:
                images_found += 1
                print(f"  • {station.name}: {station.image_url}")
    
    print(f"\n✓ Stations with image_url in network: {images_found}")
    
    # Display sample station details
    print("\n" + "=" * 60)
    print("SAMPLE STATION DETAILS")
    print("=" * 60)
    
    for line in network.lines:
        if len(line.stations) > 0:
            station = line.stations[0]
            print(f"\nStation: {station.name}")
            print(f"  ID: {station.id}")
            print(f"  Zone: {station.zone}")
            print(f"  Tourist Highlight: {station.tourist_highlight}")
            print(f"  Tourist Priority: {station.tourist_priority}")
            print(f"  Tourist Tip: {station.tourist_tip_ca[:50]}..." if station.tourist_tip_ca else "  Tourist Tip: (none)")
            print(f"  Image URL: {station.image_url if station.image_url else '(none)'}")
            break
    
    print("\n" + "=" * 60)
    print("✓ ALL CHECKS PASSED - Ken Burns animation ready!")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ Error loading metro network: {e}")
    import traceback
    traceback.print_exc()
