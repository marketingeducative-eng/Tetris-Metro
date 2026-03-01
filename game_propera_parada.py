"""
Juego 'Pròxima Parada' - Metro de Barcelona
El jugador debe seleccionar la próxima estación antes de que el tren llegue.

Refactored into three components:
- GameState: Pure game logic and state management
- Renderer: UI rendering and visual updates
- InputController: Event handling and input validation
"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image, AsyncImage
from kivy.uix.scatterlayout import ScatterLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.core.text import Label as CoreLabel
import random
import json
import math
from pathlib import Path
import time

from line_map_view import LineMapView
from train_sprite import TrainSprite


def cp(msg):
    print(f"✅ CP: {msg}", flush=True)
from station_token import StationToken
from data.metro_loader import load_metro_network, normalize_station_id
from core.audio import AudioService, AudioEvent
from core.tts import speak
from core.settings import SettingsManager
from core.progress import ProgressManager
from core.events import EventRegistry
from core.engine import GameEngine
from core.modes import FreeMode, GoalMode, SurvivalMode
from core.badges import BADGE_DEFINITIONS
from core.theme_modernisme import draw_modernisme_frame
import config as app_config
# from core.i18n import t, set_language, get_language  # Reserved for future multilingual support
from ui.screens import build_proxima_parada_root
from ui.routes import SCREEN_COVER, SCREEN_LINES, SCREEN_GAME

# ===========================
# TAG-TO-ICON MAPPING
# ===========================

def get_station_icon(tags):
    """
    Map tourist station tags to representative emoji/icon.
    Returns the first matching icon based on tag priority.
    
    Args:
        tags (list): List of tag strings from tourist_ca.json
        
    Returns:
        str: Emoji/icon representing the station's theme
    """
    if not tags:
        return "🏛️"  # Default icon
    
    # Priority mapping - first match wins
    tag_to_icon = {
        # Iconic landmarks
        "Gaudi": "🎨",
        "Park_Guell": "🏞️",
        "Camp_Nou": "⚽",
        "Sagrada_Familia": "⛪",
        
        # Architecture & culture
        "modernisme": "🏛️",
        "arquitectura": "🏗️",
        "monument": "🗿",
        "Gotic": "🏰",
        "historia": "📜",
        "cultura": "🎭",
        "museus": "🖼️",
        "teatres": "🎪",
        
        # Beach & maritime
        "platja": "🏖️",
        "mar": "🌊",
        "port": "⛵",
        "maritim": "🚢",
        "olimpic": "🏅",
        
        # Nature & parks
        "Montjuic": "⛰️",
        "jardins": "🌳",
        "miradors": "👁️",
        "Pedralbes": "🌿",
        
        # Urban life
        "Rambla": "🚶",
        "shopping": "🛍️",
        "mercat": "🥘",
        "tapes": "🍷",
        "restaurants": "🍽️",
        "barri": "🏘️",
        "passeig": "🚶‍♂️",
        
        # Transit & connections
        "centre": "🎯",
        "connexions": "🚇",
        "trens": "🚄",
        "aeroport": "✈️",
        "hub": "🔄",
        
        # Events & business
        "fires": "🎪",
        "congressos": "🏢",
        "futbol": "⚽",
        "esports": "🏃",
        
        # Other
        "nit": "🌙",
        "fotos": "📷",
        "disseny": "✨",
        "modern": "🏙️",
        "elegant": "💎",
        "campus": "🎓",
        "local": "🏠",
        "encant": "💫",
        "futur": "🚀",
    }
    
    # Return first matching icon
    for tag in tags:
        if tag in tag_to_icon:
            return tag_to_icon[tag]
    
    # Default fallback
    return "📍"


# ===========================
# GAME STATE (Logic Layer)
# ===========================

class GameState(GameEngine):
    """Alias for GameEngine to preserve existing usage."""
    pass


# ===========================
# RENDERER (UI Layer)
# ===========================

class Renderer:
    """Handles all UI rendering and visual updates"""
    
    def __init__(self, parent_widget, game_state, civic_mode=False):
        self.parent = parent_widget
        self.state = game_state
        self.civic_mode = civic_mode
        
        # UI components
        self.line_view = None
        self.train = None
        self.token_container = None
        self.tokens = []
        self.direction_indicator = None
        self.ui_font = "Roboto"
        
        # Labels
        self.next_station_label = None
        self.station_description_label = None
        self.score_label = None  # Large prominent score display
        self.streak_label = None  # Animated streak display
        self.info_label = None  # Other info (lives, progress)
        self.feedback_label = None
        
        # Progress bar
        self.progress_bar_bg = None  # Background widget
        self.progress_bar_fill = None  # Animated fill widget
        self.progress_bar_pivot = None  # Container for progress bar
        
        # Animation tracking
        self.previous_streak = 0
        
        # Event tracking - for cleanup between rounds
        self.events = EventRegistry()
        self._progress_animation = None  # Track progress bar animation
        self._color_animation = None  # Track HUD color transition animation
        
        # Overlays
        self.tutorial_overlay = None
        self.settings_overlay = None
        self.tourist_overlay = None
        self.cultural_micro_overlay = None
        self.journey_overlay = None
        self.line_completed_overlay = None
        self.onboarding_overlay = None
        self.civic_splash_overlay = None
        self.descobreix_overlay = None
        self._line_completed_pulse_event = None
        
        # Overlay scheduled events (for cleanup)
        self._tutorial_dismiss_event = None
        self._arrival_banner = None
        self._camera_shake_event = None
        self._vocab_dismiss_event = None
        self._vocab_last_id = None
        self._cultural_micro_event = None
        self._share_card_event = None
        self._last_unlocked_badge_id = None
        self._arrival_brake_event = None
        self._arrival_brake_played = False
        self._last_station_announcement_time = 0.0
        self._feedback_flash = None
        self._particle_layer = None
        self._streak_trail_active = False
        self._streak_tint_active = False
        self._score_anim_event = None
        self._displayed_score = 0
        
        # Audio service
        self.audio = AudioService()

        # Vocabulary progression (Catalan survival words)
        self.vocab_entries = self._load_vocab_data()
        self.vocab_queue = self._build_vocab_queue()
        self.learned_vocab = []
        self.learned_vocab_ids = set()
        self.vocab_overlay = None
        
        # Load tourist data
        self.tourist_data = self._load_tourist_data()
    
    def _log_overlay(self, action, overlay_name):
        """Debug log for overlay lifecycle events"""
        print(f"[Overlay] {action}: {overlay_name}")
    
    def _cleanup_overlay(self, overlay_name):
        """Safely cleanup an overlay and its resources
        
        Args:
            overlay_name (str): Name of overlay attribute (e.g., 'tutorial_overlay')
        """
        overlay = getattr(self, overlay_name, None)
        if not overlay:
            return
        
        self._log_overlay("Cleanup", overlay_name)
        
        # Stop all animations on overlay
        Animation.stop_all(overlay)
        
        # Remove from parent
        if overlay in self.parent.children:
            self.parent.remove_widget(overlay)
        
        # Clear reference
        setattr(self, overlay_name, None)
        
        # Clear related events based on overlay type
        if overlay_name == 'tutorial_overlay' and self._tutorial_dismiss_event:
            self._tutorial_dismiss_event.cancel()
            self._tutorial_dismiss_event = None
        elif overlay_name == 'line_completed_overlay' and self._line_completed_pulse_event:
            self._line_completed_pulse_event.cancel()
            self._line_completed_pulse_event = None
        elif overlay_name == 'cultural_micro_overlay' and self._cultural_micro_event:
            self._cultural_micro_event.cancel()
            self._cultural_micro_event = None
    
    def _load_tourist_data(self):
        """Load tourist information from tourist_ca.json"""
        try:
            tourist_path = Path(__file__).parent / "data" / "tourist_ca.json"
            with open(tourist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('stations', {})
        except Exception as e:
            print(f"Could not load tourist data: {e}")
            return {}

    def _load_vocab_data(self):
        """Load vocabulary progression data from vocab_ca.json"""
        try:
            vocab_path = Path(__file__).parent / "data" / "vocab_ca.json"
            with open(vocab_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('entries', [])
        except Exception as e:
            print(f"Could not load vocab data: {e}")
            return []

    def _build_vocab_queue(self):
        """Build a shuffled queue of vocabulary entries"""
        queue = list(self.vocab_entries)
        random.shuffle(queue)
        return queue

    def _select_vocab_entry(self):
        """Select next vocab entry with spaced repetition"""
        if not self.vocab_entries:
            return None, False

        is_review = False
        if self.learned_vocab and random.random() < 0.3:
            is_review = True
            entry = random.choice(self.learned_vocab)
            if len(self.learned_vocab) > 1 and entry.get('id') == self._vocab_last_id:
                entry = random.choice([e for e in self.learned_vocab if e.get('id') != self._vocab_last_id])
            return entry, is_review

        if not self.vocab_queue:
            self.vocab_queue = self._build_vocab_queue()

        if not self.vocab_queue:
            return None, False

        entry = self.vocab_queue.pop(0)
        entry_id = entry.get('id')
        if entry_id and entry_id not in self.learned_vocab_ids:
            self.learned_vocab.append(entry)
            self.learned_vocab_ids.add(entry_id)
        return entry, is_review

    def show_vocab_on_arrival(self):
        """Display a vocabulary card on station arrival"""
        if self.tourist_overlay or self.onboarding_overlay or self.line_completed_overlay:
            return

        entry, is_review = self._select_vocab_entry()
        if not entry:
            return

        self._show_vocab_card(entry, is_review)

    def _show_vocab_card(self, entry, is_review=False):
        """Render a minimal vocab card with pronunciation button"""
        if self.vocab_overlay and self.vocab_overlay in self.parent.children:
            self.parent.remove_widget(self.vocab_overlay)
        self.vocab_overlay = None

        if self._vocab_dismiss_event:
            self._vocab_dismiss_event.cancel()
            self._vocab_dismiss_event = None

        overlay = FloatLayout(size_hint=(1, 1))
        self._apply_overlay_vignette(overlay, base_alpha=0.28, edge_alpha=0.48, edge_ratio=0.07)

        panel = FloatLayout(
            size_hint=(None, None),
            size=(440, 170),
            pos_hint={'right': 0.98, 'y': 0.08}
        )

        with panel.canvas.before:
            draw_modernisme_frame(
                panel.canvas.before,
                pos=panel.pos,
                size=panel.size,
                radius=14,
                pattern=False,
                civic_mode=self._is_civic_mode()
            )

        def update_panel_bg(*args):
            panel.canvas.before.clear()
            with panel.canvas.before:
                draw_modernisme_frame(
                    panel.canvas.before,
                    pos=panel.pos,
                    size=panel.size,
                    radius=14,
                    pattern=False,
                    civic_mode=self._is_civic_mode()
                )
        panel.bind(pos=update_panel_bg, size=update_panel_bg)

        badge_label = Label(
            text="Revisio" if is_review else "Paraula nova",
            font_size='13sp',
            bold=True,
            color=(0.75, 0.82, 0.9, 1),
            size_hint=(1, None),
            height=20,
            pos_hint={'center_x': 0.5, 'top': 0.98}
        )
        panel.add_widget(badge_label)

        word_label = Label(
            text=entry.get('word', ''),
            font_size='30sp',
            bold=True,
            size_hint=(1, None),
            height=44,
            pos_hint={'center_x': 0.5, 'top': 0.86},
            color=(0.95, 0.97, 1.0, 1)
        )
        panel.add_widget(word_label)

        sentence_label = Label(
            text=entry.get('sentence', ''),
            font_size='15sp',
            size_hint=(0.9, None),
            height=54,
            pos_hint={'center_x': 0.5, 'center_y': 0.46},
            color=(0.75, 0.8, 0.9, 1),
            halign='center',
            valign='middle',
            italic=True
        )
        sentence_label.text_size = (panel.width * 0.85, 54)
        panel.add_widget(sentence_label)

        speak_button = Button(
            text="🔊 Pronuncia",
            size_hint=(None, None),
            size=(140, 34),
            pos_hint={'center_x': 0.5, 'y': 0.08},
            font_size='14sp'
        )
        self._style_overlay_button(speak_button, variant="secondary", font_size='14sp')
        self._bind_button_feedback(speak_button)
        speak_button.bind(on_release=lambda *args: speak(entry.get('word', '')))
        panel.add_widget(speak_button)

        overlay.add_widget(panel)
        overlay.opacity = 0
        Animation(opacity=1, duration=0.2, transition='out_quad').start(overlay)

        self.vocab_overlay = overlay
        self.parent.add_widget(overlay)
        self._vocab_last_id = entry.get('id')

        def dismiss(dt):
            if self.vocab_overlay != overlay:
                return
            anim = Animation(opacity=0, duration=0.2, transition='in_quad')

            def remove_card(*args):
                if overlay in self.parent.children:
                    self.parent.remove_widget(overlay)
                if self.vocab_overlay == overlay:
                    self.vocab_overlay = None
            anim.bind(on_complete=lambda *args: remove_card())
            anim.start(overlay)

        self._vocab_dismiss_event = self.schedule_event(dismiss, 3.0)
    
    def get_tourist_recommendations(self, limit=3):
        """
        Get tourist recommendations from the current line's stations.
        Returns stations sorted by distance, then priority, then completion.
        
        Args:
            limit (int): Number of recommendations to return (default: 3)
            
        Returns:
            list: List of dicts with 'station', 'station_id', 'icon', 'one_liner', 'tip', 'tags', 'distance'
        """
        recommendations = []
        current_index = self.state.current_index
        completed_ids = set()
        if hasattr(self.parent, "progress_manager") and self.parent.progress_manager:
            try:
                completed_ids = set(self.parent.progress_manager.get_completed_station_ids(self.state.line.id))
            except Exception:
                completed_ids = set()
        
        stations = self.state.get_recommendations() if hasattr(self.state, 'get_recommendations') else self.state.line.stations

        # Iterate through stations in the line
        for station in stations:
            idx = self.state.line.get_station_index(station.name)
            if idx is None:
                continue
            station_id = normalize_station_id(station.name)
            if station_id in self.tourist_data:
                tourist_info = self.tourist_data[station_id]
                
                # Only include highlighted stations with priority >= 3
                if tourist_info.get('highlight', False) and tourist_info.get('priority', 0) >= 3:
                    tags = tourist_info.get('tags', [])
                    distance = abs(idx - current_index)
                    
                    completed_flag = 1 if station_id in completed_ids else 0
                    recommendations.append({
                        'station': station.name,
                        'station_id': station_id,
                        'station_index': idx,
                        'icon': get_station_icon(tags),
                        'one_liner': tourist_info.get('one_liner_ca', ''),
                        'tip': tourist_info.get('tip_ca', ''),
                        'tags': tags,
                        'priority': tourist_info.get('priority', 0),
                        'distance': distance,
                        'completed': completed_flag
                    })
        
        # Sort by distance (ascending), then priority (descending), then completion
        # This shows closest tourist spots first
        recommendations.sort(key=lambda x: (x['distance'], -x['priority'], x['completed']))
        return recommendations[:limit]
        
    def setup_all(self):
        """Setup all UI components"""
        self._setup_background()
        self._setup_line_view()
        self._setup_train()
        self._setup_hud()
        self._setup_token_area()
    
    def _setup_background(self):
        """Urban dark gradient background with subtle depth"""
        with self.parent.canvas.before:
            # Base dark layer
            Color(0.04, 0.05, 0.07, 1)
            self.bg_base = Rectangle(pos=self.parent.pos, size=self.parent.size)
            
            # Subtle top-to-bottom gradient effect (3 layers)
            # Top layer (slightly lighter for depth)
            Color(0.09, 0.1, 0.14, 0.45)
            self.bg_top = Rectangle(
                pos=self.parent.pos,
                size=(self.parent.width, self.parent.height * 0.35)
            )
            
            # Middle radial glow (very subtle, centered)
            Color(0.07, 0.09, 0.12, 0.55)
            self.bg_center = Rectangle(
                pos=(self.parent.x + self.parent.width * 0.15, 
                     self.parent.y + self.parent.height * 0.3),
                size=(self.parent.width * 0.7, self.parent.height * 0.4)
            )
            
            # Bottom darkening (vignette effect)
            Color(0.02, 0.03, 0.05, 0.65)
            self.bg_bottom = Rectangle(
                pos=self.parent.pos,
                size=(self.parent.width, self.parent.height * 0.25)
            )
        
        self.parent.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        """Update background layers on resize"""
        self.bg_base.pos = self.parent.pos
        self.bg_base.size = self.parent.size
        
        # Top layer
        self.bg_top.pos = (self.parent.x, 
                          self.parent.y + self.parent.height * 0.65)
        self.bg_top.size = (self.parent.width, self.parent.height * 0.35)
        
        # Center glow
        self.bg_center.pos = (self.parent.x + self.parent.width * 0.15,
                             self.parent.y + self.parent.height * 0.3)
        self.bg_center.size = (self.parent.width * 0.7, self.parent.height * 0.4)
        
        # Bottom layer
        self.bg_bottom.pos = self.parent.pos
        self.bg_bottom.size = (self.parent.width, self.parent.height * 0.25)
    
    def _setup_line_view(self):
        """LineMapView centrado verticalmente"""
        self.line_view = LineMapView(
            size_hint=(None, None),
            size=(140, 550),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.line_view.set_line(
            line_id=self.state.line.id,
            line_color_hex=self.state.line.color,
            station_names=[s.name for s in self.state.line.stations]
        )
        self.parent.add_widget(self.line_view)

        self.direction_indicator = Label(
            text="",
            font_size='16sp',
            bold=True,
            size_hint=(None, None),
            size=(260, 28),
            color=(0.9, 0.9, 0.95, 0),
            halign='left',
            valign='middle',
            font_name=self.ui_font
        )
        self.direction_indicator.bind(
            size=lambda instance, value: setattr(instance, 'text_size', value)
        )
        self.parent.add_widget(self.direction_indicator)
        self._update_direction_indicator()
    
    def _setup_train(self):
        """Tren animado"""
        self.train = TrainSprite(
            size_hint=(None, None),
            size=(65, 32)
        )
        self.train.set_path(self.line_view)
        self.parent.add_widget(self.train)
        
        # Posicionar en el primer nodo
        x, y = self.line_view.get_node_pos(0)
        self.train.train_x = x
        self.train.train_y = y
    
    def _setup_hud(self):
        """HUD: minimal mobile-first layout"""
        self.hud_panel = Widget(size_hint=(1, None))
        self.hud_panel.height = 90
        self.hud_panel.pos_hint = {'top': 1, 'center_x': 0.5}

        self.hud_color = [0, 0, 0, 0.35]

        def update_panel_bg(instance, value):
            self.hud_panel.canvas.before.clear()
            with self.hud_panel.canvas.before:
                panel_pos = (self.parent.x, self.parent.height - self.hud_panel.height)
                panel_size = (self.parent.width, self.hud_panel.height)
                draw_modernisme_frame(
                    self.hud_panel.canvas.before,
                    pos=panel_pos,
                    size=panel_size,
                    radius=12,
                    pattern=False,
                    civic_mode=self._is_civic_mode()
                )
                Color(0.18, 0.2, 0.24, 0.55)
                Rectangle(
                    pos=(panel_pos[0] + 16, panel_pos[1] + panel_size[1] - 12),
                    size=(panel_size[0] - 32, 1)
                )
                # Subtle iron accent
                Color(0.1, 0.12, 0.14, 0.55)
                Rectangle(
                    pos=(panel_pos[0] + panel_size[0] * 0.08, panel_pos[1] + panel_size[1] - 6),
                    size=(panel_size[0] * 0.84, 1.2)
                )

        self.update_hud_panel_bg = update_panel_bg
        self.parent.bind(size=update_panel_bg, pos=update_panel_bg)
        update_panel_bg(None, None)
        self.parent.add_widget(self.hud_panel)

        title_text = "PRÒXIMA PARADA"
        if not self._is_civic_mode():
            if getattr(self.state, "mode_name", ""):
                title_text += f" [{self.state.mode_name}]"
            if self.state.practice_mode:
                title_text += " [PRÀCTICA]"
            if self.state.direction_mode:
                title_text += " [DIRECCIÓ]"

        self.title_label = Label(
            text="",
            font_size='16sp',
            bold=True,
            size_hint=(1, None),
            height=0,
            pos_hint={'top': 1},
            color=(0.3, 0.9, 0.5, 0),
            font_name=self.ui_font
        )
        self.parent.add_widget(self.title_label)

        self.direction_label = Label(
            text="",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=24,
            pos_hint={'center_x': 0.5, 'top': 0.91},
            color=(1, 0.9, 0.3, 0),
            italic=True,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.direction_label)

        self.goal_label = Label(
            text="",
            font_size='16sp',
            bold=True,
            size_hint=(1, None),
            height=0,
            pos_hint={'top': 0.95},
            color=(1, 0.85, 0.2, 0),
            italic=True,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.goal_label)

        self.distance_label = Label(
            text="",
            font_size='14sp',
            bold=True,
            size_hint=(1, None),
            height=0,
            pos_hint={'top': 0.93},
            color=(0.9, 0.9, 0.95, 0),
            italic=False,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.distance_label)

        self.direction_guidance_label = Label(
            text="",
            font_size='14sp',
            size_hint=(1, None),
            height=0,
            pos_hint={'top': 0.91},
            color=(0.7, 0.9, 1.0, 0),
            italic=True,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.direction_guidance_label)

        self.minimal_hud = True
        self._update_goal_label()

        self.next_station_label = Label(
            text="",
            font_size='40sp',
            bold=True,
            size_hint=(1, None),
            height=64,
            pos_hint={'top': 0.965},
            color=(1, 1, 1, 1),
            font_name=self.ui_font
        )
        self.parent.add_widget(self.next_station_label)

        self.station_description_label = Label(
            text="",
            font_size='14sp',
            size_hint=(1, None),
            height=0,
            pos_hint={'top': 0.90},
            color=(0.6, 0.7, 0.8, 0),
            italic=True,
            max_lines=2,
            shorten=True,
            shorten_from='right',
            font_name=self.ui_font
        )
        self.station_description_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None))
        )
        self.parent.add_widget(self.station_description_label)

        score_text = "Paraules: 0" if self._is_civic_mode() else "0"
        score_color = self._theme_color((0.9, 0.92, 0.95, 1), (0.75, 0.8, 0.85, 1))
        self.score_label = Label(
            text=score_text,
            font_size='16sp',
            bold=True,
            size_hint=(None, None),
            size=(180, 28),
            pos_hint={'x': 0.04, 'top': 0.985},
            color=score_color,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.score_label)

        streak_color = self._theme_color((1, 0.6, 0.2, 1), (0.85, 0.55, 0.3, 1))
        self.streak_label = Label(
            text="Ratxa 0",
            font_size='14sp',
            bold=True,
            size_hint=(None, None),
            size=(140, 22),
            pos_hint={'x': 0.04, 'top': 0.95},
            color=streak_color,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.streak_label)

        self.info_label = Label(
            text="",
            font_size='14sp',
            size_hint=(None, None),
            size=(1, 1),
            pos_hint={'x': 0, 'top': 0},
            color=(0.7, 0.75, 0.85, 0),
            font_name=self.ui_font
        )
        self.parent.add_widget(self.info_label)
        self.update_stats()

        self.progress_bar_pivot = Widget(
            size_hint=(0.5, None),
            height=6,
            pos_hint={'center_x': 0.5, 'top': 0.885}
        )
        self.parent.add_widget(self.progress_bar_pivot)
        
        # Progress bar background
        with self.progress_bar_pivot.canvas.before:
            Color(0.14, 0.15, 0.19, 0.9)
            self.progress_bar_bg = RoundedRectangle(
                pos=self.progress_bar_pivot.pos,
                size=self.progress_bar_pivot.size,
                radius=[4]
            )
        
        # Progress bar fill (will be animated)
        progress_glow_color = self._theme_color((0.5, 0.9, 0.8, 0.25), (0.4, 0.8, 0.7, 0.22))
        progress_fill_color = self._theme_color((0.4, 0.85, 0.75, 0.95), (0.35, 0.7, 0.6, 0.9))
        with self.progress_bar_pivot.canvas:
            Color(*progress_glow_color)
            self.progress_bar_glow = RoundedRectangle(
                pos=(self.progress_bar_pivot.x - 2, self.progress_bar_pivot.y - 2),
                size=(0, self.progress_bar_pivot.height + 4),
                radius=[6]
            )
            Color(*progress_fill_color)
            self.progress_bar_fill = RoundedRectangle(
                pos=self.progress_bar_pivot.pos,
                size=(0, self.progress_bar_pivot.height),
                radius=[4]
            )
        
        # Bind progress bar to updates
        def update_progress_bar_bg(instance, value):
            self.progress_bar_bg.pos = self.progress_bar_pivot.pos
            self.progress_bar_bg.size = self.progress_bar_pivot.size
            if hasattr(self, 'progress_bar_glow'):
                self.progress_bar_glow.pos = (self.progress_bar_pivot.x - 2, self.progress_bar_pivot.y - 2)
            if hasattr(self, 'progress_bar_fill'):
                self.progress_bar_fill.pos = self.progress_bar_pivot.pos
        
        self.progress_bar_pivot.bind(pos=update_progress_bar_bg, size=update_progress_bar_bg)
        
        # Initial progress bar update
        self._update_progress_display()
        
        self.feedback_label = Label(
            text="",
            font_size='28sp',
            bold=True,
            color=(1, 1, 0, 0),
            size_hint=(1, None),
            height=0,
            pos_hint={'center_y': 0.5},
            font_name=self.ui_font
        )
        self.parent.add_widget(self.feedback_label)

        self.zone_label = Label(
            text="",
            font_size='22sp',
            bold=True,
            color=(0.3, 0.8, 0.95, 0),
            size_hint=(1, None),
            height=0,
            pos_hint={'center_y': 0.4},
            italic=True,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.zone_label)

        self.intro_banner = Label(
            text="",
            font_size='28sp',
            bold=True,
            color=(0.3, 0.9, 0.5, 0),
            size_hint=(1, None),
            height=0,
            pos_hint={'center_y': 0.5},
            italic=False,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.intro_banner)

        self.civic_footer = Label(
            text="Barcelona t’acull" if self._is_civic_mode() else "",
            font_size='11sp',
            size_hint=(1, None),
            height=0,
            pos_hint={'center_x': 0.5, 'y': 0.005},
            color=(0.45, 0.5, 0.55, 0),
            italic=True,
            font_name=self.ui_font
        )
        self.parent.add_widget(self.civic_footer)

        self.first_day_progress_label = Label(
            text="",
            font_size='22sp',
            bold=True,
            size_hint=(1, None),
            height=0,
            pos_hint={'center_y': 0.075},
            color=(0.95, 0.85, 0.3, 0),
            halign='center',
            font_name=self.ui_font
        )
        self.parent.add_widget(self.first_day_progress_label)
        self._update_first_day_progress()
    
    def _setup_token_area(self):
        """Área inferior para tokens"""
        self.token_container = Widget(
            size_hint=(1, None),
            height=180,
            pos_hint={'y': 0.02}
        )
        self.parent.add_widget(self.token_container)

        self.combo_bar_pivot = Widget(
            size_hint=(0.55, None),
            height=6,
            pos_hint={'center_x': 0.5, 'y': 0.22}
        )
        self.parent.add_widget(self.combo_bar_pivot)
        if getattr(self, 'minimal_hud', False):
            self.combo_bar_pivot.height = 0
            self.combo_bar_pivot.opacity = 0

        with self.combo_bar_pivot.canvas.before:
            Color(0.18, 0.2, 0.26, 0.9)
            self.combo_bar_bg = RoundedRectangle(
                pos=self.combo_bar_pivot.pos,
                size=self.combo_bar_pivot.size,
                radius=[4]
            )

        # Combo bar fill with themed color
        combo_fill_color = self._theme_color((0.95, 0.75, 0.35, 1), (0.75, 0.6, 0.4, 1))
        with self.combo_bar_pivot.canvas:
            Color(*combo_fill_color)
            self.combo_bar_fill = Rectangle(
                pos=self.combo_bar_pivot.pos,
                size=(0, self.combo_bar_pivot.height)
            )

        def update_combo_bar_bg(instance, value):
            self.combo_bar_bg.pos = self.combo_bar_pivot.pos
            self.combo_bar_bg.size = self.combo_bar_pivot.size

        self.combo_bar_pivot.bind(pos=update_combo_bar_bg, size=update_combo_bar_bg)

    def update_title(self):
        """Update HUD title to reflect current mode and settings."""
        if not hasattr(self, 'title_label') or not self.title_label:
            return
        self.title_label.text = ""
        self.title_label.color = (0.3, 0.9, 0.5, 0)
        self._update_direction_indicator()
    
    def update_stats(self):
        """Update HUD with refactored layout: dominant score, animated streak, clean info"""
        if self._is_civic_mode():
            words_learned = len(self.learned_vocab_ids)
            self._animate_score(words_learned, prefix="Paraules: ")
            # Apply themed streak color for civic mode
            self.streak_label.color = self._theme_color((1, 0.6, 0.2, 1), (0.85, 0.55, 0.3, 1))
            self.info_label.text = ""
        else:
            # Update score - large and prominent
            self._animate_score(self.state.score)

            # Update streak with animation when it increases
            current_streak = self.state.streak
            self.streak_label.text = f"Ratxa {current_streak}"

            # Detect streak increase and animate
            if current_streak > self.previous_streak and current_streak > 0:
                self._animate_streak_highlight()
            self.previous_streak = current_streak

            self.info_label.text = ""

        if self.state.direction_mode:
            terminal = self.state.get_direction_terminal()
            if terminal:
                self.direction_label.text = f"Direccio: {terminal}"
                self.direction_label.color = (0.9, 0.9, 0.95, 1)
            else:
                self.direction_label.text = ""
                self.direction_label.color = (0.9, 0.9, 0.95, 0)
        else:
            self.direction_label.text = ""
            self.direction_label.color = (0.9, 0.9, 0.95, 0)

        self._apply_streak_visuals(self.state.streak)
        self._update_combo_bar(self.state.streak)
        
        # Update goal-related UI if in goal mode
        if self.state.goal_mode:
            self._update_distance_label()
            if self.state.direction_mode:
                self._update_direction_guidance()
            
            # Show micro-narrative messages
            self._show_proximity_message()
    
    def _update_goal_label(self):
        """Update the goal indicator label if in goal mode"""
        if not hasattr(self, 'goal_label'):
            return

        minimal_hud = getattr(self, 'minimal_hud', False)
        
        if self.state.goal_mode and self.state.goal_station_id:
            # Find the station name from the normalized ID
            goal_station_name = None
            goal_index = -1
            for idx, station in enumerate(self.state.line.stations):
                if normalize_station_id(station.name) == self.state.goal_station_id:
                    goal_station_name = station.name
                    goal_index = idx
                    break
            
            if goal_station_name:
                self.goal_label.text = "" if minimal_hud else f"⭐ Objectiu: {goal_station_name}"
                # Set goal marker on line map
                if self.line_view:
                    self.line_view.goal_index = goal_index
                
                # Update distance counter
                self._update_distance_label()

                # Update direction guidance (only if direction mode)
                if self.state.direction_mode:
                    self._update_direction_guidance()
            else:
                self.goal_label.text = ""
                if self.line_view:
                    self.line_view.goal_index = -1
                self._clear_goal_ui()
        else:
            self.goal_label.text = ""
            if self.line_view:
                self.line_view.goal_index = -1
            self._clear_goal_ui()
    
    def _update_distance_label(self):
        """Update distance-to-goal label"""
        if not hasattr(self, 'distance_label'):
            return
        if getattr(self, 'minimal_hud', False):
            self.distance_label.text = ""
            return
        
        distance = self.state.get_distance_to_goal()
        
        if distance is None:
            self.distance_label.text = ""
            return
        
        if distance == 0:
            self.distance_label.text = "Objectiu arribat!"
            self.distance_label.color = (0.3, 1.0, 0.4, 1)  # Green
        elif distance <= 3:
            # Close to goal - amber/orange
            self.distance_label.text = f"Ja només falten {distance} parades"
            self.distance_label.color = (1.0, 0.7, 0.2, 1)  # Amber
        else:
            # Normal distance
            self.distance_label.text = f"Falten {distance} parades per arribar a l’objectiu"
            self.distance_label.color = (0.9, 0.9, 0.95, 1)  # Light gray
    
    def _update_direction_guidance(self):
        """Update direction guidance arrow"""
        if not hasattr(self, 'direction_guidance_label'):
            return
        if getattr(self, 'minimal_hud', False):
            self.direction_guidance_label.text = ""
            return
        
        direction_info = self.state.get_goal_direction_indicator()
        
        if direction_info:
            arrow, text = direction_info
            self.direction_guidance_label.text = f"{arrow} Direcció: {text}"
        else:
            self.direction_guidance_label.text = ""
    
    def _clear_goal_ui(self):
        """Clear all goal-related UI elements"""
        if hasattr(self, 'distance_label'):
            self.distance_label.text = ""
        if hasattr(self, 'direction_guidance_label'):
            self.direction_guidance_label.text = ""
    
    def _show_proximity_message(self):
        """Show micro-narrative messages based on distance to goal"""
        if not self.state.goal_mode:
            return
        
        distance = self.state.get_distance_to_goal()
        
        if distance == 3:
            # Show "almost there" message
            self.show_feedback("Ja gairebé hi ets!", (1.0, 0.85, 0.2, 1), 1.5)
        elif distance == 1:
            # Show "next stop is goal" message
            self.show_feedback("La propera parada és l’objectiu!", (1.0, 0.9, 0.3, 1), 2.0)
            # Play anticipation sound
            self.audio.play_goal_anticipation_sound()
    
    def _update_first_day_progress(self):
        """Update First Day Mode progress indicator with dots"""
        if not hasattr(self, 'first_day_progress_label'):
            return
        
        if not self.state.first_day_mode:
            self.first_day_progress_label.text = ""
            return
        
        # Build dot indicator: [● ○ ○ ○ ○]
        total_stops = len(self.state.first_day_route)
        current_step = self.state.first_day_progress
        
        # Create dots: filled (●) for completed, empty (○) for remaining
        dots = []
        for i in range(total_stops):
            if i < current_step:
                dots.append("●")  # Completed
            else:
                dots.append("○")  # Not yet reached
        
        # Add journey title
        progress_text = f"El teu primer dia a Barcelona  [{' '.join(dots)}]"
        self.first_day_progress_label.text = progress_text
    
    def _update_progress_display(self):
        """Update progress bar fill with smooth animation"""
        if not self.progress_bar_fill or not self.progress_bar_pivot:
            return
        
        # Calculate progress percentage
        total_stations = len(self.state.line.stations)
        progress_ratio = self.state.current_index / total_stations if total_stations > 0 else 0
        # Calculate target width (progress bar is 60% of screen width)
        bar_width = self.progress_bar_pivot.width * progress_ratio if self.progress_bar_pivot.width > 0 else 0
        
        from kivy.animation import Animation

        if hasattr(self, '_progress_fill_anim') and self._progress_fill_anim:
            self._progress_fill_anim.cancel(self.progress_bar_fill)
        if hasattr(self, '_progress_glow_anim') and self._progress_glow_anim:
            self._progress_glow_anim.cancel(self.progress_bar_glow)

        self._progress_fill_anim = Animation(
            width=bar_width,
            duration=0.55,
            transition='in_out_quad'
        )
        self._progress_fill_anim.start(self.progress_bar_fill)

        if hasattr(self, 'progress_bar_glow'):
            glow_width = max(0, bar_width + 4)
            self._progress_glow_anim = Animation(
                width=glow_width,
                duration=0.55,
                transition='in_out_quad'
            )
            self._progress_glow_anim.start(self.progress_bar_glow)

    def _update_combo_bar(self, streak_value):
        """Update compact combo bar based on current streak."""
        if not getattr(self, 'combo_bar_fill', None) or not self.combo_bar_pivot:
            return

        streak_cap = 8
        ratio = min(streak_value, streak_cap) / float(streak_cap)
        target_width = self.combo_bar_pivot.width * ratio if self.combo_bar_pivot.width > 0 else 0

        if hasattr(self, '_combo_animation') and self._combo_animation:
            self._combo_animation.cancel(self.combo_bar_fill)

        self._combo_animation = Animation(
            width=target_width,
            duration=0.25,
            transition='out_quad'
        )
        self._combo_animation.start(self.combo_bar_fill)

    def _animate_score(self, target_value, prefix=""):
        """Subtle score increment animation for visual feedback."""
        if self._score_anim_event:
            try:
                self._score_anim_event.cancel()
            except Exception:
                pass
            self._score_anim_event = None

        start_value = int(self._displayed_score)
        end_value = int(target_value)
        if start_value == end_value:
            self.score_label.text = f"{prefix}{end_value}" if prefix else str(end_value)
            return

        steps = 10
        duration = 0.25
        step_time = duration / steps
        delta = (end_value - start_value) / float(steps)
        state = {'current': start_value, 'count': 0}

        def step(dt):
            state['count'] += 1
            state['current'] += delta
            value = int(round(state['current']))
            if state['count'] >= steps:
                value = end_value
            self.score_label.text = f"{prefix}{value}" if prefix else str(value)
            if state['count'] >= steps:
                self._displayed_score = end_value
                self._score_anim_event = None
                return False
            return True

        self._score_anim_event = Clock.schedule_interval(step, step_time)
    
    def update_next_station(self, station_name):
        """Actualizar display de próxima estación con descripción"""
        # Play announcement chime
        self.audio.play_station_announcement()
        
        # Large, prominent station name
        self.next_station_label.text = station_name
        
        if getattr(self, 'minimal_hud', False):
            self.station_description_label.text = ""
            return

        # Get the station description if available
        station_index = self.state.line.get_station_index(station_name)
        if station_index is not None:
            station = self.state.line.get_station(station_index)
            if station and station.description:
                self.station_description_label.text = station.description
            else:
                self.station_description_label.text = ""
        else:
            self.station_description_label.text = ""
    
    def play_round_start_sequence(self, next_station_name):
        """
        Play coordinated, non-blocking round start effects.
        
        Sequence (all non-blocking):
        - 0.0s: Announcement chime plays
        - 0.1s: Zoom to next station (smooth 0.3s animation)
        - 0.15s: Highlight upcoming node (pulse animation)
        - 0.2s: Set ambience to tunnel
        """
        # Get next station index for zoom and highlight
        next_index = self.state.line.get_station_index(next_station_name)
        if next_index is None:
            return
        
        # 0.0s: Announcement chime (simultaneous with other effects)
        self.audio.play_station_announcement()
        
        # 0.1s: Zoom to next station with smooth animation
        def zoom_to_next(*args):
            if self.line_view:
                self.line_view.zoom_to_node(next_index, zoom_factor=1.12, duration=0.3)
        
        self.schedule_event(zoom_to_next, 0.1)
        
        # 0.15s: Highlight upcoming node
        def highlight_next(*args):
            if self.line_view:
                self.line_view.highlight_node(next_index, duration=0.4)
        
        self.schedule_event(highlight_next, 0.15)
        
        # 0.2s: Set ambience to tunnel
        def set_tunnel_ambience(*args):
            self.audio.set_ambience("tunnel")
        
        self.schedule_event(set_tunnel_ambience, 0.2)
    
    def _animate_streak_highlight(self):
        """Animate streak label when it increases (scale + glow effect)"""
        from kivy.animation import Animation
        
        # Save original color
        original_color = self.streak_label.color[:]
        original_size = float(self.streak_label.font_size)
        
        # Elegant warm accent pulse
        glow_color = (0.95, 0.75, 0.45, 1)
        pulse_size = original_size + 2
        
        # Scale bounce + color pulse animation
        scale_up = Animation(
            font_size=pulse_size,
            color=glow_color,
            duration=0.2,
            transition='out_quad'
        )
        scale_down = Animation(
            font_size=original_size,
            color=original_color,
            duration=0.28,
            transition='in_out_quad'
        )
        
        # Chain animations
        (scale_up + scale_down).start(self.streak_label)
    
    def show_feedback(self, message, color, duration=1.2):
        """Mostrar feedback temporal (respects subtitles_enabled setting)"""
        if not self.state.subtitles_enabled:
            return  # Skip feedback if subtitles are disabled
        self.feedback_label.text = message
        self.feedback_label.color = color
        self.schedule_event(lambda dt: setattr(self.feedback_label, 'text', ''), duration)

    def _flash_screen(self, color, duration=0.18):
        """Flash a subtle overlay color across the screen."""
        if not self.parent:
            return
        
        # Apply theme intensity adjustment
        r, g, b, base_alpha = color
        themed_alpha = self._theme_flash_intensity(base_alpha)
        themed_color = (r, g, b, themed_alpha)
        themed_duration = self._theme_animation_duration(duration)

        overlay = Widget(size_hint=(1, 1), pos=self.parent.pos)
        with overlay.canvas.before:
            Color(*themed_color)
            rect = Rectangle(pos=overlay.pos, size=self.parent.size)

        def update_rect(*args):
            rect.pos = overlay.pos
            rect.size = overlay.size

        overlay.bind(pos=update_rect, size=update_rect)
        overlay.opacity = 0
        self.parent.add_widget(overlay)

        fade_in = Animation(opacity=0.35, duration=themed_duration * 0.35, transition='out_quad')
        fade_out = Animation(opacity=0, duration=themed_duration * 0.65, transition='in_quad')

        def cleanup(*args):
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)

        (fade_in + fade_out).bind(on_complete=lambda *args: cleanup())
        (fade_in + fade_out).start(overlay)

    def _spawn_success_particles(self, node_index):
        """Spawn a soft particle burst near the target node."""
        if not self.line_view:
            return
        node_pos = self.line_view.get_node_pos(node_index)
        if not node_pos:
            return

        origin_x, origin_y = node_pos
        container = Widget(size_hint=(1, 1))
        self.parent.add_widget(container)
        
        # Apply theme particle count
        particle_count = self._theme_particle_count(6)

        active = {'count': 0}
        for _ in range(particle_count):
            size = random.uniform(5, 9)
            particle = Widget(size_hint=(None, None), size=(size, size))
            particle.pos = (origin_x - size / 2, origin_y - size / 2)
            
            # Theme color for particles
            particle_color = self._theme_color((0.75, 0.95, 0.85, 0.8))
            with particle.canvas:
                Color(*particle_color)
                ellipse = Ellipse(pos=particle.pos, size=particle.size)

            def update_particle(*args, p=particle, e=ellipse):
                e.pos = p.pos
                e.size = p.size

            particle.bind(pos=update_particle, size=update_particle)
            container.add_widget(particle)

            angle = random.uniform(0, 6.283)
            distance = random.uniform(18, 34)
            target_x = origin_x + (distance * math.cos(angle)) - size / 2
            target_y = origin_y + (distance * math.sin(angle)) - size / 2

            active['count'] += 1
            particle.opacity = 0
            anim = Animation(opacity=0.9, duration=0.05, transition='out_quad')
            anim += Animation(pos=(target_x, target_y), opacity=0, duration=0.28, transition='out_quad')

            def on_done(*args, p=particle):
                if p in container.children:
                    container.remove_widget(p)
                active['count'] -= 1
                if active['count'] <= 0 and container in self.parent.children:
                    self.parent.remove_widget(container)

            anim.bind(on_complete=on_done)
            anim.start(particle)

    def _pulse_train_glow(self):
        """Apply a brief glow to the train."""
        if not self.train:
            return
        if hasattr(self.train, 'pulse_glow'):
            self.train.pulse_glow(duration=0.3, peak=0.35)

    def _train_vibrate(self, duration=0.12, intensity=2):
        """Quick vibration to emphasize incorrect feedback."""
        if not self.train:
            return

        original_pos = self.train.pos
        jitter = Animation(x=original_pos[0] + intensity, y=original_pos[1], duration=duration * 0.25, transition='out_quad')
        jitter += Animation(x=original_pos[0] - intensity, y=original_pos[1], duration=duration * 0.25, transition='in_out_quad')
        jitter += Animation(x=original_pos[0], y=original_pos[1], duration=duration * 0.25, transition='in_quad')
        jitter.start(self.train)

    def _apply_streak_visuals(self, streak_value):
        """Apply streak-based train effects and smooth resets."""
        if not self.train:
            return

        if streak_value >= 3:
            self.train.set_trail_intensity(0.45, duration=0.3)
            self._streak_trail_active = True
        elif self._streak_trail_active:
            self.train.set_trail_intensity(0.0, duration=0.4)
            self._streak_trail_active = False

        if streak_value >= 5:
            self.train.set_tint_strength(0.16, duration=0.35)
            self._streak_tint_active = True
        elif self._streak_tint_active:
            self.train.set_tint_strength(0.0, duration=0.45)
            self._streak_tint_active = False

    def play_success_feedback(self, node_index, streak_increased=False):
        """Play success feedback: flash, particles, glow, and audio."""
        self.animate_success(node_index)
        self._spawn_success_particles(node_index)
        self._pulse_train_glow()
        if streak_increased:
            self._animate_streak_highlight()
        self.audio.play_correct_feedback(volume=0.5, streak_rise=streak_increased)
        self._trigger_haptic(duration_ms=22)

    def play_fail_feedback(self, node_index=None, timeout=False):
        """Play fail feedback: shake, flash, vibration, and muted sound."""
        self._camera_shake(duration=0.1, intensity=3)
        self._flash_screen((0.75, 0.1, 0.1, 0.35), duration=0.2)
        self._train_vibrate(duration=0.12, intensity=2)
        self.audio.play_wrong_feedback(volume=0.28 if timeout else 0.32)
        self._trigger_haptic(duration_ms=16)
    
    def show_zone_transition(self, zone_name, duration=1.2):
        """Show zone transition message (e.g., 'Entrant a l'Eixample')"""
        self.zone_label.text = f"Entrant a {zone_name}"
        self.schedule_event(lambda dt: setattr(self.zone_label, 'text', ''), duration)
    
    def show_intro_banner(self):
        """Show animated intro banner with line name and endpoints"""
        # Get line info
        line_name = self.state.line.name
        from_station = self.state.line.endpoints['from']
        to_station = self.state.line.endpoints['to']
        
        # Set banner text
        self.intro_banner.text = f"{line_name} — {from_station} → {to_station}"
        
        # Fade in (0 to 1) over 0.5 seconds
        from kivy.animation import Animation
        fade_in = Animation(color=(0.3, 0.9, 0.5, 1), duration=0.5, transition='in_out_quad')
        
        # After fade in, wait 1 second, then fade out over 0.5 seconds
        def start_fade_out(anim, widget):
            self.schedule_event(lambda dt: self._fade_out_intro(), 1.0)
        
        fade_in.bind(on_complete=start_fade_out)
        fade_in.start(self.intro_banner)
    
    def _fade_out_intro(self):
        """Fade out intro banner"""
        from kivy.animation import Animation
        fade_out = Animation(color=(0.3, 0.9, 0.5, 0), duration=0.5, transition='in_out_quad')
        fade_out.bind(on_complete=lambda anim, widget: setattr(self.intro_banner, 'text', ''))
        fade_out.start(self.intro_banner)
    
    def shift_hud_color(self, zone_name):
        """Subtle HUD background color shift based on zone"""
        # Map zones to subtle color tints (RGBA with low opacity)
        zone_colors = {
            "Les Corts": [0.0, 0.03, 0.06, 0.85],      # Slightly blue-grey
            "Sants-Montjuïc": [0.04, 0.02, 0.0, 0.85],  # Slightly warm
            "Ciutat Vella": [0.05, 0.04, 0.0, 0.85],    # Slightly golden
            "Eixample": [0.02, 0.0, 0.04, 0.85],        # Slightly purple
            "Gràcia": [0.0, 0.04, 0.02, 0.85],          # Slightly green
            "Nou Barris": [0.03, 0.0, 0.03, 0.85]       # Slightly magenta
        }
        
        # Get color for zone, fallback to default dark
        target_color = zone_colors.get(zone_name, [0, 0, 0, 0.85])
        start_color = self.hud_color[:]
        
        # Smooth color transition over 0.6 seconds
        duration = 0.6
        steps = 30  # 30 steps for smooth transition
        step_interval = duration / steps
        
        def interpolate_step(step):
            t = step / steps  # Progress from 0 to 1
            # Ease in-out quad
            t = t * t * (3.0 - 2.0 * t)
            self.hud_color = [
                start_color[i] + (target_color[i] - start_color[i]) * t
                for i in range(4)
            ]
            self.update_hud_panel_bg(None, None)
        
        # Schedule interpolation steps
        for step in range(1, steps + 1):
            self.schedule_event(lambda dt, s=step: interpolate_step(s), step_interval * step)
    
    def show_milestone_moment(self, stations_completed):
        """Show celebration when reaching milestone (every 5 stations)"""
        # Create celebratory message
        milestone_number = stations_completed // 5
        message = f"Bon ritme! {stations_completed} estacions"
        
        # Create milestone label if not exists, or reuse feedback label
        self.feedback_label.text = message
        self.feedback_label.color = (1, 0.84, 0, 1)  # Bright gold
        
        # Store original position and size
        original_size = self.feedback_label.size
        
        # Animate: scale up, then scale down
        from kivy.animation import Animation
        scale_up = Animation(size=(original_size[0] * 1.15, original_size[1] * 1.15), 
                            duration=0.25, transition='out_cubic')
        scale_down = Animation(size=original_size, duration=0.35, transition='in_out_quad')
        
        # Chain the animations
        (scale_up + scale_down).start(self.feedback_label)
        
        # Slightly shift HUD accent color for 0.5 seconds
        accent_color = (0.2, 0.85, 1.0, 0.15)  # Cyan accent, subtle
        
        def restore_hud():
            self.update_hud_panel_bg(None, None)
        
        # Temporarily brighten HUD with canvas overlay
        from kivy.graphics import Color as CanvasColor, Line
        with self.hud_panel.canvas.after:
            CanvasColor(*accent_color)
            Line(rectangle=(self.parent.x, self.parent.height - self.hud_panel.height,
                           self.parent.width, self.hud_panel.height), width=2)
        
        # Clear accent line after duration
        self.schedule_event(lambda dt: self.hud_panel.canvas.after.clear(), 0.5)
        
        # Remove message after display
        self.schedule_event(lambda dt: setattr(self.feedback_label, 'text', ''), 1.2)

        self._show_milestone_badge_pop()

    def _show_milestone_badge_pop(self):
        """Show a small badge pop for milestone reinforcement."""
        if not self.parent or not self.score_label:
            return

        badge = Widget(size_hint=(None, None), size=(24, 24))
        badge.pos = (
            self.score_label.x + self.score_label.width + 6,
            self.score_label.y + 2
        )

        with badge.canvas:
            Color(0.9, 0.85, 0.45, 0.9)
            Ellipse(pos=badge.pos, size=badge.size)
            Color(1, 1, 1, 0.6)
            Ellipse(pos=(badge.x + 6, badge.y + 6), size=(badge.width - 12, badge.height - 12))

        def update_badge(*args):
            badge.canvas.clear()
            with badge.canvas:
                Color(0.9, 0.85, 0.45, 0.9)
                Ellipse(pos=badge.pos, size=badge.size)
                Color(1, 1, 1, 0.6)
                Ellipse(pos=(badge.x + 6, badge.y + 6), size=(badge.width - 12, badge.height - 12))

        badge.bind(pos=update_badge, size=update_badge)
        badge.opacity = 0
        self.parent.add_widget(badge)

        pop = Animation(opacity=1, duration=0.12, transition='out_quad')
        pop += Animation(opacity=0, duration=0.3, transition='in_quad')

        def cleanup(*args):
            if badge in self.parent.children:
                self.parent.remove_widget(badge)

        pop.bind(on_complete=lambda *args: cleanup())
        pop.start(badge)

    def show_integration_milestone(self, message):
        """Show a minimal integration milestone message."""
        if not self.state.subtitles_enabled:
            return
        if not self.feedback_label:
            return

        label = self.feedback_label
        original_size = label.font_size
        label.text = message
        label.font_size = '26sp'
        label.color = (0.7, 0.85, 0.95, 0)

        fade_in = Animation(color=(0.7, 0.85, 0.95, 1), duration=0.35, transition='out_quad')
        fade_out = Animation(color=(0.7, 0.85, 0.95, 0), duration=0.6, transition='in_quad')

        def restore(*args):
            label.text = ''
            label.font_size = original_size

        fade_out.bind(on_complete=lambda *args: restore())
        (fade_in + fade_out).start(label)
    
    def animate_success(self, node_index):
        """Animación de éxito en el nodo"""
        self.line_view.success_flash(node_index, duration=0.3)
    
    def animate_highlight(self, node_index):
        """Animación de resaltar nodo correcto"""
        self.line_view.highlight_node(node_index, duration=0.4)
    
    def move_train(self, target_index, duration):
        """Move train to target node and start tunnel sound"""
        # Transition into tunnel ambience during movement
        self.audio.set_ambience("tunnel")
        self._schedule_arrival_brake(duration)
        # Move the train
        self.train.move_to_node(target_index, duration=duration)
    
    def hide_tokens(self):
        """Ocultar todos los tokens"""
        for token in self.tokens:
            token.opacity = 0
    
    def clear_tokens(self):
        """Limpiar todos los tokens"""
        for token in self.tokens:
            self.token_container.remove_widget(token)
        self.tokens.clear()
    
    def show_tutorial(self, on_dismiss_callback):
        """Show tutorial overlay for 5 seconds"""
        # Prevent duplication
        if self.tutorial_overlay:
            self._log_overlay("Already showing", "tutorial_overlay")
            return
        
        self._log_overlay("Show", "tutorial_overlay")
        
        tutorial_layout = FloatLayout(size_hint=(1, 1))
        self._apply_overlay_vignette(tutorial_layout, base_alpha=0.66, edge_alpha=0.92, edge_ratio=0.09)
        
        panel_width = 500
        panel_height = 280
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=20,
                pattern=True,
                civic_mode=self._is_civic_mode()
            )
        
        title = Label(
            text="Com es juga",
            font_size='28sp',
            bold=True,
            color=self._theme_color((0.95, 0.92, 0.85, 1)),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.9}
        )
        panel.add_widget(title)

        instructions_lines = [
            "• Mira la pròxima estació",
        ]
        if self.state.direction_mode:
            instructions_lines.append("• Confirma la direcció del tren")
        instructions_lines.extend([
            "• Arrossega el token correcte",
            "• Deixa’l anar al cercle verd",
            "• Abans que arribi el tren",
        ])
        instructions_text = "\n".join(instructions_lines)
        instructions = Label(
            text=instructions_text,
            font_size='19sp',
            halign='left',
            valign='middle',
            color=(0.95, 0.95, 0.95, 1),
            size_hint=(0.9, 0.55),
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        instructions.text_size = (panel_width * 0.85, panel_height * 0.5)
        panel.add_widget(instructions)
        
        dismiss_label = Label(
            text="Toca per començar",
            font_size='16sp',
            italic=True,
            color=(0.65, 0.7, 0.78, 1),
            size_hint=(1, None),
            height=40,
            pos_hint={'center_x': 0.5, 'y': 0.05}
        )
        panel.add_widget(dismiss_label)
        
        tutorial_layout.add_widget(panel)
        
        def on_tutorial_touch(instance, touch):
            if tutorial_layout.collide_point(*touch.pos):
                on_dismiss_callback()
                return True
            return False
        tutorial_layout.bind(on_touch_down=on_tutorial_touch)
        
        self.tutorial_overlay = tutorial_layout
        self.parent.add_widget(tutorial_layout)
        
        # Schedule auto-dismiss and track event for cleanup
        self._tutorial_dismiss_event = self.schedule_event(lambda dt: on_dismiss_callback(), 5.0)
    
    def dismiss_tutorial(self):
        """Dismiss the tutorial overlay"""
        self._cleanup_overlay('tutorial_overlay')
    
    def show_settings_overlay(self, on_close_callback):
        """Show lightweight settings overlay with toggles"""
        # Prevent duplication
        if self.settings_overlay:
            self._log_overlay("Already showing", "settings_overlay")
            return
        
        self._log_overlay("Show", "settings_overlay")
        
        overlay = FloatLayout(size_hint=(1, 1))
        self._apply_overlay_vignette(overlay, base_alpha=0.6, edge_alpha=0.9, edge_ratio=0.09)
        
        # Settings panel
        panel_width = 400
        panel_height = 300
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=16,
                pattern=True,
                civic_mode=self._is_civic_mode()
            )
        
        # Title
        title = Label(
            text="Configuració",
            font_size='26sp',
            bold=True,
            color=self._theme_color((0.95, 0.92, 0.85, 1)),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        panel.add_widget(title)
        
        # Create toggle buttons
        y_offset = 0.75
        toggle_height = 0.20
        
        toggles = []
        settings_data = [
            ('Mode de pràctica', 'practice_mode'),
            ('Mode de direcció', 'direction_mode'),
            ('Subtítols', 'subtitles_enabled'),
        ]
        
        for i, (label_text, setting_key) in enumerate(settings_data):
            # Calculate position
            y_pos = y_offset - (i * toggle_height)
            
            # Create toggle button container
            toggle_container = Widget(
                size_hint=(0.9, None),
                height=int(panel_height * 0.18),
                pos_hint={'center_x': 0.5, 'y': y_pos}
            )
            
            # Label
            toggle_label = Label(
                text=label_text,
                font_size='18sp',
                color=(0.95, 0.95, 0.95, 1),
                size_hint=(0.6, 1),
                pos_hint={'x': 0, 'y': 0}
            )
            toggle_container.add_widget(toggle_label)
            
            # Status indicator (ON/OFF)
            current_value = getattr(self.state, setting_key, False)
            status_text = "ACTIU" if current_value else "INACTIU"
            status_color = (0.2, 1, 0.3, 1) if current_value else (1, 0.3, 0.2, 1)
            
            status_label = Label(
                text=status_text,
                font_size='16sp',
                bold=True,
                color=status_color,
                size_hint=(0.4, 1),
                pos_hint={'right': 1, 'y': 0}
            )
            toggle_container.add_widget(status_label)
            
            # Store reference for updating
            toggles.append({
                'key': setting_key,
                'container': toggle_container,
                'status_label': status_label,
                'label_text': label_text
            })
            
            panel.add_widget(toggle_container)
        
        # Close button
        close_label = Label(
            text="Toca fora per tancar",
            font_size='14sp',
            italic=True,
            color=(0.62, 0.66, 0.72, 1),
            size_hint=(1, None),
            height=40,
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        panel.add_widget(close_label)
        
        overlay.add_widget(panel)
        
        # Touch handler
        def on_settings_touch(instance, touch):
            if overlay.collide_point(*touch.pos):
                if panel.collide_point(*touch.pos):
                    # Check which toggle was tapped
                    for toggle_info in toggles:
                        container = toggle_info['container']
                        if container.collide_point(*touch.pos):
                            # Toggle the setting
                            key = toggle_info['key']
                            self._toggle_setting(key, toggle_info['status_label'])
                else:
                    # Clicked outside panel, close
                    self.parent.remove_widget(overlay)
                    on_close_callback()
                return True
            return False
        
        # Store touch handler for cleanup
        overlay._touch_handler = on_settings_touch
        overlay.bind(on_touch_down=on_settings_touch)
        
        self.settings_overlay = overlay
        self.parent.add_widget(overlay)
    
    def dismiss_settings(self):
        """Dismiss settings overlay"""
        if self.settings_overlay:
            # Unbind touch handler
            if hasattr(self.settings_overlay, '_touch_handler'):
                self.settings_overlay.unbind(on_touch_down=self.settings_overlay._touch_handler)
        self._cleanup_overlay('settings_overlay')
    
    def _toggle_setting(self, setting_key, status_label):
        """Toggle a setting and update UI"""
        # Toggle in game state
        if setting_key == 'practice_mode':
            self.state.practice_mode = not self.state.practice_mode
        elif setting_key == 'direction_mode':
            self.state.direction_mode = not self.state.direction_mode
        elif setting_key == 'subtitles_enabled':
            self.state.subtitles_enabled = not self.state.subtitles_enabled
        
        # Update UI
        new_value = getattr(self.state, setting_key, False)
        status_text = "ACTIU" if new_value else "INACTIU"
        status_color = (0.2, 1, 0.3, 1) if new_value else (1, 0.3, 0.2, 1)
        status_label.text = status_text
        status_label.color = status_color
        self.update_title()

    def _is_civic_mode(self):
        """Check if civic deployment mode is enabled."""
        return bool(self.civic_mode)
    
    def _theme_color(self, default_color, civic_color=None):
        """Return color based on mode. Civic colors are more subtle.
        
        Args:
            default_color (tuple): RGBA color for default mode
            civic_color (tuple): RGBA color for civic mode (optional, will desaturate default if None)
        
        Returns:
            tuple: RGBA color values
        """
        if not self._is_civic_mode():
            return default_color
        
        if civic_color:
            return civic_color
        
        # Auto-desaturate: reduce saturation and brightness
        r, g, b, a = default_color
        avg = (r + g + b) / 3
        factor = 0.6  # Blend 60% toward gray
        return (
            r * (1 - factor) + avg * factor,
            g * (1 - factor) + avg * factor,
            b * (1 - factor) + avg * factor,
            a * 0.85  # Slightly more transparent
        )
    
    def _theme_animation_duration(self, default_duration):
        """Return animation duration based on mode. Civic mode is 20% slower (calmer).
        
        Args:
            default_duration (float): Duration in seconds for default mode
        
        Returns:
            float: Duration adjusted for civic mode
        """
        if self._is_civic_mode():
            return default_duration * 1.2
        return default_duration
    
    def _theme_particle_count(self, default_count):
        """Return particle count based on mode. Civic mode has fewer particles.
        
        Args:
            default_count (int): Particle count for default mode
        
        Returns:
            int: Particle count adjusted for civic mode
        """
        if self._is_civic_mode():
            return max(1, int(default_count * 0.5))
        return default_count
    
    def _theme_flash_intensity(self, default_alpha):
        """Return flash intensity based on mode. Civic mode has subtler flashes.
        
        Args:
            default_alpha (float): Alpha value for default mode
        
        Returns:
            float: Alpha adjusted for civic mode
        """
        if self._is_civic_mode():
            return default_alpha * 0.6
        return default_alpha

    def _bind_button_feedback(self, button):
        """Attach standardized press/release feedback and click sound."""
        if not button:
            return

        def on_press(instance):
            Animation(opacity=0.85, duration=0.08, transition="out_quad").start(instance)

        def on_release(instance):
            Animation(opacity=1.0, duration=0.12, transition="out_quad").start(instance)
            self.audio.play(
                AudioEvent.UI_CLICK,
                volume=0.22,
                allow_overlap=True,
                cooldown_ms=120,
                priority=1,
            )

        button.bind(on_press=on_press, on_release=on_release)

    def _apply_overlay_vignette(self, overlay, base_alpha=0.6, edge_alpha=0.9, edge_ratio=0.08):
        """Apply a Modernisme poster-style vignette to full-screen overlays."""
        if not overlay:
            return

        with overlay.canvas.before:
            Color(0, 0, 0, base_alpha)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)
            Color(0, 0, 0, edge_alpha)
            overlay.edge_top = Rectangle(pos=overlay.pos, size=(0, 0))
            overlay.edge_bottom = Rectangle(pos=overlay.pos, size=(0, 0))
            overlay.edge_left = Rectangle(pos=overlay.pos, size=(0, 0))
            overlay.edge_right = Rectangle(pos=overlay.pos, size=(0, 0))

        def update_vignette(*args):
            x, y = overlay.pos
            w, h = overlay.size
            edge = max(8, int(min(w, h) * edge_ratio))
            overlay.bg.pos = (x, y)
            overlay.bg.size = (w, h)
            overlay.edge_top.pos = (x, y + h - edge)
            overlay.edge_top.size = (w, edge)
            overlay.edge_bottom.pos = (x, y)
            overlay.edge_bottom.size = (w, edge)
            overlay.edge_left.pos = (x, y)
            overlay.edge_left.size = (edge, h)
            overlay.edge_right.pos = (x + w - edge, y)
            overlay.edge_right.size = (edge, h)

        overlay.bind(pos=update_vignette, size=update_vignette)
        update_vignette()

    def _style_overlay_button(self, button, variant="primary", font_size=None):
        """Apply unified overlay button styling."""
        if not button:
            return

        palette = {
            "primary": (0.26, 0.78, 0.55, 1),
            "secondary": (0.28, 0.52, 0.78, 1),
            "accent": (0.95, 0.78, 0.3, 1),
            "ghost": (0.2, 0.22, 0.28, 1),
            "danger": (0.55, 0.32, 0.32, 1),
        }

        button.background_normal = ""
        button.background_color = palette.get(variant, palette["primary"])
        button.color = (1, 1, 1, 1)
        button.bold = True
        if hasattr(self, "ui_font") and self.ui_font:
            button.font_name = self.ui_font
        if font_size:
            button.font_size = font_size

    def _trim_words(self, text, max_words=12):
        """Return a shortened string capped to max_words words."""
        if not text:
            return ""
        words = text.replace("\n", " ").split()
        if len(words) <= max_words:
            return " ".join(words)
        return " ".join(words[:max_words]) + "..."

    def _micro_symbol_for_station(self, tags):
        """Return a minimal ASCII symbol for cultural micro-injections."""
        if tags:
            for ch in tags[0]:
                if ch.isalpha():
                    return ch.upper()
        return "*"

    def show_cultural_micro_injection(self, station):
        """Show a short cultural line on arrival without blocking gameplay."""
        if not station:
            return

        station_id = normalize_station_id(station.name)
        station_info = self.tourist_data.get(station_id, {})
        line_text = station_info.get('one_liner_ca') or station.tourist_tip_ca or station_info.get('tip_ca', '')
        line_text = self._trim_words(line_text, 12)
        if not line_text:
            return

        if self.cultural_micro_overlay and self.cultural_micro_overlay in self.parent.children:
            self.parent.remove_widget(self.cultural_micro_overlay)
        self.cultural_micro_overlay = None

        if self._cultural_micro_event:
            self._cultural_micro_event.cancel()
            self._cultural_micro_event = None

        overlay = FloatLayout(size_hint=(1, 1))
        panel = Widget(size_hint=(None, None), size=(380, 70))
        panel.pos_hint = {'center_x': 0.5, 'top': 0.9}

        with panel.canvas.before:
            draw_modernisme_frame(
                panel.canvas.before,
                pos=panel.pos,
                size=panel.size,
                radius=12,
                pattern=False,
                civic_mode=self._is_civic_mode()
            )

        def update_panel_bg(*args):
            panel.canvas.before.clear()
            with panel.canvas.before:
                draw_modernisme_frame(
                    panel.canvas.before,
                    pos=panel.pos,
                    size=panel.size,
                    radius=12,
                    pattern=False,
                    civic_mode=self._is_civic_mode()
                )
        panel.bind(pos=update_panel_bg, size=update_panel_bg)

        icon_label = Label(
            text=self._micro_symbol_for_station(station_info.get('tags', [])),
            font_size='18sp',
            bold=True,
            color=(0.9, 0.9, 0.85, 1),
            size_hint=(None, None),
            size=(24, 24),
            pos_hint={'x': 0.05, 'center_y': 0.5}
        )
        panel.add_widget(icon_label)

        line_label = Label(
            text=line_text,
            font_size='16sp',
            color=(0.92, 0.95, 0.98, 1),
            size_hint=(None, None),
            size=(300, 40),
            pos_hint={'center_x': 0.6, 'center_y': 0.5},
            halign='left',
            valign='middle',
            shorten=True,
            shorten_from='right'
        )
        line_label.text_size = (300, 40)
        panel.add_widget(line_label)

        overlay.add_widget(panel)
        overlay.opacity = 0
        self.parent.add_widget(overlay)
        self.cultural_micro_overlay = overlay

        fade_in = Animation(opacity=1, duration=0.18, transition='out_quad')
        fade_out = Animation(opacity=0, duration=0.2, transition='in_quad')

        def dismiss(*args):
            if self.cultural_micro_overlay != overlay:
                return
            fade_out.bind(on_complete=lambda *_: self._cleanup_overlay('cultural_micro_overlay'))
            fade_out.start(overlay)

        fade_in.start(overlay)
        self._cultural_micro_event = self.schedule_event(lambda dt: dismiss(), 2.0)

    def _camera_shake(self, duration=0.12, intensity=4):
        """Apply a short camera shake to the root widget."""
        target = self.parent
        if not target:
            return

        # Cancel existing shake if any
        if self._camera_shake_event:
            self._camera_shake_event.cancel()
            self._camera_shake_event = None

        original_pos = target.pos
        start_time = Clock.get_time()

        def do_shake(dt):
            elapsed = Clock.get_time() - start_time
            if elapsed >= duration:
                target.pos = original_pos  # Always reset to original
                self._camera_shake_event = None
                return False
            offset_x = random.uniform(-intensity, intensity)
            offset_y = random.uniform(-intensity, intensity)
            target.pos = (original_pos[0] + offset_x, original_pos[1] + offset_y)
            return True

        self._camera_shake_event = Clock.schedule_interval(do_shake, 1 / 60)

    def _trigger_haptic(self, duration_ms=20):
        """Trigger light haptic feedback if the platform supports it."""
        try:
            import importlib
            if importlib.util.find_spec("plyer") is None:
                return
            vibrator = importlib.import_module("plyer").vibrator
        except Exception:
            return

        if not hasattr(vibrator, "vibrate"):
            return

        try:
            vibrator.vibrate(time=duration_ms)
        except Exception:
            return

    def show_station_arrival_banner(self, station_name):
        """Show an animated banner announcing the arrival station."""
        if not station_name:
            return

        if hasattr(self, "_arrival_banner") and self._arrival_banner:
            if self._arrival_banner in self.parent.children:
                self.parent.remove_widget(self._arrival_banner)
            self._arrival_banner = None

        banner = Widget(size_hint=(0.78, None), height=54)
        target_y = self.parent.height * 0.78
        banner.pos = (self.parent.width * 0.11, target_y - 12)
        banner.opacity = 0

        with banner.canvas.before:
            Color(0.08, 0.1, 0.12, 0.92)
            bg = RoundedRectangle(pos=banner.pos, size=banner.size, radius=[12])

        def update_banner_bg(*args):
            bg.pos = banner.pos
            bg.size = banner.size

        banner.bind(pos=update_banner_bg, size=update_banner_bg)

        label = Label(
            text=station_name,
            font_size='22sp',
            bold=True,
            color=(0.9, 0.95, 1.0, 1),
            size_hint=(1, 1),
            halign='center',
            valign='middle'
        )
        label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        banner.add_widget(label)

        self.parent.add_widget(banner)
        self._arrival_banner = banner

        intro = Animation(opacity=1, y=target_y, duration=0.18, transition='out_quad')
        outro = Animation(opacity=0, y=target_y + 8, duration=0.18, transition='in_quad')

        def start_outro(*args):
            outro.start(banner)

        def remove_banner(*args):
            if banner in self.parent.children:
                self.parent.remove_widget(banner)
            if self._arrival_banner == banner:
                self._arrival_banner = None

        intro.bind(on_complete=lambda *args: self.schedule_event(lambda dt: start_outro(), 0.9))
        outro.bind(on_complete=lambda *args: remove_banner())
        intro.start(banner)

    def play_arrival_sequence(self, station_name, node_index=None):
        """Play arrival SFX, camera shake, station banner, and visual effects without blocking."""
        if self.line_view and node_index is not None:
            # Use punch zoom for dramatic arrival effect
            self.line_view.zoom_to_node(node_index, zoom_factor=1.15, duration=0.12, punch=True)
            # Trigger subtle node flash
            self.schedule_event(lambda dt: self.line_view.arrival_flash(node_index, duration=0.2), 0.05)

        if self._arrival_brake_event:
            try:
                self._arrival_brake_event.cancel()
            except Exception:
                pass
            self._arrival_brake_event = None

        if not self._arrival_brake_played:
            self.audio.play(
                AudioEvent.SFX_ARRIVAL_BRAKE,
                volume=0.38,
                allow_overlap=False,
                cooldown_ms=200,
                priority=2,
            )
        self._arrival_brake_played = False
        self._camera_shake(duration=0.08, intensity=2)
        self.schedule_event(
            lambda dt: self.audio.play(
                AudioEvent.SFX_DOOR_OPEN,
                volume=0.4,
                allow_overlap=False,
                cooldown_ms=200,
                priority=2,
            ),
            0.18
        )
        self.schedule_event(lambda dt: self.show_station_arrival_banner(station_name), 0.18)
        self.schedule_event(
            lambda dt: self.audio.play(
                AudioEvent.SFX_DOOR_CLOSE,
                volume=0.4,
                allow_overlap=False,
                cooldown_ms=200,
                priority=2,
            ),
            1.55
        )

    def _schedule_arrival_brake(self, travel_duration):
        """Schedule a softer brake cue shortly before arrival."""
        if travel_duration is None:
            return
        if self._arrival_brake_event:
            try:
                self._arrival_brake_event.cancel()
            except Exception:
                pass
            self._arrival_brake_event = None

        self._arrival_brake_played = False
        cue_delay = max(0.12, travel_duration - 0.35)
        if cue_delay <= 0:
            return

        def play_brake(dt):
            self._arrival_brake_played = True
            self.audio.play(
                AudioEvent.SFX_ARRIVAL_BRAKE,
                volume=0.36,
                allow_overlap=False,
                cooldown_ms=200,
                priority=2,
            )

        self._arrival_brake_event = self.schedule_event(play_brake, cue_delay)

    def _schedule_station_announcement(self, station_name, travel_duration):
        """Schedule a subtle Catalan voice-over for the next station."""
        if not station_name or not self.state.subtitles_enabled:
            return

        now = Clock.get_time()
        if now - self._last_station_announcement_time < 2.0:
            return

        self._last_station_announcement_time = now
        announcement_delay = min(0.8, max(0.25, travel_duration * 0.35))
        message = f"Pròxima parada: {station_name}"
        self.schedule_event(lambda dt: speak(message, interrupt=False), announcement_delay)

    def _update_direction_indicator(self):
        """Update the direction arrow indicator near the line view."""
        if not self.direction_indicator or not self.line_view:
            return
        self.direction_indicator.text = ""
        self.direction_indicator.color = (0.9, 0.9, 0.95, 0)

    def show_tourist_popup(self, station, on_close_callback=None):
        """Show micro-dose cultural info without blocking gameplay."""
        if not station:
            return

        if self.tourist_overlay:
            self.dismiss_tourist_popup()

        self._log_overlay("Show", "tourist_overlay")

        overlay = FloatLayout(size_hint=(1, 1))
        self._apply_overlay_vignette(overlay, base_alpha=0.6, edge_alpha=0.9, edge_ratio=0.09)

        panel = Widget(size_hint=(None, None), size=(520, 360))
        panel.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=18,
                pattern=True,
                civic_mode=self._is_civic_mode()
            )

        def update_panel_bg(*args):
            panel.canvas.clear()
            with panel.canvas:
                draw_modernisme_frame(
                    panel.canvas,
                    pos=panel.pos,
                    size=panel.size,
                    radius=16,
                    pattern=False,
                    civic_mode=self._is_civic_mode()
                )

        panel.bind(pos=update_panel_bg, size=update_panel_bg)

        station_id = normalize_station_id(station.name)
        station_info = self.tourist_data.get(station_id, {})
        tags = station_info.get('tags', []) if station_info else []
        image_url = station.image_url or station_info.get('image_url', '')

        image_box = FloatLayout(size_hint=(None, None), size=(460, 170))
        image_box.pos_hint = {'center_x': 0.5, 'top': 0.92}
        with image_box.canvas.before:
            Color(0.12, 0.14, 0.18, 0.9)
            RoundedRectangle(pos=image_box.pos, size=image_box.size, radius=[12])

        def update_image_box(*args):
            image_box.canvas.before.clear()
            with image_box.canvas.before:
                Color(0.12, 0.14, 0.18, 0.9)
                RoundedRectangle(pos=image_box.pos, size=image_box.size, radius=[12])
            if image_scatter:
                image_scatter.pos = image_box.pos
                image_scatter.size = image_box.size

        image_box.bind(pos=update_image_box, size=update_image_box)

        image_scatter = None
        if image_url:
            image_scatter = ScatterLayout(
                size_hint=(None, None),
                size=image_box.size,
                pos=image_box.pos,
                do_rotation=False,
                do_translation=False,
                do_scale=False
            )
            image_widget = AsyncImage(
                source=image_url,
                allow_stretch=True,
                keep_ratio=True,
                size_hint=(1, 1)
            )
            image_scatter.add_widget(image_widget)
            image_box.add_widget(image_scatter)

            ken_burns = Animation(scale=1.06, duration=2.0, transition='in_out_quad')
            ken_burns += Animation(scale=1.02, duration=2.0, transition='in_out_quad')
            ken_burns.repeat = True
            ken_burns.start(image_scatter)
        else:
            placeholder = Label(
                text="Imatge no disponible",
                font_size='14sp',
                color=(0.7, 0.75, 0.8, 1),
                size_hint=(1, 1)
            )
            image_box.add_widget(placeholder)

        panel.add_widget(image_box)

        title_label = Label(
            text=station.name,
            font_size='18sp',
            bold=True,
            color=(0.92, 0.9, 0.82, 1),
            size_hint=(1, None),
            height=26,
            pos_hint={'center_x': 0.5, 'top': 0.44},
            halign='center',
            valign='middle'
        )
        title_label.text_size = (panel.width * 0.9, 26)
        panel.add_widget(title_label)

        one_liner = station_info.get('one_liner_ca', '') or station.tourist_tip_ca or ''
        one_liner = self._trim_words(one_liner, 12)
        tip_line = station_info.get('tip_ca', '') or station.tourist_tip_ca or ''
        tip_line = self._trim_words(tip_line, 14)

        one_liner_label = Label(
            text=one_liner,
            font_size='15sp',
            color=(0.9, 0.93, 0.97, 1),
            size_hint=(0.9, None),
            height=40,
            pos_hint={'center_x': 0.5, 'center_y': 0.32},
            halign='center',
            valign='middle',
            shorten=True,
            shorten_from='right'
        )
        one_liner_label.text_size = (panel.width * 0.85, 40)
        panel.add_widget(one_liner_label)

        tip_label = Label(
            text=tip_line,
            font_size='14sp',
            color=(0.7, 0.75, 0.82, 1),
            size_hint=(0.9, None),
            height=32,
            pos_hint={'center_x': 0.5, 'center_y': 0.23},
            halign='center',
            valign='middle',
            shorten=True,
            shorten_from='right'
        )
        tip_label.text_size = (panel.width * 0.85, 32)
        panel.add_widget(tip_label)

        close_button = Button(
            text="Tancar",
            size_hint=(None, None),
            size=(140, 36),
            pos_hint={'center_x': 0.5, 'y': 0.07},
            font_size='14sp'
        )
        self._style_overlay_button(close_button, variant="secondary", font_size='14sp')
        self._bind_button_feedback(close_button)
        panel.add_widget(close_button)

        overlay.add_widget(panel)
        overlay.opacity = 0
        self.parent.add_widget(overlay)
        self.tourist_overlay = overlay

        def close_popup(*args):
            if image_scatter:
                Animation.stop_all(image_scatter)
            self.dismiss_tourist_popup()
            if callable(on_close_callback):
                on_close_callback()

        close_button.bind(on_release=close_popup)

        Animation(opacity=1, duration=0.2, transition='out_quad').start(overlay)
    
    def dismiss_tourist_popup(self):
        """Dismiss tourist popup overlay"""
        self._cleanup_overlay('tourist_overlay')
    
    def show_civic_splash(self, on_dismiss_callback=None):
        """Show civic splash screen: 'Benvingut a Barcelona'
        
        Elegant institutional welcome screen positioning the game
        as a digital civic tool for discovering Barcelona.
        """
        # Prevent duplication
        if self.civic_splash_overlay:
            self._log_overlay("Already showing", "civic_splash_overlay")
            return
        
        self._log_overlay("Show", "civic_splash_overlay")
        
        overlay = FloatLayout(size_hint=(1, 1))
        
        # Deep elegant background
        with overlay.canvas.before:
            Color(0.02, 0.03, 0.05, 0.98)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)
        
        def update_overlay_bg(*args):
            overlay.bg.pos = overlay.pos
            overlay.bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)
        
        # Elegant panel
        panel = Widget(
            size_hint=(None, None),
            size=(600, 340),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=22,
                pattern=False,
                civic_mode=True
            )
        
        # Main title - elegant and civic
        title = Label(
            text="Benvingut a Barcelona",
            font_size='38sp',
            bold=True,
            size_hint=(1, None),
            height=70,
            pos_hint={'center_x': 0.5, 'top': 0.88},
            color=(0.88, 0.92, 0.96, 1),
            halign='center'
        )
        title.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        panel.add_widget(title)
        
        # Subtitle - institutional and welcoming
        subtitle = Label(
            text="Una experiència per descobrir la ciutat\ni viure-la en català",
            font_size='18sp',
            size_hint=(1, None),
            height=70,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            color=(0.72, 0.78, 0.85, 1),
            halign='center',
            italic=True
        )
        subtitle.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None)))
        panel.add_widget(subtitle)
        
        # Call to action
        cta = Label(
            text="Toca per començar",
            font_size='15sp',
            size_hint=(1, None),
            height=40,
            pos_hint={'center_x': 0.5, 'y': 0.08},
            color=(0.5, 0.65, 0.75, 1),
            italic=True
        )
        panel.add_widget(cta)
        
        overlay.add_widget(panel)
        
        # Fade in animation
        overlay.opacity = 0
        fade_in = Animation(opacity=1, duration=0.8, transition='in_out_quad')
        fade_in.start(overlay)
        
        # Touch to dismiss
        def on_splash_touch(instance, touch):
            if overlay.collide_point(*touch.pos):
                # Fade out
                fade_out = Animation(opacity=0, duration=0.5, transition='in_out_quad')
                fade_out.bind(on_complete=lambda *args: self._dismiss_civic_splash(on_dismiss_callback))
                fade_out.start(overlay)
                return True
            return False
        
        overlay.bind(on_touch_down=on_splash_touch)
        
        self.civic_splash_overlay = overlay
        self.parent.add_widget(overlay)
        
        # Auto-dismiss after 4 seconds if not touched
        def auto_dismiss(dt):
            if self.civic_splash_overlay:
                fade_out = Animation(opacity=0, duration=0.5, transition='in_out_quad')
                fade_out.bind(on_complete=lambda *args: self._dismiss_civic_splash(on_dismiss_callback))
                fade_out.start(overlay)
        
        Clock.schedule_once(auto_dismiss, 4.0)
    
    def _dismiss_civic_splash(self, callback=None):
        """Dismiss civic splash overlay"""
        self._cleanup_overlay('civic_splash_overlay')
        if callback:
            callback()
    
    def show_descobreix_barcelona(self):
        """Show 'Descobreix Barcelona' civic information overlay
        
        Educational micro-info about Barcelona civic life:
        - What is TMB?
        - What is a barri?
        - Why Catalan matters
        - Respect for local language
        """
        # Prevent duplication
        if self.descobreix_overlay:
            self._log_overlay("Already showing", "descobreix_overlay")
            return
        
        self._log_overlay("Show", "descobreix_overlay")
        
        overlay = FloatLayout(size_hint=(1, 1))
        
        with overlay.canvas.before:
            Color(0, 0, 0, 0.88)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)
        
        def update_overlay_bg(*args):
            overlay.bg.pos = overlay.pos
            overlay.bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)
        
        # Scrollable content panel
        from kivy.uix.scrollview import ScrollView
        
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
            draw_modernisme_frame(
                content.canvas.before,
                pos=content.pos,
                size=content.size,
                radius=20,
                pattern=True,
                civic_mode=self._is_civic_mode()
            )
        
        def update_content_bg(*args):
            content.canvas.before.clear()
            with content.canvas.before:
                draw_modernisme_frame(
                    content.canvas.before,
                    pos=content.pos,
                    size=content.size,
                    radius=20,
                    pattern=True,
                    civic_mode=self._is_civic_mode()
                )
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
        close_btn.bind(on_release=lambda x: self._dismiss_descobreix())
        self._bind_button_feedback(close_btn)
        
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
                    self._dismiss_descobreix()
                    return True
            return False
        
        overlay.bind(on_touch_down=on_overlay_touch)
        
        self.descobreix_overlay = overlay
        self.parent.add_widget(overlay)
    
    def _dismiss_descobreix(self, *args):
        """Dismiss descobreix Barcelona overlay"""
        self._cleanup_overlay('descobreix_overlay')
    
    def show_badge_unlock(self, badge_id):
        """Show subtle badge unlock notification
        
        Args:
            badge_id (str): Badge identifier (e.g., "modernisme")
        """
        if badge_id not in BADGE_DEFINITIONS:
            return
        
        badge_def = BADGE_DEFINITIONS[badge_id]
        icon = badge_def["icon"]
        name = badge_def["name"]
        self._last_unlocked_badge_id = badge_id
        
        # Create a subtle floating notification
        notification = FloatLayout(size_hint=(None, None), size=(380, 100))
        notification.pos_hint = {'center_x': 0.5, 'top': 0.85}
        
        with notification.canvas.before:
            draw_modernisme_frame(
                notification.canvas.before,
                pos=notification.pos,
                size=notification.size,
                radius=12,
                accent_color=(0.95, 0.75, 0.3, 0.8),
                pattern=False,
                civic_mode=self._is_civic_mode()
            )
        
        def update_notification_bg(*args):
            notification.canvas.before.clear()
            with notification.canvas.before:
                draw_modernisme_frame(
                    notification.canvas.before,
                    pos=notification.pos,
                    size=notification.size,
                    radius=12,
                    accent_color=(0.95, 0.75, 0.3, 0.8),
                    pattern=False,
                    civic_mode=self._is_civic_mode()
                )
        
        notification.bind(pos=update_notification_bg, size=update_notification_bg)
        
        # Badge icon
        icon_label = Label(
            text=icon,
            font_size='38sp',
            size_hint=(None, 1),
            width=80,
            pos_hint={'x': 0.05, 'center_y': 0.5}
        )
        notification.add_widget(icon_label)
        
        # Badge text
        text_box = BoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=260,
            pos_hint={'x': 0.28, 'center_y': 0.5}
        )
        
        title_label = Label(
            text="Insígnia aconseguida!",
            font_size='15sp',
            bold=True,
            color=(1, 0.95, 0.4, 1),
            size_hint=(1, None),
            height=25
        )
        text_box.add_widget(title_label)
        
        name_label = Label(
            text=name,
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=30
        )
        text_box.add_widget(name_label)
        
        notification.add_widget(text_box)
        
        # Add to parent
        self.parent.add_widget(notification)
        
        # Animate in
        notification.opacity = 0
        anim_in = Animation(opacity=1, duration=0.4, transition='out_quad')
        anim_in.start(notification)
        
        # Auto-dismiss after 3 seconds
        def dismiss_badge(dt):
            anim_out = Animation(opacity=0, duration=0.4, transition='in_quad')
            
            def remove_badge(anim, widget):
                if widget in self.parent.children:
                    self.parent.remove_widget(widget)
            
            anim_out.bind(on_complete=remove_badge)
            anim_out.start(notification)
        
        self.events.schedule_once(dismiss_badge, 3.0)

    def generate_share_card(self, milestone_label, line_completed=False):
        """Generate a shareable achievement card and export as image."""
        if not self.parent:
            return

        words_learned = len(self.learned_vocab_ids)
        stations_visited = self.state.stations_completed
        line_name = getattr(self.state.line, "name", "")
        if line_completed:
            line_text = f"Línia completada: {line_name}"
        else:
            line_text = f"Línia en progrés: {line_name}"

        badge_text = "Cap encara"
        if self._last_unlocked_badge_id in BADGE_DEFINITIONS:
            badge_text = BADGE_DEFINITIONS[self._last_unlocked_badge_id]["name"]

        data = {
            "title": "Sobrevisc a Barcelona en català",
            "milestone": milestone_label,
            "line": line_text,
            "words": f"Paraules apreses: {words_learned}",
            "stations": f"Estacions visitades: {stations_visited}",
            "badge": f"Insígnia: {badge_text}",
        }

        self._render_share_card(data)

    def _render_share_card(self, data):
        """Render share card offscreen and export to PNG."""
        if self._share_card_event:
            self._share_card_event.cancel()
            self._share_card_event = None

        card = FloatLayout(size_hint=(None, None), size=(820, 460))
        card.pos = (-5000, -5000)

        with card.canvas.before:
            draw_modernisme_frame(
                card.canvas.before,
                pos=card.pos,
                size=card.size,
                radius=18,
                pattern=True,
                civic_mode=self._is_civic_mode()
            )

        def update_card_bg(*args):
            card.canvas.before.clear()
            with card.canvas.before:
                draw_modernisme_frame(
                    card.canvas.before,
                    pos=card.pos,
                    size=card.size,
                    radius=18,
                    pattern=True,
                    civic_mode=self._is_civic_mode()
                )
        card.bind(pos=update_card_bg, size=update_card_bg)

        title = Label(
            text=data["title"],
            font_size='28sp',
            bold=True,
            color=(0.88, 0.92, 0.96, 1),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        title.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] * 0.9, None)))
        card.add_widget(title)

        milestone = Label(
            text=data["milestone"],
            font_size='20sp',
            italic=True,
            color=(0.6, 0.85, 0.75, 1),
            size_hint=(1, None),
            height=32,
            pos_hint={'center_x': 0.5, 'top': 0.86}
        )
        card.add_widget(milestone)

        details = [data["line"], data["words"], data["stations"], data["badge"]]
        y_positions = [0.70, 0.58, 0.46, 0.34]
        for text, y in zip(details, y_positions):
            label = Label(
                text=text,
                font_size='17sp',
                color=(0.78, 0.82, 0.9, 1),
                size_hint=(0.9, None),
                height=28,
                pos_hint={'center_x': 0.5, 'center_y': y},
                halign='center',
                valign='middle'
            )
            label.text_size = (card.width * 0.85, 28)
            card.add_widget(label)

        footer = Label(
            text="Barcelona · Pròxima Parada",
            font_size='13sp',
            color=(0.55, 0.62, 0.7, 1),
            size_hint=(1, None),
            height=20,
            pos_hint={'center_x': 0.5, 'y': 0.08}
        )
        card.add_widget(footer)

        self.parent.add_widget(card)

        def export_card(dt):
            try:
                output_dir = Path(__file__).parent / "data" / "share_cards"
                output_dir.mkdir(parents=True, exist_ok=True)
                stamp = time.strftime("%Y%m%d_%H%M%S")
                file_path = output_dir / f"share_card_{stamp}.png"
                card.export_to_png(str(file_path))
            except Exception as e:
                print(f"Share card export failed: {e}")
            finally:
                if card in self.parent.children:
                    self.parent.remove_widget(card)

        self._share_card_event = self.schedule_event(export_card, 0.02)
    
    def show_first_day_step_popup(self, station, on_close_callback):
        """Show First Day Mode step completion popup with richer cultural narrative"""
        if self.tourist_overlay:
            return

        overlay = FloatLayout(size_hint=(1, 1))
        with overlay.canvas.before:
            Color(0, 0, 0, 0.85)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)

        def update_overlay_bg(*args):
            overlay.bg.pos = overlay.pos
            overlay.bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)

        panel_width = 560
        panel_height = 340
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=18,
                accent_color=(0.95, 0.85, 0.3, 0.6),
                pattern=False,
                civic_mode=self._is_civic_mode()
            )

        title = Label(
            text=f"🌟 {station.name}",
            font_size='26sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=45,
            pos_hint={'center_x': 0.5, 'top': 0.94}
        )
        panel.add_widget(title)

        # Enhanced cultural description (2-3 lines)
        description_text = station.tourist_tip_ca if station.tourist_tip_ca else "Gaudeix d'aquest lloc emblemàtic de Barcelona."
        
        info = Label(
            text=description_text,
            font_size='18sp',
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(0.9, None),
            height=160,
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            max_lines=4
        )
        info.text_size = (panel_width * 0.85, 160)
        panel.add_widget(info)

        continue_button = Button(
            text="Continuar el viatge",
            size_hint=(0.5, None),
            height=40,
            pos_hint={'center_x': 0.5, 'y': 0.08},
            background_normal="",
            background_color=(0.3, 0.7, 0.9, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self._bind_button_feedback(continue_button)
        panel.add_widget(continue_button)

        overlay.add_widget(panel)

        def close_popup(*args):
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)
            self.tourist_overlay = None
            if callable(on_close_callback):
                on_close_callback()

        continue_button.bind(on_release=close_popup)
        self.tourist_overlay = overlay
        self.parent.add_widget(overlay)
    
    def show_first_day_completion(self):
        """Show completion overlay for First Day Mode journey"""
        # Play celebration sound
        self.audio.play_line_completed()

        overlay = FloatLayout()
        with overlay.canvas:
            Color(0, 0, 0, 0.9)
            Rectangle(pos=self.parent.pos, size=self.parent.size)

        panel_width = 620
        panel_height = 480
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=18,
                accent_color=(0.95, 0.85, 0.3, 0.6),
                pattern=False,
                civic_mode=self._is_civic_mode()
            )

        title = Label(
            text="🎉 Has completat el teu primer dia a Barcelona! 🎉",
            font_size='26sp',
            bold=True,
            color=(1, 0.95, 0.4, 1),
            size_hint=(1, None),
            height=70,
            pos_hint={'center_x': 0.5, 'top': 0.95},
            halign='center',
            max_lines=2
        )
        title.text_size = (panel_width * 0.9, 70)
        panel.add_widget(title)

        # Cultural summary
        summary = Label(
            text=(
                "Has descobert el centre històric de Barcelona, des de la "
                "Plaça Catalunya fins al barri Gòtic, passant per la Rambla "
                "i arribant al mar a la Barceloneta. Has visitat Montjuïc, "
                "la muntanya que domina la ciutat.\\n\\n"
                "Ara coneixes els llocs més emblemàtics per començar "
                "a gaudir de Barcelona com un local!"
            ),
            font_size='17sp',
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(0.9, None),
            height=240,
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5, 'center_y': 0.52}
        )
        summary.text_size = (panel_width * 0.85, 240)
        panel.add_widget(summary)

        # Buttons
        button_box = Widget(size_hint=(1, None), height=50, pos_hint={'center_x': 0.5, 'y': 0.08})

        explore_button = Button(
            text="Explorar més línies",
            size_hint=(0.42, None),
            height=44,
            pos_hint={'x': 0.08, 'center_y': 0.5},
            background_normal="",
            background_color=(0.3, 0.7, 0.9, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self._bind_button_feedback(explore_button)

        def go_to_line_select(*args):
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)
            # Navigate to line selection screen
            from kivy.app import App
            app = App.get_running_app()
            if app and app.root and hasattr(app.root, 'current'):
                app.root.transition.duration = 0.25
                app.root.current = "line_select"

        explore_button.bind(on_release=go_to_line_select)
        button_box.add_widget(explore_button)

        restart_button = Button(
            text="Tornar a jugar",
            size_hint=(0.42, None),
            height=44,
            pos_hint={'right': 0.92, 'center_y': 0.5},
            background_normal="",
            background_color=(0.25, 0.6, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self._bind_button_feedback(restart_button)

        def restart_journey(*args):
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)
            # Reset first day mode
            self.state.first_day_progress = 0
            self.state.first_day_completed = False
            self._update_first_day_progress()
            self.events.schedule_once(lambda dt: self.parent.reset_run(first_day_mode=True), 0.1)

        restart_button.bind(on_release=restart_journey)
        button_box.add_widget(restart_button)

        panel.add_widget(button_box)
        overlay.add_widget(panel)
        self.parent.add_widget(overlay)

    def show_journey_overlay(self, on_close_callback=None):
        """Show meta-progression journey overlay with stats, badges, and milestones"""
        # Prevent duplication
        if hasattr(self, 'journey_overlay') and self.journey_overlay:
            self._log_overlay("Already showing", "journey_overlay")
            return
        
        self._log_overlay("Show", "journey_overlay")
        
        # Fetch data from ProgressManager
        progress_mgr = getattr(self.parent, 'progress_manager', None)
        if not progress_mgr:
            return  # No progress data available
        
        # Get progress data
        total_score = progress_mgr.get_total_score() if hasattr(progress_mgr, 'get_total_score') else 0
        completed_lines = progress_mgr.get_completed_lines() if hasattr(progress_mgr, 'get_completed_lines') else []
        badges = progress_mgr.get_earned_badges() if hasattr(progress_mgr, 'get_earned_badges') else []
        first_day_complete = progress_mgr.is_first_day_complete() if hasattr(progress_mgr, 'is_first_day_complete') else False
        
        # Calculate total stations visited
        total_stations = 0
        for line_id in completed_lines:
            completed_station_ids = progress_mgr.get_completed_station_ids(line_id)
            total_stations += len(completed_station_ids)
        
        # Create overlay
        overlay = FloatLayout(size_hint=(1, 1))
        self._apply_overlay_vignette(overlay, base_alpha=0.66, edge_alpha=0.92, edge_ratio=0.09)
        
        # Main panel
        panel_width = 560
        panel_height = 540
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=20,
                pattern=True,
                civic_mode=self._is_civic_mode()
            )
        
        # Title
        title = Label(
            text="El teu viatge",
            font_size='32sp',
            bold=True,
            color=self._theme_color((0.95, 0.92, 0.85, 1)),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.96}
        )
        panel.add_widget(title)
        
        # Subtitle
        subtitle = Label(
            text="Progressió",
            font_size='15sp',
            italic=True,
            color=(0.6, 0.7, 0.8, 1),
            size_hint=(1, None),
            height=25,
            pos_hint={'center_x': 0.5, 'top': 0.88}
        )
        panel.add_widget(subtitle)
        
        # Stats section (top row - 3 columns)
        stats_y = 0.75
        
        # Total score
        score_label = Label(
            text=str(total_score),
            font_size='36sp',
            bold=True,
            color=(1, 0.95, 0.4, 1),
            size_hint=(None, None),
            size=(140, 50),
            pos_hint={'x': 0.05, 'top': stats_y}
        )
        panel.add_widget(score_label)
        
        score_caption = Label(
            text="Punts totals",
            font_size='13sp',
            color=(0.7, 0.75, 0.8, 1),
            size_hint=(None, None),
            size=(140, 20),
            pos_hint={'x': 0.05, 'top': stats_y - 0.08}
        )
        panel.add_widget(score_caption)
        
        # Lines completed
        lines_label = Label(
            text=str(len(completed_lines)),
            font_size='36sp',
            bold=True,
            color=(0.3, 0.9, 0.5, 1),
            size_hint=(None, None),
            size=(140, 50),
            pos_hint={'x': 0.36, 'top': stats_y}
        )
        panel.add_widget(lines_label)
        
        lines_caption = Label(
            text="Línies fetes",
            font_size='13sp',
            color=(0.7, 0.75, 0.8, 1),
            size_hint=(None, None),
            size=(140, 20),
            pos_hint={'x': 0.36, 'top': stats_y - 0.08}
        )
        panel.add_widget(lines_caption)
        
        # Total stations
        stations_label = Label(
            text=str(total_stations),
            font_size='36sp',
            bold=True,
            color=(0.4, 0.7, 1.0, 1),
            size_hint=(None, None),
            size=(140, 50),
            pos_hint={'x': 0.67, 'top': stats_y}
        )
        panel.add_widget(stations_label)
        
        stations_caption = Label(
            text="Estacions",
            font_size='13sp',
            color=(0.7, 0.75, 0.8, 1),
            size_hint=(None, None),
            size=(140, 20),
            pos_hint={'x': 0.67, 'top': stats_y - 0.08}
        )
        panel.add_widget(stations_caption)
        
        # Badges section
        badges_y = 0.58
        badges_title = Label(
            text="🏆 Medalles aconseguides",
            font_size='18sp',
            bold=True,
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'top': badges_y}
        )
        panel.add_widget(badges_title)
        
        # Badges grid
        if badges:
            badge_grid_y = badges_y - 0.05
            badge_container = Widget(
                size_hint=(0.9, None),
                height=180,
                pos_hint={'center_x': 0.5, 'top': badge_grid_y}
            )
            
            # Display up to 12 badges in 4x3 grid
            cols = 4
            badge_size = 60
            spacing_x = 20
            spacing_y = 20
            display_badges = badges[:12]
            
            # Calculate grid centering
            grid_width = cols * badge_size + (cols - 1) * spacing_x
            start_x = (badge_container.width - grid_width) / 2
            
            for idx, badge_id in enumerate(display_badges):
                if badge_id not in BADGE_DEFINITIONS:
                    continue
                
                badge_def = BADGE_DEFINITIONS[badge_id]
                row = idx // cols
                col = idx % cols
                
                # Calculate position
                x = start_x + col * (badge_size + spacing_x)
                y = badge_container.height - (row + 1) * (badge_size + spacing_y)
                
                # Badge icon with subtle background
                badge_widget = Widget(
                    size_hint=(None, None),
                    size=(badge_size, badge_size),
                    pos=(x, y)
                )
                
                with badge_widget.canvas.before:
                    Color(0.15, 0.18, 0.22, 0.8)
                    RoundedRectangle(
                        pos=badge_widget.pos,
                        size=badge_widget.size,
                        radius=[8]
                    )
                
                badge_icon = Label(
                    text=badge_def['icon'],
                    font_size='32sp',
                    size_hint=(1, 1)
                )
                badge_widget.add_widget(badge_icon)
                badge_container.add_widget(badge_widget)
            
            panel.add_widget(badge_container)
            
            # Badge count
            badge_count = Label(
                text=f"{len(badges)} de {len(BADGE_DEFINITIONS)} medalles",
                font_size='13sp',
                italic=True,
                color=(0.6, 0.65, 0.7, 1),
                size_hint=(1, None),
                height=20,
                pos_hint={'center_x': 0.5, 'top': badge_grid_y - 0.36}
            )
            panel.add_widget(badge_count)
        else:
            no_badges = Label(
                text="Encara no has aconseguit cap medalla",
                font_size='14sp',
                italic=True,
                color=(0.5, 0.55, 0.6, 1),
                size_hint=(1, None),
                height=30,
                pos_hint={'center_x': 0.5, 'top': badges_y - 0.08}
            )
            panel.add_widget(no_badges)
        
        # First Day section
        first_day_y = 0.18
        first_day_title = Label(
            text="🗺️ El teu primer dia a Barcelona",
            font_size='16sp',
            bold=True,
            color=(0.95, 0.85, 0.3, 1),
            size_hint=(1, None),
            height=25,
            pos_hint={'center_x': 0.5, 'top': first_day_y}
        )
        panel.add_widget(first_day_title)
        
        first_day_status = Label(
            text="✓ Completat!" if first_day_complete else "En progrés...",
            font_size='14sp',
            color=(0.3, 1.0, 0.4, 1) if first_day_complete else (0.7, 0.75, 0.8, 1),
            size_hint=(1, None),
            height=25,
            pos_hint={'center_x': 0.5, 'top': first_day_y - 0.05}
        )
        panel.add_widget(first_day_status)
        
        # Close button
        close_button = Button(
            text="Tornar al mapa",
            size_hint=(0.5, None),
            height=44,
            pos_hint={'center_x': 0.5, 'y': 0.03},
            font_size='16sp'
        )
        self._style_overlay_button(close_button, variant="secondary", font_size='16sp')
        self._bind_button_feedback(close_button)
        panel.add_widget(close_button)
        
        overlay.add_widget(panel)
        
        # Touch handler
        def on_journey_touch(instance, touch):
            if overlay.collide_point(*touch.pos):
                if not panel.collide_point(*touch.pos):
                    # Clicked outside panel - close
                    close_overlay()
                    return True
            return False
        
        def close_overlay(*args):
            # Unbind touch handler before cleanup
            if self.journey_overlay and hasattr(self.journey_overlay, '_touch_handler'):
                self.journey_overlay.unbind(on_touch_down=self.journey_overlay._touch_handler)
            self._cleanup_overlay('journey_overlay')
            if on_close_callback:
                on_close_callback()
        
        close_button.bind(on_release=close_overlay)
        
        # Store touch handler for cleanup
        overlay._touch_handler = on_journey_touch
        overlay.bind(on_touch_down=on_journey_touch)
        
        self.journey_overlay = overlay
        self.parent.add_widget(overlay)

    def show_onboarding_overlay(self, on_complete_callback):
        """Show cinematic first-launch onboarding with narrative sequence.
        
        Args:
            on_complete_callback: Called when onboarding is complete
        """
        # Prevent duplication
        if self.onboarding_overlay:
            self._log_overlay("Already showing", "onboarding_overlay")
            return
        
        self._log_overlay("Show", "onboarding_overlay")
        
        # Full-screen black overlay
        overlay = FloatLayout(size_hint=(1, 1))
        overlay.opacity = 0  # Start fully transparent
        
        with overlay.canvas.before:
            Color(0, 0, 0, 1)
            overlay.bg = Rectangle(pos=overlay.pos, size=overlay.size)
        
        def update_overlay_bg(*args):
            overlay.bg.pos = overlay.pos
            overlay.bg.size = overlay.size
        overlay.bind(pos=update_overlay_bg, size=update_overlay_bg)
        
        # Narrative text container (centered)
        narrative_label = Label(
            text="",
            font_size='28sp',
            bold=False,
            color=(0.95, 0.95, 0.95, 0),  # Start transparent
            size_hint=(0.8, None),
            height=120,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            halign='center',
            valign='middle',
            italic=True
        )
        narrative_label.text_size = (self.parent.width * 0.8, 120)
        overlay.add_widget(narrative_label)
        
        # Buttons container (hidden initially)
        button_container = Widget(
            size_hint=(1, None),
            height=120,
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        button_container.opacity = 0
        
        # Primary button
        primary_button = Button(
            text="Començar el teu primer dia",
            size_hint=(None, None),
            size=(380, 56),
            pos_hint={'center_x': 0.5, 'y': 0.55},
            background_normal="",
            background_color=(0.3, 0.9, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='20sp',
            bold=True
        )
        self._bind_button_feedback(primary_button)
        button_container.add_widget(primary_button)
        
        # Secondary button (English help)
        secondary_button = Button(
            text="Need help in English?",
            size_hint=(None, None),
            size=(280, 42),
            pos_hint={'center_x': 0.5, 'y': 0},
            background_normal="",
            background_color=(0.25, 0.28, 0.35, 1),
            color=(0.8, 0.8, 0.85, 1),
            font_size='15sp',
            bold=False
        )
        self._bind_button_feedback(secondary_button)
        button_container.add_widget(secondary_button)
        
        overlay.add_widget(button_container)
        
        # Store reference for cleanup
        self.onboarding_overlay = overlay
        self.parent.add_widget(overlay)
        
        # Play subtle ambient city sound layers
        onboarding_ambience_layers = []
        try:
            self.audio.set_ambience("station")
            crowd = self.audio.play_event(AudioEvent.AMB_TUNNEL, volume=0.08, loop=True)
            street = self.audio.play_event(AudioEvent.AMB_STATION, volume=0.05, loop=True)
            onboarding_ambience_layers = [sound for sound in (crowd, street) if sound]
        except Exception:
            onboarding_ambience_layers = []
        
        # Animation sequence
        narrative_sequence = [
            "Acabes d’arribar a Barcelona.",
            "No coneixes ningú.",
            "El metro serà el teu primer aliat.",
            "Cada parada és una oportunitat."
        ]
        
        def show_text(text, delay, duration=0.6):
            """Animate text fade in"""
            def animate_in(dt):
                narrative_label.text = text
                anim = Animation(
                    color=(0.95, 0.95, 0.95, 1),
                    duration=duration,
                    transition='in_out_quad'
                )
                anim.start(narrative_label)
            self.schedule_event(animate_in, delay)
        
        def fade_out_text(delay, duration=0.5):
            """Animate text fade out"""
            def animate_out(dt):
                anim = Animation(
                    color=(0.95, 0.95, 0.95, 0),
                    duration=duration,
                    transition='in_out_quad'
                )
                anim.start(narrative_label)
            self.schedule_event(animate_out, delay)
        
        def show_buttons(delay):
            """Show buttons with fade in"""
            def animate_buttons(dt):
                anim = Animation(
                    opacity=1,
                    duration=0.8,
                    transition='in_out_quad'
                )
                anim.start(button_container)
            self.schedule_event(animate_buttons, delay)
        
        # Timeline (all times in seconds)
        # 0.0s: Fade in overlay from black
        fade_in = Animation(opacity=1, duration=0.6, transition='in_quad')
        fade_in.start(overlay)
        
        # 0.4s: First text
        show_text(narrative_sequence[0], 0.4)
        fade_out_text(1.3, 0.45)
        
        # 1.5s: Second text
        show_text(narrative_sequence[1], 1.5)
        fade_out_text(2.4, 0.45)
        
        # 2.6s: Third text
        show_text(narrative_sequence[2], 2.6)
        fade_out_text(3.5, 0.45)
        
        # 3.7s: Fourth text (stays visible)
        show_text(narrative_sequence[3], 3.7, 0.6)
        
        # 4.4s: Show buttons
        show_buttons(4.4)
        
        # Button callbacks
        def start_first_day(*args):
            # Fade out overlay
            fade_out = Animation(opacity=0, duration=0.5, transition='out_quad')
            
            def complete_onboarding(*args):
                for sound in onboarding_ambience_layers:
                    try:
                        sound.stop()
                    except Exception:
                        pass
                try:
                    self.audio.set_ambience("none")
                except Exception:
                    pass

                # Use cleanup method
                self._cleanup_overlay('onboarding_overlay')
                
                # Mark onboarding as complete
                from core.settings import SettingsManager
                settings = SettingsManager()
                settings.set('has_completed_onboarding', True)
                
                # Call completion callback (starts first_day_mode)
                if callable(on_complete_callback):
                    on_complete_callback()
            
            fade_out.bind(on_complete=complete_onboarding)
            fade_out.start(overlay)
        
        def show_english_help(*args):
            self._show_english_help_modal(start_first_day)
        
        primary_button.bind(on_release=start_first_day)
        secondary_button.bind(on_release=show_english_help)
    
    def _show_english_help_modal(self, on_close_callback):
        """Show English help modal explaining gameplay.
        
        Args:
            on_close_callback: Called when user closes the modal
        """
        # Semi-transparent overlay
        help_overlay = FloatLayout(size_hint=(1, 1))
        with help_overlay.canvas.before:
            Color(0, 0, 0, 0.85)
            help_overlay.bg = Rectangle(pos=help_overlay.pos, size=help_overlay.size)
        
        def update_help_bg(*args):
            help_overlay.bg.pos = help_overlay.pos
            help_overlay.bg.size = help_overlay.size
        help_overlay.bind(pos=update_help_bg, size=update_help_bg)
        
        # Help panel
        panel_width = 520
        panel_height = 420
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=16,
                accent_color=(0.3, 0.7, 0.9, 0.6),
                pattern=False,
                civic_mode=self._is_civic_mode()
            )
        
        # Title
        title = Label(
            text="How to Play",
            font_size='26sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        panel.add_widget(title)
        
        # Instructions
        instructions_text = (
            "Welcome to Barcelona!\n\n"
            "1. The game will show you the next station name (in Catalan)\n\n"
            "2. Drag the correct station token to the green circle\n\n"
            "3. Do it before the train arrives!\n\n"
            "Note: The entire game experience is in Catalan to help you "
            "learn the metro system and explore Barcelona like a local."
        )
        
        instructions = Label(
            text=instructions_text,
            font_size='16sp',
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(0.9, None),
            height=280,
            halign='left',
            valign='top',
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        instructions.text_size = (panel_width * 0.85, 280)
        panel.add_widget(instructions)
        
        # Start button
        start_button = Button(
            text="Start my first day in Catalan",
            size_hint=(None, None),
            size=(380, 50),
            pos_hint={'center_x': 0.5, 'y': 0.06},
            background_normal="",
            background_color=(0.3, 0.9, 0.5, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        self._bind_button_feedback(start_button)
        panel.add_widget(start_button)
        
        help_overlay.add_widget(panel)
        self.parent.add_widget(help_overlay)
        
        # Close callback
        def close_help(*args):
            if help_overlay in self.parent.children:
                self.parent.remove_widget(help_overlay)
            if callable(on_close_callback):
                on_close_callback()
        
        start_button.bind(on_release=close_help)

    def show_line_completed(self, total_stations, on_close_callback=None, title_text="LÍNIA COMPLETADA", repeat_label="Repetir línia", unlock_message=None, is_mini_route=False):
        """Show overlay when line is completed
        
        Args:
            total_stations (int): Number of stations completed
            on_close_callback (callable): Callback when overlay closes
            title_text (str): Title text to display
            repeat_label (str): Label for repeat button
            unlock_message (str): Optional unlock message (e.g., "Nova línia desbloquejada!")
            is_mini_route (bool): If True, emphasize replay button as primary action
        """
        # Prevent duplication
        if self.line_completed_overlay:
            self._log_overlay("Already showing", "line_completed_overlay")
            return
        
        self._log_overlay("Show", "line_completed_overlay")
        
        # Play completion sound (skip if already played in _show_mini_route_completed)
        if not is_mini_route:
            self.audio.play_line_completed()

        overlay = FloatLayout(size_hint=(1, 1))
        self._apply_overlay_vignette(overlay, base_alpha=0.68, edge_alpha=0.94, edge_ratio=0.1)

        panel_width = 540
        panel_height = 400 if unlock_message else 360
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=18,
                pattern=True,
                civic_mode=self._is_civic_mode()
            )

        title = Label(
            text=title_text,
            font_name=self.ui_font,
            font_size='28sp',
            bold=True,
            color=self._theme_color((0.95, 0.92, 0.85, 1)),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.92 if not unlock_message else 0.94}
        )
        panel.add_widget(title)

        subtitle = Label(
            text=f"{total_stations} estacions recorregudes",
            font_name=self.ui_font,
            font_size='18sp',
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'center_y': 0.64 if unlock_message else 0.58}
        )
        panel.add_widget(subtitle)
        
        # Unlock message (if present)
        if unlock_message:
            unlock_label = Label(
                text=unlock_message,
                font_name=self.ui_font,
                font_size='22sp',
                bold=True,
                color=(1.0, 0.85, 0.2, 1),  # Gold color
                size_hint=(1, None),
                height=40,
                pos_hint={'center_x': 0.5, 'center_y': 0.48}
            )
            panel.add_widget(unlock_label)
            
            # Pulse animation for unlock message
            def pulse_unlock(dt):
                Animation(font_size='25sp', duration=0.3, transition='out_quad').start(unlock_label)
                Animation(font_size='22sp', duration=0.3, transition='in_out_quad').start(unlock_label)
            
            unlock_pulse_event = self.events.schedule_interval(pulse_unlock, 0.8)

        # Button container
        button_container = Widget(
            size_hint=(1, None),
            height=120,
            pos_hint={'center_x': 0.5, 'y': 0.08}
        )
        panel.add_widget(button_container)

        # Choose button hierarchy based on context
        if is_mini_route:
            # Mini-route: Replay is primary action
            repeat_btn = Button(
                text=repeat_label,
                size_hint=(None, None),
                size=(220, 48),
                pos_hint={'center_x': 0.5, 'y': 0.58},
                font_size='18sp'
            )
            self._style_overlay_button(repeat_btn, variant="primary", font_size='18sp')
            self._bind_button_feedback(repeat_btn)
            button_container.add_widget(repeat_btn)
            
            # Secondary: Back to lines
            back_to_lines_btn = Button(
                text="Canviar línia",
                size_hint=(None, None),
                size=(160, 36),
                pos_hint={'center_x': 0.35, 'y': 0.05},
                font_size='14sp'
            )
            self._style_overlay_button(back_to_lines_btn, variant="secondary", font_size='14sp')
            self._bind_button_feedback(back_to_lines_btn)
            button_container.add_widget(back_to_lines_btn)
            
            # Tertiary: Exit
            exit_btn = Button(
                text="Sortir",
                size_hint=(None, None),
                size=(120, 36),
                pos_hint={'center_x': 0.68, 'y': 0.05},
                font_size='14sp'
            )
            self._style_overlay_button(exit_btn, variant="danger", font_size='14sp')
            self._bind_button_feedback(exit_btn)
            button_container.add_widget(exit_btn)
        else:
            # Full line completion: Back to lines is primary
            back_to_lines_btn = Button(
                text="Tornar a línies",
                size_hint=(None, None),
                size=(200, 42),
                pos_hint={'center_x': 0.5, 'y': 0.58},
                font_size='16sp'
            )
            self._style_overlay_button(back_to_lines_btn, variant="secondary", font_size='16sp')
            self._bind_button_feedback(back_to_lines_btn)
            button_container.add_widget(back_to_lines_btn)

            repeat_btn = Button(
                text=repeat_label,
                size_hint=(None, None),
                size=(180, 36),
                pos_hint={'center_x': 0.35, 'y': 0.05},
                font_size='14sp'
            )
            self._style_overlay_button(repeat_btn, variant="ghost", font_size='14sp')
            self._bind_button_feedback(repeat_btn)
            button_container.add_widget(repeat_btn)

            exit_btn = Button(
                text="Sortir",
                size_hint=(None, None),
                size=(120, 36),
                pos_hint={'center_x': 0.73, 'y': 0.05},
                font_size='14sp'
            )
            self._style_overlay_button(exit_btn, variant="danger", font_size='14sp')
            self._bind_button_feedback(exit_btn)
            button_container.add_widget(exit_btn)

        overlay.add_widget(panel)

        def pulse_title(dt):
            Animation(font_size='32sp', duration=0.25, transition='out_quad').start(title)
            Animation(font_size='28sp', duration=0.25, transition='in_out_quad').start(title)

        if self._line_completed_pulse_event:
            self._line_completed_pulse_event.cancel()
        self._line_completed_pulse_event = self.events.schedule_interval(pulse_title, 0.6)

        def close_overlay_and_navigate(target_screen):
            """Close overlay first, then navigate"""
            self._cleanup_overlay('line_completed_overlay')
            
            # Navigate to target screen
            from kivy.app import App
            from kivy.uix.screenmanager import FadeTransition
            app = App.get_running_app()
            manager = getattr(app, "root", None)
            if manager and hasattr(manager, "current"):
                manager.transition = FadeTransition(duration=0.25)
                manager.current = target_screen

        def repeat_line(*args):
            """Restart current line"""
            self._cleanup_overlay('line_completed_overlay')
            
            # Reset the game for current line
            if callable(on_close_callback):
                on_close_callback('repeat')

        back_to_lines_btn.bind(on_release=lambda x: close_overlay_and_navigate(SCREEN_LINES))
        repeat_btn.bind(on_release=repeat_line)
        exit_btn.bind(on_release=lambda x: close_overlay_and_navigate(SCREEN_COVER))
        
        self.line_completed_overlay = overlay
        self.parent.add_widget(overlay)
    
    def show_goal_celebration(self, station, daily_completed_today=False, daily_challenge_active=False):
        """Show celebration overlay when goal station is reached"""
        # Play celebration sound (use new dedicated sound)
        self.audio.play_goal_celebration_sound()

        overlay = FloatLayout()
        with overlay.canvas:
            Color(0, 0, 0, 0.88)
            Rectangle(pos=self.parent.pos, size=self.parent.size)

        panel_width = 520
        panel_height = 400
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=18,
                accent_color=(1.0, 0.85, 0.2, 0.6),
                pattern=False,
                civic_mode=self._is_civic_mode()
            )

        # Get station info
        station_id = normalize_station_id(station.name)
        station_info = self.tourist_data.get(station_id, {})
        icon = get_station_icon(station_info.get('tags', []))
        
        # Big icon at top
        icon_label = Label(
            text=icon,
            font_size='80sp',
            size_hint=(1, None),
            height=100,
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        panel.add_widget(icon_label)

        title = Label(
            text="OBJECTIU ACONSEGUIT!",
            font_size='28sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=50,
            pos_hint={'center_x': 0.5, 'top': 0.72}
        )
        panel.add_widget(title)

        if daily_challenge_active and daily_completed_today:
            daily_badge = Label(
                text="Repte completat avui!",
                font_size='16sp',
                bold=True,
                color=(0.3, 1.0, 0.5, 1),
                size_hint=(1, None),
                height=24,
                pos_hint={'center_x': 0.5, 'top': 0.64}
            )
            panel.add_widget(daily_badge)

        station_label = Label(
            text=f"Has arribat a {station.name}",
            font_size='24sp',
            bold=True,
            color=(0.95, 0.95, 1, 1),
            size_hint=(1, None),
            height=40,
            pos_hint={'center_x': 0.5, 'center_y': 0.52}
        )
        panel.add_widget(station_label)

        # Show station tip if available
        tip_text = station.tourist_tip_ca or station_info.get('tip_ca', 'Has arribat a la teva destinació!')
        tip_label = Label(
            text=tip_text,
            font_size='15sp',
            color=(0.9, 0.92, 0.95, 1),
            size_hint=(1, None),
            height=60,
            pos_hint={'center_x': 0.5, 'center_y': 0.35},
            halign='center',
            valign='center'
        )
        tip_label.text_size = (panel_width - 60, 60)
        panel.add_widget(tip_label)

        # Stats summary
        stats_text = f"Puntuació: {self.state.score}  •  Ratxa: {self.state.streak}"
        stats_label = Label(
            text=stats_text,
            font_size='16sp',
            bold=True,
            color=(1, 0.95, 0.7, 1),
            size_hint=(1, None),
            height=30,
            pos_hint={'center_x': 0.5, 'center_y': 0.20}
        )
        panel.add_widget(stats_label)

        # Button container
        button_container = Widget(
            size_hint=(1, None),
            height=80,
            pos_hint={'center_x': 0.5, 'y': 0.03}
        )
        panel.add_widget(button_container)

        # Primary button: Back to line selection
        back_to_lines_btn = Button(
            text="Explorar una altra línia",
            size_hint=(None, None),
            size=(240, 42),
            pos_hint={'center_x': 0.5, 'y': 0.45},
            background_normal="",
            background_color=(0.25, 0.7, 0.95, 1),
            color=(1, 1, 1, 1),
            font_size='15sp',
            bold=True
        )
        self._bind_button_feedback(back_to_lines_btn)
        button_container.add_widget(back_to_lines_btn)

        # Secondary button: Continue playing
        continue_btn = Button(
            text="Continuar jugant aquesta línia",
            size_hint=(None, None),
            size=(220, 36),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            background_normal="",
            background_color=(0.3, 0.75, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        self._bind_button_feedback(continue_btn)
        button_container.add_widget(continue_btn)

        overlay.add_widget(panel)

        # Pulse animation for title
        def pulse_title(dt):
            Animation(font_size='32sp', duration=0.25, transition='out_quad').start(title)
            Animation(font_size='28sp', duration=0.25, transition='in_out_quad').start(title)

        pulse_event = self.events.schedule_interval(pulse_title, 0.6)

        def close_and_navigate():
            """Close overlay and navigate to line selection"""
            self.events.cancel(pulse_event)
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)
            
            from kivy.app import App
            from kivy.uix.screenmanager import FadeTransition
            app = App.get_running_app()
            manager = getattr(app, "root", None)
            if manager and hasattr(manager, "current"):
                manager.transition = FadeTransition(duration=0.25)
                manager.current = SCREEN_LINES

        def continue_playing(*args):
            """Close overlay and continue playing"""
            self.events.cancel(pulse_event)
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)
            
            # Disable goal mode and continue
            self.state.goal_mode = False
            self.state.goal_station_id = None
            self._update_goal_label()
            
            # Find the game widget and schedule next round
            from kivy.app import App
            app = App.get_running_app()
            manager = getattr(app, "root", None)
            if manager and hasattr(manager, "get_screen"):
                try:
                    game_screen = manager.get_screen(SCREEN_GAME)
                    if hasattr(game_screen, "game_widget") and game_screen.game_widget:
                        # Schedule the next round
                        game_screen.game_widget.schedule_game_event(
                            lambda dt: game_screen.game_widget._start_next_round(),
                            0.3
                        )
                except Exception as e:
                    print(f"Error continuing after goal: {e}")

        back_to_lines_btn.bind(on_release=lambda x: close_and_navigate())
        continue_btn.bind(on_release=continue_playing)

        self.parent.add_widget(overlay)
    
    def schedule_event(self, callback, delay):
        """Schedule a Clock event and track it for cleanup"""
        return self.events.schedule_once(callback, delay)
    
    def cancel_all_round_events(self):
        """Cancel all scheduled events from current round to prevent overlapping callbacks"""
        self.events.cancel_all()
        
        # Cancel animation events
        if self._progress_animation:
            try:
                self._progress_animation.cancel(self.progress_bar_fill)
            except Exception:
                pass
            self._progress_animation = None
        
        if self._color_animation:
            try:
                self._color_animation.cancel(self.hud_panel)
            except Exception:
                pass
            self._color_animation = None
        
        # Clear feedback and zone labels to remove dangling messages
        self.feedback_label.text = ""
        self.zone_label.text = ""
    
    def show_game_over(self, is_new_record):
        """Mostrar pantalla de Game Over con mapa de ruta y recomendaciones turísticas"""
        overlay = FloatLayout()
        with overlay.canvas:
            Color(0, 0, 0, 0.85)
            Rectangle(pos=self.parent.pos, size=self.parent.size)
        
        panel_width = 520
        panel_height = 700  # Increased to fit recommendations
        panel = Widget(
            size_hint=(None, None),
            size=(panel_width, panel_height),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        with panel.canvas:
            draw_modernisme_frame(
                panel.canvas,
                pos=panel.pos,
                size=panel.size,
                radius=15,
                accent_color=(0.8, 0.2, 0.2, 0.6),
                pattern=False,
                civic_mode=self._is_civic_mode()
            )
        
        # Title and stats section
        game_over_text = "FI DEL TRAJECTE\n\n"
        if is_new_record:
            game_over_text += "🏆 NOU RÈCORD! 🏆\n\n"
        
        total_stations = len(self.state.line.stations)
        visited_count = len(self.state.visited_stations)
        
        # Determine which section of the line was reached
        max_station = max(self.state.visited_stations) if self.state.visited_stations else 0
        
        # Describe progress based on furthest station reached
        if max_station >= 25:
            section_text = f"Has recorregut {visited_count} estacions\ndel tram complet"
        elif max_station >= 19:
            section_text = f"Has recorregut {visited_count} estacions\ndel tram nord"
        elif max_station >= 12:
            section_text = f"Has recorregut {visited_count} estacions\ndel tram central"
        elif max_station >= 5:
            section_text = f"Has recorregut {visited_count} estacions\ndel tram central-sud"
        else:
            section_text = f"Has recorregut {visited_count} estacions\ndel tram sud"
        
        game_over_text += (
            f"Puntuació: {self.state.score}\n"
            f"Rècord: {self.state.high_score}\n"
            f"Millor ratxa: {self.state.streak}\n\n"
            f"{section_text}"
        )
        
        game_over_label = Label(
            text=game_over_text,
            font_size='20sp',
            bold=True,
            halign='center',
            valign='top',
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=160,
            pos_hint={'top': 1}
        )
        game_over_label.text_size = (panel_width - 40, 160)
        panel.add_widget(game_over_label)
        
        # Route map visualization
        route_map = Widget(
            size_hint=(None, None),
            size=(panel_width - 60, 180),  # Reduced height
            pos_hint={'center_x': 0.5, 'y': 0.62}  # Adjusted position
        )
        
        # Animation state for pulsing failed station
        pulse_state = {'time': 0}
        failed_ellipse_ref = {'ellipse': None, 'pos_instr': None}
        
        # Bind to draw the route
        def draw_route_map(widget, *args):
            widget.canvas.before.clear()
            with widget.canvas.before:
                line_y = widget.height / 2
                
                # Calculate station positions
                num_stations = len(self.state.line.stations)
                station_spacing = (widget.width - 20) / max(num_stations - 1, 1)
                
                # Find the furthest visited station
                max_visited = max(self.state.visited_stations) if self.state.visited_stations else 0
                
                # Draw line segments between consecutive stations
                for i in range(num_stations - 1):
                    segment_start_x = widget.x + 10 + (i * station_spacing)
                    segment_end_x = widget.x + 10 + ((i + 1) * station_spacing)
                    segment_width = segment_end_x - segment_start_x
                    
                    # Determine segment color based on whether both stations are visited
                    if i <= max_visited:
                        # Traveled segment - bright green
                        Color(0.3, 0.9, 0.4, 1)
                    else:
                        # Remaining segment - dim gray
                        Color(0.2, 0.2, 0.25, 0.5)
                    
                    # Draw segment
                    Rectangle(
                        pos=(segment_start_x, widget.y + line_y - 2),
                        size=(segment_width, 4)
                    )
                
                # Draw stations
                for i in range(num_stations):
                    station_x = widget.x + 10 + (i * station_spacing)
                    station_y = widget.y + line_y
                    
                    # Station visited?
                    if i in self.state.visited_stations:
                        # Reached station - bright green
                        Color(0.3, 0.9, 0.4, 1)
                        radius = 8
                    else:
                        # Not reached - dark gray
                        Color(0.25, 0.25, 0.3, 1)
                        radius = 5
                    
                    # Draw station node
                    Ellipse(
                        pos=(station_x - radius, station_y - radius),
                        size=(radius * 2, radius * 2)
                    )
                    
                    # Label terminal stations
                    if i == 0 or i == num_stations - 1:
                        station = self.state.line.stations[i]
                        label_text = station.name
                        label = CoreLabel(text=label_text, font_size=12)
                        label.refresh()
                        texture = label.texture
                        
                        label_y = station_y - 25 if i == 0 else station_y + 15
                        Color(0.8, 0.8, 0.85, 1)
                        Rectangle(
                            pos=(station_x - texture.width / 2, label_y),
                            size=texture.size,
                            texture=texture
                        )
                
                # Draw failed station with pulsing red effect
                if self.state.failed_station_index is not None:
                    failed_idx = self.state.failed_station_index
                    if 0 <= failed_idx < num_stations:
                        failed_x = widget.x + 10 + (failed_idx * station_spacing)
                        failed_y = widget.y + line_y
                        
                        # Calculate pulse radius (will be animated)
                        import math
                        base_radius = 10
                        pulse_amplitude = 3
                        pulse_radius = base_radius + pulse_amplitude * abs(math.sin(pulse_state['time'] * 3))
                        
                        # Draw pulsing red node
                        Color(0.95, 0.2, 0.2, 0.9)  # Bright red
                        failed_ellipse = Ellipse(
                            pos=(failed_x - pulse_radius, failed_y - pulse_radius),
                            size=(pulse_radius * 2, pulse_radius * 2)
                        )
                        
                        # Store reference for animation
                        failed_ellipse_ref['ellipse'] = failed_ellipse
                        failed_ellipse_ref['station_x'] = failed_x
                        failed_ellipse_ref['station_y'] = failed_y
        
        # Animation function for pulsing failed station
        def animate_pulse(dt):
            pulse_state['time'] += dt
            if failed_ellipse_ref['ellipse'] is not None:
                # Redraw to update pulse
                draw_route_map(route_map)
        
        # Schedule pulse animation
        pulse_event = self.events.schedule_interval(animate_pulse, 1/30)  # 30 FPS
        
        route_map.bind(pos=draw_route_map, size=draw_route_map)
        panel.bind(pos=draw_route_map, size=draw_route_map)
        draw_route_map(route_map)
        
        panel.add_widget(route_map)
        
        # Tourist recommendations section
        recommendations = self.get_tourist_recommendations(3)
        
        if recommendations:
            # Recommendations title
            rec_title_label = Label(
                text="LLOCS D’INTERÈS:",
                font_size='16sp',
                bold=True,
                halign='center',
                valign='center',
                color=(0.9, 0.9, 1, 1),
                size_hint=(1, None),
                height=30,
                pos_hint={'center_x': 0.5, 'y': 0.55}
            )
            panel.add_widget(rec_title_label)
            
            # Recommendations container
            rec_y_positions = [0.44, 0.31, 0.18]  # Positions for 3 recommendations
            
            for idx, rec in enumerate(recommendations):
                rec_container = Widget(
                    size_hint=(None, None),
                    size=(panel_width - 60, 80),
                    pos_hint={'center_x': 0.5, 'y': rec_y_positions[idx]}
                )
                
                # Background for recommendation
                with rec_container.canvas.before:
                    Color(0.2, 0.2, 0.25, 0.8)
                    rec_bg = RoundedRectangle(
                        pos=rec_container.pos,
                        size=rec_container.size,
                        radius=[8]
                    )
                
                # Update background position when container moves
                def update_rec_bg(widget, bg_instr=rec_bg):
                    bg_instr.pos = widget.pos
                    bg_instr.size = widget.size
                rec_container.bind(pos=update_rec_bg, size=update_rec_bg)
                
                # Icon label
                icon_label = Label(
                    text=rec['icon'],
                    font_size='32sp',
                    size_hint=(None, None),
                    size=(50, 80),
                    pos=(0, 0),
                    halign='center',
                    valign='center'
                )
                icon_label.text_size = (50, 80)
                rec_container.add_widget(icon_label)
                
                # Station name and tip
                info_text = f"[b]{rec['station']}[/b]\n[size=13sp]{rec['one_liner']}[/size]"
                info_label = Label(
                    text=info_text,
                    markup=True,
                    font_size='15sp',
                    size_hint=(None, None),
                    size=(panel_width - 220, 80),
                    pos=(60, 0),
                    halign='left',
                    valign='center',
                    color=(0.95, 0.95, 1, 1)
                )
                info_label.text_size = (panel_width - 220, 80)
                rec_container.add_widget(info_label)
                
                # "Jugar fins aquí" button
                play_to_btn = Button(
                    text="Jugar fins aquí",
                    size_hint=(None, None),
                    size=(130, 35),
                    pos=(panel_width - 190, 22),
                    background_normal="",
                    background_color=(0.3, 0.75, 0.4, 1),
                    color=(1, 1, 1, 1),
                    font_size='13sp',
                    bold=True
                )
                self._bind_button_feedback(play_to_btn)
                rec_container.add_widget(play_to_btn)
                
                # Bind button to start goal mode with this station
                def create_goal_handler(station_id):
                    def start_goal_mode(*args):
                        self.events.cancel(pulse_event)
                        if overlay in self.parent.children:
                            self.parent.remove_widget(overlay)
                        
                        # Find the game widget and reset with goal mode
                        from kivy.app import App
                        app = App.get_running_app()
                        manager = getattr(app, "root", None)
                        if manager and hasattr(manager, "get_screen"):
                            try:
                                game_screen = manager.get_screen(SCREEN_GAME)
                                if hasattr(game_screen, "game_widget") and game_screen.game_widget:
                                    game_screen.game_widget.reset_run(
                                        goal_mode=True,
                                        goal_station_id=station_id
                                    )
                            except Exception as e:
                                print(f"Error starting goal mode: {e}")
                    return start_goal_mode
                
                play_to_btn.bind(on_release=create_goal_handler(rec['station_id']))
                
                panel.add_widget(rec_container)
        
        # Add buttons at bottom
        button_container = Widget(
            size_hint=(None, None),
            size=(panel_width - 40, 50),
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        
        # Back to lines button (primary)
        back_to_lines_btn = Button(
            text="Tornar a línies",
            size_hint=(None, None),
            size=(180, 40),
            pos=(20, 5),
            background_normal="",
            background_color=(0.25, 0.7, 0.95, 1),
            color=(1, 1, 1, 1),
            font_size='15sp',
            bold=True
        )
        self._bind_button_feedback(back_to_lines_btn)
        button_container.add_widget(back_to_lines_btn)
        
        # Play again button (secondary)
        play_again_btn = Button(
            text="Jugar de nou",
            size_hint=(None, None),
            size=(150, 40),
            pos=(panel_width - 190, 5),
            background_normal="",
            background_color=(0.35, 0.55, 0.75, 1),
            color=(1, 1, 1, 1),
            font_size='15sp'
        )
        self._bind_button_feedback(play_again_btn)
        button_container.add_widget(play_again_btn)
        
        panel.add_widget(button_container)
        
        def navigate_to_lines(*args):
            """Navigate to line selection screen"""
            self.events.cancel(pulse_event)
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)
            
            from kivy.app import App
            from kivy.uix.screenmanager import FadeTransition
            app = App.get_running_app()
            manager = getattr(app, "root", None)
            if manager and hasattr(manager, "current"):
                manager.transition = FadeTransition(duration=0.25)
                manager.current = SCREEN_LINES
        
        def reset_game(*args):
            """Restart current line"""
            self.events.cancel(pulse_event)
            if overlay in self.parent.children:
                self.parent.remove_widget(overlay)
            
            # Find the game widget and reset it
            from kivy.app import App
            app = App.get_running_app()
            manager = getattr(app, "root", None)
            if manager and hasattr(manager, "get_screen"):
                try:
                    game_screen = manager.get_screen(SCREEN_GAME)
                    if hasattr(game_screen, "game_widget") and game_screen.game_widget:
                        game_screen.game_widget.reset_run()
                except Exception:
                    pass
        
        back_to_lines_btn.bind(on_release=navigate_to_lines)
        play_again_btn.bind(on_release=reset_game)
        
        overlay.add_widget(panel)
        self.parent.add_widget(overlay)


# ===========================
# INPUT CONTROLLER (Event Layer)
# ===========================

class InputController:
    """Handles all input events and validation"""
    
    def __init__(self, game_state, renderer, random_seed=None):
        self.state = game_state
        self.renderer = renderer
        self.timeout_event = None
        self.input_locked = False  # Prevent multiple drops per frame
        self._hovering_tokens = set()
        
        # Set random seed for reproducible runs
        if random_seed is not None:
            random.seed(random_seed)
    
    def generate_tokens(self, on_drop_callback):
        """Generar 3 tokens: 1 correcto + 2 distractores"""
        self.renderer.clear_tokens()
        
        all_station_ids = self.state.generate_token_ids()
        assert len(set(all_station_ids)) == 3, "Tokens must be unique!"
        
        # Calculate equal spacing with no overlap
        token_width = 140
        min_gap = 30  # Minimum visual gap between tokens
        spacing = token_width + min_gap  # Distance between token centers: 170
        
        center_x = self.renderer.parent.width / 2
        y_pos = 15
        
        # Three evenly-spaced positions (no shuffle - deterministic layout)
        positions = [
            (center_x - spacing, y_pos),  # Left
            (center_x, y_pos),            # Center
            (center_x + spacing, y_pos)   # Right
        ]
        
        # Create tokens with entrance animation
        for i, (station_name, (x, y)) in enumerate(zip(all_station_ids, positions)):
            token = StationToken(
                station_id=station_name,
                name_ca=station_name,
                line_color_hex=self.state.line.color,
                size_hint=(None, None),
                size=(140, 70),
                pos=(x - 70, y - 20)  # Start slightly below final position
            )
            token.set_on_drop_callback(on_drop_callback)
            token.set_on_drag_start_callback(self._on_token_drag_start)
            token.set_on_drag_move_callback(self._on_token_drag_move)
            token.set_on_drag_end_callback(self._on_token_drag_end)
            
            # Set initial animation state
            token.opacity = 0
            token.scale_value = 0.9
            token.rotation = random.uniform(-1, 1)  # Subtle random rotation
            
            # Add to container
            self.renderer.token_container.add_widget(token)
            self.renderer.tokens.append(token)
            
            # Animate entrance with staggered delay
            delay = i * 0.08  # 80ms stagger between tokens
            
            def animate_token(dt, tok=token, final_y=y):
                from kivy.animation import Animation
                
                # Animate upward movement and fade in
                move_anim = Animation(
                    pos=(tok.pos[0], final_y),
                    opacity=1,
                    duration=0.4,
                    transition='out_cubic'
                )
                
                # Animate scale bounce: 0.9 → 1.05 → 1.0
                scale_bounce = (
                    Animation(scale_value=1.05, duration=0.25, transition='out_quad') +
                    Animation(scale_value=1.0, duration=0.15, transition='in_out_quad')
                )
                
                # Start both animations
                move_anim.start(tok)
                scale_bounce.start(tok)
            
            self.renderer.schedule_event(lambda dt, t=token, y=y: animate_token(dt, t, y), delay)

    def _on_token_drag_start(self, token):
        """Handle token drag start feedback."""
        self.renderer.audio.play(
            AudioEvent.UI_PICK,
            volume=0.22,
            allow_overlap=True,
            cooldown_ms=150,
            priority=1,
        )

    def _on_token_drag_move(self, token, x, y):
        """Track hover state for the target drop zone."""
        if not self.state.is_waiting_for_answer or self.state.has_attempted:
            return

        node_x, node_y = self.renderer.line_view.get_node_pos(self.state.next_index)
        distance = ((x - node_x) ** 2 + (y - node_y) ** 2) ** 0.5
        acceptance_radius = self.state.calculate_drop_radius()

        token_key = id(token)
        if distance < acceptance_radius:
            if hasattr(token, "set_target_hover"):
                token.set_target_hover(True)
            if token_key not in self._hovering_tokens:
                self._hovering_tokens.add(token_key)
                self.renderer.audio.play(
                    AudioEvent.UI_HOVER_TARGET,
                    volume=0.18,
                    allow_overlap=True,
                    cooldown_ms=0,
                    priority=0,
                )
        else:
            if hasattr(token, "set_target_hover"):
                token.set_target_hover(False)
            if token_key in self._hovering_tokens:
                self._hovering_tokens.remove(token_key)

    def _on_token_drag_end(self, token, x, y):
        """Reset hover state when drag ends."""
        token_key = id(token)
        if token_key in self._hovering_tokens:
            self._hovering_tokens.remove(token_key)
        if hasattr(token, "set_target_hover"):
            token.set_target_hover(False)

        self.renderer.audio.play(
            AudioEvent.UI_DROP,
            volume=0.2,
            allow_overlap=True,
            cooldown_ms=80,
            priority=1,
        )
    
    def validate_drop(self, token, x, y):
        """Validate token drop position and timing"""
        # Input lock - prevent multiple drops in single frame
        if self.input_locked:
            return None
        
        # Check if waiting and not already attempted
        if not self.state.is_waiting_for_answer or self.state.has_attempted:
            return None
        
        # Check drop position
        node_x, node_y = self.renderer.line_view.get_node_pos(self.state.next_index)
        distance = ((x - node_x)**2 + (y - node_y)**2)**0.5
        elapsed_time = Clock.get_time() - self.state.move_start_time
        result = self.state.validate_drop(token.station_id, distance, elapsed_time)
        
        if result in ('timeout', 'correct', 'wrong'):
            self.input_locked = True
            return result
        
        # Outside drop zone
        self.renderer.audio.play(
            AudioEvent.SFX_INVALID_DROP,
            volume=0.35,
            allow_overlap=False,
            cooldown_ms=150,
            priority=2,
        )
        token.reset_position()
        return None
    
    def schedule_timeout(self, callback, duration):
        """Schedule timeout check"""
        if self.timeout_event:
            self.timeout_event.cancel()
        self.timeout_event = Clock.schedule_once(callback, duration)
    
    def cancel_timeout(self):
        """Cancel scheduled timeout"""
        if self.timeout_event:
            self.timeout_event.cancel()


# ===========================
# MAIN GAME (Orchestrator)
# ===========================

class ProximaParadaGame(FloatLayout):
    """Main game orchestrator - coordinates GameState, Renderer, and InputController"""
    
    def __init__(self, practice_mode=False, direction_mode=False, first_day_mode=False, random_seed=None, line_id="L3", metro_network=None, progress_manager=None, enable_settings_hotkey=True, goal_mode=False, goal_station_id=None, daily_challenge_date=None, mode=None, civic_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.civic_mode = civic_mode
        
        settings_manager = SettingsManager()
        practice_mode = settings_manager.get('practice_mode', practice_mode)
        direction_mode = settings_manager.get('direction_mode', direction_mode)
        subtitles_enabled = settings_manager.get('subtitles_enabled', True)

        if metro_network is None:
            data_path = Path(__file__).parent / "data" / "barcelona_metro_lines_stations.json"
            metro_network = load_metro_network(str(data_path))

        line = metro_network.get_line(line_id)
        if not line:
            line = metro_network.get_line("L3")
        if not line and metro_network.lines:
            line = metro_network.lines[0]
        if not line:
            raise ValueError("No metro line data available")
        
        # Initialize components
        self.game_state = GameState(
            line,
            line_id=line.id,
            practice_mode=practice_mode,
            direction_mode=direction_mode,
            first_day_mode=first_day_mode,
            random_seed=random_seed
        )
        mode_instance = mode
        if mode_instance is None:
            mode_instance = GoalMode(goal_station_id=goal_station_id) if goal_mode else FreeMode()
        self.game_state.set_mode(mode_instance)
        self.game_state.subtitles_enabled = subtitles_enabled
        self.line_id = line.id
        self.progress_manager = progress_manager or ProgressManager()
        self.daily_challenge_date = daily_challenge_date
        self.daily_challenge_active = bool(
            daily_challenge_date and self.game_state.goal_mode and self.game_state.goal_station_id
        )
        self.tourist_popup_open = False
        self.pending_next_round = False
        self.pending_vocab_card = False
        self.line_completed_run = False
        self.mini_route_limit = 5
        self.mini_route_progress = 0
        
        self.renderer = Renderer(self, self.game_state, civic_mode=civic_mode)
        self.input_controller = InputController(self.game_state, self.renderer, random_seed)
        self.enable_settings_hotkey = enable_settings_hotkey

        self.game_state.set_callbacks(
            on_round_start=self._on_engine_round_start,
            on_correct=self._handle_correct_answer,
            on_wrong=self._handle_wrong_answer,
            on_game_over=self._on_engine_game_over,
            on_line_completed=self._on_engine_line_completed
        )
        
        # Track game-level scheduled events (for round transitions)
        self.events = EventRegistry()
        self._game_over_event = None  # Track game over scheduling
        
        # Setup UI
        self.renderer.setup_all()

        
        # Set train arrival callback
        self.renderer.train.set_on_arrival_callback(self._on_train_arrived)
        
        # Check if first-time onboarding is needed
        has_completed_onboarding = settings_manager.get('has_completed_onboarding', False)
        
        if not has_completed_onboarding:
            # Show cinematic onboarding on first launch
            self.events.schedule_once(lambda dt: self._show_onboarding(), 0.5)
        else:
            # Show intro banner and direction mode cue if enabled
            self.events.schedule_once(lambda dt: self.renderer.show_intro_banner(), 0.1)
            if self.game_state.direction_mode:
                self.events.schedule_once(lambda dt: self.renderer.audio.play_direction_mode_cue(), 0.2)
            
            # Show tutorial and start game
            self.events.schedule_once(lambda dt: self._show_tutorial(), 0.3)
            self.events.schedule_once(lambda dt: self._start_next_round(), 0.6)
        
        # Keyboard event binding for settings
        if self.enable_settings_hotkey:
            from kivy.core.window import Window
            Window.bind(on_keyboard=self._on_keyboard)
    
    def schedule_game_event(self, callback, delay):
        """Schedule a game-level event and track it for cleanup"""
        return self.events.schedule_once(callback, delay)
    
    def cancel_game_events(self):
        """Cancel all pending game-level events (used before starting new round)"""
        self.events.cancel_all()
        
        # Cancel pending game over event
        if self._game_over_event:
            try:
                self._game_over_event.cancel()
            except Exception:
                pass
            self._game_over_event = None
    
    def _show_onboarding(self):
        """Show cinematic onboarding overlay on first launch"""
        def on_onboarding_complete():
            """Called when onboarding is completed - activate first_day_mode and start game"""
            # Activate first day mode
            self.game_state.first_day_mode = True
            self.game_state.first_day_progress = 0
            self.game_state.first_day_completed = False
            
            # Update UI to reflect first day mode
            self.renderer.update_title()
            self.renderer._update_first_day_progress()
            
            # Show intro banner
            self.renderer.show_intro_banner()
            
            # Show tutorial after a brief delay
            self.events.schedule_once(lambda dt: self._show_tutorial(), 0.5)
            
            # Start the game
            self.events.schedule_once(lambda dt: self._start_next_round(), 0.6)
        
        self.renderer.show_onboarding_overlay(on_onboarding_complete)
    
    def _show_tutorial(self):
        """Show tutorial overlay"""
        self.renderer.show_tutorial(self._dismiss_tutorial)
    
    def _dismiss_tutorial(self):
        """Dismiss tutorial"""
        self.renderer.dismiss_tutorial()
    
    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard events"""
        if not self.enable_settings_hotkey:
            return False
        # ESC or 'S' key opens settings
        if key == 27 or codepoint == 's' or codepoint == 'S':  # 27 is ESC
            self._toggle_settings_menu()
            return True
        return False

    def stop_game(self):
        """Stop scheduled events and audio when leaving the game screen."""
        self.renderer.cancel_all_round_events()
        self.input_controller.cancel_timeout()
        self.cancel_game_events()
        self.renderer.audio.stop_tunnel_sound(fade_duration=0.1)
        if self.renderer._line_completed_pulse_event:
            self.renderer._line_completed_pulse_event.cancel()
            self.renderer._line_completed_pulse_event = None

    def pause(self):
        """Pause gameplay and cancel pending events."""
        self.stop_game()
    
    def reset_run(self, goal_mode=False, goal_station_id=None, first_day_mode=False):
        """Reset the game for a fresh run of the current line
        
        Args:
            goal_mode (bool): Whether to activate goal mode
            goal_station_id (str): Normalized station ID of the goal (e.g., "SAGRADA_FAMILIA")
            first_day_mode (bool): Whether to activate first day mode
        """
        # Cancel all scheduled events
        self.renderer.cancel_all_round_events()
        self.input_controller.cancel_timeout()
        self.cancel_game_events()
        
        # Reset game state
        self.game_state.current_index = 0
        self.game_state.next_index = 1
        self.game_state.score = 0
        self.game_state.streak = 0
        self.game_state.mistakes = 0
        self.game_state.game_over = False
        self.game_state.bonus_lives = 0
        self.game_state.is_waiting_for_answer = False
        self.game_state.has_attempted = False
        self.game_state.answered_correctly = False
        self.game_state.consecutive_correct = 0
        self.game_state.consecutive_mistakes = 0
        self.game_state.stations_completed = 0
        self.game_state.visited_stations = set()
        self.game_state.visited_stations.add(0)
        self.game_state.failed_station_index = None
        
        # Set goal mode via mode selection
        mode_instance = GoalMode(goal_station_id=goal_station_id) if goal_mode else FreeMode()
        self.game_state.set_mode(mode_instance)
        
        # Set first day mode
        self.game_state.first_day_mode = first_day_mode
        if first_day_mode:
            self.game_state.first_day_progress = 0
            self.game_state.first_day_completed = False
        
        # Reset badge tracking
        self.game_state.visited_tags = set()
        self.game_state.unlocked_badges = set()
        
        # Reset flags
        self.tourist_popup_open = False
        self.pending_next_round = False
        self.line_completed_run = False
        self.mini_route_progress = 0
        
        # Reset input controller
        self.input_controller.input_locked = False
        
        # Clear UI
        self.renderer.clear_tokens()
        if hasattr(self.renderer, 'line_completed_overlay') and self.renderer.line_completed_overlay:
            if self.renderer.line_completed_overlay in self.parent.children:
                self.parent.remove_widget(self.renderer.line_completed_overlay)
            self.renderer.line_completed_overlay = None
        
        # Update UI to initial state
        self.renderer.update_hud()
        self.renderer.update_title()
        self.renderer._update_goal_label()  # Update goal marker and label
        self.renderer.line_view.set_current_index(0)
        self.renderer.train.reset()
        
        # Start intro and first round
        self.events.schedule_once(lambda dt: self.renderer.show_intro_banner(), 0.1)
        if self.game_state.direction_mode:
            self.events.schedule_once(lambda dt: self.renderer.audio.play_direction_mode_cue(), 0.2)
        self.events.schedule_once(lambda dt: self._start_next_round(), 0.5)
    
    def _toggle_settings_menu(self):
        """Show or hide settings menu"""
        if hasattr(self.renderer, 'settings_overlay') and self.renderer.settings_overlay:
            # Close settings if already open
            if self.renderer.settings_overlay in self.parent.children:
                self.parent.remove_widget(self.renderer.settings_overlay)
                self.renderer.settings_overlay = None
        else:
            # Open settings
            self.renderer.show_settings_overlay(self._on_settings_close)
    
    def _on_settings_close(self):
        """Callback when settings overlay is closed"""
        # Save current settings to JSON
        settings_manager = SettingsManager()
        settings_manager.set('practice_mode', self.game_state.practice_mode)
        settings_manager.set('direction_mode', self.game_state.direction_mode)
        settings_manager.set('subtitles_enabled', self.game_state.subtitles_enabled)
    
    def _start_next_round(self):
        """Start a new round"""
        if self.line_completed_run:
            return
        if self.game_state.game_over:
            return
        
        # Cancel all previous round's scheduled events to prevent overlapping callbacks
        self.renderer.cancel_all_round_events()
        self.input_controller.cancel_timeout()
        self.cancel_game_events()  # Cancel game-level events (game over, next round scheduling)
        
        # Unlock input for new round
        self.input_controller.input_locked = False
        
        # Start round in game state
        round_data = self.game_state.start_round(Clock.get_time())
        if not round_data:
            return

    def _on_engine_round_start(self, round_data):
        """Handle round start event from engine"""
        travel_duration = round_data.get('travel_duration')
        if travel_duration is not None:
            # Mini-route arcade timing: longer travel for comfortable decision loop
            # Target: 4-5s travel + 4-5s decision window = 8-10s per round
            # 5 rounds × 10s = 50-60s session (within 45-90s target)
            travel_duration = max(4.0, min(travel_duration * 0.85, 5.0))
        else:
            travel_duration = 4.2
        
        # Decision window extends beyond arrival for comfortable pacing
        decision_window = travel_duration + 4.5

        # Check for zone transition
        if round_data.get('zone_changed') and round_data.get('zone_name'):
            zone_name = round_data['zone_name']
            self.renderer.show_zone_transition(zone_name, duration=1.2)
            self.renderer.shift_hud_color(zone_name)

        # Update UI
        self.renderer.update_next_station(round_data['correct_station_id'])

        self.renderer._schedule_station_announcement(
            round_data['correct_station_id'],
            travel_duration
        )
        
        # Play coordinated round start sequence (zoom, highlight, ambience)
        self.renderer.play_round_start_sequence(round_data['correct_station_id'])
        
        self.renderer.update_stats()
        self.renderer._update_progress_display()  # Animate progress bar

        # Delay token generation until after arrival for cleaner pacing
        token_delay = travel_duration + 0.7
        self.renderer.schedule_event(
            lambda dt: self.input_controller.generate_tokens(self._on_token_dropped),
            token_delay
        )

        # Move train
        self.renderer.move_train(round_data['next_index'], travel_duration)

        # Schedule timeout with extended decision window
        self.input_controller.schedule_timeout(
            self._check_timeout,
            decision_window
        )
    
    def _on_token_dropped(self, token, x, y):
        """Handle token drop event"""
        result = self.input_controller.validate_drop(token, x, y)
        
        if result == 'timeout':
            self.game_state.handle_timeout()
        elif result == 'correct':
            self.game_state.handle_correct_answer()
        elif result == 'wrong':
            self.game_state.handle_wrong_answer()
        # None means invalid drop (outside zone or already attempted)
    
    def _handle_correct_answer(self, result=None):
        """Process correct answer"""
        self.input_controller.cancel_timeout()
        
        if result is None:
            result = self.game_state.handle_correct_answer()
        station = self.game_state.line.stations[self.game_state.next_index]
        station_id = normalize_station_id(station.name)
        self.progress_manager.mark_station_completed(self.line_id, station_id)
        if result.get('line_completed_run'):
            self.progress_manager.mark_line_completed(self.line_id)
            self.line_completed_run = True
        
        # Visual feedback
        streak_increased = self.game_state.streak > self.renderer.previous_streak
        self.renderer.play_success_feedback(self.game_state.next_index, streak_increased=streak_increased)
        self.renderer.show_feedback(result['message'], (0.2, 1, 0.3, 1), 1.2)
        self.renderer.hide_tokens()
        self.renderer.update_stats()

        if not self.game_state.goal_mode and not self.game_state.first_day_mode:
            self.mini_route_progress += 1
            if self.mini_route_progress >= self.mini_route_limit:
                self.mini_route_progress = 0
                self._show_mini_route_completed()
                return

        milestones = {
            5: "Primer trajecte superat",
            10: "Ja saps moure’t pel centre",
            20: "Comences a entendre la ciutat",
            40: "Ja no ets nouvingut",
        }
        share_milestones = {20, 40}
        stations_completed = result.get('stations_completed')
        if stations_completed in milestones:
            self.renderer.schedule_event(
                lambda dt, msg=milestones[stations_completed]: self.renderer.show_integration_milestone(msg),
                0.35
            )
        if stations_completed in share_milestones:
            self.renderer.schedule_event(
                lambda dt, msg=milestones[stations_completed]: self.renderer.generate_share_card(msg),
                0.6
            )
        if result.get('line_completed_run'):
            self.renderer.schedule_event(
                lambda dt: self.renderer.show_integration_milestone("Barceloní en procés"),
                0.2
            )
            self.renderer.schedule_event(
                lambda dt: self.renderer.generate_share_card("Barceloní en procés", line_completed=True),
                0.5
            )
        
        # Play bonus life sound if granted
        if result.get('life_granted'):
            self.renderer.audio.play_bonus_life_sound()
        
        # Check for milestone moment (every 5 stations)
        if result.get('is_milestone'):
            self.renderer.schedule_event(
                lambda dt: self.renderer.show_milestone_moment(result['stations_completed']),
                0.2
            )
            self.renderer.schedule_event(
                lambda dt: self.renderer.audio.play_milestone_cue(),
                0.3
            )
        
        # Check for badge unlocks
        unlocked_badges = result.get('unlocked_badges', [])
        if unlocked_badges:
            # Persist badges
            for badge_id in unlocked_badges:
                self.progress_manager.mark_badge_unlocked(self.line_id, badge_id)
            
            # Show badge notifications (staggered if multiple)
            for idx, badge_id in enumerate(unlocked_badges):
                delay = 0.8 + (idx * 1.5)  # Stagger multiple badges
                self.renderer.schedule_event(
                    lambda dt, bid=badge_id: self.renderer.show_badge_unlock(bid),
                    delay
                )
        
        # Check for goal reached
        if result.get('goal_reached'):
            # Persist goal completion
            self.progress_manager.mark_goal_completed(self.line_id)
            daily_completed_today = False
            if self.daily_challenge_active and self.daily_challenge_date:
                newly_marked = self.progress_manager.mark_daily_completed(self.daily_challenge_date)
                daily_completed_today = newly_marked or self.progress_manager.is_daily_completed(self.daily_challenge_date)

            self.renderer.schedule_event(
                lambda dt: self.renderer.show_goal_celebration(
                    station,
                    daily_completed_today=daily_completed_today,
                    daily_challenge_active=self.daily_challenge_active
                ),
                0.5
            )
            return  # Don't proceed to tourist popup or next round
        
        # Check for First Day Mode step completion
        if result.get('first_day_step_reached'):
            self.renderer._update_first_day_progress()
            
            # Show cultural popup for this step
            if result.get('first_day_completed'):
                # Full journey completed - persist
                self.progress_manager.mark_first_day_completed()
                
                self.renderer.schedule_event(
                    lambda dt: self.renderer.show_first_day_completion(),
                    0.5
                )
                return  # Don't proceed to next round
            else:
                # Step completed, show cultural narrative
                self.tourist_popup_open = True
                self.renderer.show_first_day_step_popup(station, lambda: self._after_first_day_step())
                return

        if self.line_completed_run:
            self._show_line_completed()
    
    def _handle_wrong_answer(self, result=None):
        """Process wrong answer or timeout"""
        if result is None:
            result = self.game_state.handle_wrong_answer()
        
        # Visual feedback
        self.renderer.animate_highlight(self.game_state.next_index)
        self.renderer.play_fail_feedback(self.game_state.next_index, timeout=result.get('type') == 'timeout')
        if result.get('type') == 'timeout':
            self.renderer.show_feedback(result['message'], (1, 0.7, 0.2, 1), 1.8)
        else:
            self.renderer.show_feedback(result['message'], (1, 0.2, 0.2, 1), 1.5)
        self.renderer.hide_tokens()
        self.renderer.update_stats()
    
    def _check_timeout(self, dt):
        """Check timeout callback"""
        if not self.game_state.has_attempted and self.game_state.is_waiting_for_answer:
            self.game_state.handle_timeout()
    
    def _on_train_arrived(self, node_index):
        """Train arrival callback - fade out tunnel sound and schedule next round"""
        # Transition into station ambience on arrival
        self.renderer.audio.set_ambience("station")

        station_name = None
        station = None
        if 0 <= node_index < len(self.game_state.line.stations):
            station = self.game_state.line.stations[node_index]
            station_name = station.name
        self.renderer.play_arrival_sequence(station_name, node_index=node_index)

        if station and station.tourist_highlight and station.tourist_priority >= 4:
            self.renderer.show_cultural_micro_injection(station)

        if self.tourist_popup_open:
            self.pending_vocab_card = True
        else:
            self.renderer.schedule_event(lambda dt: self.renderer.show_vocab_on_arrival(), 0.4)

        if self.line_completed_run:
            return

        if self.tourist_popup_open:
            self.pending_next_round = True
            return
        
        if self.game_state.answered_correctly:
            self.schedule_game_event(lambda dt: self._start_next_round(), 0.5)
        else:
            self.schedule_game_event(lambda dt: self._start_next_round(), 0.35)
    
    def _after_first_day_step(self):
        """Callback after First Day Mode step popup is closed"""
        self.tourist_popup_open = False
        if self.pending_vocab_card:
            self.pending_vocab_card = False
            self.renderer.show_vocab_on_arrival()
        # Continue to next round
        self.schedule_game_event(lambda dt: self._start_next_round(), 0.2)

    def _on_engine_game_over(self, game_over_data):
        """Handle game over event from engine"""
        self._game_over_event = self.schedule_game_event(lambda dt: self._game_over(), 0.6)

    def _on_engine_line_completed(self):
        """Handle line completed event from engine"""
        if not self.line_completed_run:
            self.line_completed_run = True
            self.progress_manager.mark_line_completed(self.line_id)

    def _show_line_completed(self):
        self.cancel_game_events()
        self.input_controller.cancel_timeout()
        total_stations = len(self.game_state.line.stations)
        def on_close(action=None):
            if action == 'repeat':
                # Reset and restart current line
                self.reset_run()
            else:
                # Default behavior or specific navigation handled by overlay buttons
                pass

        self.renderer.show_line_completed(total_stations, on_close_callback=on_close)

    def _show_mini_route_completed(self):
        """Show mini-route completion with celebration and unlock message"""
        self.cancel_game_events()
        self.input_controller.cancel_timeout()
        self.renderer.hide_tokens()
        
        # Check if this is the first mini-route completion
        is_first_completion = self.progress_manager.mark_mini_route_completed(self.line_id)
        
        # Strong celebration effects (themed)
        self.renderer._flash_screen((0.2, 0.9, 0.6, 0.4), duration=0.5)
        self.renderer.audio.play_line_completed()
        
        # Spawn celebration particles at center (use current index for visual reference)
        if hasattr(self.renderer, '_spawn_success_particles') and self.game_state.next_index is not None:
            self.renderer._spawn_success_particles(self.game_state.next_index)

        def on_close(action=None):
            if action == 'repeat':
                self.reset_run()

        # Show completion overlay with unlock message if first time
        unlock_message = "Nova línia desbloquejada!" if is_first_completion else None
        
        self.renderer.show_line_completed(
            self.mini_route_limit,
            on_close_callback=on_close,
            title_text="TRAM COMPLETAT",
            repeat_label="Una altra ruta",
            unlock_message=unlock_message,
            is_mini_route=True
        )
    
    def _game_over(self):
        """Handle game over"""
        self.cancel_game_events()
        self.renderer.cancel_all_round_events()
        game_over_data = self.game_state.check_game_over()
        if game_over_data:
            self.renderer.show_game_over(game_over_data['is_new_record'])


class ProximaParadaApp(App):
    """Aplicación principal"""
    
    def __init__(self, practice_mode=False, direction_mode=False, random_seed=None, civic_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.practice_mode = practice_mode
        self.direction_mode = direction_mode
        self.random_seed = random_seed
        self.civic_mode = civic_mode
    
    def build(self):
        cp("inside ProximaParadaApp.build()")
        cp("calling build_proxima_parada_root()")
        root_widget = build_proxima_parada_root(
            practice_mode=self.practice_mode,
            direction_mode=self.direction_mode,
            random_seed=self.random_seed,
            civic_mode=self.civic_mode
        )
        cp("build_proxima_parada_root() returned, exiting build()")
        return root_widget


if __name__ == '__main__':
    import sys
    direction_mode = '--direction' in sys.argv
    practice_mode = '--practice' in sys.argv
    civic_mode = '--civic' in sys.argv
    ProximaParadaApp(practice_mode=practice_mode, direction_mode=direction_mode, civic_mode=civic_mode).run()

