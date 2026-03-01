"""
TTS Service Test
Test the Text-to-Speech service with metro station announcements
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from core.tts import TTSService, get_tts
from data.metro_loader import load_metro_network
from pathlib import Path


class TTSTestApp(App):
    """Test app for TTS service"""
    
    def build(self):
        """Build UI"""
        self.tts = get_tts()
        
        # Load metro data
        data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
        try:
            self.network = load_metro_network(str(data_path))
            self.l3 = self.network.get_line("L3")
            self.station_index = 0
        except Exception as e:
            print(f"Error loading metro data: {e}")
            self.l3 = None
        
        # Create UI
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='TTS Service Test\n(Text-to-Speech en Català)',
            font_size='24sp',
            size_hint_y=0.2
        )
        layout.add_widget(title)
        
        # Status label
        self.status_label = Label(
            text=f'TTS Status: {"✓ Available" if self.tts.is_available else "✗ Not Available"}\n'
                 f'Platform: {self.tts.tts.__class__.__name__ if self.tts.tts else "Mock"}',
            font_size='16sp',
            size_hint_y=0.15
        )
        layout.add_widget(self.status_label)
        
        # Current station label
        self.station_label = Label(
            text='Ready to test',
            font_size='20sp',
            size_hint_y=0.15
        )
        layout.add_widget(self.station_label)
        
        # Buttons
        button_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)
        
        # Test basic speech
        btn_hello = Button(
            text='Test: "Hola, benvingut al metro"',
            size_hint_y=None,
            height=60
        )
        btn_hello.bind(on_press=lambda x: self.test_basic())
        button_layout.add_widget(btn_hello)
        
        # Test station announcement
        btn_station = Button(
            text='Announce Next Station (L3)',
            size_hint_y=None,
            height=60,
            disabled=self.l3 is None
        )
        btn_station.bind(on_press=lambda x: self.announce_next_station())
        button_layout.add_widget(btn_station)
        
        # Test line announcement
        btn_line = Button(
            text='Announce Line L3',
            size_hint_y=None,
            height=60
        )
        btn_line.bind(on_press=lambda x: self.announce_line())
        button_layout.add_widget(btn_line)
        
        # Test sequence
        btn_sequence = Button(
            text='Announce Station + Line',
            size_hint_y=None,
            height=60,
            disabled=self.l3 is None
        )
        btn_sequence.bind(on_press=lambda x: self.announce_sequence())
        button_layout.add_widget(btn_sequence)
        
        # Stop button
        btn_stop = Button(
            text='Stop Speech',
            size_hint_y=None,
            height=60,
            background_color=(1, 0.3, 0.3, 1)
        )
        btn_stop.bind(on_press=lambda x: self.stop_speech())
        button_layout.add_widget(btn_stop)
        
        layout.add_widget(button_layout)
        
        return layout
    
    def test_basic(self):
        """Test basic speech"""
        self.status_label.text = '🗣️ Speaking...'
        success = self.tts.speak("Hola, benvingut al metro de Barcelona")
        if not success:
            self.status_label.text = '❌ Speech failed (check logs)'
    
    def announce_next_station(self):
        """Announce next station on L3"""
        if not self.l3 or self.station_index >= len(self.l3.stations):
            self.station_index = 0
        
        station = self.l3.stations[self.station_index]
        self.station_label.text = f'Station {self.station_index + 1}: {station}'
        self.tts.announce_station(station)
        
        self.station_index += 1
        if self.station_index >= len(self.l3.stations):
            self.station_index = 0
    
    def announce_line(self):
        """Announce line"""
        if self.l3:
            self.tts.announce_line(self.l3.name)
            self.station_label.text = f'Announcing: {self.l3.name}'
    
    def announce_sequence(self):
        """Announce station and line"""
        if not self.l3:
            return
        
        station = self.l3.stations[self.station_index]
        self.tts.announce_sequence(station, self.l3.name)
        self.station_label.text = f'{station} - {self.l3.name}'
        
        self.station_index += 1
        if self.station_index >= len(self.l3.stations):
            self.station_index = 0
    
    def stop_speech(self):
        """Stop current speech"""
        self.tts.stop()
        self.status_label.text = '⏹️ Speech stopped'
    
    def on_stop(self):
        """Cleanup on app close"""
        self.tts.shutdown()


if __name__ == '__main__':
    TTSTestApp().run()
