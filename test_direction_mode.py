"""Test Direction Mode - Verify terminal station display"""

from game_propera_parada import ProximaParadaApp


if __name__ == '__main__':
    # Launch with direction mode enabled
    print("Starting Pròxima Parada with Direction Mode...")
    print("Expected: HUD should show '→ Direcció: Trinitat Nova' (L3 terminal)")
    ProximaParadaApp(direction_mode=True).run()

