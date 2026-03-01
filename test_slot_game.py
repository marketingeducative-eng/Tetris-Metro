"""
Integration Example - SlotManager with LineMapView and StationTokens
Demonstrates complete game flow
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from line_map_view import LineMapView
from token_drop_area import TokenDropArea
from slot_manager import SlotManager
from data.metro_loader import load_metro_network
from pathlib import Path
import random


class SlotGameApp(App):
    """Complete game with SlotManager logic"""
    
    def build(self):
        """Build UI"""
        # Load metro data
        data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
        network = load_metro_network(str(data_path))
        self.l3 = network.get_line("L3")
        
        # Use first 8 stations for demo
        self.stations = self.l3.stations[:8]
        self.station_ids = [f"station_{i}" for i in range(len(self.stations))]
        
        # Initialize SlotManager
        self.slot_manager = SlotManager(
            ordered_station_ids=self.station_ids,
            window_size=3,
            parking_capacity=3
        )
        
        # Main layout
        root = FloatLayout()
        
        # Background
        with root.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text=f'🎮 Slot Game - {self.l3.name}',
            size_hint=(1, None),
            height=60,
            pos_hint={'x': 0, 'top': 1},
            font_size='22sp'
        )
        root.add_widget(title)
        
        # Score panel
        self.score_label = Label(
            text=f'Score: 0\nStreak: 0',
            size_hint=(None, None),
            size=(150, 60),
            pos_hint={'right': 0.98, 'top': 0.98},
            font_size='16sp',
            halign='right'
        )
        root.add_widget(self.score_label)
        
        # Parking indicator
        self.parking_label = Label(
            text='🚗 Parking: 0/3',
            size_hint=(None, None),
            size=(150, 40),
            pos_hint={'x': 0.02, 'top': 0.98},
            font_size='16sp',
            halign='left',
            color=(0.8, 0.8, 0.8, 1)
        )
        root.add_widget(self.parking_label)
        
        # Instructions
        self.instructions = Label(
            text='Drag tokens to the glowing slot\nWindow: Next 3 stations accepted',
            size_hint=(1, None),
            height=50,
            pos_hint={'x': 0, 'top': 0.88},
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        root.add_widget(self.instructions)
        
        # Line map view
        self.line_map = LineMapView(
            size_hint=(None, None),
            size=(250, 450),
            pos_hint={'x': 0.05, 'center_y': 0.45}
        )
        
        self.line_map.set_line(
            line_id=self.l3.id,
            line_color_hex=self.l3.color,
            station_names=self.stations
        )
        self.line_map.set_next_index(0)
        
        root.add_widget(self.line_map)
        
        # Target info
        self.target_label = Label(
            text=f'🎯 Next: {self.stations[0]}\nWindow: {", ".join(self.stations[:3])}',
            size_hint=(None, None),
            size=(320, 60),
            pos_hint={'center_x': 0.5, 'y': 0.15},
            font_size='15sp',
            color=(0.3, 1, 0.3, 1)
        )
        root.add_widget(self.target_label)
        
        # Token drop area
        self.token_area = TokenDropArea(
            size_hint=(0.9, None),
            height=80,
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        
        # Prepare token queue (shuffled)
        shuffled_stations = list(zip(self.station_ids, self.stations))
        random.shuffle(shuffled_stations)
        
        token_queue = [
            {
                'id': station_id,
                'name': station_name,
                'color': self.l3.color
            }
            for station_id, station_name in shuffled_stations
        ]
        
        self.token_area.set_token_queue(token_queue)
        self.token_area.set_on_token_dropped_callback(self._on_token_dropped)
        
        root.add_widget(self.token_area)
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def _on_token_dropped(self, token, x, y) -> bool:
        """Handle token drop"""
        # Check if dropped on line map
        if not self.line_map.collide_point(x, y):
            self.instructions.text = '❌ Drop on the line map!'
            self.instructions.color = (1, 0.3, 0.3, 1)
            return False
        
        # Get slot at drop position
        slot_index = self.line_map.get_slot_at(x, y)
        if slot_index is None:
            self.instructions.text = '❌ Drop on a station slot!'
            self.instructions.color = (1, 0.3, 0.3, 1)
            return False
        
        # Use SlotManager to validate placement
        result = self.slot_manager.attempt_place(token.station_id, slot_index)
        
        # Update UI based on result
        if result["game_over"]:
            self.instructions.text = f'🎮 {result["feedback"]}'
            if "completat" in result["feedback"]:
                self.instructions.color = (0.3, 1, 0.3, 1)
            else:
                self.instructions.color = (1, 0.3, 0.3, 1)
            return result["accepted"]
        
        if result["accepted"]:
            if result["perfect"]:
                self.instructions.text = f'✅ {result["feedback"]} (+{result["points"]})'
                self.instructions.color = (0.3, 1, 0.3, 1)
            else:
                self.instructions.text = f'⚠️ {result["feedback"]} (+{result["points"]})'
                self.instructions.color = (1, 0.8, 0.3, 1)
            
            # Update line map
            self.line_map.set_next_index(result["next_index"])
            
            # Update target window
            self._update_target_window()
            
        else:
            self.instructions.text = f'❌ {result["feedback"]}'
            self.instructions.color = (1, 0.3, 0.3, 1)
        
        # Update stats
        stats = self.slot_manager.get_stats()
        self.score_label.text = f'Score: {stats["total_score"]}\nStreak: {stats["streak"]}'
        self.parking_label.text = f'🚗 Parking: {stats["parking_count"]}/{self.slot_manager.parking_capacity}'
        
        if stats["parking_count"] >= self.slot_manager.parking_capacity:
            self.parking_label.color = (1, 0.3, 0.3, 1)
        
        return result["accepted"]
    
    def _update_target_window(self):
        """Update target window display"""
        stats = self.slot_manager.get_stats()
        next_idx = stats["next_index"]
        
        if next_idx >= len(self.stations):
            self.target_label.text = '🎉 All stations placed!'
            return
        
        # Show next station and window
        next_station = self.stations[next_idx]
        window_end = min(next_idx + self.slot_manager.window_size, len(self.stations))
        window_stations = self.stations[next_idx:window_end]
        
        self.target_label.text = f'🎯 Next: {next_station}\nWindow: {", ".join(window_stations)}'


if __name__ == '__main__':
    SlotGameApp().run()
