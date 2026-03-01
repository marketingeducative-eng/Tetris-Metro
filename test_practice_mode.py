"""
Test script to demonstrate practice mode functionality.

Practice mode allows:
- Unlimited mistakes (no game over)
- Separate high score tracking
- Perfect for learning station sequences
"""
from game_propera_parada import ProximaParadaApp

if __name__ == '__main__':
    print("=" * 60)
    print("PRACTICE MODE")
    print("=" * 60)
    print("Features:")
    print("  ✓ Unlimited mistakes - no game over!")
    print("  ✓ Separate high score tracking")
    print("  ✓ Same difficulty scaling as normal mode")
    print("  ✓ Perfect for learning and experimentation")
    print()
    print("Visual indicators:")
    print("  - Title shows '[PRÀCTICA]'")
    print("  - Blue color scheme instead of green")
    print("  - Error counter shows total (not X/3)")
    print()
    print("High scores saved to: data/high_score_practice.json")
    print()
    print("Press Ctrl+C to exit or close the window")
    print("=" * 60)
    
    # Run in practice mode
    app = ProximaParadaApp(practice_mode=True)
    app.run()

