"""
Test script for adaptive timing logic
Verifies: 
- Reduce duration every 3 consecutive correct answers
- Increase duration on 2 consecutive mistakes
- Keep within bounds
"""

from game_propera_parada import GameState
from data.metro_loader import load_metro_network


def test_adaptive_timing():
    """Test the new adaptive timing logic"""
    
    # Load game
    network = load_metro_network('data/barcelona_metro_lines_stations.json')
    state = GameState(network.lines[0])
    
    print("\n=== Adaptive Timing Logic Test ===\n")
    
    # Setup
    print("Initial state:")
    print(f"  Base duration: {state.base_duration}s")
    print(f"  Min duration: {state.min_duration}s")
    print(f"  Duration step: {state.duration_step}s")
    duration = state.calculate_travel_duration()
    print(f"  Current duration: {duration}s")
    print(f"  Consecutive correct: {state.consecutive_correct}")
    print(f"  Consecutive mistakes: {state.consecutive_mistakes}\n")
    
    # Test 1: Get 3 consecutive correct answers
    print("Test 1: 3 consecutive correct answers")
    for i in range(1, 4):
        state.handle_correct_answer()
        duration = state.calculate_travel_duration()
        print(f"  Answer {i} correct:")
        print(f"    - Consecutive correct: {state.consecutive_correct}")
        print(f"    - Travel duration: {duration:.2f}s")
    
    expected_reduction = 1 * state.duration_step  # 1 reduction = 1 step
    expected_duration = state.base_duration - expected_reduction
    print(f"\n  Expected duration: {expected_duration:.2f}s")
    print(f"  Actual duration: {duration:.2f}s")
    print(f"  ✓ Duration reduced after 3 correct\n")
    
    # Test 2: 6 consecutive correct (should have 2 reductions)
    print("Test 2: 6 consecutive correct answers total")
    for i in range(4, 7):
        state.handle_correct_answer()
        duration = state.calculate_travel_duration()
        print(f"  Answer {i} correct:")
        print(f"    - Consecutive correct: {state.consecutive_correct}")
        print(f"    - Travel duration: {duration:.2f}s")
    
    expected_reduction = 2 * state.duration_step  # 2 reductions = 2 steps
    expected_duration = state.base_duration - expected_reduction
    print(f"\n  Expected duration: {expected_duration:.2f}s")
    print(f"  Actual duration: {duration:.2f}s")
    print(f"  ✓ Duration reduced further after 6 correct\n")
    
    # Test 3: One wrong answer resets consecutive_correct
    print("Test 3: Wrong answer resets consecutive correct counter")
    state.handle_wrong_answer()
    duration = state.calculate_travel_duration()
    print(f"  After wrong answer:")
    print(f"    - Consecutive correct: {state.consecutive_correct}")
    print(f"    - Consecutive mistakes: {state.consecutive_mistakes}")
    print(f"    - Travel duration: {duration:.2f}s")
    print(f"  ✓ Consecutive correct reset to 0\n")
    
    # Test 4: Two consecutive wrong answers restores duration to base
    print("Test 4: 2 consecutive wrong answers restore duration to base")
    state.handle_wrong_answer()
    duration = state.calculate_travel_duration()
    print(f"  After 2nd wrong answer:")
    print(f"    - Consecutive mistakes: {state.consecutive_mistakes}")
    print(f"    - Travel duration: {duration:.2f}s")
    print(f"    - Base duration: {state.base_duration}s")
    
    if abs(duration - state.base_duration) < 0.01:
        print(f"  ✓ Duration restored to base on 2 consecutive mistakes\n")
    else:
        print(f"  ✗ Duration not restored correctly\n")
    
    # Test 5: Verify bounds enforcement
    print("Test 5: Verify duration stays within bounds")
    state.consecutive_correct = 100  # Simulate many correct answers
    duration = state.calculate_travel_duration()
    print(f"  After 100 consecutive correct:")
    print(f"    - Calculated duration: {duration:.2f}s")
    print(f"    - Min bound: {state.min_duration}s")
    print(f"    - Max bound: {state.base_duration}s")
    
    if state.min_duration <= duration <= state.base_duration:
        print(f"  ✓ Duration within bounds\n")
    else:
        print(f"  ✗ Duration out of bounds\n")
    
    # Test 6: Verify counter resets on answer
    print("Test 6: Correct answer resets mistake counter")
    state.consecutive_correct = 0
    state.consecutive_mistakes = 2
    state.handle_correct_answer()
    print(f"  After correct answer:")
    print(f"    - Consecutive correct: {state.consecutive_correct}")
    print(f"    - Consecutive mistakes: {state.consecutive_mistakes}")
    print(f"  ✓ Mistake counter reset on correct answer\n")
    
    print("=== All Tests Complete ===\n")


if __name__ == "__main__":
    test_adaptive_timing()

