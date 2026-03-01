"""
Screen flow for Proxima Parada.
"""
from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from pathlib import Path
from datetime import date
import hashlib
import random

from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from data.metro_loader import load_metro_network, normalize_station_id
from core.settings import SettingsManager
from core.audio import AudioEvent
from core.progress import ProgressManager
from core.app_context import AppContext
from core.badges import BADGE_DEFINITIONS
from ui.routes import SCREEN_COVER, SCREEN_LINES, SCREEN_GAME


def cp(msg):
    print(f"✅ CP: {msg}", flush=True)


def _daily_seed_from_date(date_str):
    digest = hashlib.sha256(date_str.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def get_daily_challenge(metro_network, date_str=None):
    if not metro_network or not metro_network.lines:
        return None

    date_str = date_str or date.today().isoformat()
    rng = random.Random(_daily_seed_from_date(date_str))

    eligible_lines = []
    for line in metro_network.lines:
        eligible_stations = [
            station for station in line.stations
            if station.tourist_highlight and station.tourist_priority >= 4
        ]
        if eligible_stations:
            eligible_lines.append((line, eligible_stations))

    fallback_used = False
    if eligible_lines:
        line, stations = rng.choice(eligible_lines)
    else:
        fallback_used = True
        line = rng.choice(metro_network.lines)
        stations = list(line.stations)

    if not stations:
        return None

    station = rng.choice(stations)

    return {
        "date": date_str,
        "line_id": line.id,
        "line_name": line.name,
        "line_color": line.color,
        "station_id": normalize_station_id(station.name),
        "station_name": station.name,
        "fallback": fallback_used,
    }


class GradientOverlay(Widget):
    """Simple stepped gradient overlay for readability."""

    def __init__(self, steps=12, **kwargs):
        super().__init__(**kwargs)
        self.steps = max(2, steps)
        self._rects = []
        with self.canvas:
            for i in range(self.steps):
                alpha = 0.05 + (i / (self.steps - 1)) * 0.55
                Color(0, 0, 0, alpha)
                rect = Rectangle(pos=self.pos, size=self.size)
                self._rects.append(rect)
        self.bind(pos=self._update_rects, size=self._update_rects)
        self._update_rects()

    def _update_rects(self, *args):
        if not self._rects:
            return
        step_height = self.height / float(self.steps)
        for i, rect in enumerate(self._rects):
            rect.pos = (self.x, self.y + i * step_height)
            rect.size = (self.width, step_height + 1)


class NarrativeOnboardingOverlay(FloatLayout):
    """
    Immersive narrative onboarding sequence.
    
    Cinematic 'arrival in Barcelona' experience with:
    - Sequential narrative text (Catalan) with fade effects
    - Optional English explanatory support
    - Ambient audio integration
    - Seamless transition into First Day Mode
    """

    def __init__(self, on_complete_callback, app_context=None, **kwargs):
        super().__init__(**kwargs)
        self.on_complete = on_complete_callback
        self.app_context = app_context
        self.settings_manager = SettingsManager()
        self.audio = None  # Will load if app_context has AudioService
        self._city_ambience_layers = []
        
        # Try to get audio service from app_context
        if app_context and hasattr(app_context, 'audio'):
            self.audio = app_context.audio
        
        self.current_phase = 0  # Track which text is showing
        self.english_modal = None
        self.narrative_complete = False
        
        # Dark urban gradient background
        with self.canvas.before:
            Color(0.04, 0.06, 0.12, 1)  # Deep dark blue
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Main narrative container (semi-transparent)
        self.narrative_container = FloatLayout(
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        
        # Overlay gradient (subtle top-to-bottom)
        with self.narrative_container.canvas.before:
            Color(0.0, 0.0, 0.0, 0.3)
            self._overlay_top = Rectangle(pos=self.narrative_container.pos, size=self.narrative_container.size)
        
        self.add_widget(self.narrative_container)
        
        # Narrative text lines (will be filled and animated in sequence)
        self.narrative_labels = []
        self._create_narrative_labels()
        
        # English support text (always present but initially hidden)
        self.english_support_label = Label(
            text="You've just arrived in Barcelona. You don't know anyone.",
            font_size="14sp",
            color=(0.6, 0.65, 0.75, 0.7),  # Grey, subtle, semi-transparent
            italic=True,
            size_hint=(0.9, None),
            height=30,
            pos_hint={"center_x": 0.5, "y": 0.35},
            opacity=0
        )
        self.narrative_container.add_widget(self.english_support_label)
        
        # Fade in English support after all Catalan text
        self._english_support_visible = False
        
        # Call-to-action button (initially hidden)
        self.start_button = Button(
            text="Començar el teu primer dia",
            size_hint=(0.6, None),
            height=52,
            pos_hint={"center_x": 0.5, "y": 0.12},
            background_normal="",
            background_color=(0.3, 0.9, 0.5, 1),
            color=(0.05, 0.08, 0.08, 1),
            bold=True,
            opacity=0
        )
        self.start_button.bind(on_release=self._on_start_first_day)
        self.narrative_container.add_widget(self.start_button)
        
        # English help link (initially hidden)
        self.help_link = Button(
            text="Need help in English?",
            size_hint=(0.6, None),
            height=38,
            pos_hint={"center_x": 0.5, "y": 0.02},
            background_normal="",
            background_color=(0.2, 0.45, 0.75, 1),
            color=(1, 1, 1, 1),
            opacity=0
        )
        self.help_link.bind(on_release=self._on_help_english)
        self.narrative_container.add_widget(self.help_link)
        
        # Start the narrative sequence
        self.schedule_narrative_sequence()
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    
    def _create_narrative_labels(self):
        """Create the narrative text labels (initially hidden)"""
        narrative_texts = [
            "Acabes d’arribar a Barcelona.",
            "No coneixes ningú.",
            "El metro serà el teu primer aliat.",
            "Cada parada és una oportunitat."
        ]
        
        # Position the narrative lines vertically centered
        positions = [
            {"center_x": 0.5, "y": 0.70},  # First line - high
            {"center_x": 0.5, "y": 0.60},  # Second line
            {"center_x": 0.5, "y": 0.50},  # Third line
            {"center_x": 0.5, "y": 0.40}   # Fourth line - lowest
        ]
        
        for i, (text, pos_hint) in enumerate(zip(narrative_texts, positions)):
            label = Label(
                text=text,
                font_size="28sp" if i < 3 else "26sp",  # Slightly smaller for final line
                bold=True,
                color=(0.9, 0.92, 0.95, 1),  # Soft white
                size_hint=(0.9, None),
                height=50 if i < 3 else 45,
                pos_hint=pos_hint,
                opacity=0,
                halign="center",
                valign="middle"
            )
            label.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
            self.narrative_container.add_widget(label)
            self.narrative_labels.append(label)
    
    def schedule_narrative_sequence(self):
        """Schedule the narrative text to appear sequentially with pauses"""
        # Intro: Play ambient sound and fade background
        Clock.schedule_once(lambda dt: self._play_intro_audio(), 0.05)
        
        # Line 1: "Acabes d’arribar a Barcelona." (0.2s)
        Clock.schedule_once(lambda dt: self._fade_in_line(0), 0.2)
        
        # Line 2: "No coneixes ningú." (1.2s)
        Clock.schedule_once(lambda dt: self._fade_in_line(1), 1.2)
        
        # Line 3: "El metro serà el teu primer aliat." (2.2s)
        Clock.schedule_once(lambda dt: self._fade_in_line(2), 2.2)
        
        # Line 4: "Cada parada és una oportunitat." (3.2s)
        Clock.schedule_once(lambda dt: self._fade_in_line(3), 3.2)
        
        # Show English support text (3.9s)
        Clock.schedule_once(lambda dt: self._show_english_support(), 3.9)
        
        # Show call-to-action buttons (4.4s)
        Clock.schedule_once(lambda dt: self._show_cta_buttons(), 4.4)
    
    def _play_intro_audio(self):
        """Play ambient tunnel/city arrival sound"""
        if self.audio:
            try:
                # Play subtle city ambience layers
                self._start_city_ambience()
            except:
                pass  # Audio service not available, continue silently

    def _start_city_ambience(self):
        """Start layered city ambience (crowd, metro, street) for onboarding."""
        if not self.audio:
            return

        self._stop_city_ambience()

        layers = []
        try:
            # Metro ambience (base layer)
            self.audio.set_ambience("station")

            # Distant crowd layer (soft, low volume)
            crowd = self.audio.play_event(AudioEvent.AMB_TUNNEL, volume=0.08, loop=True)
            if crowd:
                layers.append(crowd)

            # Subtle street layer (very low volume)
            street = self.audio.play_event(AudioEvent.AMB_STATION, volume=0.05, loop=True)
            if street:
                layers.append(street)
        except Exception:
            layers = []

        self._city_ambience_layers = layers

    def _stop_city_ambience(self):
        """Stop any layered onboarding ambience."""
        for sound in self._city_ambience_layers:
            try:
                sound.stop()
            except Exception:
                pass
        self._city_ambience_layers = []
        if self.audio:
            try:
                self.audio.set_ambience("none")
            except Exception:
                pass
    
    def _fade_in_line(self, line_index):
        """Fade in a narrative text line"""
        label = self.narrative_labels[line_index]
        # Fade in over 0.5 seconds
        anim = Animation(opacity=1, duration=0.5, transition="in_out_quad")
        anim.start(label)
        
        # After 1 second, fade out to make room for next line
        # (except for the last line which stays visible)
        if line_index < len(self.narrative_labels) - 1:
            Clock.schedule_once(
                lambda dt: Animation(opacity=0, duration=0.4, transition="in_out_quad").start(label),
                1.4
            )
    
    def _show_english_support(self):
        """Show optional English support text"""
        self._english_support_visible = True
        anim = Animation(opacity=1, duration=0.6, transition="in_out_quad")
        anim.start(self.english_support_label)
    
    def _show_cta_buttons(self):
        """Show call-to-action buttons"""
        # Fade in start button
        anim_start = Animation(opacity=1, duration=0.5, transition="in_out_quad")
        anim_start.start(self.start_button)
        
        # Fade in help link (slightly delayed)
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, duration=0.5, transition="in_out_quad").start(self.help_link),
            0.2
        )
        
        self.narrative_complete = True
    
    def _on_start_first_day(self, instance):
        """User clicked 'Começar el teu primer dia' - activate First Day Mode and proceed"""
        # Mark onboarding as complete
        self.settings_manager.set("has_completed_onboarding", True)

        # Stop onboarding ambience layers
        self._stop_city_ambience()
        
        # Activate First Day Mode
        if self.app_context:
            try:
                # Set First Day Mode flags
                if hasattr(self.app_context, 'first_day_mode'):
                    self.app_context.first_day_mode = True
                if hasattr(self.app_context, 'first_day_progress'):
                    self.app_context.first_day_progress = 0
            except:
                pass
        
        # Play subtle station announcement
        if self.audio:
            try:
                self.audio.play_station_announcement()
            except:
                pass
        
        # Fade out overlay
        anim = Animation(opacity=0, duration=0.4, transition="in_out_quad")
        def on_complete(*args):
            if self.in_parent:
                self.parent.remove_widget(self)
            if self.on_complete:
                self.on_complete()
        anim.bind(on_complete=lambda *args: on_complete())
        anim.start(self)
    
    def _on_help_english(self, instance):
        """Show English explanation modal"""
        self._show_english_modal()
    
    def _show_english_modal(self):
        """Display English help modal with game instructions"""
        modal = FloatLayout(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        
        # Semi-transparent dark background
        with modal.canvas.before:
            Color(0, 0, 0, 0.92)
            modal_bg = Rectangle(pos=modal.pos, size=modal.size)
        
        def update_modal_bg(*args):
            modal_bg.pos = modal.pos
            modal_bg.size = modal.size
        modal.bind(pos=update_modal_bg, size=update_modal_bg)
        
        # Modal panel
        panel_width = 540
        panel_height = 420
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        # Panel background with styled border
        with panel.canvas:
            Color(0.12, 0.15, 0.2, 1)
            RoundedRectangle(pos=panel.pos, size=panel.size, radius=[18])
            # Green accent border
            Color(0.3, 0.9, 0.5, 1)
            RoundedRectangle(
                pos=(panel.x + 3, panel.y + 3),
                size=(panel.width - 6, panel.height - 6),
                radius=[16]
            )
        
        # Title
        title = Label(
            text="How to Play",
            font_size="28sp",
            bold=True,
            color=(0.3, 0.9, 0.5, 1),
            size_hint=(1, None),
            height=55,
            pos_hint={"center_x": 0.5, "top": 0.94}
        )
        panel.add_widget(title)
        
        # Instructions text (English)
        instructions_text = (
            "1. Look at the next station (top of screen)\n\n"
            "2. Drag the correct token to the green circle\n\n"
            "3. Release it before the train arrives\n\n"
            "4. Progress through Barcelona\n\n"
            "5. The game is entirely in Catalan"
        )
        
        instructions = Label(
            text=instructions_text,
            font_size="16sp",
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(0.85, None),
            height=200,
            pos_hint={"center_x": 0.5, "y": 0.15},
            halign="left",
            valign="top"
        )
        instructions.text_size = (panel_width * 0.8, 200)
        panel.add_widget(instructions)
        
        # Start button
        start_button = Button(
            text="Start my first day in Catalan",
            size_hint=(0.75, None),
            height=50,
            pos_hint={"center_x": 0.5, "y": 0.05},
            background_normal="",
            background_color=(0.3, 0.9, 0.5, 1),
            color=(0.05, 0.08, 0.08, 1),
            bold=True
        )
        
        def on_start_from_modal(*args):
            # Remove modal
            if modal in self.parent.children:
                self.parent.remove_widget(modal)
            # Proceed with First Day Mode activation
            self._on_start_first_day(None)
        
        start_button.bind(on_release=on_start_from_modal)
        panel.add_widget(start_button)
        
        modal.add_widget(panel)
        
        # Touch handler: tapping outside modal returns to narrative
        def on_modal_touch(instance, touch):
            if not panel.collide_point(*touch.pos):
                if modal in self.parent.children:
                    self.parent.remove_widget(modal)
                return True
            return False
        
        modal.bind(on_touch_down=on_modal_touch)
        
        self.english_modal = modal
        self.parent.add_widget(modal)
    
    def in_parent(self):
        """Check if overlay is still in parent"""
        return self in self.parent.children if self.parent else False


class OnboardingOverlay(NarrativeOnboardingOverlay):
    """Alias for backward compatibility"""
    pass


class SettingsOverlay(FloatLayout):
    """Simple settings modal for toggles."""

    def __init__(self, on_close, **kwargs):
        super().__init__(**kwargs)
        self.on_close = on_close
        self.settings_manager = SettingsManager()
        self.toggle_buttons = {}

        with self.canvas.before:
            Color(0, 0, 0, 0.75)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        panel_width = 420
        panel_height = 380  # Increased for language toggle
        self.panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        with self.panel.canvas:
            Color(0.14, 0.15, 0.2, 1)
            RoundedRectangle(pos=self.panel.pos, size=self.panel.size, radius=[16])

        self.add_widget(self.panel)
        self.panel.bind(pos=self._update_panel, size=self._update_panel)

        title = Label(
            text="Configuració",
            font_size="24sp",
            bold=True,
            color=(0.3, 0.9, 0.5, 1),
            size_hint=(1, None),
            height=40,
            pos_hint={"center_x": 0.5, "top": 0.93}
        )
        self.panel.add_widget(title)

        rows = BoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint=(0.9, None),
            height=230,  # Increased for 4 settings
            pos_hint={"center_x": 0.5, "center_y": 0.55}
        )

        settings_data = [
            ("Idioma", "language"),  # Language selector
            ("Mode de pràctica", "practice_mode"),
            ("Mode de direcció", "direction_mode"),
            ("Subtítols", "subtitles_enabled"),
        ]

        for label_text, key in settings_data:
            if key == "language":
                rows.add_widget(self._build_language_row(label_text))
            else:
                rows.add_widget(self._build_toggle_row(label_text, key))

        self.panel.add_widget(rows)

        close_button = Button(
            text="Tancar",
            size_hint=(0.4, None),
            height=40,
            pos_hint={"center_x": 0.5, "y": 0.08},
            background_normal="",
            background_color=(0.2, 0.5, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        close_button.bind(on_release=self._close)
        self.panel.add_widget(close_button)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _update_panel(self, *args):
        self.panel.canvas.clear()
        with self.panel.canvas:
            Color(0.14, 0.15, 0.2, 1)
            RoundedRectangle(pos=self.panel.pos, size=self.panel.size, radius=[16])

    def _build_toggle_row(self, label_text, key):
        row = BoxLayout(orientation="horizontal", spacing=10)
        label = Label(
            text=label_text,
            font_size="16sp",
            color=(0.95, 0.95, 0.95, 1),
            size_hint=(0.7, 1),
            halign="left",
            valign="middle"
        )
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        current_value = self.settings_manager.get(key, False)
        toggle_button = Button(
            text="ACTIU" if current_value else "INACTIU",
            size_hint=(0.3, 1),
            background_normal="",
            background_color=(0.2, 1, 0.3, 1) if current_value else (1, 0.3, 0.2, 1),
            color=(0, 0, 0, 1)
        )
        toggle_button.bind(on_release=lambda instance: self._toggle_setting(key, instance))
        self.toggle_buttons[key] = toggle_button

        row.add_widget(label)
        row.add_widget(toggle_button)
        return row

    def _build_language_row(self, label_text):
        """Build a language selector row"""
        row = BoxLayout(orientation="horizontal", spacing=10)
        label = Label(
            text=label_text,
            font_size="16sp",
            color=(0.95, 0.95, 0.95, 1),
            size_hint=(0.7, 1),
            halign="left",
            valign="middle"
        )
        label.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        current_lang = self.settings_manager.get("language", "ca")
        lang_text = "Català" if current_lang == "ca" else "English"
        
        lang_button = Button(
            text=lang_text,
            size_hint=(0.3, 1),
            background_normal="",
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        lang_button.bind(on_release=lambda instance: self._toggle_language(instance))

        row.add_widget(label)
        row.add_widget(lang_button)
        return row

    def _toggle_language(self, button):
        """Toggle between Catalan and English"""
        current_lang = self.settings_manager.get("language", "ca")
        new_lang = "en" if current_lang == "ca" else "ca"
        self.settings_manager.set("language", new_lang)
        button.text = "English" if new_lang == "ca" else "Català"
        
        # Update global language
        try:
            from core.i18n import set_language
            set_language(new_lang)
        except ImportError:
            pass  # i18n not yet initialized

    def _toggle_setting(self, key, button):
        new_value = not self.settings_manager.get(key, False)
        self.settings_manager.set(key, new_value)
        button.text = "ACTIU" if new_value else "INACTIU"
        button.background_color = (0.2, 1, 0.3, 1) if new_value else (1, 0.3, 0.2, 1)

    def _close(self, *args):
        if callable(self.on_close):
            self.on_close()

    def on_touch_down(self, touch):
        if self.panel.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._close()
        return True


class CoverScreen(Screen):
    """Splash / cover screen with animated background."""

    def __init__(self, app_context, daily_challenge_info=None, **kwargs):
        super().__init__(**kwargs)
        self.settings_overlay = None
        self.settings_manager = SettingsManager()
        self.onboarding_overlay = None
        self.bg_animation = None
        self.fade_widgets = []
        self.app_context = app_context
        self.metro_network = app_context.metro_network
        self.progress_manager = app_context.progress_manager
        self.daily_challenge_info = daily_challenge_info

        root = FloatLayout()
        self.add_widget(root)

        self.bg_scatter = Scatter(
            size_hint=(1, 1),
            pos=(0, 0),
            do_translation=False,
            do_rotation=False,
            do_scale=False
        )
        self.bg_image = Image(
            source="assets/cover_proxima_parada.png",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos=(0, 0)
        )
        self.bg_scatter.add_widget(self.bg_image)
        root.add_widget(self.bg_scatter)

        self.gradient = GradientOverlay(size_hint=(1, 1), pos=(0, 0))
        root.add_widget(self.gradient)

        self.content = FloatLayout()
        root.add_widget(self.content)

        self.title_label = Label(
            text="PRÒXIMA PARADA",
            font_size="48sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(0.9, None),
            height=60,
            pos_hint={"center_x": 0.5, "center_y": 0.62}
        )
        self.subtitle_label = Label(
            text="Aprèn a moure’t pel Metro de Barcelona",
            font_size="18sp",
            color=(0.85, 0.9, 0.95, 1),
            size_hint=(0.9, None),
            height=30,
            pos_hint={"center_x": 0.5, "center_y": 0.54}
        )

        self.button_box = BoxLayout(
            orientation="vertical",
            spacing=12,
            size_hint=(0.7, None),
            height=280,  # Increased to fit 5 buttons
            pos_hint={"center_x": 0.5, "y": 0.08}
        )
        self.play_button = Button(
            text="Jugar",
            size_hint=(1, None),
            height=48,
            background_normal="",
            background_color=(0.2, 0.85, 0.55, 1),
            color=(0.05, 0.08, 0.08, 1),
            bold=True
        )
        self.daily_challenge_button = Button(
            text="Repte del dia",
            size_hint=(1, None),
            height=46,
            background_normal="",
            background_color=(0.95, 0.85, 0.35, 1),
            color=(0.1, 0.1, 0.1, 1),
            bold=True
        )
        self.first_day_button = Button(
            text="🌟 El teu primer dia a Barcelona",
            size_hint=(1, None),
            height=46,
            background_normal="",
            background_color=(0.95, 0.75, 0.2, 1),
            color=(0.1, 0.1, 0.1, 1),
            bold=True
        )
        self.descobreix_button = Button(
            text="🏛️ Descobreix Barcelona",
            size_hint=(1, None),
            height=44,
            background_normal="",
            background_color=(0.28, 0.72, 0.48, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.settings_button = Button(
            text="Configuració",
            size_hint=(1, None),
            height=44,
            background_normal="",
            background_color=(0.2, 0.45, 0.75, 1),
            color=(1, 1, 1, 1)
        )
        self.button_box.add_widget(self.play_button)
        self.button_box.add_widget(self.daily_challenge_button)
        self.button_box.add_widget(self.first_day_button)
        self.button_box.add_widget(self.descobreix_button)
        self.button_box.add_widget(self.settings_button)

        self.footer_label = Label(
            text="L3 — Zona Universitària → Trinitat Nova",
            font_size="14sp",
            color=(0.7, 0.75, 0.8, 0.9),
            size_hint=(0.9, None),
            height=22,
            pos_hint={"center_x": 0.5, "y": 0.04}
        )

        self.content.add_widget(self.title_label)
        self.content.add_widget(self.subtitle_label)
        self.content.add_widget(self.button_box)
        self.content.add_widget(self.footer_label)

        self.fade_widgets = [
            self.title_label,
            self.subtitle_label,
            self.button_box,
            self.footer_label,
        ]

        self.play_button.bind(on_release=self._start_game)
        self.daily_challenge_button.bind(on_release=self._start_daily_challenge)
        self.first_day_button.bind(on_release=self._start_first_day)
        self.descobreix_button.bind(on_release=self._show_descobreix_info)
        self.settings_button.bind(on_release=self._open_settings)

        self.bind(size=self._sync_bg)
        self._sync_bg()
        self._prepare_fade()

    def _sync_bg(self, *args):
        self.bg_scatter.size = self.size
        self.bg_image.size = self.size

    def _prepare_fade(self):
        for widget in self.fade_widgets:
            widget.opacity = 0

    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self._on_keyboard)
        self._refresh_daily_challenge()
        self._start_bg_motion()
        
        # Check if onboarding needs to be shown
        if not self.settings_manager.get("has_completed_onboarding", False):
            self._show_onboarding()
        else:
            self._animate_in()

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self._on_keyboard)
        self._stop_bg_motion()

    def _show_onboarding(self):
        """Show the narrative immersion onboarding overlay."""
        def _on_onboarding_complete():
            # After onboarding is done, navigate directly to First Day Mode
            if not self.manager:
                return
            self.manager.transition = FadeTransition(duration=0.4)
            self.manager.current = SCREEN_LINES  # Goes to line selection
            # First Day Mode will be activated by the overlay
        
        self.onboarding_overlay = NarrativeOnboardingOverlay(
            on_complete_callback=_on_onboarding_complete,
            app_context=self.app_context,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(self.onboarding_overlay)

    def _animate_in(self):
        self._prepare_fade()
        for index, widget in enumerate(self.fade_widgets):
            delay = 0.12 * index
            anim = Animation(opacity=1, duration=0.6, transition="out_quad")
            Clock.schedule_once(lambda dt, w=widget, a=anim: a.start(w), delay)

    def _start_bg_motion(self):
        if self.bg_animation:
            self.bg_animation.cancel(self.bg_scatter)
        self.bg_scatter.scale = 1.0
        self.bg_animation = (
            Animation(scale=1.04, duration=12, transition="in_out_quad") +
            Animation(scale=1.0, duration=12, transition="in_out_quad")
        )
        self.bg_animation.repeat = True
        self.bg_animation.start(self.bg_scatter)

    def _stop_bg_motion(self):
        if self.bg_animation:
            self.bg_animation.cancel(self.bg_scatter)
            self.bg_animation = None

    def _start_game(self, *args):
        if not self.manager:
            return
        self.manager.transition = FadeTransition(duration=0.3)
        self.manager.current = SCREEN_LINES

    def _refresh_daily_challenge(self):
        if self.metro_network is None:
            self.app_context.load_all()
            self.metro_network = self.app_context.metro_network
        self.daily_challenge_info = get_daily_challenge(self.metro_network)

    def _start_daily_challenge(self, *args):
        if not self.manager:
            return
        if not self.daily_challenge_info:
            return
        self._show_daily_challenge_intro(self.daily_challenge_info)
    
    def _start_first_day(self, *args):
        """Start First Day Mode - curated journey through Barcelona"""
        if not self.manager:
            return
        
        # Show intro overlay first
        self._show_first_day_intro()

    def _show_daily_challenge_intro(self, challenge_info):
        """Show intro overlay for Daily Challenge Mode"""
        overlay = FloatLayout(size_hint=(1, 1))
        from kivy.graphics import Color, Rectangle, RoundedRectangle

        with overlay.canvas.before:
            Color(0, 0, 0, 0.9)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)

        def update_overlay_bg(*args):
            overlay.bg.pos = overlay.pos
            overlay.bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)

        panel_width = 560
        panel_height = 300
        from kivy.uix.widget import Widget
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with panel.canvas:
            Color(0.12, 0.15, 0.2, 1)
            RoundedRectangle(pos=panel.pos, size=panel.size, radius=[18])
            Color(0.95, 0.85, 0.35, 1)
            RoundedRectangle(
                pos=(panel.x + 3, panel.y + 3),
                size=(panel.width - 6, panel.height - 6),
                radius=[16]
            )

        title = Label(
            text="Repte del dia",
            font_size='28sp',
            bold=True,
            color=(1, 0.95, 0.5, 1),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.94}
        )
        panel.add_widget(title)

        station_name = challenge_info.get("station_name", "")
        line_id = challenge_info.get("line_id", "")

        subtitle = Label(
            text=f"Arriba fins a {station_name}",
            font_size='20sp',
            color=(0.9, 0.9, 0.95, 1),
            size_hint=(1, None),
            height=35,
            pos_hint={'center_x': 0.5, 'top': 0.77}
        )
        panel.add_widget(subtitle)

        line_label = Label(
            text=f"Línia: [{line_id}]",
            font_size='18sp',
            color=(0.8, 0.85, 0.95, 1),
            size_hint=(1, None),
            height=28,
            pos_hint={'center_x': 0.5, 'top': 0.68}
        )
        panel.add_widget(line_label)

        if self.progress_manager.is_daily_completed(challenge_info.get("date", "")):
            completed_label = Label(
                text="Repte completat avui!",
                font_size='16sp',
                bold=True,
                color=(0.3, 1.0, 0.5, 1),
                size_hint=(1, None),
                height=24,
                pos_hint={'center_x': 0.5, 'top': 0.58}
            )
            panel.add_widget(completed_label)

        start_button = Button(
            text="Començar",
            size_hint=(0.45, None),
            height=44,
            pos_hint={'center_x': 0.5, 'y': 0.08},
            background_normal="",
            background_color=(0.3, 0.7, 0.9, 1),
            color=(1, 1, 1, 1),
            bold=True
        )

        def start_daily(*args):
            if overlay in self.children:
                self.remove_widget(overlay)
            game_screen = self.manager.get_screen(SCREEN_GAME)
            if hasattr(game_screen, 'set_daily_challenge'):
                game_screen.set_daily_challenge(challenge_info)
            game_screen._build_game()
            self.manager.transition = FadeTransition(duration=0.3)
            self.manager.current = SCREEN_GAME

        start_button.bind(on_release=start_daily)
        panel.add_widget(start_button)

        overlay.add_widget(panel)
        self.add_widget(overlay)
    
    def _show_first_day_intro(self):
        """Show intro overlay for First Day Mode"""
        overlay = FloatLayout(size_hint=(1, 1))
        from kivy.graphics import Color, Rectangle, RoundedRectangle
        
        with overlay.canvas.before:
            Color(0, 0, 0, 0.9)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)

        def update_overlay_bg(*args):
            overlay.bg.pos = overlay.pos
            overlay.bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)

        panel_width = 580
        panel_height = 360
        from kivy.uix.widget import Widget
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with panel.canvas:
            Color(0.12, 0.15, 0.2, 1)
            RoundedRectangle(pos=panel.pos, size=panel.size, radius=[18])
            Color(0.95, 0.85, 0.3, 1)  # Gold accent
            RoundedRectangle(
                pos=(panel.x + 3, panel.y + 3),
                size=(panel.width - 6, panel.height - 6),
                radius=[16]
            )

        title = Label(
            text="🌟 El teu primer dia a Barcelona",
            font_size='28sp',
            bold=True,
            color=(1, 0.95, 0.4, 1),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.94}
        )
        panel.add_widget(title)

        subtitle = Label(
            text="Descobreix el centre històric i el mar",
            font_size='20sp',
            color=(0.9, 0.9, 0.95, 1),
            size_hint=(1, None),
            height=35,
            pos_hint={'center_x': 0.5, 'top': 0.80},
            italic=True
        )
        panel.add_widget(subtitle)

        description = Label(
            text=(
                "Comença un viatge guiat pels llocs més emblemàtics:\\n\\n"
                "• Catalunya — El cor de la ciutat\\n"
                "• Liceu — La Rambla i el teatre\\n"
                "• Jaume I — Entrada al Barri Gòtic\\n"
                "• Barceloneta — La platja i el mar\\n"
                "• Espanya — Montjuïc i les vistes"
            ),
            font_size='17sp',
            color=(0.85, 0.88, 0.92, 1),
            size_hint=(0.9, None),
            height=180,
            halign='left',
            valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        description.text_size = (panel_width * 0.85, 180)
        panel.add_widget(description)

        start_button = Button(
            text="Començar el viatge",
            size_hint=(0.5, None),
            height=44,
            pos_hint={'center_x': 0.5, 'y': 0.08},
            background_normal="",
            background_color=(0.3, 0.7, 0.9, 1),
            color=(1, 1, 1, 1),
            bold=True
        )

        def start_journey(*args):
            if overlay in self.children:
                self.remove_widget(overlay)
            # Navigate to game screen with first_day_mode=True
            game_screen = self.manager.get_screen(SCREEN_GAME)
            if hasattr(game_screen, 'set_line_id'):
                game_screen.set_line_id("L3")  # First day uses L3
            game_screen.first_day_mode = True  # Enable first day mode
            game_screen._build_game()  # Rebuild game with new mode
            self.manager.transition = FadeTransition(duration=0.3)
            self.manager.current = SCREEN_GAME

        start_button.bind(on_release=start_journey)
        panel.add_widget(start_button)

        overlay.add_widget(panel)
        self.add_widget(overlay)

    def _open_settings(self, *args):
        if self.settings_overlay:
            return

        def on_close():
            if self.settings_overlay and self.settings_overlay in self.children:
                self.remove_widget(self.settings_overlay)
            self.settings_overlay = None

        self.settings_overlay = SettingsOverlay(on_close=on_close)
        self.add_widget(self.settings_overlay)
    
    def _show_descobreix_info(self, *args):
        """Show 'Descobreix Barcelona' civic information overlay"""
        from kivy.graphics import Color, Rectangle, RoundedRectangle
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.widget import Widget
        
        overlay = FloatLayout(size_hint=(1, 1))
        
        with overlay.canvas.before:
            Color(0, 0, 0, 0.88)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)
        
        def update_overlay_bg(*args):
            overlay.bg.pos = overlay.pos
            overlay.bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)
        
        # Scrollable content panel
        scroll_view = ScrollView(
            size_hint=(None, None),
            size=(620, 520),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        # Content container
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[30, 30],
            spacing=20
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Panel background
        with content.canvas.before:
            Color(0.10, 0.13, 0.18, 1)
            content.bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[20])
        
        def update_content_bg(*args):
            content.bg.pos = content.pos
            content.bg.size = content.size
        content.bind(pos=update_content_bg, size=update_content_bg)
        
        # Title
        title = Label(
            text="🏛️ Descobreix Barcelona",
            font_size='30sp',
            bold=True,
            size_hint=(1, None),
            height=60,
            color=(0.3, 0.85, 0.5, 1),
            halign='left',
            valign='top'
        )
        title.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None)))
        content.add_widget(title)
        
        # Sections with civic information
        sections = [
            {
                'icon': '🚇',
                'title': 'Què és TMB?',
                'text': (
                    "Transports Metropolitans de Barcelona és l'empresa pública "
                    "que gestiona el metro i els busos de la ciutat. "
                    "Fundada el 1997, TMB connecta Barcelona i la seva àrea metropolitana, "
                    "facilitant la mobilitat diària de milions de persones."
                )
            },
            {
                'icon': '🏘️',
                'title': 'Què és un barri?',
                'text': (
                    "Un 'barri' és un veïnat o districte dins de Barcelona. "
                    "Cada barri té la seva pròpia personalitat, història i comunitat. "
                    "De Gràcia a Barceloneta, del Gòtic a l'Eixample, "
                    "cada barri ofereix una experiència única de la ciutat."
                )
            },
            {
                'icon': '💬',
                'title': 'Per què el català importa?',
                'text': (
                    "El català és la llengua oficial de Catalunya i una part essencial "
                    "de la identitat cultural de Barcelona. Parlar català no només "
                    "facilita la vida diària, sinó que també mostra respecte per la cultura local "
                    "i ajuda a integrar-te millor a la comunitat."
                )
            },
            {
                'icon': '🤝',
                'title': 'Respecte per la llengua local',
                'text': (
                    "A Barcelona, tant el català com el castellà són llengües oficials. "
                    "Tot i que molts barcelonins parlen ambdues, fer l'esforç de parlar català "
                    "és molt valorat. No tinguis por de cometre errors - "
                    "l'important és intentar-ho i mostrar interès per la llengua i la cultura."
                )
            }
        ]
        
        for section in sections:
            # Section container
            section_widget = BoxLayout(
                orientation='vertical',
                size_hint=(1, None),
                spacing=8
            )
            section_widget.bind(minimum_height=section_widget.setter('height'))
            
            # Section title with icon
            section_title = Label(
                text=f"{section['icon']} {section['title']}",
                font_size='22sp',
                bold=True,
                size_hint=(1, None),
                height=40,
                color=(0.85, 0.90, 0.95, 1),
                halign='left',
                valign='top'
            )
            section_title.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None)))
            section_widget.add_widget(section_title)
            
            # Section text
            section_text = Label(
                text=section['text'],
                font_size='16sp',
                size_hint=(1, None),
                color=(0.70, 0.75, 0.82, 1),
                halign='left',
                valign='top',
                markup=True
            )
            section_text.bind(
                texture_size=lambda instance, value: setattr(instance, 'height', value[1] + 10)
            )
            section_text.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None)))
            section_widget.add_widget(section_text)
            
            content.add_widget(section_widget)
        
        # Close button at bottom
        close_btn = Button(
            text="Tancar",
            size_hint=(0.4, None),
            height=44,
            background_normal="",
            background_color=(0.25, 0.75, 0.45, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        
        def dismiss_overlay(*args):
            if overlay in self.children:
                self.remove_widget(overlay)
        
        close_btn.bind(on_release=dismiss_overlay)
        
        # Add button to bottom of content
        button_container = BoxLayout(
            size_hint=(1, None),
            height=60,
            padding=[0, 15, 0, 0]
        )
        button_container.add_widget(Widget())  # Spacer
        button_container.add_widget(close_btn)
        button_container.add_widget(Widget())  # Spacer
        content.add_widget(button_container)
        
        scroll_view.add_widget(content)
        overlay.add_widget(scroll_view)
        
        # Touch outside to close
        def on_overlay_touch(instance, touch):
            if overlay.collide_point(*touch.pos):
                if not scroll_view.collide_point(*touch.pos):
                    dismiss_overlay()
                    return True
            return False
        
        overlay.bind(on_touch_down=on_overlay_touch)
        self.add_widget(overlay)

    def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
        if key == 27:
            App.get_running_app().stop()
            return True
        return False


class GameScreen(Screen):
    """Hosts the actual game widget."""
    
    # Class variable to track if civic splash has been shown
    _civic_splash_shown = False

    def __init__(self, app_context, random_seed=None, civic_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.app_context = app_context
        self.practice_mode = app_context.settings.get("practice_mode", False)
        self.direction_mode = app_context.settings.get("direction_mode", False)
        self.first_day_mode = False
        self.random_seed = random_seed
        self.civic_mode = civic_mode
        self.line_id = app_context.current_line_id
        self.metro_network = app_context.metro_network
        self.progress_manager = app_context.progress_manager
        self.game_widget = None
        self.goal_mode = False
        self.goal_station_id = None
        self.daily_challenge_date = None

    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self._on_keyboard)
        self._build_game()
        if self.game_widget and hasattr(self.game_widget, "reset_run"):
            self.game_widget.reset_run(
                goal_mode=self.goal_mode,
                goal_station_id=self.goal_station_id,
                first_day_mode=self.first_day_mode
            )
        
        # Show civic splash on first game (if onboarding completed)
        if not GameScreen._civic_splash_shown and not self.first_day_mode:
            settings_manager = SettingsManager()
            if settings_manager.get("has_completed_onboarding", False):
                GameScreen._civic_splash_shown = True
                if self.game_widget and hasattr(self.game_widget, "show_civic_splash"):
                    # Delay slightly to let game load
                    Clock.schedule_once(lambda dt: self.game_widget.show_civic_splash(), 0.5)

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self._on_keyboard)
        if self.game_widget:
            if hasattr(self.game_widget, "pause"):
                self.game_widget.pause()
            elif hasattr(self.game_widget, "stop_game"):
                self.game_widget.stop_game()
        self.goal_mode = False
        self.goal_station_id = None
        self.daily_challenge_date = None

    def _build_game(self):
        if self.game_widget:
            if hasattr(self.game_widget, "stop_game"):
                self.game_widget.stop_game()
            self.remove_widget(self.game_widget)
            self.game_widget = None
        from game_propera_parada import ProximaParadaGame
        self.practice_mode = self.app_context.settings.get("practice_mode", self.practice_mode)
        self.direction_mode = self.app_context.settings.get("direction_mode", self.direction_mode)
        if self.goal_mode:
            self.app_context.set_mode("GOAL", goal_station_id=self.goal_station_id)
        else:
            self.app_context.set_mode("FREE")
        self.game_widget = ProximaParadaGame(
            practice_mode=self.practice_mode,
            direction_mode=self.direction_mode,
            first_day_mode=self.first_day_mode,
            random_seed=self.random_seed,
            line_id=self.line_id,
            metro_network=self.metro_network,
            progress_manager=self.progress_manager,
            mode=self.app_context.mode_instance,
            goal_mode=self.goal_mode,
            goal_station_id=self.goal_station_id,
            daily_challenge_date=self.daily_challenge_date,
            enable_settings_hotkey=False,
            civic_mode=self.civic_mode
        )
        self.add_widget(self.game_widget)

    def set_line_id(self, line_id):
        self.line_id = line_id
        self.app_context.set_line(line_id)
        self.goal_mode = False
        self.goal_station_id = None
        self.daily_challenge_date = None
        self.app_context.set_mode("FREE")

    def set_daily_challenge(self, challenge_info):
        if not challenge_info:
            return
        self.line_id = challenge_info.get("line_id", self.line_id)
        self.goal_mode = True
        self.goal_station_id = challenge_info.get("station_id")
        self.daily_challenge_date = challenge_info.get("date")
        self.first_day_mode = False
        self.app_context.set_mode("GOAL", goal_station_id=self.goal_station_id)

    def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
        if key == 27 and self.manager:  # ESC key
            self.manager.transition = FadeTransition(duration=0.25)
            self.manager.current = SCREEN_LINES
            return True
        return False


class HoverBehavior:
    """Simple hover detection for desktop mouse users."""

    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        local_pos = self.to_widget(*pos)
        inside = self.collide_point(*local_pos)
        if inside == self.hovered:
            return
        self.hovered = inside
        if inside:
            self.on_hover()
        else:
            self.on_unhover()

    def on_hover(self):
        pass

    def on_unhover(self):
        pass

    def on_parent(self, instance, parent):
        if parent is None:
            Window.unbind(mouse_pos=self._on_mouse_pos)


class LineCard(ButtonBehavior, BoxLayout, HoverBehavior):
    """Clickable card for a metro line."""

    line_id = StringProperty("")
    endpoints_text = StringProperty("")
    pitch_text = StringProperty("")
    progress_text = StringProperty("")
    badge_text = StringProperty("")
    progress_ratio = NumericProperty(0.0)
    completed = BooleanProperty(False)
    goals_completed = NumericProperty(0)
    badges = ListProperty([])  # List of badge dicts with 'icon' and 'name'
    daily_challenge = BooleanProperty(False)
    bg_rgba = ListProperty([0.12, 0.13, 0.18, 0.95])
    stripe_rgba = ListProperty([0.2, 0.85, 0.55, 1])

    def __init__(self, line_id, line_color_hex, endpoints_text, pitch_text, progress_text, progress_ratio, badge_text, completed, goals_completed, badges, on_select, daily_challenge=False, **kwargs):
        super().__init__(orientation="vertical", spacing=6, padding=[18, 14, 18, 14], **kwargs)
        self.line_id = line_id
        self.endpoints_text = endpoints_text
        self.goals_completed = goals_completed
        self.badges = badges
        self.pitch_text = pitch_text
        self.progress_text = progress_text
        self.progress_ratio = progress_ratio
        self.badge_text = badge_text
        self.completed = completed
        self.on_select = on_select
        self.daily_challenge = daily_challenge

        if self.completed:
            self.bg_rgba = [0.11, 0.12, 0.14, 0.9]

        base_color = get_color_from_hex(line_color_hex)
        self.stripe_rgba = [base_color[0], base_color[1], base_color[2], 1]

        with self.canvas.before:
            self._bg_color = Color(rgba=self.bg_rgba)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
            self._stripe_color = Color(rgba=self.stripe_rgba)
            self._stripe_rect = Rectangle(pos=self.pos, size=(10, self.height))

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(bg_rgba=self._update_bg_color, stripe_rgba=self._update_stripe_color)

        header_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=34)
        title = Label(
            text=self.line_id,
            font_size="30sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(0.6, 1),
            halign="left",
            valign="middle"
        )
        title.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        badge = Label(
            text=self.badge_text,
            font_size="12sp",
            bold=True,
            color=(1, 0.85, 0.3, 1),
            size_hint=(0.3, 1),
            halign="right",
            valign="middle"
        )
        badge.bind(size=lambda instance, value: setattr(instance, "text_size", value))
        
        # Add goal completion badge if goals > 0
        if hasattr(self, 'goals_completed') and self.goals_completed > 0:
            goals_label = Label(
                text=f"🎯 x{self.goals_completed}",
                font_size="11sp",
                bold=True,
                color=(1, 0.85, 0.2, 1),
                size_hint=(None, 1),
                width=50,
                halign="right",
                valign="middle"
            )
            goals_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
            header_row.add_widget(goals_label)
        
        header_row.add_widget(title)

        if self.daily_challenge:
            calendar_label = Label(
                text="📅",
                font_size="16sp",
                size_hint=(None, 1),
                width=24,
                halign="center",
                valign="middle",
                color=(1, 0.9, 0.4, 1)
            )
            calendar_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
            header_row.add_widget(calendar_label)
        header_row.add_widget(badge)

        subtitle = Label(
            text=self.endpoints_text,
            font_size="14sp",
            color=(0.8, 0.85, 0.9, 1),
            size_hint=(1, None),
            height=22,
            halign="left",
            valign="middle"
        )
        subtitle.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        pitch = Label(
            text=self.pitch_text,
            font_size="12sp",
            color=(0.65, 0.75, 0.85, 1),
            size_hint=(1, None),
            height=18 if self.pitch_text else 0,
            halign="left",
            valign="middle",
            max_lines=1,
            shorten=True,
            shorten_from="right"
        )
        pitch.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        progress = Label(
            text=self.progress_text,
            font_size="13sp",
            color=(0.65, 0.7, 0.8, 1),
            size_hint=(1, None),
            height=18,
            halign="left",
            valign="middle"
        )
        progress.bind(size=lambda instance, value: setattr(instance, "text_size", value))

        bar_container = Widget(size_hint=(1, None), height=8)
        with bar_container.canvas.before:
            Color(0.2, 0.2, 0.25, 1)
            self._progress_bg = RoundedRectangle(pos=bar_container.pos, size=bar_container.size, radius=[4])
        with bar_container.canvas:
            Color(0.2, 0.95, 0.6, 1)
            self._progress_fill = Rectangle(pos=bar_container.pos, size=(0, bar_container.height))
        bar_container.bind(pos=self._update_progress_bar, size=self._update_progress_bar)
        self.bind(progress_ratio=lambda instance, value: self._update_progress_bar())

        self.add_widget(header_row)
        self.add_widget(subtitle)
        self.add_widget(pitch)
        self.add_widget(progress)
        self.add_widget(bar_container)
        
        # Badge row (cultural exploration badges)
        if self.badges:
            badge_row = BoxLayout(
                orientation="horizontal",
                size_hint=(1, None),
                height=22,
                spacing=4
            )
            
            badge_label = Label(
                text="Insígnies:",
                font_size="11sp",
                color=(0.6, 0.65, 0.7, 1),
                size_hint=(None, 1),
                width=60,
                halign="left",
                valign="middle"
            )
            badge_label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
            badge_row.add_widget(badge_label)
            
            # Badge icons
            badges_text = " ".join([b["icon"] for b in self.badges])
            badge_icons = Label(
                text=badges_text,
                font_size="16sp",
                size_hint=(None, 1),
                width=120,
                halign="left",
                valign="middle"
            )
            badge_row.add_widget(badge_icons)
            
            # Badge count
            badge_count = Label(
                text=f"({len(self.badges)}/4)",
                font_size="11sp",
                color=(0.95, 0.75, 0.3, 1),
                size_hint=(1, 1),
                halign="right",
                valign="middle"
            )
            badge_count.bind(size=lambda instance, value: setattr(instance, "text_size", value))
            badge_row.add_widget(badge_count)
            
            self.add_widget(badge_row)

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._stripe_rect.pos = (self.x, self.y)
        self._stripe_rect.size = (10, self.height)

    def _update_bg_color(self, *args):
        self._bg_color.rgba = self.bg_rgba

    def _update_stripe_color(self, *args):
        self._stripe_color.rgba = self.stripe_rgba

    def _update_progress_bar(self, *args):
        if not hasattr(self, "_progress_bg"):
            return
        bar = self.children[0]
        self._progress_bg.pos = bar.pos
        self._progress_bg.size = bar.size
        fill_width = bar.width * max(0.0, min(1.0, self.progress_ratio))
        self._progress_fill.pos = bar.pos
        self._progress_fill.size = (fill_width, bar.height)

    def on_hover(self):
        if not self.state == "down":
            if self.completed:
                Animation(bg_rgba=[0.13, 0.14, 0.16, 0.95], duration=0.15).start(self)
            else:
                Animation(bg_rgba=[0.18, 0.2, 0.27, 1], duration=0.15).start(self)

    def on_unhover(self):
        if not self.state == "down":
            if self.completed:
                Animation(bg_rgba=[0.11, 0.12, 0.14, 0.9], duration=0.15).start(self)
            else:
                Animation(bg_rgba=[0.12, 0.13, 0.18, 0.95], duration=0.15).start(self)

    def on_press(self):
        Animation(bg_rgba=[0.22, 0.24, 0.32, 1], duration=0.08).start(self)

    def on_release(self):
        if self.completed:
            target = [0.13, 0.14, 0.16, 0.95] if self.hovered else [0.11, 0.12, 0.14, 0.9]
        else:
            target = [0.18, 0.2, 0.27, 1] if self.hovered else [0.12, 0.13, 0.18, 0.95]
        Animation(bg_rgba=target, duration=0.12).start(self)
        if callable(self.on_select):
            self.on_select(self.line_id)


class LineSelectScreen(Screen):
    """Screen to select which metro line to play."""

    def __init__(self, app_context, daily_challenge_info=None, **kwargs):
        super().__init__(**kwargs)
        self.app_context = app_context
        self.metro_network = app_context.metro_network
        self.progress_manager = app_context.progress_manager
        self.daily_challenge_info = daily_challenge_info
        self.daily_challenge_line_id = daily_challenge_info.get("line_id") if daily_challenge_info else None
        self.cards = []
        self.card_aspect_ratio = 3.0

        root = FloatLayout()
        self.add_widget(root)

        with root.canvas.before:
            Color(0.07, 0.08, 0.12, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_bg, size=self._update_bg)

        header = Label(
            text="Escull la línia",
            font_size="28sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=40,
            pos_hint={"center_x": 0.5, "top": 0.96}
        )
        root.add_widget(header)

        back_button = Button(
            text="Enrere",
            size_hint=(None, None),
            size=(100, 36),
            pos_hint={"x": 0.04, "top": 0.96},
            background_normal="",
            background_color=(0.2, 0.45, 0.75, 1),
            color=(1, 1, 1, 1)
        )
        back_button.bind(on_release=self._go_back)
        root.add_widget(back_button)

        scroll = ScrollView(
            size_hint=(1, 0.82),
            pos_hint={"center_x": 0.5, "y": 0.05},
            do_scroll_x=False
        )
        root.add_widget(scroll)

        self.grid = GridLayout(
            cols=2,
            spacing=16,
            padding=[28, 16, 28, 16],
            size_hint=(1, None)
        )
        self.grid.bind(minimum_height=self._update_grid_height)
        self.grid.bind(size=self._on_grid_size)
        scroll.add_widget(self.grid)

        self._build_cards()
        self.bind(size=self._update_columns)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _update_grid_height(self, *args):
        self.grid.height = self.grid.minimum_height

    def _update_columns(self, *args):
        if self.width < 700:
            self.grid.cols = 1
        elif self.width < 1100:
            self.grid.cols = 2
        else:
            self.grid.cols = 3
        self._update_card_sizes()

    def _on_grid_size(self, *args):
        self._update_card_sizes()

    def _update_card_sizes(self):
        if not self.cards:
            return
        cols = max(1, self.grid.cols)
        padding_left, padding_top, padding_right, padding_bottom = self.grid.padding
        available = self.grid.width - padding_left - padding_right - (self.grid.spacing[0] * (cols - 1))
        if available <= 0:
            return
        card_width = available / cols
        card_height = card_width / self.card_aspect_ratio
        for card in self.cards:
            card.size = (card_width, card_height)

    def _build_cards(self):
        self.grid.clear_widgets()
        self.cards = []
        daily_line_id = self.daily_challenge_line_id
        for line in self.metro_network.lines:
            endpoints = f"{line.endpoints.get('from', '')} \u2192 {line.endpoints.get('to', '')}"
            progress = self.progress_manager.get_line_progress(line.id)
            completed_ids = self.progress_manager.get_completed_station_ids(line.id)
            station_ids = [normalize_station_id(station.name) for station in line.stations]
            total = len(station_ids)
            unique_completed = len(set(completed_ids) & set(station_ids))
            ratio = (unique_completed / total) if total else 0.0
            percent = int(ratio * 100)
            progress_text = f"Progrés: {percent}%"
            is_completed = bool(progress.get("line_completed", False))
            badge_text = "COMPLETADA" if is_completed else ""
            pitch_text = getattr(line, "tourist_pitch_ca", "")
            goals_completed = self.progress_manager.get_goals_completed(line.id)
            
            # Get badges for this line
            line_badges_dict = self.progress_manager.get_line_badges(line.id)
            badges = []
            for badge_id, unlocked in line_badges_dict.items():
                if unlocked and badge_id in BADGE_DEFINITIONS:
                    badge_def = BADGE_DEFINITIONS[badge_id]
                    badges.append({
                        "icon": badge_def["icon"],
                        "name": badge_def["name"]
                    })
            
            card = LineCard(
                line_id=line.id,
                line_color_hex=line.color,
                endpoints_text=endpoints,
                pitch_text=pitch_text,
                progress_text=progress_text,
                progress_ratio=ratio,
                badge_text=badge_text,
                completed=is_completed,
                goals_completed=goals_completed,
                badges=badges,
                on_select=self._select_line,
                daily_challenge=(line.id == daily_line_id),
                size_hint=(None, None)
            )
            self.grid.add_widget(card)
            self.cards.append(card)
        self._update_card_sizes()

    def on_pre_enter(self, *args):
        Window.bind(on_keyboard=self._on_keyboard)
        self.progress_manager.load()
        self.daily_challenge_info = get_daily_challenge(self.metro_network)
        self.daily_challenge_line_id = self.daily_challenge_info.get("line_id") if self.daily_challenge_info else None
        self._build_cards()

    def on_pre_leave(self, *args):
        Window.unbind(on_keyboard=self._on_keyboard)

    def _select_line(self, line_id):
        if not self.manager:
            return
        game_screen = self.manager.get_screen(SCREEN_GAME)
        if hasattr(game_screen, "set_line_id"):
            game_screen.set_line_id(line_id)
        self.app_context.set_line(line_id)
        self.manager.transition = FadeTransition(duration=0.25)
        self.manager.current = SCREEN_GAME

    def _go_back(self, *args):
        if self.manager:
            self.manager.transition = FadeTransition(duration=0.25)
            self.manager.current = SCREEN_COVER

    def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
        if key == 27:
            self._go_back()
            return True
        return False


def build_proxima_parada_root(practice_mode=False, direction_mode=False, random_seed=None, civic_mode=False):
    cp("entered build_proxima_parada_root()")
    
    cp("creating AppContext")
    app_context = AppContext()
    cp("calling app_context.load_all()")
    app_context.load_all()
    cp("app_context.load_all() completed")
    
    cp("getting daily challenge")
    daily_challenge_info = get_daily_challenge(app_context.metro_network)
    
    cp("creating ScreenManager")
    manager = ScreenManager(transition=FadeTransition(duration=0.35))
    
    cp("adding CoverScreen")
    manager.add_widget(CoverScreen(
        name=SCREEN_COVER,
        app_context=app_context,
        daily_challenge_info=daily_challenge_info
    ))
    
    cp("adding LineSelectScreen")
    manager.add_widget(LineSelectScreen(
        name=SCREEN_LINES,
        app_context=app_context,
        daily_challenge_info=daily_challenge_info
    ))
    
    cp("adding GameScreen")
    manager.add_widget(GameScreen(
        name=SCREEN_GAME,
        random_seed=random_seed,
        app_context=app_context,
        civic_mode=civic_mode
    ))
    
    cp("setting manager.current to SCREEN_COVER")
    manager.current = SCREEN_COVER
    
    cp("exiting build_proxima_parada_root(), returning manager")
    return manager

