"""
Test high score persistence
"""
import json
from pathlib import Path

# High score file path
high_score_file = Path(__file__).parent / "data" / "high_score.json"

def load_high_score():
    """Load high score from JSON"""
    try:
        if high_score_file.exists():
            with open(high_score_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        return 0
    except Exception as e:
        print(f"Error loading: {e}")
        return 0

def save_high_score(score):
    """Save high score to JSON"""
    try:
        high_score_file.parent.mkdir(parents=True, exist_ok=True)
        with open(high_score_file, 'w', encoding='utf-8') as f:
            json.dump({'high_score': score}, f, indent=2)
        print(f"✅ Saved high score: {score}")
    except Exception as e:
        print(f"❌ Error saving: {e}")

def main():
    """Test high score persistence"""
    print("High Score Persistence Test")
    print("=" * 50)
    
    # Load current high score
    current = load_high_score()
    print(f"\nCurrent high score: {current}")
    
    # Test save with new score
    test_score = 1250
    print(f"\nTesting save with score: {test_score}")
    save_high_score(test_score)
    
    # Verify it was saved
    loaded = load_high_score()
    print(f"Loaded back: {loaded}")
    
    if loaded == test_score:
        print("\n✅ HIGH SCORE PERSISTENCE WORKING!")
        print(f"   File location: {high_score_file}")
    else:
        print("\n❌ High score not persisted correctly")
    
    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()
