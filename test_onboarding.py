"""
Test script for narrative onboarding system
Tests the first-launch onboarding experience
"""
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from game_propera_parada import ProximaParadaGame
from core.settings import SettingsManager
from data.metro_loader import load_metro_network
from pathlib import Path


class OnboardingTestScreen(Screen):
    """Test screen for onboarding flow"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load metro network
        data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
        metro_network = load_metro_network(str(data_path))
        
        # Create game widget
        self.game_widget = ProximaParadaGame(
            line_id="L3",
            metro_network=metro_network,
            enable_settings_hotkey=True
        )
        self.add_widget(self.game_widget)


class OnboardingTestApp(App):
    """Test app for onboarding system"""
    
    def build(self):
        # Reset onboarding flag for testing
        settings = SettingsManager()
        current_flag = settings.get('has_completed_onboarding', False)
        print(f"Current onboarding status: {current_flag}")
        
        # Optionally reset for testing (uncomment to force onboarding)
        # settings.set('has_completed_onboarding', False)
        # print("Reset onboarding flag for testing")
        
        # Create screen manager
        manager = ScreenManager()
        manager.add_widget(OnboardingTestScreen(name='game'))
        return manager


if __name__ == '__main__':
    print("=" * 50)
    print("ONBOARDING TEST")
    print("=" * 50)
    print("\nTo reset onboarding and test from scratch:")
    print("1. Uncomment line 37 in this file")
    print("2. Run the test again")
    print("\nFeatures to test:")
    print("- Cinematic fade-in from black")
    print("- Sequential Catalan narrative text")
    print("- Primary button: 'Començar el teu primer dia'")
    print("- Secondary button: 'Need help in English?'")
    print("- English help modal")
    print("- First day mode activation after completion")
    print("=" * 50)
    
    OnboardingTestApp().run()

