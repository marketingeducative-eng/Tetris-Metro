"""
Test Goal Mode Feature

Tests the goal mode implementation including:
- Tag-to-icon mapping
- Goal marker visualization
- Goal celebration
- Recommendations UI
"""
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.clock import Clock
from game_propera_parada import ProximaParadaGame, get_station_icon
from data.metro_loader import load_metro_network, normalize_station_id


def test_tag_to_icon_mapping():
    """Test tag-to-icon mapping function"""
    print("Testing tag-to-icon mapping...")
    
    test_cases = [
        (['Gaudi', 'modernisme'], '🎨'),  # Gaudi should take priority
        (['platja', 'mar'], '🏖️'),  # Beach
        (['Park_Guell', 'miradors'], '🏞️'),  # Park
        (['Gotic', 'historia'], '🏰'),  # Gothic
        (['Camp_Nou', 'futbol'], '⚽'),  # Football
        ([], '📍'),  # Empty should return default
    ]
    
    for tags, expected in test_cases:
        result = get_station_icon(tags)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Tags {tags} → {result} (expected {expected})")


def test_tourist_recommendations():
    """Test that recommendations can be generated"""
    print("\nTesting tourist recommendations...")
    
    # Load metro network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro_network = load_metro_network(str(data_path))
    line = metro_network.get_line("L3")
    
    if not line:
        print("  ✗ Could not load L3")
        return
    
    # Create a temporary game state
    from game_propera_parada import GameState, Renderer
    from kivy.uix.floatlayout import FloatLayout
    
    parent = FloatLayout()
    state = GameState(line, line_id="L3")
    renderer = Renderer(parent, state)
    
    # Get recommendations
    recommendations = renderer.get_tourist_recommendations(3)
    
    print(f"  Found {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"    {i}. {rec['station']} {rec['icon']}")
        print(f"       → {rec['one_liner']}")
        print(f"       Priority: {rec['priority']}")
    
    if len(recommendations) >= 3:
        print("  ✓ Successfully generated recommendations")
    else:
        print(f"  ✗ Expected 3 recommendations, got {len(recommendations)}")


def test_goal_mode_state():
    """Test goal mode state management"""
    print("\nTesting goal mode state...")
    
    # Load metro network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro_network = load_metro_network(str(data_path))
    line = metro_network.get_line("L3")
    
    from game_propera_parada import GameState
    
    # Test 1: Normal mode (no goal)
    state = GameState(line, line_id="L3")
    if not state.goal_mode and state.goal_station_id is None:
        print("  ✓ Normal mode initialized correctly")
    else:
        print("  ✗ Normal mode initialization failed")
    
    # Test 2: Set goal mode
    state.goal_mode = True
    state.goal_station_id = "SAGRADA_FAMILIA"
    
    if state.goal_mode and state.goal_station_id == "SAGRADA_FAMILIA":
        print("  ✓ Goal mode set correctly")
    else:
        print("  ✗ Goal mode setting failed")
    
    # Test 3: Check goal reached detection
    for idx, station in enumerate(line.stations):
        station_id = normalize_station_id(station.name)
        if station_id == "SAGRADA_FAMILIA":
            print(f"  ✓ Found goal station at index {idx}: {station.name}")
            break
    else:
        print("  ✗ Could not find goal station in line")


def test_line_map_goal_marker():
    """Test that LineMapView supports goal markers"""
    print("\nTesting line map goal marker...")
    
    from line_map_view import LineMapView
    
    line_view = LineMapView()
    
    # Check that goal properties exist
    if hasattr(line_view, 'goal_index'):
        print("  ✓ goal_index property exists")
    else:
        print("  ✗ goal_index property missing")
    
    if hasattr(line_view, 'goal_pulse'):
        print("  ✓ goal_pulse property exists")
    else:
        print("  ✗ goal_pulse property missing")
    
    # Check that draw method includes goal
    if hasattr(line_view, '_draw_goal_slot'):
        print("  ✓ _draw_goal_slot method exists")
    else:
        print("  ✗ _draw_goal_slot method missing")
    
    if hasattr(line_view, '_start_goal_pulse'):
        print("  ✓ _start_goal_pulse method exists")
    else:
        print("  ✗ _start_goal_pulse method missing")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("GOAL MODE FEATURE TEST SUITE")
    print("=" * 60)
    
    test_tag_to_icon_mapping()
    test_tourist_recommendations()
    test_goal_mode_state()
    test_line_map_goal_marker()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == '__main__':
    run_all_tests()

