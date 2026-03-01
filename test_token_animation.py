"""
Test script for token entrance animation
Verifies: upward fade-in + scale bounce with staggered delays
"""

import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from station_token import StationToken


class TokenAnimationTest(Widget):
    """Test widget for token entrance animation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.setup_test, 0.5)
    
    def setup_test(self, dt):
        """Create and animate test tokens"""
        print("\n=== Token Entrance Animation Test ===")
        print("Expected behavior:")
        print("- Tokens start 20px below, transparent, scale 0.9")
        print("- 80ms stagger between tokens")
        print("- 0.4s upward movement + fade in")
        print("- Scale bounce: 0.9 → 1.05 → 1.0")
        print("\nCreating 3 test tokens...\n")
        
        # Test data
        test_stations = [
            {"id": "L3_ZU", "name_ca": "Zona Universitària", "line_color_hex": "#FF0000"},
            {"id": "L3_PR", "name_ca": "Palau Reial", "line_color_hex": "#00FF00"},
            {"id": "L3_MC", "name_ca": "Maria Cristina", "line_color_hex": "#0000FF"}
        ]
        
        # Create tokens at fixed positions with animation
        positions = [100, 270, 440]  # 170px spacing
        final_y = 300
        
        for i, station in enumerate(test_stations):
            # Create token below final position
            token = StationToken(
                station_id=station["id"],
                name_ca=station["name_ca"],
                line_color_hex=station["line_color_hex"],
                pos=(positions[i], final_y - 20),  # Start 20px below
                size=(140, 60)
            )
            
            # Set initial state
            token.opacity = 0
            token.scale_value = 0.9
            
            self.add_widget(token)
            
            # Schedule staggered animation
            delay = i * 0.08  # 80ms stagger
            Clock.schedule_once(lambda dt, t=token, y=final_y, idx=i: 
                                self.animate_token(t, y, idx), delay)
    
    def animate_token(self, token, final_y, index):
        """Animate single token entrance"""
        print(f"Token {index+1} animation start:")
        print(f"  - Position: {token.pos}")
        print(f"  - Opacity: {token.opacity}")
        print(f"  - Scale: {token.scale_value}")
        
        # Movement + fade animation
        move_anim = Animation(
            y=final_y,
            opacity=1,
            duration=0.4,
            transition='out_cubic'
        )
        
        # Scale bounce: 0.9 → 1.05 → 1.0
        scale_up = Animation(
            scale_value=1.05,
            duration=0.25,
            transition='out_quad'
        )
        scale_down = Animation(
            scale_value=1.0,
            duration=0.15,
            transition='in_out_quad'
        )
        
        # Chain animations
        move_anim.start(token)
        scale_up.start(token)
        scale_up.bind(on_complete=lambda *args: scale_down.start(token))
        
        # Log completion
        def log_complete(anim, widget):
            print(f"Token {index+1} animation complete:")
            print(f"  - Final position: {widget.pos}")
            print(f"  - Final opacity: {widget.opacity}")
            print(f"  - Final scale: {widget.scale_value}\n")
        
        scale_down.bind(on_complete=log_complete)


class TestApp(App):
    """Test application"""
    
    def build(self):
        return TokenAnimationTest()


if __name__ == "__main__":
    print("Starting token animation test...")
    TestApp().run()
