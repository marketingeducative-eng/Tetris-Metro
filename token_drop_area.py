"""
TokenDropArea - Container for managing draggable station tokens
"""
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from station_token import StationToken
from typing import List, Dict, Optional, Callable
import random


class TokenDropArea(BoxLayout):
    """
    Container that manages a queue of station tokens
    Shows 3 visible tokens at a time, spawns new ones as they're used
    """
    
    # Properties
    visible_count = NumericProperty(3)
    token_spacing = NumericProperty(10)
    
    def __init__(self, **kwargs):
        # Set defaults
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('spacing', 10)
        kwargs.setdefault('padding', [10, 10, 10, 10])
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 80)
        
        super().__init__(**kwargs)
        
        # Token queue
        self.token_queue: List[Dict] = []
        self.visible_tokens: List[StationToken] = []
        
        # Callbacks
        self.on_token_used_callback: Optional[Callable] = None
        self.on_token_dropped_callback: Optional[Callable] = None
        
        # Background
        with self.canvas.before:
            Color(0.2, 0.2, 0.25, 0.8)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        """Update background rectangle"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def set_token_queue(self, stations: List[Dict]):
        """
        Set the queue of stations to display as tokens
        
        Args:
            stations: List of dicts with keys: 'id', 'name', 'color'
                     Example: [{'id': 'station_1', 'name': 'Liceu', 'color': '#00923F'}, ...]
        """
        self.token_queue = stations.copy()
        self._refresh_visible_tokens()
    
    def add_to_queue(self, station: Dict):
        """
        Add a station to the queue
        
        Args:
            station: Dict with keys: 'id', 'name', 'color'
        """
        self.token_queue.append(station)
        if len(self.visible_tokens) < self.visible_count:
            self._refresh_visible_tokens()
    
    def set_on_token_used_callback(self, callback: Callable):
        """
        Set callback for when a token is successfully used
        
        Args:
            callback: Function with signature callback(token)
        """
        self.on_token_used_callback = callback
    
    def set_on_token_dropped_callback(self, callback: Callable):
        """
        Set callback for when a token is dropped
        
        Args:
            callback: Function with signature callback(token, x, y) -> bool
                     Should return True if drop was successful
        """
        self.on_token_dropped_callback = callback
    
    def _refresh_visible_tokens(self):
        """Refresh the visible tokens from the queue"""
        # Remove all current tokens
        for token in self.visible_tokens:
            self.remove_widget(token)
        self.visible_tokens.clear()
        
        # Add tokens from queue (up to visible_count)
        for i in range(min(self.visible_count, len(self.token_queue))):
            station = self.token_queue[i]
            self._create_and_add_token(station)
    
    def _create_and_add_token(self, station: Dict):
        """Create and add a token widget"""
        token = StationToken(
            station_id=station['id'],
            name_ca=station['name'],
            line_color_hex=station['color']
        )
        
        # Set drop callback
        token.set_on_drop_callback(self._on_token_dropped)
        
        self.add_widget(token)
        self.visible_tokens.append(token)
    
    def _on_token_dropped(self, token: StationToken, x: float, y: float):
        """Handle token drop"""
        # Call external callback if set
        accepted = False
        if self.on_token_dropped_callback:
            accepted = self.on_token_dropped_callback(token, x, y)
        
        if accepted:
            # Token was accepted - remove it and spawn next
            self._remove_token(token)
            
            # Callback for token used
            if self.on_token_used_callback:
                self.on_token_used_callback(token)
        else:
            # Token was rejected - return to original position
            token.reset_position()
    
    def _remove_token(self, token: StationToken):
        """Remove a token and spawn the next one"""
        # Remove from visible list
        if token in self.visible_tokens:
            self.visible_tokens.remove(token)
        
        # Remove widget
        self.remove_widget(token)
        
        # Remove from queue (first item)
        if self.token_queue:
            self.token_queue.pop(0)
        
        # Add next token if available
        if len(self.visible_tokens) < self.visible_count and self.token_queue:
            next_index = len(self.visible_tokens)
            if next_index < len(self.token_queue):
                self._create_and_add_token(self.token_queue[next_index])
    
    def get_visible_tokens(self) -> List[StationToken]:
        """Get list of currently visible tokens"""
        return self.visible_tokens.copy()
    
    def get_queue_length(self) -> int:
        """Get total length of token queue"""
        return len(self.token_queue)
    
    def clear(self):
        """Clear all tokens"""
        for token in self.visible_tokens:
            self.remove_widget(token)
        self.visible_tokens.clear()
        self.token_queue.clear()


class TokenDropAreaVertical(TokenDropArea):
    """Vertical variant of TokenDropArea"""
    
    def __init__(self, **kwargs):
        kwargs['orientation'] = 'vertical'
        super().__init__(**kwargs)
