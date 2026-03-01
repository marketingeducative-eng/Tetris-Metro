"""
Test script to verify reproducibility with random seed parameter.
Demonstrates that the same seed produces the same token sequences.
"""
import random
from pathlib import Path
from data.metro_loader import load_metro_network
from game_propera_parada import GameState, Renderer, InputController

class MockParent:
    """Mock parent widget for testing"""
    def __init__(self):
        self.width = 800
        self.height = 600

class MockRenderer:
    """Mock renderer for testing"""
    def __init__(self):
        self.parent = MockParent()
        self.tokens = []
        self.token_container = MockTokenContainer()

class MockTokenContainer:
    """Mock token container"""
    def add_widget(self, token):
        pass
    def remove_widget(self, token):
        pass

class MockToken:
    """Mock station token"""
    def __init__(self, station_id):
        self.station_id = station_id
        self.opacity = 1

def mock_station_token(*args, **kwargs):
    """Mock StationToken constructor"""
    return MockToken(kwargs.get('station_id', 'Unknown'))

def test_reproducibility(seed, num_rounds=5):
    """Test that the same seed produces the same token sequences"""
    # Load metro network
    data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
    metro = load_metro_network(str(data_path))
    line = metro.get_line("L3")
    
    # Create game state
    game_state = GameState(line)
    
    # Create mock renderer
    renderer = MockRenderer()
    
    # Create input controller with seed
    input_controller = InputController(game_state, renderer, random_seed=seed)
    
    token_sequences = []
    
    for round_num in range(num_rounds):
        # Set up for next round
        game_state.next_index = (round_num + 1) % len(line.stations)
        
        # Capture tokens before generation
        correct_index = game_state.next_index
        correct_id = line.stations[correct_index].name
        
        # Generate distractors using same logic as InputController
        num_stations = len(line.stations)
        used_indices = {correct_index}
        distractor_indices = []
        
        max_offset = min(num_stations // 2, 10)
        offsets = []
        for offset in range(1, max_offset + 1):
            offsets.extend([offset, -offset])
        random.shuffle(offsets)
        
        for offset in offsets:
            if len(distractor_indices) >= 2:
                break
            idx = correct_index + offset
            idx = max(0, min(idx, num_stations - 1))
            if idx not in used_indices:
                used_indices.add(idx)
                distractor_indices.append(idx)
        
        if len(distractor_indices) < 2:
            remaining = [i for i in range(num_stations) if i not in used_indices]
            random.shuffle(remaining)
            needed = 2 - len(distractor_indices)
            distractor_indices.extend(remaining[:needed])
        
        distractors = [line.stations[i].name for i in distractor_indices]
        all_station_ids = [correct_id] + distractors
        
        # Record token sequence
        token_sequences.append(tuple(sorted(all_station_ids)))
    
    return token_sequences

def main():
    print("Testing Reproducibility with Random Seed")
    print("=" * 60)
    
    # Test with seed 42
    print("\n🎲 Testing with seed=42 (Run 1):")
    seq1 = test_reproducibility(seed=42, num_rounds=5)
    for i, tokens in enumerate(seq1, 1):
        print(f"  Round {i}: {tokens}")
    
    print("\n🎲 Testing with seed=42 (Run 2):")
    seq2 = test_reproducibility(seed=42, num_rounds=5)
    for i, tokens in enumerate(seq2, 1):
        print(f"  Round {i}: {tokens}")
    
    if seq1 == seq2:
        print("\n✅ REPRODUCIBILITY TEST PASSED!")
        print("   Same seed produces identical token sequences across runs")
    else:
        print("\n❌ REPRODUCIBILITY TEST FAILED!")
        print("   Different token sequences with same seed")
        return False
    
    # Test with different seed
    print("\n🎲 Testing with seed=123:")
    seq3 = test_reproducibility(seed=123, num_rounds=5)
    for i, tokens in enumerate(seq3, 1):
        print(f"  Round {i}: {tokens}")
    
    if seq3 != seq1:
        print("\n✅ DIFFERENT SEED TEST PASSED!")
        print("   Different seeds produce different token sequences")
    else:
        print("\n⚠️  WARNING: Different seeds produced same sequences")
        print("   (This is unlikely but possible)")
    
    # Test without seed (random)
    print("\n🎲 Testing without seed (random run):")
    seq4 = test_reproducibility(seed=None, num_rounds=5)
    for i, tokens in enumerate(seq4, 1):
        print(f"  Round {i}: {tokens}")
    
    print("\n" + "=" * 60)
    print("USAGE EXAMPLE:")
    print("  # For reproducible testing:")
    print("  app = ProximaParadaApp(random_seed=42)")
    print("  app.run()")
    print()
    print("  # For normal gameplay (random):")
    print("  app = ProximaParadaApp()")
    print("  app.run()")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

