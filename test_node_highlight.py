"""
Node Highlight Demo - Test scale pulse animation on station nodes
Shows the subtle scale pulse (1.0 → 1.15 → 1.0) with glow effect
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from line_map_view import LineMapView
from data.metro_loader import load_metro_network
from pathlib import Path


class NodeHighlightApp(App):
    """Demo of node highlight with scale pulse animation"""
    
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
            text='🎯 Node Highlight Animation Demo',
            size_hint=(1, None),
            height=70,
            pos_hint={'x': 0, 'top': 1},
            font_size='24sp',
            bold=True
        )
        root.add_widget(title)
        
        # Instructions
        instructions = Label(
            text='Click buttons to see scale pulse (1.0 → 1.15 → 1.0) on different nodes',
            size_hint=(1, None),
            height=40,
            pos_hint={'x': 0, 'top': 0.92},
            font_size='14sp',
            color=(0.7, 0.8, 1, 1)
        )
        root.add_widget(instructions)
        
        # Line map view (centered)
        self.line_map = LineMapView(
            size_hint=(None, None),
            size=(300, 550),
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        
        # Use 8 stations for demo
        l3_stations = [s.name for s in self.l3.stations[:8]]
        self.line_map.set_line(
            line_id=self.l3.id,
            line_color_hex=self.l3.color,
            station_names=l3_stations
        )
        self.line_map.set_next_index(3)  # Set active node in middle
        
        root.add_widget(self.line_map)
        
        # Control buttons
        button_layout = FloatLayout(
            size_hint=(0.9, None),
            height=120,
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        
        # Sequential highlight button
        seq_btn = Button(
            text='▶ Sequential Highlight',
            size_hint=(0.45, None),
            height=50,
            pos_hint={'x': 0, 'y': 0.55},
            font_size='14sp'
        )
        seq_btn.bind(on_press=self.start_sequential)
        button_layout.add_widget(seq_btn)
        
        # Random highlight button
        random_btn = Button(
            text='🎲 Random Highlight',
            size_hint=(0.45, None),
            height=50,
            pos_hint={'right': 1, 'y': 0.55},
            font_size='14sp'
        )
        random_btn.bind(on_press=self.highlight_random)
        button_layout.add_widget(random_btn)
        
        # Top node button
        top_btn = Button(
            text='Highlight Top',
            size_hint=(0.3, None),
            height=45,
            pos_hint={'x': 0, 'y': 0},
            font_size='13sp'
        )
        top_btn.bind(on_press=lambda x: self.highlight_node(0))
        button_layout.add_widget(top_btn)
        
        # Middle node button
        mid_btn = Button(
            text='Highlight Middle',
            size_hint=(0.3, None),
            height=45,
            pos_hint={'center_x': 0.5, 'y': 0},
            font_size='13sp'
        )
        mid_btn.bind(on_press=lambda x: self.highlight_node(3))
        button_layout.add_widget(mid_btn)
        
        # Bottom node button
        bot_btn = Button(
            text='Highlight Bottom',
            size_hint=(0.3, None),
            height=45,
            pos_hint={'right': 1, 'y': 0},
            font_size='13sp'
        )
        bot_btn.bind(on_press=lambda x: self.highlight_node(7))
        button_layout.add_widget(bot_btn)
        
        root.add_widget(button_layout)
        
        # Sequential state
        self.is_sequential_running = False
        self.sequential_index = 0
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def highlight_node(self, index):
        """Highlight a specific node with scale pulse"""
        self.line_map.highlight_node(index, duration=0.5)
    
    def highlight_random(self, instance):
        """Highlight a random node"""
        import random
        node_count = len(self.line_map.station_names)
        random_index = random.randint(0, node_count - 1)
        self.highlight_node(random_index)
    
    def start_sequential(self, instance):
        """Start sequential highlighting of all nodes"""
        if self.is_sequential_running:
            return
        
        self.is_sequential_running = True
        self.sequential_index = 0
        self._highlight_next_sequential()
    
    def _highlight_next_sequential(self):
        """Highlight next node in sequence"""
        if not self.is_sequential_running:
            return
        
        node_count = len(self.line_map.station_names)
        
        if self.sequential_index >= node_count:
            # Completed sequence
            self.is_sequential_running = False
            return
        
        # Highlight current node
        self.highlight_node(self.sequential_index)
        
        # Move to next
        self.sequential_index += 1
        
        # Schedule next highlight
        Clock.schedule_once(lambda dt: self._highlight_next_sequential(), 0.6)


if __name__ == '__main__':
    NodeHighlightApp().run()
