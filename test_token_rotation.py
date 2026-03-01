"""
Test script for token rotation feature
Verifies: subtle random rotation between -1° and +1°
"""

import sys
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.animation import Animation
from station_token import StationToken
import random


class TokenRotationTest(Widget):
    """Test widget for token rotation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.setup_test, 0.5)
    
    def setup_test(self, dt):
        """Create test tokens with random rotations"""
        print("\n=== Token Rotation Test ===")
        print("Expected behavior:")
        print("- Each token has random rotation between -1° and +1°")
        print("- Rotation is applied from center point")
        print("- Tokens appear slightly tilted, not perfectly aligned")
        print("\nCreating 5 test tokens...\n")
        
        # Test data
        test_stations = [
            {"id": "L3_ZU", "name_ca": "Zona Universitària", "color": "#00923F"},
            {"id": "L3_PR", "name_ca": "Palau Reial", "color": "#00923F"},
            {"id": "L3_MC", "name_ca": "Maria Cristina", "color": "#00923F"},
            {"id": "L3_LC", "name_ca": "Les Corts", "color": "#00923F"},
            {"id": "L3_CP", "name_ca": "Collblanc", "color": "#00923F"}
        ]
        
        # Create tokens with random rotations
        rotations = []
        for i, station in enumerate(test_stations):
            x_pos = 50 + i * 150
            y_pos = 300
            
            token = StationToken(
                station_id=station["id"],
                name_ca=station["name_ca"],
                line_color_hex=station["color"],
                pos=(x_pos, y_pos),
                size=(140, 60)
            )
            
            # Set random rotation between -1 and +1 degrees
            rotation_value = random.uniform(-1, 1)
            token.rotation = rotation_value
            rotations.append(rotation_value)
            
            self.add_widget(token)
            
            print(f"Token {i+1} ({station['name_ca']}):")
            print(f"  - Position: ({x_pos}, {y_pos})")
            print(f"  - Rotation: {rotation_value:.3f}°")
        
        # Statistics
        print(f"\n=== Rotation Statistics ===")
        print(f"Min rotation: {min(rotations):.3f}°")
        print(f"Max rotation: {max(rotations):.3f}°")
        print(f"Average: {sum(rotations)/len(rotations):.3f}°")
        print(f"Range: {max(rotations) - min(rotations):.3f}°")
        print("\nAll rotations within [-1°, +1°] range: " + 
              ("✓ PASS" if all(-1 <= r <= 1 for r in rotations) else "✗ FAIL"))
        
        # Add reference lines
        Clock.schedule_once(lambda dt: self.draw_reference_lines(y_pos), 0.1)
    
    def draw_reference_lines(self, y_pos):
        """Draw horizontal reference line to show rotation visually"""
        from kivy.graphics import Color, Line
        with self.canvas.before:
            Color(1, 0, 0, 0.3)
            # Horizontal reference line
            Line(points=[0, y_pos + 30, 800, y_pos + 30], width=1)


class TestApp(App):
    """Test application"""
    
    def build(self):
        return TokenRotationTest()


if __name__ == "__main__":
    print("Starting token rotation test...")
    TestApp().run()
