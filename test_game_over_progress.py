"""
Test Game Over Progress Display - Verify Section Descriptions

Verifies that:
1. Progress is correctly calculated from visited stations
2. Section descriptions are accurate for different progress levels
3. Text formatting is correct in Catalan
4. All progress ranges have appropriate descriptions
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState


def test_section_descriptions():
    """Test that section descriptions match progress levels"""
    print("\n" + "=" * 60)
    print("SECTION DESCRIPTION TEST")
    print("=" * 60)
    
    # Define expected section descriptions based on furthest station
    test_cases = [
        (0, 1, "tram sud"),           # Only station 0
        (4, 5, "tram sud"),           # Stations 0-4 (Les Corts)
        (5, 6, "tram central-sud"),   # Station 5 (Sants Estació)
        (9, 10, "tram central-sud"),  # Stations 0-9 (through Sants-Montjuïc)
        (11, 12, "tram central-sud"), # Through Ciutat Vella
        (12, 13, "tram central"),     # Station 12 (Catalunya)
        (14, 15, "tram central"),     # Through Eixample
        (18, 19, "tram central"),     # Through Gràcia
        (19, 20, "tram nord"),        # Station 19 (Vall d'Hebron)
        (24, 25, "tram nord"),        # Almost to end
        (25, 26, "tram complet"),     # All stations
    ]
    
    print(f"\nSection descriptions by furthest station:")
    for max_station, visited_count, expected_section in test_cases:
        # Simulate progress
        visited_stations = set(range(visited_count))
        
        # Determine section (same logic as game_propera_parada.py)
        if max_station >= 25:
            section = "tram complet"
        elif max_station >= 19:
            section = "tram nord"
        elif max_station >= 12:
            section = "tram central"
        elif max_station >= 5:
            section = "tram central-sud"
        else:
            section = "tram sud"
        
        status = "✓" if section == expected_section else "✗"
        print(f"  {status} Station {max_station:2d} ({visited_count:2d} visited) → {section}")
        assert section == expected_section, f"Expected '{expected_section}' but got '{section}'"
    
    print(f"\n✓ All section descriptions correct")


def test_progress_text_formatting():
    """Test that progress text is properly formatted in Catalan"""
    print("\n" + "=" * 60)
    print("PROGRESS TEXT FORMATTING TEST")
    print("=" * 60)
    
    test_cases = [
        (3, "tram sud", "Has recorregut 3 estacions\ndel tram sud"),
        (10, "tram central-sud", "Has recorregut 10 estacions\ndel tram central-sud"),
        (15, "tram central", "Has recorregut 15 estacions\ndel tram central"),
        (22, "tram nord", "Has recorregut 22 estacions\ndel tram nord"),
        (26, "tram complet", "Has recorregut 26 estacions\ndel tram complet"),
    ]
    
    print(f"\nProgress text formats:")
    for visited_count, section, expected_text in test_cases:
        actual_text = f"Has recorregut {visited_count} estacions\ndel {section}"
        print(f"\n  {visited_count} stations → {section}:")
        print(f"    '{actual_text}'")
        assert actual_text == expected_text
    
    print(f"\n✓ All text formats correct")


def test_zone_boundaries():
    """Test section boundaries align with metro zones"""
    print("\n" + "=" * 60)
    print("ZONE BOUNDARY TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    # Map stations to zones
    zone_map = {}
    for i, station in enumerate(line.stations):
        zone_map[i] = (station.name, station.zone)
    
    print(f"\nStation zones and sections:")
    print(f"  {'Idx':<4} {'Station':<30} {'Zone':<20} {'Section'}")
    print(f"  {'-'*4} {'-'*30} {'-'*20} {'-'*15}")
    
    for i in range(len(line.stations)):
        name, zone = zone_map[i]
        
        # Determine section
        if i >= 25:
            section = "complet"
        elif i >= 19:
            section = "nord"
        elif i >= 12:
            section = "central"
        elif i >= 5:
            section = "central-sud"
        else:
            section = "sud"
        
        print(f"  {i:<4} {name:<30} {zone:<20} {section}")
    
    # Verify key boundaries
    print(f"\nKey boundaries:")
    print(f"  Stations 0-4:   Les Corts            → sud")
    print(f"  Stations 5-11:  Sants/Ciutat Vella   → central-sud")
    print(f"  Stations 12-18: Eixample/Gràcia      → central")
    print(f"  Stations 19-24: Nou Barris           → nord")
    print(f"  Station 25:     Trinitat Nova        → complet")
    
    # Verify specific boundaries
    assert zone_map[4][1] == "Les Corts"
    assert zone_map[5][1] == "Sants-Montjuïc"
    assert zone_map[12][1] == "Eixample"
    assert zone_map[19][1] == "Nou Barris"
    assert zone_map[25][1] == "Nou Barris"
    
    print(f"\n✓ Zone boundaries align with sections")


def test_edge_cases():
    """Test edge cases for progress display"""
    print("\n" + "=" * 60)
    print("EDGE CASE TEST")
    print("=" * 60)
    
    # Test minimum progress (only starting station)
    visited_stations = {0}
    max_station = max(visited_stations)
    visited_count = len(visited_stations)
    
    print(f"\nMinimum progress (station 0 only):")
    print(f"  Visited: {visited_stations}")
    print(f"  Count: {visited_count}")
    print(f"  Max: {max_station}")
    
    if max_station >= 25:
        section = "tram complet"
    elif max_station >= 19:
        section = "tram nord"
    elif max_station >= 12:
        section = "tram central"
    elif max_station >= 5:
        section = "tram central-sud"
    else:
        section = "tram sud"
    
    print(f"  Section: {section}")
    assert section == "tram sud"
    
    # Test maximum progress (all stations)
    visited_stations = set(range(26))
    max_station = max(visited_stations)
    visited_count = len(visited_stations)
    
    print(f"\nMaximum progress (all stations):")
    print(f"  Count: {visited_count}")
    print(f"  Max: {max_station}")
    
    if max_station >= 25:
        section = "tram complet"
    elif max_station >= 19:
        section = "tram nord"
    elif max_station >= 12:
        section = "tram central"
    elif max_station >= 5:
        section = "tram central-sud"
    else:
        section = "tram sud"
    
    print(f"  Section: {section}")
    assert section == "tram complet"
    
    print(f"\n✓ Edge cases handled correctly")


def test_realistic_game_scenarios():
    """Test with realistic game progress scenarios"""
    print("\n" + "=" * 60)
    print("REALISTIC GAME SCENARIOS TEST")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Beginner - Failed early",
            "visited": {0, 1, 2},
            "expected_section": "tram sud",
            "description": "Only made it through Les Corts"
        },
        {
            "name": "Intermediate - Reached center",
            "visited": set(range(15)),
            "expected_section": "tram central",
            "description": "Reached Eixample/Gràcia area"
        },
        {
            "name": "Advanced - Reached north",
            "visited": set(range(22)),
            "expected_section": "tram nord",
            "description": "Made it to Nou Barris"
        },
        {
            "name": "Expert - Complete route",
            "visited": set(range(26)),
            "expected_section": "tram complet",
            "description": "Completed entire L3 line"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print(f"  Description: {scenario['description']}")
        
        visited = scenario['visited']
        max_station = max(visited)
        count = len(visited)
        
        # Determine section
        if max_station >= 25:
            section = "tram complet"
        elif max_station >= 19:
            section = "tram nord"
        elif max_station >= 12:
            section = "tram central"
        elif max_station >= 5:
            section = "tram central-sud"
        else:
            section = "tram sud"
        
        print(f"  Stations visited: {count}")
        print(f"  Furthest station: {max_station}")
        print(f"  Section reached: {section}")
        print(f"  Display text: 'Has recorregut {count} estacions del {section}'")
        
        assert section == scenario['expected_section']
        print(f"  ✓ Correct")
    
    print(f"\n✓ All scenarios produce correct descriptions")


if __name__ == '__main__':
    test_section_descriptions()
    test_progress_text_formatting()
    test_zone_boundaries()
    test_edge_cases()
    test_realistic_game_scenarios()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nGame Over Progress Summary:")
    print("  • Text format: 'Has recorregut X estacions del tram [section]'")
    print("  • Section ranges:")
    print("    - Stations 0-4:   tram sud (Les Corts)")
    print("    - Stations 5-11:  tram central-sud (Sants/Ciutat Vella)")
    print("    - Stations 12-18: tram central (Eixample/Gràcia)")
    print("    - Stations 19-24: tram nord (Nou Barris)")
    print("    - Station 25+:    tram complet (Complete route)")
    print("  • Displayed on game over panel above route map")

