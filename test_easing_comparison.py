"""
Easing Comparison Demo - Compare different easing functions for train movement
Shows multiple trains moving with different easing functions side by side
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from line_map_view import LineMapView
from train_sprite import TrainSprite
from data.metro_loader import load_metro_network
from pathlib import Path


class EasingComparisonApp(App):
    """Demo comparing different easing functions"""
    
    def build(self):
        """Build UI"""
        # Load metro data
        data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
        network = load_metro_network(str(data_path))
        self.l3 = network.get_line("L3")
        
        # Main layout
        root = FloatLayout()
        
        # Background
        with root.canvas.before:
            Color(0.10, 0.10, 0.15, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text='🚇 Easing Function Comparison',
            size_hint=(1, None),
            height=60,
            pos_hint={'x': 0, 'top': 1},
            font_size='22sp',
            bold=True
        )
        root.add_widget(title)
        
        # Subtitle
        subtitle = Label(
            text='Watch trains move with different easing functions',
            size_hint=(1, None),
            height=35,
            pos_hint={'x': 0, 'top': 0.93},
            font_size='14sp',
            color=(0.7, 0.8, 1, 1)
        )
        root.add_widget(subtitle)
        
        # Easing functions to compare
        self.easing_configs = [
            ('linear', 'Linear (No Easing)', [0.7, 0.7, 0.7, 1]),
            ('in_out_quint', 'Quintic (Smooth)', [0.3, 0.9, 0.3, 1]),
            ('in_out_cubic', 'Cubic (Moderate)', [0.95, 0.6, 0.2, 1]),
            ('in_out_sine', 'Sine (Gentle)', [0.4, 0.7, 0.95, 1]),
            ('in_out_expo', 'Exponential (Dramatic)', [0.95, 0.3, 0.3, 1]),
        ]
        
        # Create line views and trains for each easing function
        self.line_maps = []
        self.trains = []
        self.labels = []
        
        num_configs = len(self.easing_configs)
        spacing = 0.7 / (num_configs + 1)
        
        for i, (easing, label_text, color) in enumerate(self.easing_configs):
            # Position from top
            y_pos = 0.80 - (i * 0.16)
            
            # Label for this easing function
            ease_label = Label(
                text=label_text,
                size_hint=(None, None),
                size=(200, 30),
                pos_hint={'x': 0.05, 'center_y': y_pos},
                font_size='13sp',
                halign='left',
                valign='middle'
            )
            ease_label.bind(size=ease_label.setter('text_size'))
            root.add_widget(ease_label)
            self.labels.append(ease_label)
            
            # Line map view (horizontal, compact)
            line_map = LineMapView(
                size_hint=(None, None),
                size=(450, 50),
                pos_hint={'x': 0.30, 'center_y': y_pos}
            )
            
            # Use 5 stations for compact demo
            l3_stations = [s.name for s in self.l3.stations[:5]]
            line_map.set_line(
                line_id=self.l3.id,
                line_color_hex=self.l3.color,
                station_names=l3_stations
            )
            line_map.set_next_index(0)
            
            root.add_widget(line_map)
            self.line_maps.append(line_map)
            
            # Create train sprite with specific easing
            train = TrainSprite(
                size=(35, 50),
                easing_function=easing
            )
            train.train_color = color
            train.set_path(line_map)
            
            root.add_widget(train)
            self.trains.append(train)
        
        # Control button
        self.race_btn = Button(
            text='▶ Race Trains',
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            font_size='16sp'
        )
        self.race_btn.bind(on_press=self.start_race)
        root.add_widget(self.race_btn)
        
        # Race state
        self.is_racing = False
        self.race_duration = 2.5  # seconds
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def start_race(self, instance):
        """Start the race - all trains move simultaneously"""
        if self.is_racing:
            return
        
        self.is_racing = True
        self.race_btn.disabled = True
        self.race_btn.text = '⏳ Racing...'
        
        # Reset all trains to first node
        for i, train in enumerate(self.trains):
            line_map = self.line_maps[i]
            first_pos = line_map.get_node_pos(0)
            if first_pos:
                train.train_x, train.train_y = first_pos
                train.current_node = 0
        
        # Start all trains moving to last node simultaneously
        target_node = 4  # Last of 5 stations
        for i, train in enumerate(self.trains):
            line_map = self.line_maps[i]
            line_map.set_next_index(target_node)
            train.move_to_node(target_node, self.race_duration)
        
        # Re-enable button after race
        Clock.schedule_once(self._race_complete, self.race_duration + 0.5)
    
    def _race_complete(self, dt):
        """Called when race is complete"""
        self.is_racing = False
        self.race_btn.disabled = False
        self.race_btn.text = '🔄 Race Again'


if __name__ == '__main__':
    EasingComparisonApp().run()
