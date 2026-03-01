"""
LineMapView Test - Minimal example showing schematic metro line
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from line_map_view import LineMapView
from data.metro_loader import load_metro_network
from pathlib import Path


class LineMapTestApp(App):
    """Test app for LineMapView"""
    
    def build(self):
        """Build UI"""
        # Load metro data
        data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
        network = load_metro_network(str(data_path))
        self.l3 = network.get_line("L3")
        
        # Main layout (portrait)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text=f'{self.l3.name}\n{self.l3.endpoints["from"]} ↔ {self.l3.endpoints["to"]}',
            size_hint_y=0.15,
            font_size='20sp'
        )
        main_layout.add_widget(title)
        
        # Line map view (takes most of the space)
        self.line_map = LineMapView(size_hint_y=0.7)
        
        # Set L3 data (using first 12 stations for cleaner display)
        l3_stations_subset = self.l3.stations[:12]
        self.line_map.set_line(
            line_id=self.l3.id,
            line_color_hex=self.l3.color,
            station_names=l3_stations_subset
        )
        
        # Set active index to 0
        self.line_map.set_next_index(0)
        
        main_layout.add_widget(self.line_map)
        
        # Station info label
        self.station_label = Label(
            text=f'Next: {l3_stations_subset[0]}',
            size_hint_y=0.08,
            font_size='18sp'
        )
        main_layout.add_widget(self.station_label)
        
        # Control buttons
        button_layout = BoxLayout(size_hint_y=0.07, spacing=5)
        
        btn_prev = Button(text='◀ Previous')
        btn_prev.bind(on_press=self.prev_station)
        button_layout.add_widget(btn_prev)
        
        btn_next = Button(text='Next ▶')
        btn_next.bind(on_press=self.next_station)
        button_layout.add_widget(btn_next)
        
        main_layout.add_widget(button_layout)
        
        return main_layout
    
    def next_station(self, instance):
        """Move to next station"""
        current = self.line_map.next_index
        if current < self.line_map.num_slots - 1:
            new_index = current + 1
            self.line_map.set_next_index(new_index)
            self.station_label.text = f'Next: {self.line_map.station_names[new_index]}'
    
    def prev_station(self, instance):
        """Move to previous station"""
        current = self.line_map.next_index
        if current > 0:
            new_index = current - 1
            self.line_map.set_next_index(new_index)
            self.station_label.text = f'Next: {self.line_map.station_names[new_index]}'


if __name__ == '__main__':
    LineMapTestApp().run()
