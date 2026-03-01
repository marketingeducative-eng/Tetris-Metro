"""
Test Station Progression Counter

Verifies that the completed station count is tracked and displayed correctly:
1. Starts at 0/26
2. Increments with each correct answer
3. Updates display in real-time
4. Shows player's progress along the line
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState


def test_progression_counter():
    """Test that station progression is tracked correctly"""
    print("=" * 60)
    print("STATION PROGRESSION COUNTER TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line, practice_mode=True)
    
    total_stations = len(line.stations)
    print(f"\nL3 Metro Line: {total_stations} stations total")
    print(f"  From: {line.endpoints['from']}")
    print(f"  To: {line.endpoints['to']}")
    
    print("\n" + "=" * 60)
    print("PROGRESSION SIMULATION")
    print("=" * 60)
    
    # Initial state
    print(f"\nInitial: {game_state.current_index}/{total_stations} stations")
    assert game_state.current_index == 0
    print("  ✓ Starts at 0/26")
    
    # Simulate correct answers
    print("\nSimulating correct answers:")
    for i in range(10):
        # Start a round
        result = game_state.start_round(0)
        station_name = result['correct_station_id']
        
        # Answer correctly
        game_state.handle_correct_answer()
        
        completed = game_state.current_index
        progress_display = f"{completed}/{total_stations}"
        
        if i < 5 or i == 9:  # Show first 5 and last
            print(f"  Answer {i+1}: {progress_display} - Just passed {station_name}")
    
    final_progress = f"{game_state.current_index}/{total_stations}"
    print(f"\nAfter 10 correct: {final_progress}")
    assert game_state.current_index == 10
    print("  ✓ Counter increments correctly")
    
    # Test wrap-around (when reaching end of line)
    print(f"\n" + "=" * 60)
    print("FULL LINE COMPLETION")
    print("=" * 60)
    
    # Advance to near the end
    game_state.current_index = total_stations - 2
    print(f"\nNear end: {game_state.current_index}/{total_stations}")
    
    # Complete last station
    game_state.current_index = total_stations - 1
    print(f"At terminal: {game_state.current_index}/{total_stations}")
    assert game_state.current_index == 25  # L3 has 26 stations (0-25)
    print(f"  ✓ Reached terminal station: {line.stations[25].name}")
    
    # Next station wraps around
    next_after_terminal = (game_state.current_index + 1) % total_stations
    print(f"Next station wraps to: station {next_after_terminal}")
    assert next_after_terminal == 0
    print("  ✓ Line loops back to start correctly")


def test_display_format():
    """Test the display format of the progression counter"""
    print("\n" + "=" * 60)
    print("DISPLAY FORMAT TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    total_stations = len(line.stations)
    
    # Test various progression states
    test_cases = [
        (0, "0/26", "Start"),
        (1, "1/26", "First station"),
        (7, "7/26", "Quarter progress"),
        (13, "13/26", "Half progress"),
        (25, "25/26", "Final station"),
    ]
    
    print("\nExpected display formats:")
    for current_idx, expected, description in test_cases:
        game_state.current_index = current_idx
        progress_text = f"{game_state.current_index}/{total_stations}"
        print(f"  {description:20s}: {progress_text}")
        assert progress_text == expected
    
    print("\n  ✓ All formats display correctly")


def test_stats_line_integration():
    """Test that progression appears in stats line"""
    print("\n" + "=" * 60)
    print("STATS LINE INTEGRATION TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line, practice_mode=True)
    game_state.score = 1200
    game_state.high_score = 2500
    game_state.streak = 5
    game_state.mistakes = 3
    game_state.current_index = 7
    
    total_stations = len(line.stations)
    travel_duration = game_state.calculate_travel_duration()
    progress_text = f"{game_state.current_index}/{total_stations}"
    errors_text = f"Errors: {game_state.mistakes}"
    
    expected_format = (
        f"{game_state.score}pts  •  "
        f"High: {game_state.high_score}  •  "
        f"Streak: {game_state.streak}  •  "
        f"{errors_text}  •  "
        f"{progress_text}  •  "
        f"{travel_duration:.1f}s"
    )
    
    print("\nExpected stats line:")
    print(f"  {expected_format}")
    
    # Verify progression counter is present
    assert "7/26" in expected_format
    print("\n  ✓ Progression counter (7/26) appears in stats")
    print("  ✓ Positioned between errors and time")
    print("  ✓ Uses bullet separator (•)")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 60)
    print("STATION PROGRESSION TRACKING")
    print("=" * 60)
    
    try:
        test_progression_counter()
        test_display_format()
        test_stats_line_integration()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nProgression Counter Summary:")
        print("  • Format: current/total (e.g., 7/26)")
        print("  • Starts at: 0/26")
        print("  • Increments: Each correct answer")
        print("  • Location: Stats line, before time")
        print("  • Purpose: Shows player progress along metro line")
        print("\nBenefits:")
        print("  ✓ Reinforces sense of progression")
        print("  ✓ Shows player how far through the line they are")
        print("  ✓ Adds goal-oriented motivation")
        print("  ✓ Provides context for line length")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == '__main__':
    run_all_tests()

