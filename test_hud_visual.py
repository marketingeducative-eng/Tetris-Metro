"""
Quick Test: Launch game with HUD background panel

This test launches the game so you can visually verify the background panel.
"""

from game_propera_parada import ProximaParadaApp


if __name__ == '__main__':
    print("=" * 60)
    print("VISUAL TEST: HUD Background Panel")
    print("=" * 60)
    print("\nLaunching game with background panel...")
    print("\nWhat to look for:")
    print("  ✓ Dark semi-transparent panel behind all HUD text")
    print("  ✓ Panel has subtle rounded corners (10px)")
    print("  ✓ Improves text readability")
    print("  ✓ Doesn't block game view below HUD")
    print("\nPress Escape to close the game.")
    print("=" * 60)
    
    ProximaParadaApp().run()

