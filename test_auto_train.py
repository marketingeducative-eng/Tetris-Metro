"""
Auto Train Demo - Train automatically loops through stations
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from line_map_view import LineMapView
from train_sprite import TrainSprite
from data.metro_loader import load_metro_network
from pathlib import Path


class AutoTrainApp(App):
    """Auto-running train demo"""
    
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
            Color(0.08, 0.08, 0.12, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text=f'🚇 Auto Train - {self.l3.name}',
            size_hint=(1, None),
            height=70,
            pos_hint={'x': 0, 'top': 1},
            font_size='26sp',
            bold=True
        )
        root.add_widget(title)
        
        # Current station label
        self.station_label = Label(
            text='',
            size_hint=(1, None),
            height=60,
            pos_hint={'x': 0, 'top': 0.90},
            font_size='20sp',
            color=(0.3, 1, 0.3, 1)
        )
        root.add_widget(self.station_label)
        
        # Progress label
        self.progress_label = Label(
            text='0 / 0',
            size_hint=(None, None),
            size=(100, 40),
            pos_hint={'right': 0.98, 'top': 0.98},
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        root.add_widget(self.progress_label)
        
        # Line map view (centered)
        self.line_map = LineMapView(
            size_hint=(None, None),
            size=(320, 580),
            pos_hint={'center_x': 0.5, 'center_y': 0.45}
        )
        
        # Use 12 stations
        station_objects = self.l3.stations[:12]
        self.stations = [s.name for s in station_objects]
        self.line_map.set_line(
            line_id=self.l3.id,
            line_color_hex=self.l3.color,
            station_names=self.stations
        )
        self.line_map.set_next_index(0)
        
        root.add_widget(self.line_map)
        
        # Create train sprite
        self.train = TrainSprite(size=(50, 70))
        self.train.train_color = [0.98, 0.25, 0.25, 1]  # Bright red
        self.train.set_path(self.line_map)
        self.train.set_on_arrival_callback(self._on_train_arrival)
        
        root.add_widget(self.train)
        
        # Journey state
        self.current_node = 0
        self.journey_duration = 1.2
        
        # Auto-start after short delay
        Clock.schedule_once(lambda dt: self._start_journey(), 1.0)
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def _start_journey(self):
        """Start the journey automatically"""
        self.current_node = 0
        self.station_label.text = f'Partint de: {self.stations[0]}'
        self.progress_label.text = f'0 / {len(self.stations)}'
        
        # Move to first station (already there, so move to second)
        Clock.schedule_once(lambda dt: self._move_to_next(), 0.5)
    
    def _move_to_next(self):
        """Move to next station"""
        self.current_node += 1
        
        # Check if completed
        if self.current_node >= len(self.stations):
            # Loop back to start
            self.current_node = 0
            self.station_label.text = '🔄 Tornant al inici...'
            self.station_label.color = (1, 0.8, 0.3, 1)
            Clock.schedule_once(lambda dt: self._move_to_next(), 1.5)
            return
        
        # Update UI
        station_name = self.stations[self.current_node]
        self.station_label.text = f'→ {station_name}'
        self.station_label.color = (0.3, 0.8, 1, 1)
        self.progress_label.text = f'{self.current_node} / {len(self.stations)}'
        
        # Update line map highlight
        self.line_map.set_next_index(self.current_node)
        
        # Move train
        self.train.move_to_node(self.current_node, self.journey_duration)
    
    def _on_train_arrival(self, node_index: int):
        """Called when train arrives"""
        station_name = self.stations[node_index]
        print(f"🚇 Arrived at: {station_name}")
        
        # Update UI
        self.station_label.text = f'📍 {station_name}'
        self.station_label.color = (0.3, 1, 0.3, 1)
        
        # Schedule next move
        Clock.schedule_once(lambda dt: self._move_to_next(), 0.8)


if __name__ == '__main__':
    AutoTrainApp().run()
