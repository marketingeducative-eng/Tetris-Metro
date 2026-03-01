"""
Test script for metro visualization enhancements

Tests:
1. Enhanced station node styling with hierarchy
2. Train arrival micro bounce
3. Camera punch zoom effect  
4. Subtle background gradient
5. Arrival flash animation
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from line_map_view import LineMapView
from train_sprite import TrainSprite


class MetroVisualsTestApp(App):
    def build(self):
        layout = FloatLayout()
        
        # Create line view with test data
        self.line_view = LineMapView(
            size_hint=(None, None),
            size=(140, 550),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Test data: Metro Line 3 (Green Line)
        test_stations = [
            "Zona Universitària",
            "Palau Reial",
            "Maria Cristina",
            "Les Corts",
            "Plaça del Centre",
            "Sants Estació",
            "Tarragona",
            "Espanya",
            "Poble Sec",
            "Paral·lel"
        ]
        
        self.line_view.set_line(
            line_id="L3",
            line_color_hex="#00923F",  # Green
            station_names=test_stations
        )
        
        layout.add_widget(self.line_view)
        
        # Create train
        self.train = TrainSprite(
            size_hint=(None, None),
            size=(65, 32)
        )
        self.train.set_path(self.line_view)
        layout.add_widget(self.train)
        
        # Start test sequence
        Clock.schedule_once(self.test_sequence, 1.0)
        
        return layout
    
    def test_sequence(self, dt):
        """Run through visual enhancement tests"""
        print("🚇 Testing Metro Visualization Enhancements")
        print("=" * 50)
        
        # Test 1: Node highlighting (should show enhanced glow)
        print("\n✓ Test 1: Enhanced node glow effect")
        self.line_view.highlight_node(3, duration=0.6)
        
        # Test 2: Train movement with arrival
        print("✓ Test 2: Train movement to station 2")
        self.train.move_to_node(2, duration=2.0)
        
        # Test 3: Arrival flash after train arrives
        Clock.schedule_once(lambda dt: self.test_arrival_flash(), 2.2)
        
        # Test 4: Punch zoom effect
        Clock.schedule_once(lambda dt: self.test_punch_zoom(), 2.5)
        
        # Test 5: Move to another station
        Clock.schedule_once(lambda dt: self.test_second_move(), 4.0)
        
        # Test 6: Goal marker test
        Clock.schedule_once(lambda dt: self.test_goal_marker(), 6.0)
        
        print("\n" + "=" * 50)
        print("✓ All visual enhancement tests running")
        print("  Watch for:")
        print("  - Enhanced node styling with depth")
        print("  - Train bounce on arrival")
        print("  - Subtle arrival flash")
        print("  - Punch zoom effect")
        print("  - Layered background gradient")
    
    def test_arrival_flash(self):
        """Test arrival flash animation"""
        print("✓ Test 3: Arrival flash at station 2")
        self.line_view.arrival_flash(2, duration=0.2)
    
    def test_punch_zoom(self):
        """Test punch zoom camera effect"""
        print("✓ Test 4: Punch zoom on station 2")
        self.line_view.zoom_to_node(2, zoom_factor=1.2, duration=0.3, punch=True)
    
    def test_second_move(self):
        """Test second movement with all effects"""
        print("✓ Test 5: Moving to station 5 with full effects")
        self.train.move_to_node(5, duration=2.5)
        # Schedule arrival effects
        Clock.schedule_once(lambda dt: self.line_view.arrival_flash(5, duration=0.2), 2.5)
        Clock.schedule_once(lambda dt: self.line_view.zoom_to_node(5, zoom_factor=1.2, punch=True), 2.5)
    
    def test_goal_marker(self):
        """Test goal marker visualization"""
        print("✓ Test 6: Goal marker at station 7")
        self.line_view.goal_index = 7


if __name__ == '__main__':
    MetroVisualsTestApp().run()
