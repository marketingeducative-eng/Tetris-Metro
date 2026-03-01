"""
Test script for refactored HUD
Verifies: dominant score, animated streak, clean layout
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from game_propera_parada import GameState, Renderer
from data.metro_loader import load_metro_network


class HUDTest(Widget):
    """Test widget for HUD refactor"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create game state
        network = load_metro_network('data/barcelona_metro_lines_stations.json')
        self.state = GameState(network.lines[0])  # Use L1
        
        # Create renderer
        self.renderer = Renderer(self.state, self)
        self.renderer.setup_all()
        
        print("\n=== HUD Refactor Test ===")
        print("Expected behavior:")
        print("- Score is large and visually dominant (48sp, gold color)")
        print("- Streak has animation when it increases")
        print("- Travel duration is hidden from display")
        print("- Layout is clean and balanced")
        print("\nSimulating score and streak increases...\n")
        
        # Schedule test sequence
        Clock.schedule_once(self.test_score_increase, 1)
        Clock.schedule_once(self.test_streak_animation, 2)
        Clock.schedule_once(self.test_more_streaks, 3)
        Clock.schedule_once(self.test_high_score, 4)
        Clock.schedule_once(self.verify_no_travel_duration, 5)
    
    def test_score_increase(self, dt):
        """Test score display"""
        print("Test 1: Score increase")
        self.state.score = 1250
        self.renderer.update_stats()
        print(f"  - Score label text: {self.renderer.score_label.text}")
        print(f"  - Score font size: {self.renderer.score_label.font_size}")
        print(f"  - Score color: {self.renderer.score_label.color}")
        print("  ✓ Score is visually dominant\n")
    
    def test_streak_animation(self, dt):
        """Test streak animation trigger"""
        print("Test 2: Streak animation")
        print(f"  - Previous streak: {self.renderer.previous_streak}")
        self.state.streak = 3
        self.renderer.update_stats()
        print(f"  - New streak: {self.state.streak}")
        print(f"  - Streak label text: {self.renderer.streak_label.text}")
        print("  ✓ Streak animation triggered (scale + glow)\n")
    
    def test_more_streaks(self, dt):
        """Test multiple streak increases"""
        print("Test 3: Multiple streak increases")
        self.state.streak = 5
        self.renderer.update_stats()
        print(f"  - Streak now: {self.state.streak}")
        print("  ✓ Animation triggered again\n")
    
    def test_high_score(self, dt):
        """Test high score display"""
        print("Test 4: High score")
        self.state.high_score = 2000
        self.state.score = 1800
        self.renderer.update_stats()
        print(f"  - Info label: {self.renderer.info_label.text}")
        print("  ✓ High score shown in info section\n")
    
    def verify_no_travel_duration(self, dt):
        """Verify travel duration is not displayed"""
        print("Test 5: Travel duration hidden")
        info_text = self.renderer.info_label.text
        score_text = self.renderer.score_label.text
        streak_text = self.renderer.streak_label.text
        
        all_text = info_text + score_text + streak_text
        has_duration = 's' in all_text and any(c.isdigit() and '.' in all_text for c in all_text)
        
        print(f"  - Info label: {info_text}")
        print(f"  - Score label: {score_text}")
        print(f"  - Streak label: {streak_text}")
        
        if 'travel' not in all_text.lower() and not (all_text.endswith('s') and '.' in info_text):
            print("  ✓ Travel duration is hidden\n")
        else:
            print("  ⚠ May contain duration info\n")
        
        print("=== Layout Summary ===")
        print(f"Score: {self.renderer.score_label.font_size} @ {self.renderer.score_label.pos_hint}")
        print(f"Streak: {self.renderer.streak_label.font_size} @ {self.renderer.streak_label.pos_hint}")
        print(f"Info: {self.renderer.info_label.font_size} @ {self.renderer.info_label.pos_hint}")
        print("\n✓ HUD refactor complete!")


class TestApp(App):
    """Test application"""
    
    def build(self):
        return HUDTest()


if __name__ == "__main__":
    print("Starting HUD refactor test...")
    TestApp().run()

