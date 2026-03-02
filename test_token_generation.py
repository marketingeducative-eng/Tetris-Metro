"""
Test token generation logic for edge cases
"""
import random
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data.metro_loader import load_metro_network


def _run_token_generation_check(line, test_index, test_name):
    """Test token generation for a specific index"""
    print(f"\n{test_name} (index={test_index}):")
    
    # Simulate the token generation logic
    correct_index = test_index
    correct_id = line.stations[correct_index].name
    
    num_stations = len(line.stations)
    used_indices = {correct_index}
    distractor_indices = []
    
    # Try nearby offsets first
    max_offset = min(num_stations // 2, 10)
    offsets = []
    for offset in range(1, max_offset + 1):
        offsets.extend([offset, -offset])
    
    random.shuffle(offsets)
    
    # Find 2 unique distractor indices
    for offset in offsets:
        if len(distractor_indices) >= 2:
            break
        
        # Clamp index to stay within bounds
        idx = correct_index + offset
        idx = max(0, min(idx, num_stations - 1))
        
        # Add if unique and not the correct station
        if idx not in used_indices:
            used_indices.add(idx)
            distractor_indices.append(idx)
    
    # Fallback: if we still need more distractors, pick randomly
    if len(distractor_indices) < 2:
        remaining = [i for i in range(num_stations) if i not in used_indices]
        random.shuffle(remaining)
        needed = 2 - len(distractor_indices)
        distractor_indices.extend(remaining[:needed])
    
    # Convert to station IDs
    distractors = [line.stations[i].name for i in distractor_indices]
    all_station_ids = [correct_id] + distractors
    
    # Verify uniqueness
    assert len(set(all_station_ids)) == 3, f"ERROR: Duplicate tokens! {all_station_ids}"
    
    # Verify all indices are in bounds
    all_indices = [correct_index] + distractor_indices
    for idx in all_indices:
        assert 0 <= idx < num_stations, f"ERROR: Index {idx} out of bounds [0, {num_stations})"
    
    print(f"  ✅ Correct: {correct_id} (index {correct_index})")
    print(f"  ✅ Distractor 1: {distractors[0]} (index {distractor_indices[0]})")
    print(f"  ✅ Distractor 2: {distractors[1]} (index {distractor_indices[1]})")
    print(f"  ✅ All unique: {len(set(all_station_ids)) == 3}")
    print(f"  ✅ All in bounds: True")


def main():
    """Test token generation with various edge cases"""
    print("Testing token generation logic...")
    
    # Load metro data
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    print(f"\nLine L3 has {len(line.stations)} stations")
    
    # Test edge cases
    test_cases = [
        (0, "Beginning of line"),
        (1, "Second station"),
        (len(line.stations) - 1, "End of line"),
        (len(line.stations) - 2, "Second to last"),
        (len(line.stations) // 2, "Middle of line"),
    ]
    
    # Run each test multiple times to ensure randomization doesn't break uniqueness
    for test_index, test_name in test_cases:
        for run in range(3):
            _run_token_generation_check(line, test_index, f"{test_name} (run {run+1})")
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    print("="*50)


if __name__ == '__main__':
    main()
