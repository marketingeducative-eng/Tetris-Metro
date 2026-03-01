"""
Station Description Demo
Shows station names with their contextual descriptions below
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from data.metro_loader import load_metro_network
from pathlib import Path


class StationDescriptionApp(App):
    """Demo showing station descriptions"""
    
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
            text='📍 Station Descriptions Demo',
            size_hint=(1, None),
            height=60,
            pos_hint={'x': 0, 'top': 1},
            font_size='24sp',
            bold=True,
            color=(0.3, 0.9, 0.5, 1)
        )
        root.add_widget(title)
        
        # Instruction
        instruction = Label(
            text='Press button to cycle through stations',
            size_hint=(1, None),
            height=35,
            pos_hint={'x': 0, 'top': 0.92},
            font_size='14sp',
            color=(0.7, 0.8, 1, 1)
        )
        root.add_widget(instruction)
        
        # Station name (simulating "Pròxima parada:")
        self.station_label = Label(
            text="",
            font_size='26sp',
            bold=True,
            size_hint=(1, None),
            height=50,
            pos_hint={'top': 0.85},
            color=(1, 1, 1, 1)
        )
        root.add_widget(self.station_label)
        
        # Station description (contextual info below)
        self.description_label = Label(
            text="",
            font_size='15sp',
            size_hint=(1, None),
            height=30,
            pos_hint={'top': 0.815},
            color=(0.7, 0.8, 0.9, 1),
            italic=True
        )
        root.add_widget(self.description_label)
        
        # Station info panel
        self.info_label = Label(
            text="",
            font_size='16sp',
            size_hint=(0.8, None),
            height=200,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            color=(0.8, 0.9, 1, 1),
            halign='center',
            valign='middle'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        root.add_widget(self.info_label)
        
        # Control buttons
        button_layout = FloatLayout(
            size_hint=(0.8, None),
            height=60,
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        
        # Previous button
        prev_btn = Button(
            text='◀ Previous',
            size_hint=(0.3, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        prev_btn.bind(on_press=self.show_previous)
        button_layout.add_widget(prev_btn)
        
        # Next button
        next_btn = Button(
            text='Next ▶',
            size_hint=(0.3, 1),
            pos_hint={'right': 1, 'y': 0}
        )
        next_btn.bind(on_press=self.show_next)
        button_layout.add_widget(next_btn)
        
        # Random button
        random_btn = Button(
            text='🎲 Random',
            size_hint=(0.3, 1),
            pos_hint={'center_x': 0.5, 'y': 0}
        )
        random_btn.bind(on_press=self.show_random)
        button_layout.add_widget(random_btn)
        
        root.add_widget(button_layout)
        
        # State
        self.current_index = 0
        self.show_station(self.current_index)
        
        # Auto-cycle through stations
        Clock.schedule_interval(lambda dt: self.show_next(None), 3.0)
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def show_station(self, index):
        """Display station at given index"""
        if 0 <= index < len(self.l3.stations):
            station = self.l3.get_station(index)
            if station:
                # Update main display (simulating game display)
                self.station_label.text = f"Pròxima parada: {station.name}"
                self.description_label.text = station.description
                
                # Update info panel
                self.info_label.text = (
                    f"Station {index + 1} of {len(self.l3.stations)}\\n\\n"
                    f"{station.name}\\n\\n"
                    f"📍 {station.description}\\n\\n"
                    f"Description length: {len(station.description)} chars"
                )
                
                self.current_index = index
    
    def show_next(self, instance):
        """Show next station"""
        next_index = (self.current_index + 1) % len(self.l3.stations)
        self.show_station(next_index)
    
    def show_previous(self, instance):
        """Show previous station"""
        prev_index = (self.current_index - 1) % len(self.l3.stations)
        self.show_station(prev_index)
    
    def show_random(self, instance):
        """Show random station"""
        import random
        random_index = random.randint(0, len(self.l3.stations) - 1)
        self.show_station(random_index)


if __name__ == '__main__':
    StationDescriptionApp().run()
