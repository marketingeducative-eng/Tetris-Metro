"""
Visual Test: Game Over Route Map

This test launches the game and intentionally triggers a game over
to demonstrate the route map visualization.
"""

from game_propera_parada import ProximaParadaApp, GameState
from pathlib import Path
from data.metro_loader import load_metro_network


class TestGameOverApp(ProximaParadaApp):
    """Modified app to quickly trigger game over with visited stations"""
    
    def build(self):
        game = super().build()
        
        # Simulate having visited several stations before game over
        # This gives us something interesting to display in the route map
        game.game_state.visited_stations = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
        game.game_state.current_index = 12
        game.game_state.score = 1800
        game.game_state.streak = 5
        game.game_state.mistakes = 0
        
        # Immediately show game over screen to see the route map
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: game._game_over(), 0.1)
        
        return game


if __name__ == '__main__':
    print("=" * 60)
    print("VISUAL TEST: Game Over Route Map")
    print("=" * 60)
    print("\nThis test will:")
    print("  1. Launch the game")
    print("  2. Immediately show game over screen")
    print("  3. Display route map with 13 visited stations")
    print("\nWhat to look for:")
    print("  ✓ Game over panel (500x500px)")
    print("  ✓ Stats showing 'Estacions: 13/26'")
    print("  ✓ 'RUTA COMPLETADA:' label")
    print("  ✓ Horizontal route line")
    print("  ✓ Green nodes for visited stations (0-12)")
    print("  ✓ Gray nodes for unvisited stations (13-25)")
    print("  ✓ Terminal labels: 'Zona Universitària' and 'Trinitat Nova'")
    print("\nThe visited section should be bright green,")
    print("showing clear progress along the first half of L3.")
    print("\nPress Escape to close.")
    print("=" * 60)
    
    TestGameOverApp().run()

