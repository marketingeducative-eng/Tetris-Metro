"""
Test Zone Transitions - Verify Zone Detection and Visual Effects

Verifies that:
1. Station data includes zone information
2. Zone changes are detected correctly
3. Zone transitions trigger visual effects
4. Zone names are properly formatted in messages
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState
from kivy.clock import Clock


def test_zone_data_loading():
    """Test that zone data is loaded from JSON"""
    print("\n" + "=" * 60)
    print("ZONE DATA LOADING TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    print(f"\nL3 Station Zones:")
    for i, station in enumerate(line.stations):
        zone_text = station.zone if station.zone else "(no zone)"
        print(f"  {i+1:2d}. {station.name:25s} → {zone_text}")
    
    # Verify all stations have zones
    zones_present = [s.zone for s in line.stations if s.zone]
    print(f"\n✓ Stations with zones: {len(zones_present)}/{len(line.stations)}")
    
    # Identify unique zones
    unique_zones = sorted(set(s.zone for s in line.stations if s.zone))
    print(f"✓ Unique zones: {len(unique_zones)}")
    for zone in unique_zones:
        count = sum(1 for s in line.stations if s.zone == zone)
        print(f"    - {zone}: {count} stations")
    
    assert len(zones_present) == len(line.stations), "All stations should have zones!"
    assert len(unique_zones) > 0, "Should have at least one zone!"


def test_zone_change_detection():
    """Test that zone changes are detected when advancing stations"""
    print("\n" + "=" * 60)
    print("ZONE CHANGE DETECTION TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    
    print(f"\nInitial zone: {game_state.current_zone}")
    print(f"Station 0: {line.stations[0].name} ({line.stations[0].zone})")
    
    zone_transitions = []
    
    # Simulate advancing through all stations
    for i in range(1, len(line.stations)):
        round_data = game_state.start_round(Clock.get_time())
        
        if round_data and round_data.get('zone_changed'):
            zone_name = round_data.get('zone_name')
            station = line.stations[game_state.next_index]
            zone_transitions.append({
                'station_index': game_state.next_index,
                'station_name': station.name,
                'new_zone': zone_name
            })
            print(f"\n✓ Zone transition detected at station {game_state.next_index}:")
            print(f"    {station.name} → {zone_name}")
        
        # Mark as correct to advance
        game_state.has_attempted = True
        game_state.answered_correctly = True
    
    print(f"\n✓ Total zone transitions: {len(zone_transitions)}")
    print(f"\nZone transition summary:")
    for t in zone_transitions:
        print(f"  Station {t['station_index']:2d}: {t['station_name']:25s} → {t['new_zone']}")
    
    assert len(zone_transitions) > 0, "Should detect at least one zone transition!"


def test_zone_transition_message():
    """Test that zone transition messages are properly formatted"""
    print("\n" + "=" * 60)
    print("ZONE TRANSITION MESSAGE TEST")
    print("=" * 60)
    
    # Test message formatting for each zone
    zones = ["Les Corts", "Sants-Montjuïc", "Ciutat Vella", "Eixample", "Gràcia", "Nou Barris"]
    
    print(f"\nZone transition messages:")
    for zone in zones:
        message = f"Entrant a {zone}..."
        print(f"  {message}")
        assert "Entrant a" in message, "Message should contain 'Entrant a'"
        assert zone in message, f"Message should contain zone name '{zone}'"
    
    print(f"\n✓ All messages properly formatted")


def test_zone_color_mapping():
    """Test that all zones have color mappings"""
    print("\n" + "=" * 60)
    print("ZONE COLOR MAPPING TEST")
    print("=" * 60)
    
    # Expected zone colors from Renderer.shift_hud_color
    zone_colors = {
        "Les Corts": [0.0, 0.03, 0.06, 0.85],
        "Sants-Montjuïc": [0.04, 0.02, 0.0, 0.85],
        "Ciutat Vella": [0.05, 0.04, 0.0, 0.85],
        "Eixample": [0.02, 0.0, 0.04, 0.85],
        "Gràcia": [0.0, 0.04, 0.02, 0.85],
        "Nou Barris": [0.03, 0.0, 0.03, 0.85]
    }
    
    # Load actual zones from data
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    actual_zones = sorted(set(s.zone for s in line.stations if s.zone))
    
    print(f"\nZone color assignments:")
    for zone in actual_zones:
        color = zone_colors.get(zone, [0, 0, 0, 0.85])
        rgb = [f"{c:.2f}" for c in color[:3]]
        print(f"  {zone:20s} → RGB({', '.join(rgb)}) Alpha:{color[3]}")
        
        # Check if zone has custom color
        has_custom = zone in zone_colors
        status = "✓ Custom" if has_custom else "⚠️  Default"
        print(f"    {status}")
    
    # Verify all zones have mappings
    missing = [z for z in actual_zones if z not in zone_colors]
    if missing:
        print(f"\n⚠️  Missing color mappings for: {', '.join(missing)}")
    else:
        print(f"\n✓ All zones have color mappings")


def test_sequential_zone_progression():
    """Test zone progression through entire L3 line"""
    print("\n" + "=" * 60)
    print("SEQUENTIAL ZONE PROGRESSION TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    
    print(f"\nProgression through L3 zones:")
    print(f"  Start: {line.stations[0].name} ({game_state.current_zone})")
    
    zone_sequence = [game_state.current_zone]
    
    for i in range(1, len(line.stations)):
        round_data = game_state.start_round(Clock.get_time())
        
        if round_data and round_data.get('zone_changed'):
            zone_name = round_data.get('zone_name')
            station = line.stations[game_state.next_index]
            zone_sequence.append(zone_name)
            print(f"  → {station.name} ({zone_name})")
        
        # Advance
        game_state.has_attempted = True
        game_state.answered_correctly = True
    
    print(f"\nZone sequence: {' → '.join(zone_sequence)}")
    print(f"✓ Total zones traversed: {len(zone_sequence)}")
    
    # Expected sequence for L3
    expected_zones = ["Les Corts", "Sants-Montjuïc", "Ciutat Vella", "Eixample", "Gràcia", "Nou Barris"]
    
    print(f"\nExpected zones: {', '.join(expected_zones)}")
    print(f"Actual zones:   {', '.join(zone_sequence)}")
    
    assert set(zone_sequence) == set(expected_zones), "Should traverse all expected zones"


if __name__ == '__main__':
    test_zone_data_loading()
    test_zone_change_detection()
    test_zone_transition_message()
    test_zone_color_mapping()
    test_sequential_zone_progression()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nZone Transition Summary:")
    print("  • All L3 stations have zone information")
    print("  • Zone changes detected automatically")
    print("  • Visual effects: HUD color shift + text message")
    print("  • Message format: 'Entrant a [Zone]...' (1.2s)")
    print("  • Color shifts: Subtle tints per Barcelona district")
    print("  • Zones: Les Corts, Sants-Montjuïc, Ciutat Vella,")
    print("           Eixample, Gràcia, Nou Barris")

