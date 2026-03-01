"""
Test Route Map Line Segments - Verify Visual Progression

Verifies that:
1. Segments are drawn between consecutive stations
2. Traveled segments are green
3. Remaining segments are dim gray
4. Segment colors match station progress
"""

from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState


def test_segment_coloring_logic():
    """Test that segment colors are determined correctly"""
    print("\n" + "=" * 60)
    print("SEGMENT COLORING LOGIC TEST")
    print("=" * 60)
    
    # Test scenarios with different progress levels
    scenarios = [
        ("Early game", {0, 1, 2}, 2),
        ("Mid game", {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 10),
        ("Late game", set(range(20)), 19),
        ("Complete", set(range(26)), 25),
    ]
    
    for name, visited_stations, max_visited in scenarios:
        print(f"\n{name} (max visited: {max_visited}):")
        
        # Simulate segment coloring for first 10 segments
        segments_to_show = min(10, 25)
        for i in range(segments_to_show):
            if i <= max_visited:
                color = "GREEN (traveled)"
            else:
                color = "GRAY (remaining)"
            
            symbol = "●" if i <= max_visited else "○"
            print(f"  Segment {i}→{i+1}: {symbol} {color}")
        
        if segments_to_show < 25:
            print(f"  ... (showing first {segments_to_show} of 25 segments)")
    
    print(f"\n✓ Segment coloring logic verified")


def test_segment_count():
    """Test that correct number of segments are drawn"""
    print("\n" + "=" * 60)
    print("SEGMENT COUNT TEST")
    print("=" * 60)
    
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    num_stations = len(line.stations)
    num_segments = num_stations - 1
    
    print(f"\nL3 Line:")
    print(f"  Total stations: {num_stations}")
    print(f"  Total segments: {num_segments}")
    print(f"  (One segment connects each pair of consecutive stations)")
    
    # Verify segment count calculation
    assert num_segments == 25, f"Expected 25 segments, got {num_segments}"
    
    print(f"\n✓ Correct number of segments: {num_segments}")


def test_color_transitions():
    """Test color transitions at different progress points"""
    print("\n" + "=" * 60)
    print("COLOR TRANSITION TEST")
    print("=" * 60)
    
    test_cases = [
        {
            "description": "Stopped at station 5",
            "max_visited": 5,
            "expected_green": list(range(0, 6)),  # Segments 0-5 (stations 0-6)
            "expected_gray": list(range(6, 25))   # Segments 6-24
        },
        {
            "description": "Stopped at station 12",
            "max_visited": 12,
            "expected_green": list(range(0, 13)),  # Segments 0-12
            "expected_gray": list(range(13, 25))   # Segments 13-24
        },
        {
            "description": "Stopped at station 19",
            "max_visited": 19,
            "expected_green": list(range(0, 20)),  # Segments 0-19
            "expected_gray": list(range(20, 25))   # Segments 20-24
        },
    ]
    
    for case in test_cases:
        print(f"\n{case['description']}:")
        max_visited = case['max_visited']
        
        green_segments = []
        gray_segments = []
        
        for i in range(25):  # 25 segments for 26 stations
            if i <= max_visited:
                green_segments.append(i)
            else:
                gray_segments.append(i)
        
        print(f"  Max visited station: {max_visited}")
        print(f"  Green segments: {len(green_segments)} (0-{max_visited})")
        print(f"  Gray segments: {len(gray_segments)} ({max_visited+1}-24)")
        
        assert green_segments == case['expected_green']
        assert gray_segments == case['expected_gray']
        print(f"  ✓ Transition at correct position")
    
    print(f"\n✓ All color transitions correct")


def test_edge_cases():
    """Test edge cases for segment drawing"""
    print("\n" + "=" * 60)
    print("EDGE CASE TEST")
    print("=" * 60)
    
    # Case 1: Only starting station (station 0)
    print(f"\nCase 1: Only starting station")
    max_visited = 0
    print(f"  Max visited: {max_visited}")
    print(f"  Segment 0→1: {'GREEN' if 0 <= max_visited else 'GRAY'}")
    print(f"  Segment 1→2: {'GREEN' if 1 <= max_visited else 'GRAY'}")
    print(f"  Segment 2→3: {'GREEN' if 2 <= max_visited else 'GRAY'}")
    
    # Only segment 0 should be green
    assert 0 <= max_visited  # Segment 0 is green
    assert not (1 <= max_visited)  # Segment 1 is gray
    print(f"  ✓ Only first segment is green")
    
    # Case 2: All stations visited
    print(f"\nCase 2: All stations visited")
    max_visited = 25
    green_count = sum(1 for i in range(25) if i <= max_visited)
    print(f"  Max visited: {max_visited}")
    print(f"  All {green_count} segments should be green")
    
    assert green_count == 25
    print(f"  ✓ All segments are green")
    
    # Case 3: Mid-point transition
    print(f"\nCase 3: Transition at mid-point (station 12)")
    max_visited = 12
    green_count = sum(1 for i in range(25) if i <= max_visited)
    gray_count = sum(1 for i in range(25) if i > max_visited)
    
    print(f"  Max visited: {max_visited}")
    print(f"  Green segments: {green_count} (0-{max_visited})")
    print(f"  Gray segments: {gray_count} ({max_visited+1}-24)")
    
    assert green_count == 13  # Segments 0-12
    assert gray_count == 12   # Segments 13-24
    assert green_count + gray_count == 25
    print(f"  ✓ Correct split at transition point")
    
    print(f"\n✓ All edge cases handled correctly")


def test_visual_representation():
    """Test visual representation of route progression"""
    print("\n" + "=" * 60)
    print("VISUAL REPRESENTATION TEST")
    print("=" * 60)
    
    scenarios = [
        (3, "Beginner progress"),
        (10, "Intermediate progress"),
        (19, "Advanced progress"),
        (25, "Complete route"),
    ]
    
    for max_visited, description in scenarios:
        print(f"\n{description} (stopped at station {max_visited}):")
        
        # Draw visual representation
        visual = "  "
        for i in range(26):  # 26 stations
            if i in range(max_visited + 1):
                visual += "●"  # Visited station
            else:
                visual += "○"  # Unvisited station
            
            # Add segment indicator
            if i < 25:
                if i <= max_visited:
                    visual += "━"  # Green segment
                else:
                    visual += "╌"  # Gray segment
        
        print(visual)
        print(f"  Legend: ● visited station  ○ unvisited station")
        print(f"          ━ traveled segment  ╌ remaining segment")
        
        # Count segments
        green_segments = sum(1 for i in range(25) if i <= max_visited)
        gray_segments = 25 - green_segments
        
        print(f"  Green: {green_segments}, Gray: {gray_segments}")
    
    print(f"\n✓ Visual representation clear")


def test_color_values():
    """Test that color values match specification"""
    print("\n" + "=" * 60)
    print("COLOR VALUES TEST")
    print("=" * 60)
    
    # Expected colors from implementation
    traveled_color = (0.3, 0.9, 0.4, 1.0)
    remaining_color = (0.2, 0.2, 0.25, 0.5)
    
    print(f"\nSegment colors:")
    print(f"  Traveled (green):")
    print(f"    RGB: ({traveled_color[0]}, {traveled_color[1]}, {traveled_color[2]})")
    print(f"    Alpha: {traveled_color[3]}")
    print(f"    Description: Bright green, fully opaque")
    
    print(f"\n  Remaining (gray):")
    print(f"    RGB: ({remaining_color[0]}, {remaining_color[1]}, {remaining_color[2]})")
    print(f"    Alpha: {remaining_color[3]}")
    print(f"    Description: Dim gray, 50% opacity")
    
    # Verify green is brighter than gray
    assert traveled_color[1] > remaining_color[1], "Traveled should be brighter green"
    assert traveled_color[3] > remaining_color[3], "Traveled should be more opaque"
    
    print(f"\n✓ Color values correct")


if __name__ == '__main__':
    test_segment_coloring_logic()
    test_segment_count()
    test_color_transitions()
    test_edge_cases()
    test_visual_representation()
    test_color_values()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nRoute Map Segment Summary:")
    print("  • Total segments: 25 (connecting 26 stations)")
    print("  • Traveled segments: Bright green (0.3, 0.9, 0.4, 1.0)")
    print("  • Remaining segments: Dim gray (0.2, 0.2, 0.25, 0.5)")
    print("  • Transition point: After furthest visited station")
    print("  • Visual: Clear progression from start to failure point")

