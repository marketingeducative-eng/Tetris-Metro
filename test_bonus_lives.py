"""
Test script to verify the bonus life system.

Tests:
1. Bonus life granted at 7 streak
2. Second bonus life granted at 14 streak
3. No more than 2 bonus lives
4. Lives correctly extend game over threshold
"""
from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState

def test_bonus_life_system():
    print("=" * 60)
    print("BONUS LIFE SYSTEM TEST")
    print("=" * 60)
    print()
    
    # Load metro network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    # Create game state in normal mode
    state = GameState(line, practice_mode=False)
    
    print("Initial State:")
    print(f"  Base Lives: {state.base_lives}")
    print(f"  Bonus Lives: {state.bonus_lives}")
    print(f"  Total Lives: {state.base_lives + state.bonus_lives}")
    print(f"  Streak: {state.streak}")
    print()
    
    # Test 1: Grant first bonus life at 7 streak
    print("Test 1: First Bonus Life at 7 Streak")
    print("-" * 40)
    for i in range(1, 8):
        result = state.handle_correct_answer()
        print(f"  Correct #{i}: streak={state.streak}, bonus_lives={state.bonus_lives}")
        if i == 7:
            assert result.get('life_granted') == True, "Should grant life at streak 7"
            assert state.bonus_lives == 1, "Should have 1 bonus life"
            assert "VIDA" in result['message'], "Message should mention life granted"
            print(f"    ✓ Life granted! Total lives: {state.base_lives + state.bonus_lives}")
    print()
    
    # Test 2: Grant second bonus life at 14 streak
    print("Test 2: Second Bonus Life at 14 Streak")
    print("-" * 40)
    for i in range(8, 15):
        result = state.handle_correct_answer()
        print(f"  Correct #{i}: streak={state.streak}, bonus_lives={state.bonus_lives}")
        if i == 14:
            assert result.get('life_granted') == True, "Should grant life at streak 14"
            assert state.bonus_lives == 2, "Should have 2 bonus lives"
            assert "VIDA" in result['message'], "Message should mention life granted"
            print(f"    ✓ Life granted! Total lives: {state.base_lives + state.bonus_lives}")
    print()
    
    # Test 3: No more bonus lives after cap
    print("Test 3: Cap at 2 Bonus Lives")
    print("-" * 40)
    for i in range(15, 22):
        result = state.handle_correct_answer()
        print(f"  Correct #{i}: streak={state.streak}, bonus_lives={state.bonus_lives}")
        if i == 21:
            assert result.get('life_granted', False) == False, "Should not grant life at streak 21 (cap reached)"
            assert state.bonus_lives == 2, "Should still have 2 bonus lives (capped)"
            print(f"    ✓ No extra life granted (capped at 2)")
    print()
    
    # Test 4: Lives extend game over threshold
    print("Test 4: Bonus Lives Extend Survival")
    print("-" * 40)
    total_lives = state.base_lives + state.bonus_lives
    print(f"  Total Lives: {total_lives} (3 base + 2 bonus)")
    print(f"  Testing {total_lives - 1} mistakes (should survive):")
    
    for i in range(1, total_lives):
        result = state.handle_wrong_answer()
        print(f"    Mistake {i}: mistakes={state.mistakes}, game_over={result['game_over']}")
        assert result['game_over'] == False, f"Should not be game over after {i} mistakes"
    
    print(f"  Testing mistake #{total_lives} (should trigger game over):")
    result = state.handle_wrong_answer()
    print(f"    Mistake {total_lives}: mistakes={state.mistakes}, game_over={result['game_over']}")
    assert result['game_over'] == True, f"Should be game over after {total_lives} mistakes"
    print(f"    ✓ Game over correctly triggered after {total_lives} mistakes")
    print()
    
    # Test 5: Lives reset on new game
    print("Test 5: Fresh Game Without Bonus Lives")
    print("-" * 40)
    state2 = GameState(line, practice_mode=False)
    print(f"  Total Lives: {state2.base_lives + state2.bonus_lives}")
    
    for i in range(1, 4):
        result = state2.handle_wrong_answer()
        print(f"    Mistake {i}: game_over={result['game_over']}")
        if i < 3:
            assert result['game_over'] == False
        else:
            assert result['game_over'] == True
    print(f"    ✓ Game over after 3 mistakes (no bonus lives)")
    print()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("SYSTEM SUMMARY:")
    print("  • 7 correct answers in a row → +1 life")
    print("  • 14 correct answers in a row → +2 lives (max)")
    print("  • Base lives: 3")
    print("  • Max total lives: 5 (3 base + 2 bonus)")
    print("  • Lives shown in HUD with heart emojis ❤️💚")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        success = test_bonus_life_system()
        exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

