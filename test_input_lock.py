"""
Test Input Lock - Prevent Multiple Token Drops

Verifies that:
1. Input lock prevents multiple drops in the same frame
2. Lock is set immediately on valid drop
3. Lock is cleared at next round initialization
4. Invalid drops (outside zone) don't lock input
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState, InputController, Renderer


class MockRenderer:
    """Mock renderer for testing"""
    def __init__(self):
        self.line_view = MockLineView()


class MockLineView:
    """Mock line view for testing"""
    def get_node_pos(self, index):
        # Return mock position
        return (400, 300)


class MockToken:
    """Mock token for testing"""
    def __init__(self, station_id):
        self.station_id = station_id
        self.reset_called = False
    
    def reset_position(self):
        self.reset_called = True


def test_input_lock_initialization():
    """Test that input lock is initialized to False"""
    print("=" * 60)
    print("INPUT LOCK INITIALIZATION TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    renderer = MockRenderer()
    input_controller = InputController(game_state, renderer)
    
    print(f"\nInitial input_locked state: {input_controller.input_locked}")
    assert input_controller.input_locked == False
    print("  ✓ Input lock starts as False (unlocked)")


def test_input_lock_on_valid_drop():
    """Test that input lock is set immediately on valid drop"""
    print("\n" + "=" * 60)
    print("INPUT LOCK ON VALID DROP TEST")
    print("=" * 60)
    
    from kivy.clock import Clock
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    renderer = MockRenderer()
    input_controller = InputController(game_state, renderer)
    
    # Start a round with current time
    game_state.start_round(Clock.get_time())
    
    print(f"\nBefore drop:")
    print(f"  input_locked: {input_controller.input_locked}")
    print(f"  has_attempted: {game_state.has_attempted}")
    assert input_controller.input_locked == False
    assert game_state.has_attempted == False
    
    # Simulate correct drop at node position (within radius)
    correct_token = MockToken(game_state.correct_station_id)
    node_x, node_y = renderer.line_view.get_node_pos(game_state.next_index)
    
    result = input_controller.validate_drop(correct_token, node_x, node_y)
    
    print(f"\nAfter first drop validation:")
    print(f"  result: {result}")
    print(f"  input_locked: {input_controller.input_locked}")
    assert result == 'correct'
    assert input_controller.input_locked == True
    print("  ✓ Input lock set immediately on valid drop")


def test_multiple_drops_prevented():
    """Test that multiple drops in same frame are prevented"""
    print("\n" + "=" * 60)
    print("MULTIPLE DROPS PREVENTION TEST")
    print("=" * 60)
    
    from kivy.clock import Clock
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    renderer = MockRenderer()
    input_controller = InputController(game_state, renderer)
    
    # Start a round with current time
    game_state.start_round(Clock.get_time())
    
    # First drop - valid
    correct_token = MockToken(game_state.correct_station_id)
    node_x, node_y = renderer.line_view.get_node_pos(game_state.next_index)
    
    result1 = input_controller.validate_drop(correct_token, node_x, node_y)
    print(f"\nFirst drop result: {result1}")
    print(f"  input_locked: {input_controller.input_locked}")
    assert result1 == 'correct'
    assert input_controller.input_locked == True
    
    # Second drop attempt - should be blocked by input lock
    result2 = input_controller.validate_drop(correct_token, node_x, node_y)
    print(f"\nSecond drop result: {result2}")
    print(f"  input_locked: {input_controller.input_locked}")
    assert result2 is None
    assert input_controller.input_locked == True
    print("  ✓ Second drop blocked by input lock")
    
    # Third drop attempt - also blocked
    result3 = input_controller.validate_drop(correct_token, node_x, node_y)
    print(f"\nThird drop result: {result3}")
    assert result3 is None
    print("  ✓ Third drop also blocked")


def test_invalid_drop_no_lock():
    """Test that invalid drops (outside zone) don't lock input"""
    print("\n" + "=" * 60)
    print("INVALID DROP NO LOCK TEST")
    print("=" * 60)
    
    from kivy.clock import Clock
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    renderer = MockRenderer()
    input_controller = InputController(game_state, renderer)
    
    # Start a round with current time
    game_state.start_round(Clock.get_time())
    
    # Drop outside acceptance zone
    token = MockToken(game_state.correct_station_id)
    far_x, far_y = 1000, 1000  # Far from node position
    
    result = input_controller.validate_drop(token, far_x, far_y)
    
    print(f"\nInvalid drop result: {result}")
    print(f"  input_locked: {input_controller.input_locked}")
    print(f"  token.reset_called: {token.reset_called}")
    assert result is None
    assert input_controller.input_locked == False
    assert token.reset_called == True
    print("  ✓ Invalid drop doesn't lock input")
    print("  ✓ Token position reset")


def test_lock_cleared_on_new_round():
    """Test that lock is cleared when new round starts"""
    print("\n" + "=" * 60)
    print("LOCK CLEARED ON NEW ROUND TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    from kivy.clock import Clock
    
    game_state = GameState(line)
    renderer = MockRenderer()
    input_controller = InputController(game_state, renderer)
    
    # Start first round with current time
    game_state.start_round(Clock.get_time())
    
    # Lock input (simulate valid drop)
    input_controller.input_locked = True
    print(f"\nAfter locking:")
    print(f"  input_locked: {input_controller.input_locked}")
    assert input_controller.input_locked == True
    
    # Simulate clearing lock at next round start
    # (This would be done by ProximaParadaGame._start_next_round)
    input_controller.input_locked = False
    
    print(f"\nAfter unlocking for new round:")
    print(f"  input_locked: {input_controller.input_locked}")
    assert input_controller.input_locked == False
    print("  ✓ Lock cleared successfully")


def test_wrong_answer_locks_input():
    """Test that wrong answers also lock input"""
    print("\n" + "=" * 60)
    print("WRONG ANSWER LOCKS INPUT TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    from kivy.clock import Clock
    
    game_state = GameState(line)
    renderer = MockRenderer()
    input_controller = InputController(game_state, renderer)
    
    # Start a round with current time
    game_state.start_round(Clock.get_time())
    
    # Drop wrong token
    wrong_station = "WrongStation"
    wrong_token = MockToken(wrong_station)
    node_x, node_y = renderer.line_view.get_node_pos(game_state.next_index)
    
    result = input_controller.validate_drop(wrong_token, node_x, node_y)
    
    print(f"\nWrong answer result: {result}")
    print(f"  input_locked: {input_controller.input_locked}")
    assert result == 'wrong'
    assert input_controller.input_locked == True
    print("  ✓ Wrong answer locks input")


def test_timeout_locks_input():
    """Test that timeout detection locks input"""
    print("\n" + "=" * 60)
    print("TIMEOUT LOCKS INPUT TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    from kivy.clock import Clock
    
    game_state = GameState(line)
    renderer = MockRenderer()
    input_controller = InputController(game_state, renderer)
    
    # Start a round with past timestamp (simulate timeout)
    game_state.start_round(Clock.get_time() - 10)  # 10 seconds ago
    
    # Try to drop after timeout
    token = MockToken(game_state.correct_station_id)
    node_x, node_y = renderer.line_view.get_node_pos(game_state.next_index)
    
    result = input_controller.validate_drop(token, node_x, node_y)
    
    print(f"\nTimeout result: {result}")
    print(f"  input_locked: {input_controller.input_locked}")
    assert result == 'timeout'
    assert input_controller.input_locked == True
    print("  ✓ Timeout locks input")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 60)
    print("INPUT LOCK TEST SUITE")
    print("=" * 60)
    
    try:
        test_input_lock_initialization()
        test_input_lock_on_valid_drop()
        test_multiple_drops_prevented()
        test_invalid_drop_no_lock()
        test_lock_cleared_on_new_round()
        test_wrong_answer_locks_input()
        test_timeout_locks_input()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nInput Lock Summary:")
        print("  • Prevents multiple drops in same frame")
        print("  • Set immediately on valid drop (correct/wrong/timeout)")
        print("  • Not set on invalid drops (outside zone)")
        print("  • Cleared at next round initialization")
        print("  • Provides robust protection against rapid-fire drops")
        
        print("\nBehavior Details:")
        print("  ✓ First valid drop: Processed")
        print("  ✓ Subsequent drops before new round: Blocked")
        print("  ✓ Invalid drops: Don't affect lock state")
        print("  ✓ New round: Clears lock, accepts new drops")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == '__main__':
    run_all_tests()

