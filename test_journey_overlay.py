"""
Test for Journey Overlay - Meta-progression screen

Tests the "El teu viatge" overlay which displays:
- Total score
- Lines completed
- Total stations visited
- Badges earned
- First Day progress
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from game_propera_parada import Renderer
from core.progress import ProgressManager
from core.badges import BADGE_DEFINITIONS


class MockGameState:
    """Mock game state for testing"""
    def __init__(self):
        self.practice_mode = False
        self.direction_mode = False
        self.subtitles_enabled = True


class MockLine:
    """Mock metro line"""
    def __init__(self):
        self.id = "L3"
        self.name = "Línia 3"
        self.color = "#00AA00"
        self.stations = []


class TestJourneyOverlay(App):
    def build(self):
        root = FloatLayout()
        
        # Create mock game state
        game_state = MockGameState()
        game_state.line = MockLine()
        
        # Create renderer
        renderer = Renderer(root, game_state)
        
        # Setup progress manager with test data
        progress_mgr = ProgressManager()
        
        # Mock some progress data
        # Add some completed lines
        if hasattr(progress_mgr, 'mark_line_complete'):
            progress_mgr.mark_line_complete("L1")
            progress_mgr.mark_line_complete("L3")
        
        # Add some badges
        if hasattr(progress_mgr, 'unlock_badge'):
            badge_ids = list(BADGE_DEFINITIONS.keys())[:3]  # First 3 badges
            for badge_id in badge_ids:
                progress_mgr.unlock_badge(badge_id)
        
        # Add score
        if hasattr(progress_mgr, 'add_score'):
            progress_mgr.add_score(12500)
        
        root.progress_manager = progress_mgr
        
        # Add trigger button for testing
        trigger_button = Button(
            text="Mostra El teu viatge",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        def show_journey(*args):
            renderer.show_journey_overlay()
        
        trigger_button.bind(on_release=show_journey)
        root.add_widget(trigger_button)
        
        return root


if __name__ == '__main__':
    TestJourneyOverlay().run()

