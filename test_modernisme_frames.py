"""
Test Modernisme 2.0 Frame Styles
=================================

Visual test to demonstrate the new unified frame system applied to all UI panels.

Features:
- RoundedRectangle base
- Thin inner stroke (wrought iron accent)
- Subtle corner ornaments
- Optional faint mosaic pattern fill

Press numbers 1-4 to see different frame styles.
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.theme_modernisme import draw_modernisme_frame


class ModernismeFrameTestApp(App):
    """Test app for visualizing Modernisme 2.0 frames"""
    
    def build(self):
        root = FloatLayout()
        
        # Dark background
        with root.canvas.before:
            Color(0.02, 0.03, 0.05, 1)
            Rectangle(pos=root.pos, size=root.size)
        
        def update_bg(*args):
            root.canvas.before.clear()
            with root.canvas.before:
                Color(0.02, 0.03, 0.05, 1)
                Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=update_bg, size=update_bg)
        
        # Title
        title = Label(
            text='Modernisme 2.0 Frame Style Test',
            font_size='32sp',
            bold=True,
            size_hint=(1, None),
            height=60,
            pos_hint={'center_x': 0.5, 'top': 0.98},
            color=(0.95, 0.96, 0.98, 1)
        )
        root.add_widget(title)
        
        # Instructions
        instructions = Label(
            text='Panel styles showcase Barcelona wrought iron-inspired accents',
            font_size='16sp',
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'top': 0.90},
            color=(0.75, 0.80, 0.85, 1)
        )
        root.add_widget(instructions)
        
        # Sample panels
        panels_config = [
            {
                'title': 'HUD Panel',
                'subtitle': 'Standard frame, no pattern',
                'pos_hint': {'x': 0.05, 'top': 0.78},
                'size': (350, 200),
                'radius': 12,
                'pattern': False,
                'civic_mode': False,
                'accent': None
            },
            {
                'title': 'Tutorial Overlay',
                'subtitle': 'Larger radius, clean style',
                'pos_hint': {'right': 0.95, 'top': 0.78},
                'size': (350, 200),
                'radius': 20,
                'pattern': False,
                'civic_mode': False,
                'accent': None
            },
            {
                'title': 'Journey Panel',
                'subtitle': 'With mosaic pattern fill',
                'pos_hint': {'x': 0.05, 'top': 0.48},
                'size': (350, 200),
                'radius': 20,
                'pattern': True,
                'civic_mode': False,
                'accent': None
            },
            {
                'title': 'Goal Achievement',
                'subtitle': 'Gold accent stroke',
                'pos_hint': {'right': 0.95, 'top': 0.48},
                'size': (350, 200),
                'radius': 18,
                'pattern': False,
                'civic_mode': False,
                'accent': (1.0, 0.85, 0.2, 0.6)
            },
            {
                'title': 'Civic Mode Panel',
                'subtitle': 'Subdued colors, calmer',
                'pos_hint': {'x': 0.05, 'top': 0.18},
                'size': (350, 200),
                'radius': 16,
                'pattern': False,
                'civic_mode': True,
                'accent': None
            },
            {
                'title': 'Civic + Pattern',
                'subtitle': 'Subtle mosaic overlay',
                'pos_hint': {'right': 0.95, 'top': 0.18},
                'size': (350, 200),
                'radius': 16,
                'pattern': True,
                'civic_mode': True,
                'accent': None
            },
        ]
        
        for config in panels_config:
            panel = Widget(
                size_hint=(None, None),
                size=config['size'],
                pos_hint=config['pos_hint']
            )
            
            with panel.canvas.before:
                draw_modernisme_frame(
                    panel.canvas.before,
                    pos=panel.pos,
                    size=panel.size,
                    radius=config['radius'],
                    accent_color=config['accent'],
                    pattern=config['pattern'],
                    civic_mode=config['civic_mode']
                )
            
            def update_panel_bg(widget, *args):
                widget.canvas.before.clear()
                with widget.canvas.before:
                    c = None
                    for conf in panels_config:
                        if conf['title'] == widget.title_text:
                            c = conf
                            break
                    if c:
                        draw_modernisme_frame(
                            widget.canvas.before,
                            pos=widget.pos,
                            size=widget.size,
                            radius=c['radius'],
                            accent_color=c['accent'],
                            pattern=c['pattern'],
                            civic_mode=c['civic_mode']
                        )
            
            panel.title_text = config['title']
            panel.bind(pos=update_panel_bg, size=update_panel_bg)
            
            # Title label
            title_label = Label(
                text=config['title'],
                font_size='20sp',
                bold=True,
                size_hint=(1, None),
                height=40,
                pos_hint={'center_x': 0.5, 'top': 0.95},
                color=(0.95, 0.96, 0.98, 1)
            )
            panel.add_widget(title_label)
            
            # Subtitle
            subtitle_label = Label(
                text=config['subtitle'],
                font_size='14sp',
                size_hint=(1, None),
                height=30,
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                color=(0.75, 0.80, 0.85, 1)
            )
            panel.add_widget(subtitle_label)
            
            # Details
            details_text = []
            if config['pattern']:
                details_text.append('- Mosaic pattern')
            if config['civic_mode']:
                details_text.append('- Civic mode')
            if config['accent']:
                details_text.append('- Custom accent')
            details_text.append(f"- Radius: {config['radius']}px")
            
            details_label = Label(
                text='\n'.join(details_text),
                font_size='12sp',
                size_hint=(1, None),
                height=80,
                pos_hint={'center_x': 0.5, 'y': 0.05},
                color=(0.5, 0.55, 0.62, 1),
                halign='center'
            )
            panel.add_widget(details_label)
            
            root.add_widget(panel)
        
        # Legend
        legend = Label(
            text='Design inspired by Barcelona modernisme architecture - Wrought iron accents - Subtle ornamentation',
            font_size='13sp',
            italic=True,
            size_hint=(1, None),
            height=25,
            pos_hint={'center_x': 0.5, 'y': 0.01},
            color=(0.4, 0.45, 0.5, 1)
        )
        root.add_widget(legend)
        
        return root


if __name__ == '__main__':
    print("="*70)
    print("MODERNISME 2.0 FRAME STYLE TEST")
    print("="*70)
    print("\nThis test showcases the unified frame system:")
    print("  - RoundedRectangle base with theme background color")
    print("  - Thin inner stroke (wrought iron-inspired)")
    print("  - Subtle corner ornaments (Gaudi influence)")
    print("  - Optional faint mosaic pattern fill (5-8% opacity)")
    print("  - Civic mode variants with subdued colors")
    print("\n" + "="*70 + "\n")
    
    ModernismeFrameTestApp().run()
