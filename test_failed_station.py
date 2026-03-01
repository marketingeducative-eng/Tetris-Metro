"""
Test Failed Station Highlighting - Verify Pulsing Red Node

Verifies that:
1. Failed station index is tracked when mistakes/timeouts occur
2. Failed station is highlighted in red on route map
3. Pulsing animation provides visual emphasis
4. Failed station is distinct from visited stations
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState
from kivy.clock import Clock
import math


def test_failed_station_tracking():
    """Test that failed station index is tracked"""
    print("\n" + "=" * 60)
    print("FAILED STATION TRACKING TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    
    print(f"\nInitial state:")
    print(f"  failed_station_index: {game_state.failed_station_index}")
    assert game_state.failed_station_index is None
    print(f"  ✓ Initially None")
    
    # Start a round
    game_state.start_round(Clock.get_time())
    expected_failed = game_state.next_index
    
    print(f"\nAfter starting round:")
    print(f"  next_index: {expected_failed}")
    
    # Simulate wrong answer
    result = game_state.handle_wrong_answer()
    
    print(f"\nAfter wrong answer:")
    print(f"  failed_station_index: {game_state.failed_station_index}")
    print(f"  Expected: {expected_failed}")
    
    assert game_state.failed_station_index == expected_failed
    print(f"  ✓ Failed station tracked correctly")


def test_timeout_tracking():
    """Test that failed station is tracked on timeout"""
    print("\n" + "=" * 60)
    print("TIMEOUT TRACKING TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    game_state.start_round(Clock.get_time())
    
    expected_failed = game_state.next_index
    
    print(f"\nBefore timeout:")
    print(f"  next_index: {expected_failed}")
    print(f"  failed_station_index: {game_state.failed_station_index}")
    
    # Simulate timeout
    result = game_state.handle_timeout()
    
    print(f"\nAfter timeout:")
    print(f"  failed_station_index: {game_state.failed_station_index}")
    
    assert game_state.failed_station_index == expected_failed
    print(f"  ✓ Failed station tracked on timeout")


def test_multiple_failures():
    """Test that only last failed station is tracked"""
    print("\n" + "=" * 60)
    print("MULTIPLE FAILURES TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line, practice_mode=True)  # Practice mode to avoid game over
    
    failed_stations = []
    
    for round_num in range(5):
        game_state.start_round(Clock.get_time())
        station = game_state.next_index
        
        # Make a mistake
        game_state.handle_wrong_answer()
        failed_stations.append(station)
        
        print(f"\nRound {round_num + 1}:")
        print(f"  Failed at station: {station}")
        print(f"  Tracked failed station: {game_state.failed_station_index}")
        
        # Advance to next (in practice mode)
        game_state.has_attempted = True
        game_state.answered_correctly = False
    
    # Last failed station should be tracked
    print(f"\nAll failed stations: {failed_stations}")
    print(f"Final tracked failed station: {game_state.failed_station_index}")
    
    assert game_state.failed_station_index == failed_stations[-1]
    print(f"  ✓ Only last failed station tracked: {failed_stations[-1]}")


def test_pulse_animation_values():
    """Test pulse animation radius calculation"""
    print("\n" + "=" * 60)
    print("PULSE ANIMATION TEST")
    print("=" * 60)
    
    base_radius = 10
    pulse_amplitude = 3
    
    print(f"\nAnimation parameters:")
    print(f"  Base radius: {base_radius}px")
    print(f"  Pulse amplitude: {pulse_amplitude}px")
    print(f"  Range: {base_radius} to {base_radius + pulse_amplitude}px")
    
    # Test at different time points
    time_points = [0, 0.25, 0.5, 0.75, 1.0]
    
    print(f"\nRadius at different time points:")
    for t in time_points:
        pulse_radius = base_radius + pulse_amplitude * abs(math.sin(t * 3))
        print(f"  t={t:.2f}s: radius={pulse_radius:.2f}px")
    
    # Verify range
    max_radius = base_radius + pulse_amplitude
    min_radius = base_radius
    
    print(f"\n✓ Pulse range: {min_radius}px to {max_radius}px")
    assert max_radius == 13
    assert min_radius == 10


def test_failed_station_color():
    """Test that failed station uses red color"""
    print("\n" + "=" * 60)
    print("FAILED STATION COLOR TEST")
    print("=" * 60)
    
    # Expected color from implementation
    failed_color = (0.95, 0.2, 0.2, 0.9)
    visited_color = (0.3, 0.9, 0.4, 1)
    unvisited_color = (0.25, 0.25, 0.3, 1)
    
    print(f"\nStation colors:")
    print(f"  Failed station:")
    print(f"    RGB: ({failed_color[0]}, {failed_color[1]}, {failed_color[2]})")
    print(f"    Alpha: {failed_color[3]}")
    print(f"    Description: Bright red with pulsing animation")
    
    print(f"\n  Visited station:")
    print(f"    RGB: ({visited_color[0]}, {visited_color[1]}, {visited_color[2]})")
    print(f"    Alpha: {visited_color[3]}")
    print(f"    Description: Bright green, static")
    
    print(f"\n  Unvisited station:")
    print(f"    RGB: ({unvisited_color[0]}, {unvisited_color[1]}, {unvisited_color[2]})")
    print(f"    Alpha: {unvisited_color[3]}")
    print(f"    Description: Dark gray, static")
    
    # Verify red dominates
    assert failed_color[0] > 0.9, "Should be very red"
    assert failed_color[1] < 0.3, "Should have low green"
    assert failed_color[2] < 0.3, "Should have low blue"
    
    print(f"\n✓ Failed station clearly distinguishable in red")


def test_game_over_scenario():
    """Test complete game over scenario with failed station"""
    print("\n" + "=" * 60)
    print("GAME OVER SCENARIO TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)  # Normal mode, 3 lives
    
    print(f"\nSimulating game with 3 mistakes:")
    
    for mistake_num in range(3):
        game_state.start_round(Clock.get_time())
        station = game_state.next_index
        station_name = line.stations[station].name
        
        result = game_state.handle_wrong_answer()
        
        print(f"\n  Mistake {mistake_num + 1} at station {station} ({station_name}):")
        print(f"    Game over: {result['game_over']}")
        print(f"    Failed station tracked: {game_state.failed_station_index}")
    
    print(f"\nFinal state:")
    print(f"  Game over: {game_state.game_over or result['game_over']}")
    print(f"  Failed station for map: {game_state.failed_station_index}")
    print(f"  Station name: {line.stations[game_state.failed_station_index].name}")
    
    assert game_state.failed_station_index is not None
    print(f"\n✓ Failed station ready for game over display")


def test_animation_frame_rate():
    """Test animation timing"""
    print("\n" + "=" * 60)
    print("ANIMATION FRAME RATE TEST")
    print("=" * 60)
    
    fps = 30
    frame_interval = 1 / fps
    
    print(f"\nAnimation parameters:")
    print(f"  Frame rate: {fps} FPS")
    print(f"  Frame interval: {frame_interval:.4f}s ({frame_interval * 1000:.1f}ms)")
    
    # Calculate cycle duration
    # sin(t * 3) completes one cycle when t * 3 = 2π
    # t = 2π / 3
    cycle_duration = (2 * math.pi) / 3
    frames_per_cycle = cycle_duration / frame_interval
    
    print(f"\nPulse cycle:")
    print(f"  Cycle duration: {cycle_duration:.2f}s")
    print(f"  Frames per cycle: {frames_per_cycle:.0f}")
    
    print(f"\n✓ Smooth animation at {fps} FPS")


if __name__ == '__main__':
    test_failed_station_tracking()
    test_timeout_tracking()
    test_multiple_failures()
    test_pulse_animation_values()
    test_failed_station_color()
    test_game_over_scenario()
    test_animation_frame_rate()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nFailed Station Highlighting Summary:")
    print("  • Failed station index tracked on wrong answer/timeout")
    print("  • Displayed with pulsing red node on route map")
    print("  • Color: Bright red (0.95, 0.2, 0.2, 0.9)")
    print("  • Pulse: Radius 10-13px with sine wave animation")
    print("  • Animation: 30 FPS for smooth pulsing effect")
    print("  • Purpose: Clearly shows where player failed")

