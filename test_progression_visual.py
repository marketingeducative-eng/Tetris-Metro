"""
Quick Visual Test: Station Progression Counter in HUD

Launch the game to see the progression counter (e.g., 7/26) in action.
"""

from game_propera_parada import ProximaParadaApp


if __name__ == '__main__':
    print("=" * 60)
    print("VISUAL TEST: Station Progression Counter")
    print("=" * 60)
    print("\nLaunching game with progression tracking...")
    print("\nWhat to look for in the HUD stats line:")
    print("  ✓ Counter format: 0/26, 1/26, 2/26, etc.")
    print("  ✓ Increments with each correct answer")
    print("  ✓ Shows current position along L3 line")
    print("  ✓ Appears between errors/lives and time")
    print("\nExample HUD stats line:")
    print("  1200pts • High: 2500 • Streak: 5 • Lives: ❤️❤️❤️ • 7/26 • 3.1s")
    print("\nPlay a few rounds to see the counter increment!")
    print("Press Escape to close the game.")
    print("=" * 60)
    
    ProximaParadaApp().run()

