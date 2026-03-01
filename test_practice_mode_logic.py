"""
Test script to verify practice mode behavior.

Verifies:
1. Practice mode doesn't trigger game over after 3 mistakes
2. Normal mode triggers game over after 3 mistakes
3. Separate high score files are used
4. Stats are tracked correctly in both modes
"""
from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState

def test_normal_mode():
    """Test normal mode behavior"""
    print("Testing NORMAL MODE:")
    print("-" * 40)
    
    # Load metro network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    # Create game state in normal mode
    state = GameState(line, practice_mode=False)
    
    # Verify initial state
    assert state.practice_mode == False, "Should be in normal mode"
    assert state.game_over == False, "Should not be game over initially"
    assert state.mistakes == 0, "Should start with 0 mistakes"
    
    print(f"  ✓ Initial state: mistakes={state.mistakes}, game_over={state.game_over}")
    
    # Simulate 3 wrong answers
    for i in range(1, 4):
        result = state.handle_wrong_answer()
        print(f"  ✓ Mistake {i}: mistakes={state.mistakes}, game_over={result['game_over']}")
        
        if i < 3:
            assert result['game_over'] == False, f"Should not be game over after {i} mistakes"
        else:
            assert result['game_over'] == True, "Should be game over after 3 mistakes"
    
    # Verify game over state
    game_over_data = state.check_game_over()
    assert game_over_data is not None, "Should return game over data"
    assert state.game_over == True, "Game should be over"
    
    # Verify high score file path
    assert "high_score.json" in str(state.high_score_file), "Should use normal high score file"
    
    print(f"  ✓ Game over after 3 mistakes")
    print(f"  ✓ High score file: {state.high_score_file.name}")
    print()
    
    return True

def test_practice_mode():
    """Test practice mode behavior"""
    print("Testing PRACTICE MODE:")
    print("-" * 40)
    
    # Load metro network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    # Create game state in practice mode
    state = GameState(line, practice_mode=True)
    
    # Verify initial state
    assert state.practice_mode == True, "Should be in practice mode"
    assert state.game_over == False, "Should not be game over initially"
    assert state.mistakes == 0, "Should start with 0 mistakes"
    
    print(f"  ✓ Initial state: mistakes={state.mistakes}, game_over={state.game_over}")
    
    # Simulate 5 wrong answers (more than normal limit)
    for i in range(1, 6):
        result = state.handle_wrong_answer()
        print(f"  ✓ Mistake {i}: mistakes={state.mistakes}, game_over={result['game_over']}")
        assert result['game_over'] == False, f"Should never be game over in practice mode (mistake {i})"
    
    # Verify game over check
    game_over_data = state.check_game_over()
    assert game_over_data is None, "Should not return game over data in practice mode"
    assert state.game_over == False, "Game should never be over in practice mode"
    
    # Verify high score file path
    assert "high_score_practice.json" in str(state.high_score_file), "Should use practice high score file"
    
    print(f"  ✓ No game over even after {state.mistakes} mistakes!")
    print(f"  ✓ High score file: {state.high_score_file.name}")
    
    # Test that bonus lives are still tracked in practice mode
    state2 = GameState(line, practice_mode=True)
    for i in range(7):
        result = state2.handle_correct_answer()
        if i == 6:  # 7th correct answer
            assert state2.bonus_lives == 1, "Should earn bonus life in practice mode"
            print(f"  ✓ Bonus life earned at streak 7 (even in practice mode)")
    
    print()
    
    return True

def test_timeout_behavior():
    """Test timeout behavior in both modes"""
    print("Testing TIMEOUT BEHAVIOR:")
    print("-" * 40)
    
    # Load metro network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    # Test normal mode timeout
    normal_state = GameState(line, practice_mode=False)
    for i in range(3):
        result = normal_state.handle_timeout()
    assert result['game_over'] == True, "Normal mode should trigger game over after 3 timeouts"
    print(f"  ✓ Normal mode: game over after 3 timeouts")
    
    # Test practice mode timeout
    practice_state = GameState(line, practice_mode=True)
    for i in range(5):
        result = practice_state.handle_timeout()
    assert result['game_over'] == False, "Practice mode should never trigger game over"
    print(f"  ✓ Practice mode: no game over after 5 timeouts")
    print()
    
    return True

def main():
    print("=" * 60)
    print("PRACTICE MODE TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        # Run tests
        test_normal_mode()
        test_practice_mode()
        test_timeout_behavior()
        
        # Summary
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("USAGE:")
        print("  # Normal mode (default):")
        print("  app = ProximaParadaApp()")
        print("  app.run()")
        print()
        print("  # Practice mode:")
        print("  app = ProximaParadaApp(practice_mode=True)")
        print("  app.run()")
        print()
        print("  # Practice mode with fixed seed:")
        print("  app = ProximaParadaApp(practice_mode=True, random_seed=42)")
        print("  app.run()")
        print("=" * 60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

