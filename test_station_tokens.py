"""
Station Tokens Test - Drag & Drop demo with LineMapView
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from line_map_view import LineMapView
from station_token import StationToken
from token_drop_area import TokenDropArea
from data.metro_loader import load_metro_network
from pathlib import Path


class StationTokensTestApp(App):
    """Test app for station tokens with drag & drop"""
    
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
            Color(0.1, 0.1, 0.15, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text=f'🎯 Drag & Drop Stations\n{self.l3.name}',
            size_hint=(1, None),
            height=80,
            pos_hint={'x': 0, 'top': 1},
            font_size='20sp'
        )
        root.add_widget(title)
        
        # Instructions
        self.instructions = Label(
            text='Drag tokens to matching slots on the line →',
            size_hint=(1, None),
            height=40,
            pos_hint={'x': 0, 'top': 0.88},
            font_size='14sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        root.add_widget(self.instructions)
        
        # Score label
        self.score = 0
        self.score_label = Label(
            text='Score: 0',
            size_hint=(None, None),
            size=(120, 40),
            pos_hint={'right': 0.98, 'top': 0.98},
            font_size='18sp'
        )
        root.add_widget(self.score_label)
        
        # Line map view (centered left side)
        self.line_map = LineMapView(
            size_hint=(None, None),
            size=(250, 500),
            pos_hint={'x': 0.05, 'center_y': 0.45}
        )
        
        # Use all 12 stations from L3
        l3_stations = self.l3.stations[:12]
        self.line_map.set_line(
            line_id=self.l3.id,
            line_color_hex=self.l3.color,
            station_names=l3_stations
        )
        self.line_map.set_next_index(0)
        
        root.add_widget(self.line_map)
        
        # Token drop area (bottom)
        self.token_area = TokenDropArea(
            size_hint=(0.9, None),
            height=80,
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        
        # Prepare token queue (shuffled stations)
        import random
        shuffled_stations = l3_stations.copy()
        random.shuffle(shuffled_stations)
        
        token_queue = [
            {
                'id': f'station_{i}',
                'name': station,
                'color': self.l3.color
            }
            for i, station in enumerate(shuffled_stations)
        ]
        
        self.token_area.set_token_queue(token_queue)
        
        # Set callbacks
        self.token_area.set_on_token_dropped_callback(self._on_token_dropped)
        self.token_area.set_on_token_used_callback(self._on_token_used)
        
        root.add_widget(self.token_area)
        
        # Current target label
        self.target_label = Label(
            text=f'Next target: {l3_stations[0]}',
            size_hint=(None, None),
            size=(300, 40),
            pos_hint={'center_x': 0.5, 'y': 0.12},
            font_size='18sp',
            color=(0.3, 1, 0.3, 1)
        )
        root.add_widget(self.target_label)
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def _on_token_dropped(self, token: StationToken, x: float, y: float) -> bool:
        """
        Handle token drop
        Returns True if drop was accepted
        """
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
        
        # Check if it's the correct station
        target_station = self.line_map.station_names[self.line_map.next_index]
        
        if token.name_ca == target_station:
            # Correct!
            self.instructions.text = f'✅ Correct! {token.name_ca}'
            self.instructions.color = (0.3, 1, 0.3, 1)
            
            # Update score
            self.score += 10
            self.score_label.text = f'Score: {self.score}'
            
            # Move to next station
            next_index = self.line_map.next_index + 1
            if next_index < self.line_map.num_slots:
                self.line_map.set_next_index(next_index)
                self.target_label.text = f'Next target: {self.line_map.station_names[next_index]}'
            else:
                # Completed all stations!
                self.target_label.text = '🎉 All stations completed!'
                self.instructions.text = '🎊 You won!'
                self.instructions.color = (1, 1, 0.3, 1)
            
            return True
        else:
            # Wrong station
            self.instructions.text = f'❌ Wrong! Expected: {target_station}'
            self.instructions.color = (1, 0.3, 0.3, 1)
            return False
    
    def _on_token_used(self, token: StationToken):
        """Called when a token is successfully used"""
        print(f"Token used: {token.name_ca}")


if __name__ == '__main__':
    StationTokensTestApp().run()
