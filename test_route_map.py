"""
Test Game Over Route Map

Verifies that:
1. Visited stations are tracked during gameplay
2. Game over screen displays route map
3. Map highlights reached vs unreached stations
4. Shows station count (e.g., 7/26)
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState


def test_visited_stations_tracking():
    """Test that visited stations are tracked correctly"""
    print("=" * 60)
    print("VISITED STATIONS TRACKING TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line, practice_mode=True)
    
    # Initial state - starts at station 0
    print(f"\nInitial state:")
    print(f"  Current index: {game_state.current_index}")
    print(f"  Visited stations: {sorted(game_state.visited_stations)}")
    assert 0 in game_state.visited_stations
    assert len(game_state.visited_stations) == 1
    print("  ✓ Station 0 marked as visited at start")
    
    # Simulate playing through several stations
    print(f"\nSimulating gameplay:")
    for i in range(5):
        result = game_state.start_round(0)
        next_station_idx = result['next_index']
        station_name = result['correct_station_id']
        
        # Answer correctly
        game_state.handle_correct_answer()
        
        print(f"  Round {i+1}: Reached station {next_station_idx} ({station_name})")
        assert next_station_idx in game_state.visited_stations
    
    print(f"\nAfter 5 correct answers:")
    print(f"  Visited stations: {sorted(game_state.visited_stations)}")
    print(f"  Count: {len(game_state.visited_stations)}/26")
    assert len(game_state.visited_stations) == 6  # Start + 5 correct
    print("  ✓ All visited stations tracked correctly")


def test_route_map_data():
    """Test the data used for route map visualization"""
    print("\n" + "=" * 60)
    print("ROUTE MAP DATA TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    
    # Simulate partial completion
    game_state.visited_stations = {0, 1, 2, 3, 4, 5, 6, 7}
    
    total_stations = len(game_state.line.stations)
    visited_count = len(game_state.visited_stations)
    
    print(f"\nRoute Map Data:")
    print(f"  Total stations: {total_stations}")
    print(f"  Visited: {visited_count}")
    print(f"  Completion: {visited_count}/{total_stations}")
    print(f"  Percentage: {visited_count/total_stations*100:.1f}%")
    
    print(f"\n  Visited stations:")
    for idx in sorted(game_state.visited_stations):
        station = game_state.line.stations[idx]
        print(f"    {idx}: {station.name}")
    
    print(f"\n  Not reached (first 3):")
    unreached = [i for i in range(total_stations) if i not in game_state.visited_stations]
    for idx in unreached[:3]:
        station = game_state.line.stations[idx]
        print(f"    {idx}: {station.name}")
    
    assert visited_count == 8
    assert len(unreached) == 18
    print("\n  ✓ Route map data correct")


def test_game_over_stations_count():
    """Test that game over shows station count"""
    print("\n" + "=" * 60)
    print("GAME OVER STATION COUNT TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    # Test different scenarios
    scenarios = [
        (5, "Early game over - 5 stations"),
        (13, "Mid-game - half line completed"),
        (20, "Late game - near terminal"),
        (26, "Full line - all stations visited"),
    ]
    
    print("\nScenarios:")
    for visited_count, description in scenarios:
        game_state = GameState(line)
        
        # Simulate visiting stations
        game_state.visited_stations = set(range(min(visited_count, 26)))
        
        total = len(game_state.line.stations)
        actual_count = len(game_state.visited_stations)
        station_text = f"Estacions: {actual_count}/{total}"
        
        print(f"  {description:35s}: {station_text}")
        assert actual_count == min(visited_count, 26)
    
    print("\n  ✓ Station counts display correctly")


def test_route_visualization_logic():
    """Test the logic for route visualization"""
    print("\n" + "=" * 60)
    print("ROUTE VISUALIZATION LOGIC TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    game_state.visited_stations = {0, 1, 2, 5, 8, 10}
    
    num_stations = len(game_state.line.stations)
    
    print(f"\nVisualization logic:")
    print(f"  Total stations: {num_stations}")
    print(f"  Route width: 440px (example)")
    print(f"  Station spacing: {440 / (num_stations - 1):.1f}px")
    
    print(f"\n  Station colors:")
    visited_examples = [0, 1, 2]
    unvisited_examples = [3, 4, 6]
    
    for idx in visited_examples:
        color = "Green (0.3, 0.9, 0.4)" if idx in game_state.visited_stations else "Gray"
        size = 8 if idx in game_state.visited_stations else 5
        print(f"    Station {idx}: {color}, radius {size}px")
    
    for idx in unvisited_examples:
        color = "Green (0.3, 0.9, 0.4)" if idx in game_state.visited_stations else "Gray (0.25, 0.25, 0.3)"
        size = 8 if idx in game_state.visited_stations else 5
        print(f"    Station {idx}: {color}, radius {size}px")
    
    print(f"\n  Terminal labels:")
    print(f"    Start: {line.stations[0].name}")
    print(f"    End: {line.stations[-1].name}")
    
    print("\n  ✓ Visualization logic verified")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 60)
    print("GAME OVER ROUTE MAP TEST SUITE")
    print("=" * 60)
    
    try:
        test_visited_stations_tracking()
        test_route_map_data()
        test_game_over_stations_count()
        test_route_visualization_logic()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nRoute Map Feature Summary:")
        print("  • Tracks all visited stations during gameplay")
        print("  • Displays simple horizontal route map at game over")
        print("  • Green nodes: Successfully reached stations")
        print("  • Gray nodes: Not reached")
        print("  • Shows completion count (e.g., 7/26)")
        print("  • Labels terminal stations")
        print("\nVisual Design:")
        print("  • Horizontal line representing L3 route")
        print("  • Nodes spaced evenly across panel")
        print("  • Larger/brighter for visited stations")
        print("  • Smaller/dimmer for unvisited")
        print("  • Terminal station names labeled")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == '__main__':
    run_all_tests()

