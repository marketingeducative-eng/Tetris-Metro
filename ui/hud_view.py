"""
HUDView - Candy-style game info display with rounded panels
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.animation import Animation


class CandyPanel(FloatLayout):
    """Rounded panel with candy-style background"""
    
    def __init__(self, pos, size, color=(0.15, 0.15, 0.25, 0.9), **kwargs):
        super().__init__(**kwargs)
        
        self.pos = pos
        self.size = size
        
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.3)
            self.shadow = RoundedRectangle(
                pos=(pos[0] + 2, pos[1] - 2),
                size=size,
                radius=[8]
            )
            
            # Main panel
            Color(*color)
            self.bg = RoundedRectangle(
                pos=pos,
                size=size,
                radius=[8]
            )
            
            # Highlight at top
            Color(1, 1, 1, 0.1)
            self.highlight = RoundedRectangle(
                pos=(pos[0] + 4, pos[1] + size[1] - 8),
                size=(size[0] - 8, 4),
                radius=[4]
            )


class CandyLabel(Label):
    """Label with candy-style text"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', '14sp')
        kwargs.setdefault('bold', False)
        kwargs.setdefault('color', (1, 1, 1, 1))
        super().__init__(**kwargs)
        
        # Add text shadow/outline effect via canvas
        with self.canvas.before:
            Color(0, 0, 0, 0.5)
            # Text shadow will be handled by padding


class ComboWidget(FloatLayout):
    """Animated combo badge"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.visible = False
        self.opacity = 0
        
        # Badge background
        with self.canvas.before:
            Color(1, 0.8, 0, 1)
            self.badge_bg = RoundedRectangle(
                pos=(Window.width // 2 - 60, Window.height // 2 + 100),
                size=(120, 40),
                radius=[20]
            )
            
            # Badge shadow
            Color(0, 0, 0, 0.4)
            self.badge_shadow = RoundedRectangle(
                pos=(Window.width // 2 - 58, Window.height // 2 + 98),
                size=(120, 40),
                radius=[20]
            )
        
        # Combo text
        self.label = Label(
            text='',
            pos=(Window.width // 2 - 60, Window.height // 2 + 100),
            size_hint=(None, None),
            size=(120, 40),
            font_size='18sp',
            bold=True,
            color=(0.2, 0.1, 0, 1)
        )
        self.add_widget(self.label)
    
    def show_combo(self, combo_count):
        """Show combo with bounce animation"""
        if combo_count < 2:
            return
        
        self.label.text = f'COMBO x{combo_count}!'
        self.visible = True
        
        # Bounce animation
        self.opacity = 0
        self.badge_bg.size = (80, 30)
        self.badge_shadow.size = (80, 30)
        
        # Scale up with bounce
        anim = Animation(opacity=1, duration=0.1)
        anim += Animation(opacity=1, duration=1.5)
        anim += Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=self._hide)
        anim.start(self)
        
        # Badge size animation
        size_anim = Animation(size=(140, 50), duration=0.15)
        size_anim += Animation(size=(120, 40), duration=0.1)
        size_anim.start(self.badge_bg)
        size_anim.start(self.badge_shadow)
    
    def _hide(self, *args):
        """Hide combo badge"""
        self.visible = False


class HUDView(FloatLayout):
    """Displays game information with candy style"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.labels = {}
        self.panels = []
        self.station_labels = []  # For mini-map
        self._create_panels()
        self._create_labels()
        self._create_minimap()
        
        # Combo widget
        self.combo_widget = ComboWidget()
        self.add_widget(self.combo_widget)
    
    def _create_panels(self):
        """Create candy-style panels"""
        # Top panel (score, level)
        top_panel = CandyPanel(
            pos=(5, Window.height - 160),
            size=(180, 150),
            color=(0.12, 0.12, 0.22, 0.95)
        )
        self.add_widget(top_panel)
        self.panels.append(top_panel)
        
        # ORDER TRACK panel (center top)
        order_track_panel = CandyPanel(
            pos=(Window.width // 2 - 150, Window.height - 120),
            size=(300, 110),
            color=(0.08, 0.15, 0.20, 0.95)
        )
        self.add_widget(order_track_panel)
        self.panels.append(order_track_panel)
        
        # Mini-map panel (right side)
        minimap_panel = CandyPanel(
            pos=(Window.width - 205, Window.height - 350),
            size=(200, 340),
            color=(0.10, 0.10, 0.18, 0.95)
        )
        self.add_widget(minimap_panel)
        self.panels.append(minimap_panel)
    
    def _create_labels(self):
        """Create all HUD labels"""
        label_config = {
            'score': {'text': 'Score: 0', 'pos': (15, Window.height - 45), 'font_size': '16sp', 'bold': True},
            'high_score': {'text': 'High: 0', 'pos': (15, Window.height - 70), 'font_size': '13sp'},
            'level': {'text': 'Level: 1', 'pos': (15, Window.height - 95), 'font_size': '14sp'},
            'streak': {'text': 'Streak: 0', 'pos': (15, Window.height - 120), 'font_size': '13sp', 'color': (1, 0.8, 0, 1)},
            
            # ORDER TRACK labels (center top)
            'line_name': {'text': 'Línia 1', 'pos': (Window.width // 2 - 140, Window.height - 35), 'font_size': '16sp', 'bold': True, 'color': (0.3, 0.8, 1, 1)},
            'next_station': {'text': 'Catalunya', 'pos': (Window.width // 2 - 140, Window.height - 65), 'font_size': '20sp', 'bold': True, 'color': (1, 1, 1, 1)},
            'progress': {'text': '0/27', 'pos': (Window.width // 2 - 140, Window.height - 90), 'font_size': '14sp', 'color': (0.8, 0.8, 0.8, 1)},
            
            # Mini-map header
            'minimap_header': {'text': 'Pròximes estacions', 'pos': (Window.width - 200, Window.height - 25), 'font_size': '13sp', 'bold': True, 'color': (0.8, 0.9, 1, 1)},
            
            'feedback': {'text': '', 'pos': (Window.width // 2 - 150, Window.height // 2 + 50), 'size': (300, 30), 'font_size': '22sp', 'color': (1, 1, 0, 1), 'bold': True}
        }
        
        for key, config in label_config.items():
            label = CandyLabel(
                text=config['text'],
                pos=config['pos'],
                size_hint=(None, None),
                size=config.get('size', (200, 25)),
                font_size=config.get('font_size', '14sp'),
                color=config.get('color', (1, 1, 1, 1)),
                bold=config.get('bold', False)
            )
            self.labels[key] = label
            self.add_widget(label)
    
    def _create_minimap(self):
        """Create mini-map station labels"""
        # Create 10 station label slots
        for i in range(10):
            y_pos = Window.height - 60 - (i * 28)
            label = CandyLabel(
                text='',
                pos=(Window.width - 195, y_pos),
                size_hint=(None, None),
                size=(180, 25),
                font_size='11sp',
                color=(0.7, 0.7, 0.7, 1)
            )
            self.station_labels.append(label)
            self.add_widget(label)
    
    def update(self, game_state):
        """
        Update HUD with game state
        
        Args:
            game_state: dict with ORDER TRACK progress and other data
        """
        self.labels['score'].text = f"Score: {game_state.get('score', 0)}"
        self.labels['high_score'].text = f"High: {game_state.get('high_score', 0)}"
        self.labels['level'].text = f"Level: {game_state.get('level', 1)}"
        
        # ORDER TRACK data
        order_track = game_state.get('order_track', {})
        
        self.labels['line_name'].text = order_track.get('line_name', '')
        self.labels['next_station'].text = order_track.get('next_station', '---')
        self.labels['progress'].text = order_track.get('progress', '0/0')
        self.labels['streak'].text = f"Ratxa: {order_track.get('streak', 0)}"
        
        # Update mini-map
        upcoming = order_track.get('upcoming_stations', [])
        for i, label in enumerate(self.station_labels):
            if i < len(upcoming):
                station = upcoming[i]
                name = station['name']
                
                # Truncate long names
                if len(name) > 18:
                    name = name[:15] + '...'
                
                # Mark unlocked stations
                if station['is_unlocked']:
                    label.text = f"✓ {name}"
                    label.color = (0.4, 1, 0.4, 1)
                elif station['is_next']:
                    label.text = f"→ {name}"
                    label.color = (1, 1, 0, 1)
                    label.bold = True
                else:
                    label.text = f"  {name}"
                    label.color = (0.7, 0.7, 0.7, 1)
                    label.bold = False
            else:
                label.text = ''
        
        # Show feedback if exists
        feedback = game_state.get('feedback', '')
        if feedback:
            self.labels['feedback'].text = feedback
            self.labels['feedback'].opacity = 1
        else:
            self.labels['feedback'].text = ''
            self.labels['feedback'].opacity = 0
    
    def show_feedback(self, message):
        """Show temporary feedback message with animation"""
        self.labels['feedback'].text = message
        self.labels['feedback'].opacity = 0
        
        # Fade in and scale
        anim = Animation(opacity=1, duration=0.15)
        anim.start(self.labels['feedback'])
    
    def hide_feedback(self):
        """Clear feedback"""
        self.labels['feedback'].text = ''
    
    def show_combo(self, combo_count):
        """Show combo badge"""
        self.combo_widget.show_combo(combo_count)
