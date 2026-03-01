"""
Simple Station Token Demo - Just shows 3 draggable tokens
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from token_drop_area import TokenDropArea


class SimpleTokenApp(App):
    """Simple demo of draggable tokens"""
    
    def build(self):
        """Build UI"""
        root = FloatLayout()
        
        # Background
        with root.canvas.before:
            Color(0.15, 0.15, 0.2, 1)
            self.bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)
        
        # Title
        title = Label(
            text='Drag the Station Tokens!',
            size_hint=(1, None),
            height=60,
            pos_hint={'x': 0, 'top': 1},
            font_size='24sp'
        )
        root.add_widget(title)
        
        # Status label
        self.status = Label(
            text='Drag tokens anywhere',
            size_hint=(1, None),
            height=40,
            pos_hint={'x': 0, 'top': 0.9},
            font_size='16sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        root.add_widget(self.status)
        
        # Token area
        self.token_area = TokenDropArea(
            size_hint=(0.9, None),
            height=80,
            pos_hint={'center_x': 0.5, 'y': 0.1}
        )
        
        # Create some example tokens
        tokens = [
            {'id': '1', 'name': 'Liceu', 'color': '#00923F'},
            {'id': '2', 'name': 'Catalunya', 'color': '#00923F'},
            {'id': '3', 'name': 'Passeig de Gràcia', 'color': '#00923F'},
            {'id': '4', 'name': 'Diagonal', 'color': '#00923F'},
            {'id': '5', 'name': 'Fontana', 'color': '#00923F'},
        ]
        
        self.token_area.set_token_queue(tokens)
        self.token_area.set_on_token_dropped_callback(self._on_drop)
        
        root.add_widget(self.token_area)
        
        return root
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg.pos = instance.pos
        self.bg.size = instance.size
    
    def _on_drop(self, token, x, y):
        """Handle token drop"""
        self.status.text = f'Dropped {token.name_ca} at ({int(x)}, {int(y)})'
        # Accept the token (remove it)
        return True


if __name__ == '__main__':
    SimpleTokenApp().run()
