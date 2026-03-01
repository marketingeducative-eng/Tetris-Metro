"""
Test Overlay Lifecycle Hardening
=================================

This test validates that overlay lifecycle management prevents:
- Duplication (only one overlay of each type exists at a time)
- Animation leaks (all animations cancelled on close)
- Event leaks (scheduled Clock events cancelled on close)
- Touch handler leaks (event handlers unbound on close)
- Camera shake position leaks (parent position always reset)

Test Coverage:
1. Tutorial overlay
2. Settings overlay
3. Tourist overlay
4. Journey overlay
5. Onboarding overlay
6. Line completed overlay

Expected Behavior:
- Debug log shows "Already showing" when attempting to open duplicate
- Overlay count stays at 0 or 1 (never duplicates)
- Camera position returns to (0, 0) after shake
- No console errors about missing widgets or unbound methods
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.animation import Animation

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_propera_parada import Renderer, GameState
from data.metro_loader import load_metro_network


class MockStation:
    """Mock station for testing"""
    def __init__(self):
        self.id = 'test_station'
        self.name = 'Test Station'
        self.x = 400
        self.y = 300
        self.description = 'This is a test station for overlay lifecycle validation.'
        self.image_url = None  # No image to avoid Ken Burns complexity


class MockProgressManager:
    """Mock progress manager with sample data"""
    def get_total_score(self):
        return 15000
    
    def get_completed_lines(self):
        return ['L1', 'L3', 'L5']
    
    def get_earned_badges(self):
        return [
            {'id': 'modernisme', 'name': 'Modernisme', 'icon': '🏛️'},
            {'id': 'mar', 'name': 'Mar i Muntanya', 'icon': '🌊'},
            {'id': 'explorador', 'name': 'Explorador', 'icon': '🗺️'},
        ]
    
    def is_first_day_complete(self):
        return True
    
    def get_completed_station_ids(self, line_id):
        # Mock: each line has 10 stations
        return [f'{line_id}_S{i}' for i in range(1, 11)]


class TestOverlayLifecycleApp(App):
    """Test app for overlay lifecycle validation"""
    
    def build(self):
        manager = ScreenManager()
        test_screen = Screen(name='test')
        
        # Container for renderer
        container = FloatLayout()
        
        # Initialize game state
        network = load_metro_network()
        line = network.get_line("L1") if network else None
        if not line and getattr(network, "lines", None):
            line = network.lines[0]
        if not line:
            raise RuntimeError("Metro network not available for overlay test")

        state = GameState(line, line_id=line.id, practice_mode=True)

        # Initialize renderer
        renderer = Renderer(container, state)
        renderer.setup_all()
        
        # Attach mock progress manager
        container.progress_manager = MockProgressManager()
        
        # Test control panel
        panel = FloatLayout(size_hint=(1, None), height=400, pos_hint={'x': 0, 'y': 0})
        
        # Title
        title = Label(
            text='Overlay Lifecycle Test Suite',
            font_size='20sp',
            bold=True,
            size_hint=(1, None),
            height=40,
            pos_hint={'center_x': 0.5, 'top': 1}
        )
        panel.add_widget(title)
        
        # Status label
        status = Label(
            text='Click buttons to test overlays. Check console for debug logs.',
            font_size='14sp',
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        panel.add_widget(status)
        
        # Test buttons
        button_configs = [
            ('Test Tutorial', lambda x: self._test_tutorial(renderer)),
            ('Test Settings', lambda x: self._test_settings(renderer)),
            ('Test Tourist', lambda x: self._test_tourist(renderer)),
            ('Test Journey', lambda x: self._test_journey(renderer)),
            ('Test Onboarding', lambda x: self._test_onboarding(renderer)),
            ('Test Line Completed', lambda x: self._test_line_completed(renderer)),
            ('Test Camera Shake', lambda x: self._test_camera_shake(renderer, container)),
            ('Test Rapid Cycles', lambda x: self._test_rapid_cycles(renderer)),
        ]
        
        for i, (text, callback) in enumerate(button_configs):
            row = i // 2
            col = i % 2
            btn = Button(
                text=text,
                size_hint=(None, None),
                size=(180, 40),
                pos=(20 + col * 200, 300 - row * 50)
            )
            btn.bind(on_release=callback)
            panel.add_widget(btn)
        
        container.add_widget(panel)
        test_screen.add_widget(container)
        manager.add_screen(test_screen)
        
        return manager
    
    def _test_tutorial(self, renderer):
        """Test tutorial overlay lifecycle"""
        print("\n=== Testing Tutorial Overlay ===")
        print(f"Before: tutorial_overlay = {renderer.tutorial_overlay}")
        
        # First call should succeed
        renderer.show_tutorial(lambda: renderer.dismiss_tutorial())
        print(f"After show_tutorial(): tutorial_overlay = {renderer.tutorial_overlay}")
        
        # Second call should log "Already showing"
        renderer.show_tutorial(lambda: renderer.dismiss_tutorial())
        
        # Close after 2 seconds
        def close_tutorial(dt):
            print("Closing tutorial overlay...")
            renderer.dismiss_tutorial()
            print(f"After dismiss: tutorial_overlay = {renderer.tutorial_overlay}")
        
        Clock.schedule_once(close_tutorial, 2)
    
    def _test_settings(self, renderer):
        """Test settings overlay lifecycle"""
        print("\n=== Testing Settings Overlay ===")
        print(f"Before: settings_overlay = {renderer.settings_overlay}")
        
        # First call should succeed
        renderer.show_settings_overlay(lambda: print("Settings closed"))
        print(f"After show_settings_overlay(): settings_overlay = {renderer.settings_overlay}")
        
        # Second call should log "Already showing"
        renderer.show_settings_overlay(lambda: None)
        
        # Close after 2 seconds
        def close_settings(dt):
            print("Closing settings overlay...")
            renderer.dismiss_settings()
            print(f"After dismiss: settings_overlay = {renderer.settings_overlay}")
        
        Clock.schedule_once(close_settings, 2)
    
    def _test_tourist(self, renderer):
        """Test tourist overlay lifecycle"""
        print("\n=== Testing Tourist Overlay ===")
        print(f"Before: tourist_overlay = {renderer.tourist_overlay}")
        
        station = MockStation()
        
        # First call should succeed
        renderer.show_tourist_popup(station, lambda: print("Tourist closed"))
        print(f"After show_tourist_popup(): tourist_overlay = {renderer.tourist_overlay}")
        
        # Second call should log "Already showing"
        renderer.show_tourist_popup(station, lambda: None)
        
        # Close after 2 seconds
        def close_tourist(dt):
            print("Closing tourist overlay...")
            renderer.dismiss_tourist_popup()
            print(f"After dismiss: tourist_overlay = {renderer.tourist_overlay}")
        
        Clock.schedule_once(close_tourist, 2)
    
    def _test_journey(self, renderer):
        """Test journey overlay lifecycle"""
        print("\n=== Testing Journey Overlay ===")
        print(f"Before: journey_overlay = {getattr(renderer, 'journey_overlay', None)}")
        
        # First call should succeed
        renderer.show_journey_overlay(lambda: print("Journey closed"))
        print(f"After show_journey_overlay(): journey_overlay = {renderer.journey_overlay}")
        
        # Second call should log "Already showing"
        renderer.show_journey_overlay(lambda: None)
        
        # Note: Journey overlay closes when user clicks the close button or outside panel
        # For automated testing, we'll close it programmatically after 3 seconds
        def close_journey(dt):
            if renderer.journey_overlay:
                print("Closing journey overlay programmatically...")
                # Simulate close button click
                renderer._cleanup_overlay('journey_overlay')
                print(f"After cleanup: journey_overlay = {renderer.journey_overlay}")
        
        Clock.schedule_once(close_journey, 3)
    
    def _test_onboarding(self, renderer):
        """Test onboarding overlay lifecycle"""
        print("\n=== Testing Onboarding Overlay ===")
        print(f"Before: onboarding_overlay = {renderer.onboarding_overlay}")
        
        # First call should succeed
        renderer.show_onboarding_overlay(lambda: None)
        print(f"After show_onboarding_overlay(): onboarding_overlay = {renderer.onboarding_overlay}")
        
        # Second call should log "Already showing"
        renderer.show_onboarding_overlay(lambda: None)
        
        # Note: Onboarding auto-closes after narrative sequence
        # For testing, we'll close it after 2 seconds
        def close_onboarding(dt):
            if renderer.onboarding_overlay:
                print("Closing onboarding overlay...")
                renderer._cleanup_overlay('onboarding_overlay')
                print(f"After cleanup: onboarding_overlay = {renderer.onboarding_overlay}")
        
        Clock.schedule_once(close_onboarding, 2)
    
    def _test_line_completed(self, renderer):
        """Test line completed overlay lifecycle"""
        print("\n=== Testing Line Completed Overlay ===")
        print(f"Before: line_completed_overlay = {renderer.line_completed_overlay}")
        
        # First call should succeed
        renderer.show_line_completed(12, lambda action: print(f"Line completed action: {action}"))
        print(f"After show_line_completed(): line_completed_overlay = {renderer.line_completed_overlay}")
        
        # Second call should log "Already showing"
        renderer.show_line_completed(12, lambda action: None)
        
        # Close after 3 seconds (let pulse animation run)
        def close_line_completed(dt):
            if renderer.line_completed_overlay:
                print("Closing line completed overlay...")
                renderer._cleanup_overlay('line_completed_overlay')
                print(f"After cleanup: line_completed_overlay = {renderer.line_completed_overlay}")
                print(f"Pulse event: {renderer._line_completed_pulse_event}")
        
        Clock.schedule_once(close_line_completed, 3)
    
    def _test_camera_shake(self, renderer, container):
        """Test camera shake position reset"""
        print("\n=== Testing Camera Shake ===")
        print(f"Initial container position: {container.pos}")
        
        # Trigger camera shake
        renderer._camera_shake(duration=0.3, intensity=5)
        
        # Check position after shake completes
        def check_position(dt):
            print(f"After shake: container position = {container.pos}")
            print(f"Camera shake event: {renderer._camera_shake_event}")
            if container.pos == [0, 0]:
                print("✓ Position correctly reset to (0, 0)")
            else:
                print(f"✗ Position not reset! Still at {container.pos}")
        
        Clock.schedule_once(check_position, 0.5)
    
    def _test_rapid_cycles(self, renderer):
        """Test rapid open/close cycles to detect leaks"""
        print("\n=== Testing Rapid Open/Close Cycles ===")
        
        station = MockStation()
        
        # Rapidly open and close tutorial
        def cycle_tutorial(dt):
            renderer.show_tutorial(lambda: renderer.dismiss_tutorial())
            Clock.schedule_once(lambda dt: renderer.dismiss_tutorial(), 0.1)
        
        for i in range(5):
            Clock.schedule_once(cycle_tutorial, i * 0.3)
        
        # Rapidly open and close settings
        def cycle_settings(dt):
            renderer.show_settings_overlay(lambda: None)
            Clock.schedule_once(lambda dt: renderer.dismiss_settings(), 0.1)
        
        for i in range(5):
            Clock.schedule_once(cycle_settings, 2 + i * 0.3)
        
        print("Running 10 rapid cycles. Watch for 'Already showing' logs and check overlay counts.")
        
        def final_check(dt):
            print("\n=== Final State Check ===")
            print(f"tutorial_overlay: {renderer.tutorial_overlay}")
            print(f"settings_overlay: {renderer.settings_overlay}")
            print(f"tourist_overlay: {renderer.tourist_overlay}")
            print(f"journey_overlay: {getattr(renderer, 'journey_overlay', None)}")
            print(f"onboarding_overlay: {renderer.onboarding_overlay}")
            print(f"line_completed_overlay: {renderer.line_completed_overlay}")
            print("All overlays should be None if lifecycle cleanup is correct.")
        
        Clock.schedule_once(final_check, 5)


if __name__ == '__main__':
    print("="*60)
    print("OVERLAY LIFECYCLE TEST SUITE")
    print("="*60)
    print("\nThis test validates:")
    print("1. Duplication prevention")
    print("2. Animation cleanup")
    print("3. Event cancellation")
    print("4. Touch handler unbinding")
    print("5. Camera shake position reset")
    print("\nWatch console for debug logs:")
    print("  [Overlay] Show: overlay_name")
    print("  [Overlay] Already showing: overlay_name")
    print("  [Overlay] Cleanup: overlay_name")
    print("\n" + "="*60 + "\n")
    
    TestOverlayLifecycleApp().run()

