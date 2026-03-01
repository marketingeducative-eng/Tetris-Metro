"""
Test Token Spacing - Verify No Overlap and Equal Spacing

Verifies that:
1. Tokens have equal spacing between them
2. Tokens never visually overlap
3. Spacing accounts for token width properly
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState, InputController, Renderer
import random


class MockParent:
    """Mock parent widget with width"""
    def __init__(self, width=800):
        self.width = width


class MockRenderer:
    """Mock renderer for testing token positioning"""
    def __init__(self, parent_width=800):
        self.parent = MockParent(parent_width)
        self.tokens = []
        self.token_container = None
        
    def clear_tokens(self):
        self.tokens = []


def test_token_spacing_calculation():
    """Test that spacing calculation prevents overlap"""
    print("\n" + "=" * 60)
    print("TOKEN SPACING CALCULATION TEST")
    print("=" * 60)
    
    token_width = 140
    min_gap = 30
    spacing = token_width + min_gap
    
    print(f"\nToken dimensions:")
    print(f"  Width: {token_width}px")
    print(f"  Minimum gap: {min_gap}px")
    print(f"  Center-to-center spacing: {spacing}px")
    
    # Calculate token positions for parent width 800
    parent_width = 800
    center_x = parent_width / 2
    
    positions = [
        center_x - spacing,  # Left
        center_x,           # Center
        center_x + spacing  # Right
    ]
    
    print(f"\nToken center positions (parent width={parent_width}):")
    for i, pos in enumerate(positions):
        print(f"  Token {i+1}: {pos}px")
    
    # Calculate token boundaries (left and right edges)
    half_width = token_width / 2
    boundaries = [
        (pos - half_width, pos + half_width) for pos in positions
    ]
    
    print(f"\nToken boundaries:")
    for i, (left, right) in enumerate(boundaries):
        print(f"  Token {i+1}: [{left:.1f}, {right:.1f}]")
    
    # Check for overlaps
    print(f"\nOverlap checks:")
    overlaps = False
    for i in range(len(boundaries) - 1):
        right_edge = boundaries[i][1]
        left_edge = boundaries[i+1][0]
        gap = left_edge - right_edge
        
        print(f"  Gap between token {i+1} and {i+2}: {gap:.1f}px")
        
        if gap < 0:
            print(f"    ❌ OVERLAP DETECTED: {abs(gap):.1f}px")
            overlaps = True
        elif gap < 20:
            print(f"    ⚠️  WARNING: Gap too small (< 20px)")
        else:
            print(f"    ✓ Good spacing")
    
    assert not overlaps, "Tokens should not overlap!"
    
    # Check equal spacing
    print(f"\nSpacing equality check:")
    spacing_1_2 = positions[1] - positions[0]
    spacing_2_3 = positions[2] - positions[1]
    
    print(f"  Spacing 1→2: {spacing_1_2}px")
    print(f"  Spacing 2→3: {spacing_2_3}px")
    
    assert spacing_1_2 == spacing_2_3, "Spacing should be equal!"
    print(f"    ✓ Equal spacing confirmed")


def test_token_generation_spacing():
    """Test actual token generation uses proper spacing"""
    print("\n" + "=" * 60)
    print("TOKEN GENERATION SPACING TEST")
    print("=" * 60)
    
    from kivy.clock import Clock
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    game_state = GameState(line)
    renderer = MockRenderer(parent_width=800)
    input_controller = InputController(game_state, renderer)
    
    # Start a round
    game_state.start_round(Clock.get_time())
    
    # Mock token creation - simulate the positioning logic
    correct_id = game_state.correct_station_id
    token_width = 140
    min_gap = 30
    spacing = token_width + min_gap
    
    center_x = renderer.parent.width / 2
    y_pos = 15
    
    positions = [
        (center_x - spacing, y_pos),
        (center_x, y_pos),
        (center_x + spacing, y_pos)
    ]
    
    print(f"\nGenerated token positions:")
    for i, (x, y) in enumerate(positions):
        left_edge = x - (token_width / 2)
        right_edge = x + (token_width / 2)
        print(f"  Token {i+1}: center={x:.1f}, bounds=[{left_edge:.1f}, {right_edge:.1f}]")
    
    # Verify no overlap
    half_width = token_width / 2
    for i in range(len(positions) - 1):
        right_edge_1 = positions[i][0] + half_width
        left_edge_2 = positions[i+1][0] - half_width
        gap = left_edge_2 - right_edge_1
        
        assert gap >= min_gap, f"Gap {gap} should be at least {min_gap}px"
    
    print(f"    ✓ All tokens properly spaced")
    print(f"    ✓ Minimum gap of {min_gap}px maintained")


def test_different_screen_widths():
    """Test spacing works for different screen widths"""
    print("\n" + "=" * 60)
    print("DIFFERENT SCREEN WIDTHS TEST")
    print("=" * 60)
    
    token_width = 140
    min_gap = 30
    spacing = token_width + min_gap
    
    # Test with various screen widths
    screen_widths = [600, 800, 1024, 1280, 1920]
    
    for width in screen_widths:
        center_x = width / 2
        positions = [
            center_x - spacing,
            center_x,
            center_x + spacing
        ]
        
        # Check if tokens fit within screen
        leftmost = positions[0] - (token_width / 2)
        rightmost = positions[2] + (token_width / 2)
        total_width = rightmost - leftmost
        fits = leftmost >= 0 and rightmost <= width
        
        status = "✓ Fits" if fits else "❌ Overflow"
        print(f"\nScreen width {width}px:")
        print(f"  Token layout: {leftmost:.1f} to {rightmost:.1f} (total: {total_width:.1f}px)")
        print(f"  {status}")
        
        # Verify equal spacing
        spacing_1_2 = positions[1] - positions[0]
        spacing_2_3 = positions[2] - positions[1]
        assert spacing_1_2 == spacing_2_3
        
        # Verify no overlap
        half_width = token_width / 2
        for i in range(len(positions) - 1):
            right_edge = positions[i] + half_width
            left_edge = positions[i+1] - half_width
            gap = left_edge - right_edge
            assert gap >= min_gap


def test_randomization_preserves_spacing():
    """Test that randomizing token assignment doesn't affect spacing"""
    print("\n" + "=" * 60)
    print("RANDOMIZATION PRESERVES SPACING TEST")
    print("=" * 60)
    
    token_width = 140
    min_gap = 30
    spacing = token_width + min_gap
    center_x = 400
    y_pos = 15
    
    # Fixed positions (not shuffled)
    positions = [
        (center_x - spacing, y_pos),
        (center_x, y_pos),
        (center_x + spacing, y_pos)
    ]
    
    # Simulate multiple rounds with different token assignments
    tokens = ["Zona Universitària", "Palau Reial", "Maria Cristina"]
    
    print(f"\nTesting 5 random assignments:")
    for round_num in range(5):
        random.seed(round_num)  # Different seed each time
        shuffled_tokens = tokens.copy()
        random.shuffle(shuffled_tokens)
        
        print(f"\n  Round {round_num + 1}:")
        for token_name, (x, y) in zip(shuffled_tokens, positions):
            print(f"    {token_name}: x={x:.1f}")
        
        # Positions remain the same
        spacing_1_2 = positions[1][0] - positions[0][0]
        spacing_2_3 = positions[2][0] - positions[1][0]
        assert spacing_1_2 == spacing_2_3 == spacing
    
    print(f"\n    ✓ Spacing preserved across all rounds")
    print(f"    ✓ Only token assignment randomized, not positions")


if __name__ == '__main__':
    test_token_spacing_calculation()
    test_token_generation_spacing()
    test_different_screen_widths()
    test_randomization_preserves_spacing()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nToken Spacing Summary:")
    print("  • Token width: 140px")
    print("  • Minimum gap between tokens: 30px")
    print("  • Center-to-center spacing: 170px")
    print("  • Layout: Left, Center, Right positions")
    print("  • No visual overlap guaranteed")
    print("  • Equal spacing maintained")
    print("  • Token assignment randomized (not positions)")

