"""
Overlays - Pause and Game Over screens
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle


class PauseOverlay(FloatLayout):
    """Pause screen overlay"""
    
    def __init__(self, on_resume=None, **kwargs):
        super().__init__(**kwargs)
        
        self.on_resume = on_resume
        self.visible = False
        
        # Semi-transparent background
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.bg = Rectangle(pos=self.pos, size=Window.size)
        
        # Title
        self.title = Label(
            text='PAUSA',
            pos=(Window.width // 2 - 100, Window.height // 2 + 50),
            size_hint=(None, None),
            size=(200, 50),
            font_size='32sp',
            bold=True
        )
        self.add_widget(self.title)
        
        # Resume button
        self.resume_btn = Button(
            text='Continuar',
            pos=(Window.width // 2 - 75, Window.height // 2 - 25),
            size_hint=(None, None),
            size=(150, 50),
            font_size='18sp'
        )
        self.resume_btn.bind(on_press=self._on_resume_press)
        self.add_widget(self.resume_btn)
        
        self.hide()
    
    def show(self):
        """Show overlay"""
        self.visible = True
        self.opacity = 1
    
    def hide(self):
        """Hide overlay"""
        self.visible = False
        self.opacity = 0
    
    def _on_resume_press(self, instance):
        """Handle resume button"""
        if self.on_resume:
            self.on_resume()


class GameOverOverlay(FloatLayout):
    """Game over screen"""
    
    def __init__(self, on_retry=None, on_exit=None, **kwargs):
        super().__init__(**kwargs)
        
        self.on_retry = on_retry
        self.on_exit = on_exit
        self.visible = False
        
        # Background
        with self.canvas.before:
            Color(0, 0, 0, 0.8)
            self.bg = Rectangle(pos=self.pos, size=Window.size)
        
        # Title
        self.title = Label(
            text='GAME OVER',
            pos=(Window.width // 2 - 150, Window.height // 2 + 80),
            size_hint=(None, None),
            size=(300, 50),
            font_size='36sp',
            bold=True,
            color=(1, 0.3, 0.3, 1)
        )
        self.add_widget(self.title)
        
        # Score display
        self.score_label = Label(
            text='Score: 0',
            pos=(Window.width // 2 - 100, Window.height // 2 + 20),
            size_hint=(None, None),
            size=(200, 40),
            font_size='24sp'
        )
        self.add_widget(self.score_label)
        
        # New record badge
        self.record_label = Label(
            text='NUEVO RÉCORD!',
            pos=(Window.width // 2 - 100, Window.height // 2 - 20),
            size_hint=(None, None),
            size=(200, 30),
            font_size='18sp',
            color=(1, 1, 0, 1),
            bold=True
        )
        self.add_widget(self.record_label)
        self.record_label.opacity = 0
        
        # Retry button
        self.retry_btn = Button(
            text='Reintentar',
            pos=(Window.width // 2 - 160, Window.height // 2 - 80),
            size_hint=(None, None),
            size=(150, 50),
            font_size='18sp'
        )
        self.retry_btn.bind(on_press=self._on_retry_press)
        self.add_widget(self.retry_btn)
        
        # Exit button
        self.exit_btn = Button(
            text='Salir',
            pos=(Window.width // 2 + 10, Window.height // 2 - 80),
            size_hint=(None, None),
            size=(150, 50),
            font_size='18sp'
        )
        self.exit_btn.bind(on_press=self._on_exit_press)
        self.add_widget(self.exit_btn)
        
        self.hide()
    
    def show(self, score, is_new_record=False):
        """Show game over with score"""
        self.visible = True
        self.opacity = 1
        
        self.score_label.text = f'Score: {score}'
        self.record_label.opacity = 1 if is_new_record else 0
    
    def hide(self):
        """Hide overlay"""
        self.visible = False
        self.opacity = 0
    
    def _on_retry_press(self, instance):
        """Handle retry"""
        if self.on_retry:
            self.on_retry()
    
    def _on_exit_press(self, instance):
        """Handle exit"""
        if self.on_exit:
            self.on_exit()


class DirectionMissionOverlay(FloatLayout):
    """Overlay for direction selection mini-challenge"""
    
    def __init__(self, on_answer=None, **kwargs):
        super().__init__(**kwargs)
        
        self.on_answer = on_answer
        self.visible = False
        
        # Semi-transparent background
        with self.canvas.before:
            Color(0, 0, 0, 0.6)
            self.bg = Rectangle(pos=self.pos, size=Window.size)
        
        # Mission panel
        from kivy.graphics import RoundedRectangle
        with self.canvas:
            Color(0.1, 0.15, 0.25, 0.98)
            self.panel_bg = RoundedRectangle(
                pos=(Window.width // 2 - 200, Window.height // 2 - 100),
                size=(400, 220),
                radius=[15]
            )
        
        # Title
        self.title = Label(
            text='MISSIÓ DE DIRECCIÓ',
            pos=(Window.width // 2 - 180, Window.height // 2 + 80),
            size_hint=(None, None),
            size=(360, 30),
            font_size='20sp',
            bold=True,
            color=(0.3, 0.8, 1, 1)
        )
        self.add_widget(self.title)
        
        # Question text
        self.question = Label(
            text='',
            pos=(Window.width // 2 - 180, Window.height // 2 + 20),
            size_hint=(None, None),
            size=(360, 60),
            font_size='16sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        self.question.bind(size=self.question.setter('text_size'))
        self.add_widget(self.question)
        
        # Option A button
        self.btn_a = Button(
            text='A. Direcció X',
            pos=(Window.width // 2 - 180, Window.height // 2 - 40),
            size_hint=(None, None),
            size=(360, 40),
            font_size='16sp',
            background_color=(0.2, 0.6, 0.9, 1)
        )
        self.btn_a.bind(on_press=lambda x: self._on_answer(0))
        self.add_widget(self.btn_a)
        
        # Option B button
        self.btn_b = Button(
            text='B. Direcció Y',
            pos=(Window.width // 2 - 180, Window.height // 2 - 90),
            size_hint=(None, None),
            size=(360, 40),
            font_size='16sp',
            background_color=(0.2, 0.6, 0.9, 1)
        )
        self.btn_b.bind(on_press=lambda x: self._on_answer(1))
        self.add_widget(self.btn_b)
        
        self.hide()
    
    def show(self, mission_data):
        """
        Show mission overlay
        
        Args:
            mission_data: dict with 'text' and 'options' list
        """
        self.visible = True
        self.opacity = 1
        
        self.question.text = mission_data.get('text', '')
        options = mission_data.get('options', ['A', 'B'])
        
        self.btn_a.text = f"A. {options[0]}" if len(options) > 0 else "A."
        self.btn_b.text = f"B. {options[1]}" if len(options) > 1 else "B."
    
    def hide(self):
        """Hide overlay"""
        self.visible = False
        self.opacity = 0
    
    def _on_answer(self, option_index):
        """Handle answer selection"""
        if self.on_answer:
            self.on_answer(option_index)
        self.hide()


class StationUnlockOverlay(FloatLayout):
    """Overlay showing unlocked station notification"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.visible = False
        
        # Background panel
        from kivy.graphics import RoundedRectangle
        with self.canvas:
            Color(0.1, 0.3, 0.2, 0.95)
            self.panel_bg = RoundedRectangle(
                pos=(Window.width // 2 - 180, Window.height // 2 - 60),
                size=(360, 120),
                radius=[12]
            )
        
        # "Unlocked!" text
        self.title = Label(
            text='ESTACIÓ DESBLOQUEJADA!',
            pos=(Window.width // 2 - 170, Window.height // 2 + 20),
            size_hint=(None, None),
            size=(340, 30),
            font_size='18sp',
            bold=True,
            color=(0.4, 1, 0.4, 1)
        )
        self.add_widget(self.title)
        
        # Station name
        self.station_name = Label(
            text='Catalunya',
            pos=(Window.width // 2 - 170, Window.height // 2 - 10),
            size_hint=(None, None),
            size=(340, 40),
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.station_name)
        
        # Lines
        self.lines_label = Label(
            text='L1, L3',
            pos=(Window.width // 2 - 170, Window.height // 2 - 45),
            size_hint=(None, None),
            size=(340, 20),
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.lines_label)
        
        self.hide()
    
    def show(self, station_name, lines):
        """
        Show unlock notification
        
        Args:
            station_name: Name of unlocked station
            lines: List of metro lines
        """
        self.visible = True
        self.opacity = 1
        
        self.station_name.text = station_name
        self.lines_label.text = ', '.join(lines) if lines else ''
        
        # Auto-hide after 2 seconds
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.hide(), 2.0)
    
    def hide(self):
        """Hide overlay"""
        self.visible = False
        self.opacity = 0
