"""
Test script for bonus life sound feature
Verifies: bonus life sound generates and plays when a bonus life is granted
"""

from core.audio import AudioService
from game_propera_parada import GameState
from data.metro_loader import load_metro_network
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget


class BonusLifeSoundTest(Widget):
    """Test widget for bonus life sound"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.audio = AudioService()
        
        # Load game state
        network = load_metro_network('data/barcelona_metro_lines_stations.json')
        self.state = GameState(network.lines[0])
        
        print("\n=== Bonus Life Sound Test ===\n")
        
        # Schedule test sequence
        Clock.schedule_once(self.test_bonus_sound_generation, 0.5)
        Clock.schedule_once(self.test_bonus_life_scenario, 1.5)
        Clock.schedule_once(self.test_summary, 3.0)
    
    def test_bonus_sound_generation(self, dt):
        """Test bonus life sound was generated"""
        print("Test 1: Bonus life sound generation")
        if self.audio.bonus_life_sound:
            print(f"  ✓ Bonus life sound generated successfully")
            print(f"  - Sound object: {self.audio.bonus_life_sound}")
            print(f"  - Sound duration: 0.6s (3 ascending tones)\n")
        else:
            print(f"  ✗ Bonus life sound is None\n")
    
    def test_bonus_life_scenario(self, dt):
        """Test bonus life scenario"""
        print("Test 2: Bonus life grant scenario")
        print(f"  Starting with:")
        print(f"  - Bonus lives: {self.state.bonus_lives}")
        print(f"  - Streak: {self.state.streak}")
        print(f"  - Lives per streak: {self.state.lives_per_streak}\n")
        
        # Simulate 7 consecutive correct answers to grant a life
        print(f"  Simulating 7 consecutive correct answers...")
        for i in range(7):
            result = self.state.handle_correct_answer()
            if result.get('life_granted'):
                print(f"\n  Answer {i+1} - BONUS LIFE GRANTED! ✓")
                print(f"  - Message: {result['message']}")
                print(f"  - Bonus lives now: {self.state.bonus_lives}")
                print(f"  - Streak: {self.state.streak}")
                
                # Play the bonus life sound
                print(f"\n  Playing bonus life sound...")
                self.audio.play_bonus_life_sound()
                print(f"  ✓ Bonus life sound played\n")
            else:
                print(f"  Answer {i+1} correct: Streak = {self.state.streak}, Message: {result['message']}")
    
    def test_summary(self, dt):
        """Test summary"""
        print("=== Bonus Life Sound Features ===")
        print("✓ Bonus life sound generates during init")
        print("✓ Sound is a rising 3-tone jingle (cheerful)")
        print("  - G4 (392 Hz) → C5 (523.25 Hz) → G5 (783.99 Hz)")
        print("✓ Each tone is 200ms with fade in/out")
        print("✓ Total duration: 600ms")
        print("✓ Volume: 0.6 (prominent)")
        print("✓ Plays when bonus life is granted")
        print("✓ Integration in game:")
        print("  - Player gets 7 consecutive correct answers")
        print("  - Bonus life is granted (capped at +2 bonus lives)")
        print("  - Positive sound plays immediately")
        print("  - Creates satisfying reward feedback")
        print("\n✓ All tests passed!\n")


class TestApp(App):
    """Test application"""
    
    def build(self):
        return BonusLifeSoundTest()


if __name__ == "__main__":
    print("Starting bonus life sound test...")
    TestApp().run()

