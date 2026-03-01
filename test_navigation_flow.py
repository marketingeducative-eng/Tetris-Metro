#!/usr/bin/env python3
"""
Manual Navigation Flow Test Script
Tests the complete navigation loop for line completion and game over scenarios.

Usage:
    python test_navigation_flow.py

Test Cases:
1. Line completion -> Back to lines
2. Line completion -> Repeat line
3. Line completion -> Exit to cover
4. Game over -> Back to lines
5. Game over -> Play again
6. ESC key behavior at each screen
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from ui.screens import build_proxima_parada_root

class NavigationTestApp(App):
    """Test app for navigation flow"""
    
    def build(self):
        # Build the main UI
        root = build_proxima_parada_root(
            practice_mode=False,
            direction_mode=False,
            random_seed=42  # For reproducible testing
        )
        
        # Schedule test instructions
        Clock.schedule_once(lambda dt: self.show_test_instructions(), 1.0)
        
        return root
    
    def show_test_instructions(self):
        """Show test instructions overlay"""
        print("\n" + "="*70)
        print("NAVIGATION FLOW TEST")
        print("="*70)
        print("\nTest Scenarios:")
        print("\n1. LINE COMPLETION FLOW:")
        print("   - Play a line until completion (or use practice mode)")
        print("   - Test 'Tornar a línies' button -> Should go to line select")
        print("   - Test 'Repetir línia' button -> Should restart same line")
        print("   - Test 'Sortir' button -> Should go to cover screen")
        
        print("\n2. GAME OVER FLOW:")
        print("   - Play until game over (run out of lives)")
        print("   - Test 'Tornar a línies' button -> Should go to line select")
        print("   - Test 'Jugar de nou' button -> Should restart same line")
        
        print("\n3. ESC KEY FLOW:")
        print("   - From Game: ESC -> Line Select")
        print("   - From Line Select: ESC -> Cover")
        print("   - From Cover: ESC -> Exit App")
        
        print("\n4. MULTI-LINE FLOW:")
        print("   - Complete line -> Back to lines -> Select different line")
        print("   - Verify new line loads correctly")
        print("   - Verify progress is saved")
        
        print("\n" + "="*70)
        print("Press ESC at any time to navigate back")
        print("="*70 + "\n")


def main():
    """Run the navigation test"""
    print("\nStarting Navigation Flow Test...")
    print("This will launch the game in test mode.")
    print("Follow the on-screen instructions to test each scenario.\n")
    
    NavigationTestApp().run()
    
    print("\n✓ Test completed!")


if __name__ == '__main__':
    main()
