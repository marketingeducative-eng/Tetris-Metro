"""
Test Audio Service
Verify that the station announcement chime plays correctly
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from core.audio import AudioService


class AudioTestApp(App):
    """Simple app to test audio service"""
    
    def build(self):
        """Build UI"""
        root = FloatLayout()
        
        # Background
        with root.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text='🔊 Audio Service Test',
            size_hint=(1, None),
            height=70,
            pos_hint={'x': 0, 'top': 1},
            font_size='28sp',
            bold=True,
            color=(0.3, 0.9, 0.5, 1)
        )
        root.add_widget(title)
        
        # Info label
        self.info_label = Label(
            text='Click button to test station announcement chime',
            size_hint=(1, None),
            height=50,
            pos_hint={'x': 0, 'center_y': 0.6},
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        root.add_widget(self.info_label)
        
        # Status label
        self.status_label = Label(
            text='',
            size_hint=(1, None),
            height=40,
            pos_hint={'x': 0, 'center_y': 0.5},
            font_size='14sp',
            color=(0.7, 1, 0.7, 1)
        )
        root.add_widget(self.status_label)
        
        # Play button
        play_btn = Button(
            text='▶ Play Station Chime',
            size_hint=(None, None),
            size=(300, 60),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            font_size='18sp'
        )
        play_btn.bind(on_press=self.play_chime)
        root.add_widget(play_btn)
        
        # Rapid test button
        rapid_btn = Button(
            text='🔁 Rapid Test (5 chimes)',
            size_hint=(None, None),
            size=(300, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            font_size='16sp'
        )
        rapid_btn.bind(on_press=self.rapid_test)
        root.add_widget(rapid_btn)
        
        # Volume controls
        vol_down_btn = Button(
            text='🔉 Volume Down',
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.35, 'center_y': 0.15},
            font_size='14sp'
        )
        vol_down_btn.bind(on_press=lambda x: self.adjust_volume(-0.1))
        root.add_widget(vol_down_btn)
        
        vol_up_btn = Button(
            text='🔊 Volume Up',
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.65, 'center_y': 0.15},
            font_size='14sp'
        )
        vol_up_btn.bind(on_press=lambda x: self.adjust_volume(0.1))
        root.add_widget(vol_up_btn)
        
        # Initialize audio service
        self.audio = AudioService()
        self.volume = 0.4
        self.play_count = 0
        
        # Check if audio is available
        if self.audio.sounds.get('station_chime'):
            self.info_label.text = '✅ Audio service ready - Click to test'
        else:
            self.info_label.text = '⚠️ Audio service failed to initialize'
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def play_chime(self, instance):
        """Play the station chime"""
        self.audio.play_station_announcement()
        self.play_count += 1
        self.status_label.text = f'🔔 Chime played! (Total: {self.play_count})'
    
    def rapid_test(self, instance):
        """Play 5 chimes in sequence"""
        self.status_label.text = '🔔 Rapid test: Playing 5 chimes...'
        
        for i in range(5):
            Clock.schedule_once(lambda dt, idx=i: self._play_with_feedback(idx), i * 0.5)
    
    def _play_with_feedback(self, index):
        """Play chime with feedback"""
        self.audio.play_station_announcement()
        self.play_count += 1
        self.status_label.text = f'🔔 Chime {index + 1}/5 (Total: {self.play_count})'
    
    def adjust_volume(self, delta):
        """Adjust volume"""
        self.volume = max(0.0, min(1.0, self.volume + delta))
        self.audio.set_volume(self.volume)
        self.status_label.text = f'🔊 Volume: {int(self.volume * 100)}%'


if __name__ == '__main__':
    AudioTestApp().run()
