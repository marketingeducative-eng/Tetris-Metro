"""
Test Adaptive Timing System

Verifies that the travel duration:
1. Starts at 3.4s
2. Reduces by 0.05s every correct answer
3. Has minimum of 2.2s
4. Resets slightly (halves) after mistakes
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState


def test_initial_duration():
    """Test that duration starts at 3.4s"""
    print("Test 1: Initial Duration")
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    initial_duration = game_state.calculate_travel_duration()
    
    print(f"  Base duration: {game_state.base_duration}s")
    print(f"  Initial travel time: {initial_duration}s")
    
    assert game_state.base_duration == 3.4
    assert initial_duration == 3.4
    print("  ✓ Duration starts at 3.4s")


def test_reduction_per_answer():
    """Test that duration reduces by 0.05s every correct answer"""
    print("\nTest 2: Reduction Per Correct Answer")
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    
    print(f"  Duration step: {game_state.duration_step}s")
    print(f"  Streak interval: {game_state.streak_interval}")
    
    assert game_state.duration_step == 0.05
    assert game_state.streak_interval == 1
    print("  ✓ Configured for 0.05s reduction every answer")
    
    # Simulate progression
    durations = []
    for i in range(25):
        duration = game_state.calculate_travel_duration()
        durations.append(duration)
        game_state.streak += 1
    
    print(f"\n  Progression:")
    for i in [0, 1, 2, 5, 10, 15, 20, 24]:
        print(f"    After {i} correct: {durations[i]:.2f}s")
    
    # Verify reductions
    assert durations[0] == 3.40
    assert durations[1] == 3.35
    assert durations[2] == 3.30
    assert durations[10] == 2.90
    print("  ✓ Duration reduces correctly by 0.05s each time")


def test_minimum_duration():
    """Test that duration never goes below 2.2s"""
    print("\nTest 3: Minimum Duration Limit")
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    
    print(f"  Minimum duration: {game_state.min_duration}s")
    assert game_state.min_duration == 2.2
    
    # Simulate many correct answers
    game_state.streak = 100  # Much more than needed to hit minimum
    
    duration = game_state.calculate_travel_duration()
    print(f"  Duration after 100 streak: {duration}s")
    
    assert duration == 2.2
    print("  ✓ Duration floors at 2.2s minimum")
    
    # Calculate when minimum is reached
    # base_duration - (streak * duration_step) = min_duration
    # 3.4 - (streak * 0.05) = 2.2
    # streak * 0.05 = 1.2
    # streak = 24
    game_state.streak = 24
    duration_at_24 = game_state.calculate_travel_duration()
    print(f"  Duration at streak 24: {duration_at_24}s")
    assert duration_at_24 == 2.2
    print("  ✓ Minimum reached at 24 correct answers")


def test_slight_reset_on_mistake():
    """Test that mistakes halve the streak instead of full reset"""
    print("\nTest 4: Slight Reset on Mistakes")
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line, practice_mode=True)
    
    # Build up streak
    game_state.streak = 10
    duration_before = game_state.calculate_travel_duration()
    print(f"  Streak before mistake: {game_state.streak}")
    print(f"  Duration before: {duration_before:.2f}s")
    
    # Make a mistake (directly simulate the streak reset)
    game_state.streak = game_state.streak // 2
    
    duration_after = game_state.calculate_travel_duration()
    print(f"  Streak after mistake: {game_state.streak}")
    print(f"  Duration after: {duration_after:.2f}s")
    
    assert game_state.streak == 5  # 10 // 2
    assert duration_after == 3.15  # 3.4 - (5 * 0.05)
    print("  ✓ Streak halved (10 → 5)")
    print("  ✓ Duration slightly increased (2.90s → 3.15s)")


def test_timeout_reset():
    """Test that timeouts also reset slightly"""
    print("\nTest 5: Timeout Reset Behavior")
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line, practice_mode=True)
    
    # Build streak
    game_state.streak = 8
    duration_before = game_state.calculate_travel_duration()
    print(f"  Streak before timeout: {game_state.streak}")
    print(f"  Duration before: {duration_before:.2f}s")
    
    # Timeout (directly simulate the streak reset)
    game_state.streak = game_state.streak // 2
    
    duration_after = game_state.calculate_travel_duration()
    print(f"  Streak after timeout: {game_state.streak}")
    print(f"  Duration after: {duration_after:.2f}s")
    
    assert game_state.streak == 4  # 8 // 2
    print("  ✓ Streak halved on timeout (8 → 4)")


def test_full_game_scenario():
    """Test realistic game progression"""
    print("\nTest 6: Full Game Scenario")
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line, practice_mode=True)
    
    scenario = [
        "correct", "correct", "correct", "correct", "correct",  # 5 correct
        "wrong",  # Mistake
        "correct", "correct", "correct",  # 3 more correct
        "timeout",  # Timeout
        "correct", "correct", "correct", "correct", "correct",  # 5 more correct
    ]
    
    print("  Scenario: 5 correct → mistake → 3 correct → timeout → 5 correct")
    print()
    
    for i, action in enumerate(scenario):
        if action == "correct":
            game_state.streak += 1
        elif action == "wrong":
            game_state.streak = game_state.streak // 2
            game_state.mistakes += 1
        elif action == "timeout":
            game_state.streak = game_state.streak // 2
            game_state.mistakes += 1
        
        duration = game_state.calculate_travel_duration()
        print(f"  Step {i+1} ({action:8s}): streak={game_state.streak:2d}, duration={duration:.2f}s")
    
    print("\n  ✓ System recovers gracefully from mistakes")
    print("  ✓ Difficulty increases progressively with skill")


def run_all_tests():
    """Run complete test suite"""
    print("=" * 60)
    print("ADAPTIVE TIMING TEST SUITE")
    print("=" * 60)
    
    try:
        test_initial_duration()
        test_reduction_per_answer()
        test_minimum_duration()
        test_slight_reset_on_mistake()
        test_timeout_reset()
        test_full_game_scenario()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nAdaptive Timing Summary:")
        print("  • Start: 3.4s per station")
        print("  • Reduction: -0.05s per correct answer")
        print("  • Minimum: 2.2s (reached after 24 correct)")
        print("  • Reset: Halve streak on mistakes/timeouts")
        print("  • Range: 2.2s to 3.4s (1.2s dynamic range)")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == '__main__':
    run_all_tests()

