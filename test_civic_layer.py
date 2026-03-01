"""
Test civic institutional layer integration.

Tests:
1. Civic footer is visible
2. Civic splash overlay displays correctly
3. "Descobreix Barcelona" info overlay works
4. Civic tone is elegant, welcoming, non-political

Run: python test_civic_layer.py
"""

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

# Import the game to test civic methods
from game_propera_parada import ProximaParadaGame


class CivicLayerTestApp(App):
    """Test application for civic institutional layer"""
    
    def build(self):
        root = FloatLayout()
        
        # Test panel
        test_panel = BoxLayout(
            orientation='vertical',
            spacing=15,
            padding=20,
            size_hint=(0.5, None),
            height=250,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Title
        title = Label(
            text="🏛️ Civic Layer Test",
            font_size='28sp',
            bold=True,
            size_hint=(1, None),
            height=40,
            color=(0.3, 0.85, 0.5, 1)
        )
        test_panel.add_widget(title)
        
        # Info
        info = Label(
            text="Test the Barcelona civic institutional layer",
            font_size='16sp',
            size_hint=(1, None),
            height=30,
            color=(0.7, 0.75, 0.8, 1)
        )
        test_panel.add_widget(info)
        
        # Button: Show Civic Splash
        btn_splash = Button(
            text="Show Civic Splash",
            size_hint=(1, None),
            height=48,
            background_normal="",
            background_color=(0.28, 0.72, 0.48, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        btn_splash.bind(on_release=self._show_civic_splash)
        test_panel.add_widget(btn_splash)
        
        # Button: Show Descobreix Info
        btn_descobreix = Button(
            text="Show Descobreix Barcelona",
            size_hint=(1, None),
            height=48,
            background_normal="",
            background_color=(0.28, 0.72, 0.48, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        btn_descobreix.bind(on_release=self._show_descobreix)
        test_panel.add_widget(btn_descobreix)
        
        # Button: Test Footer Visibility
        btn_footer = Button(
            text="Check Civic Footer",
            size_hint=(1, None),
            height=48,
            background_normal="",
            background_color=(0.35, 0.55, 0.75, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        btn_footer.bind(on_release=self._check_footer)
        test_panel.add_widget(btn_footer)
        
        root.add_widget(test_panel)
        
        # Create a minimal game widget to test civic methods
        # Note: We create it hidden to access the civic methods
        self.game_widget = None
        Clock.schedule_once(self._create_game_widget, 0.5)
        
        return root
    
    def _create_game_widget(self, dt):
        """Create game widget for testing civic methods"""
        try:
            from core.app_context import AppContext
            
            app_context = AppContext()
            app_context.load_all()
            
            self.game_widget = ProximaParadaGame(
                practice_mode=False,
                direction_mode=False,
                first_day_mode=False,
                random_seed=None,
                line_id="L1",
                metro_network=app_context.metro_network,
                progress_manager=app_context.progress_manager,
                mode=app_context.mode_instance,
                goal_mode=False,
                goal_station_id=None,
                enable_settings_hotkey=False
            )
            
            # Add game widget (hidden)
            self.game_widget.opacity = 0
            self.game_widget.size_hint = (0.01, 0.01)
            self.root.add_widget(self.game_widget)
            
            print("[Test] Game widget created - civic methods available")
            
        except Exception as e:
            print(f"[Test] Error creating game widget: {e}")
    
    def _show_civic_splash(self, instance):
        """Test civic splash overlay"""
        if not self.game_widget:
            print("[Test] Game widget not ready yet")
            return
        
        if hasattr(self.game_widget, 'show_civic_splash'):
            self.game_widget.show_civic_splash()
            print("[Test] ✅ Civic splash displayed")
        else:
            print("[Test] ❌ show_civic_splash method not found")
    
    def _show_descobreix(self, instance):
        """Test Descobreix Barcelona info overlay"""
        if not self.game_widget:
            print("[Test] Game widget not ready yet")
            return
        
        if hasattr(self.game_widget, 'show_descobreix_barcelona'):
            self.game_widget.show_descobreix_barcelona()
            print("[Test] ✅ Descobreix Barcelona info displayed")
        else:
            print("[Test] ❌ show_descobreix_barcelona method not found")
    
    def _check_footer(self, instance):
        """Check if civic footer is present"""
        if not self.game_widget:
            print("[Test] Game widget not ready yet")
            return
        
        if hasattr(self.game_widget, 'civic_footer'):
            footer = self.game_widget.civic_footer
            print("[Test] ✅ Civic footer found:")
            print(f"  Text: {footer.text}")
            print(f"  Font size: {footer.font_size}")
            print(f"  Color: {footer.color}")
            print(f"  Italic: {footer.italic}")
        else:
            print("[Test] ❌ Civic footer not found")


if __name__ == '__main__':
    CivicLayerTestApp().run()

