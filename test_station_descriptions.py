"""
Test Station Descriptions
Verify that station descriptions are loaded and displayed correctly
"""
from pathlib import Path
from data.metro_loader import load_metro_network


def main():
    print("=" * 70)
    print("STATION DESCRIPTIONS TEST")
    print("=" * 70)
    
    # Load network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    network = load_metro_network(str(data_path))
    
    # Test L3
    l3 = network.get_line("L3")
    
    if not l3:
        print("❌ Line L3 not found")
        return
    
    print(f"\n🚇 {l3.name} ({l3.id})")
    print(f"   Color: {l3.color}")
    print(f"   Stations: {len(l3.stations)}")
    print("\n" + "=" * 70)
    print("STATIONS WITH DESCRIPTIONS")
    print("=" * 70)
    
    # Display all stations with descriptions
    for i, station in enumerate(l3.stations):
        desc_display = f" → {station.description}" if station.description else " (no description)"
        print(f"{i+1:2d}. {station.name:<25} {desc_display}")
    
    # Test specific stations
    print("\n" + "=" * 70)
    print("TESTING STATION ACCESS")
    print("=" * 70)
    
    # Test get_station_index
    test_name = "Liceu"
    index = l3.get_station_index(test_name)
    print(f"\n🔍 Finding '{test_name}':")
    if index is not None:
        print(f"   ✅ Found at index: {index}")
        station = l3.get_station(index)
        if station:
            print(f"   Name: {station.name}")
            print(f"   Description: {station.description}")
    else:
        print(f"   ❌ Not found")
    
    # Test get_station
    print(f"\n🔍 Get station at index 5:")
    station = l3.get_station(5)
    if station:
        print(f"   ✅ {station.name}")
        print(f"   Description: {station.description}")
    else:
        print(f"   ❌ Invalid index")
    
    # Test get_station_names
    print(f"\n📋 Get all station names:")
    names = l3.get_station_names()
    print(f"   ✅ Retrieved {len(names)} station names")
    print(f"   First 5: {names[:5]}")
    
    # Test description length validation
    print("\n" + "=" * 70)
    print("DESCRIPTION LENGTH VALIDATION")
    print("=" * 70)
    
    max_length = 0
    longest_station = None
    
    for station in l3.stations:
        if len(station.description) > max_length:
            max_length = len(station.description)
            longest_station = station
    
    print(f"   Longest description: {max_length} chars")
    if longest_station:
        print(f"   Station: {longest_station.name}")
        print(f"   Description: '{longest_station.description}'")
    
    if max_length <= 40:
        print(f"   ✅ All descriptions within 40 char limit")
    else:
        print(f"   ❌ Some descriptions exceed 40 char limit!")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
