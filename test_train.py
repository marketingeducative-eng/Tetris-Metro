"""
Train Demo - Animated train moving along metro line
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from line_map_view import LineMapView
from train_sprite import TrainSprite
from data.metro_loader import load_metro_network
from pathlib import Path


class TrainDemoApp(App):
    """Demo of train moving along metro line"""
    
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
            Color(0.12, 0.12, 0.18, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text=f'🚇 Train Demo - {self.l3.name}',
            size_hint=(1, None),
            height=70,
            pos_hint={'x': 0, 'top': 1},
            font_size='24sp'
        )
        root.add_widget(title)
        
        # Status label
        self.status_label = Label(
            text='Press Start to begin journey',
            size_hint=(1, None),
            height=50,
            pos_hint={'x': 0, 'top': 0.92},
            font_size='16sp',
            color=(0.7, 0.8, 1, 1)
        )
        root.add_widget(self.status_label)
        
        # Line map view (centered)
        self.line_map = LineMapView(
            size_hint=(None, None),
            size=(300, 550),
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        
        # Use 10 stations for cleaner demo
        l3_stations = [s.name for s in self.l3.stations[:10]]
        self.line_map.set_line(
            line_id=self.l3.id,
            line_color_hex=self.l3.color,
            station_names=l3_stations
        )
        self.line_map.set_next_index(0)
        
        root.add_widget(self.line_map)
        
        # Create train sprite
        self.train = TrainSprite(size=(45, 65))
        self.train.train_color = [0.95, 0.2, 0.2, 1]  # Bright red
        self.train.set_path(self.line_map)
        self.train.set_on_arrival_callback(self._on_train_arrival)
        
        root.add_widget(self.train)
        
        # Control buttons
        button_layout = FloatLayout(
            size_hint=(0.8, None),
            height=60,
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        
        # Start button
        self.start_btn = Button(
            text='▶ Start Journey',
            size_hint=(0.45, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.start_btn.bind(on_press=self.start_journey)
        button_layout.add_widget(self.start_btn)
        
        # Stop button
        self.stop_btn = Button(
            text='⏹ Stop',
            size_hint=(0.45, 1),
            pos_hint={'right': 1, 'y': 0},
            disabled=True
        )
        self.stop_btn.bind(on_press=self.stop_journey)
        button_layout.add_widget(self.stop_btn)
        
        root.add_widget(button_layout)
        
        # Journey state
        self.is_journey_active = False
        self.current_destination = 0
        self.journey_duration = 1.2  # seconds per segment
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def start_journey(self, instance):
        """Start the automatic journey"""
        if self.is_journey_active:
            return
        
        self.is_journey_active = True
        self.current_destination = 0
        
        # Update UI
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.status_label.text = '🚇 Journey started...'
        self.status_label.color = (0.3, 1, 0.3, 1)
        
        # Reset train to first node
        first_pos = self.line_map.get_node_pos(0)
        if first_pos:
            self.train.train_x, self.train.train_y = first_pos
            self.train.current_node = 0
        
        # Start moving to next node
        self._move_to_next_node()
    
    def stop_journey(self, instance):
        """Stop the journey"""
        self.is_journey_active = False
        self.train.stop()
        
        # Update UI
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.status_label.text = '⏹ Journey stopped'
        self.status_label.color = (1, 0.5, 0.3, 1)
    
    def _move_to_next_node(self):
        """Move train to next node"""
        if not self.is_journey_active:
            return
        
        self.current_destination += 1
        
        # Check if journey is complete
        if self.current_destination >= self.line_map.node_count:
            self._complete_journey()
            return
        
        # Update line map highlight
        self.line_map.set_next_index(self.current_destination)
        
        # Move train
        station_name = self.line_map.station_names[self.current_destination]
        self.status_label.text = f'🚇 Next stop: {station_name}'
        
        self.train.move_to_node(self.current_destination, self.journey_duration)
    
    def _on_train_arrival(self, node_index: int):
        """Called when train arrives at a node"""
        if not self.is_journey_active:
            return
        
        station_name = self.line_map.station_names[node_index]
        print(f"Train arrived at node {node_index}: {station_name}")
        
        # Update status
        self.status_label.text = f'📍 Arrived: {station_name}'
        self.status_label.color = (0.3, 1, 0.3, 1)
        
        # Schedule next movement (with small delay)
        Clock.schedule_once(lambda dt: self._move_to_next_node(), 0.5)
    
    def _complete_journey(self):
        """Journey completed"""
        self.is_journey_active = False
        
        # Update UI
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.status_label.text = '🎉 Journey completed! All stations visited.'
        self.status_label.color = (1, 1, 0.3, 1)


if __name__ == '__main__':
    TrainDemoApp().run()
