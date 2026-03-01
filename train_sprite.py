"""
TrainSprite - Animated train widget that moves along metro line nodes

Features smooth ease-in-out animation for natural train movement:
- Uses quintic easing (in_out_quint) by default for smooth acceleration/deceleration
- Interpolates position over time_to_arrival duration
- Starts slowly, accelerates smoothly, then decelerates before arrival
- Configurable easing functions for different movement styles
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from typing import Optional, Callable


class TrainSprite(Widget):
    """
    Animated train sprite that moves smoothly between line nodes
    Drawn as a candy-style rounded capsule
    
    Uses ease-in-out interpolation for smooth, natural movement:
    - Starts slowly (ease-in)
    - Accelerates in the middle
    - Slows down before arrival (ease-out)
    """
    
    # Properties for smooth animation
    train_x = NumericProperty(0)
    train_y = NumericProperty(0)
    glow_alpha = NumericProperty(0.0)
    trail_alpha = NumericProperty(0.0)
    tint_strength = NumericProperty(0.0)
    front_glow_alpha = NumericProperty(0.0)
    glow_color = ListProperty([0.85, 0.95, 1.0, 1])
    trail_color = ListProperty([1.0, 0.65, 0.25, 1])
    tint_color = ListProperty([0.25, 0.7, 1.0, 1])
    accent_color = ListProperty([0.2, 0.22, 0.26, 1])
    glass_glow_color = ListProperty([0.7, 0.9, 1.0, 1])
    
    def __init__(self, easing_function='in_out_cubic', **kwargs):
        # Set default size
        if 'size' not in kwargs and 'size_hint' not in kwargs:
            kwargs['size_hint'] = (None, None)
            kwargs['size'] = (40, 60)  # Vertical capsule
        
        super().__init__(**kwargs)
        
        # Path/line reference
        self.line_view = None
        self.current_node = 0
        
        # Visual settings
        self.train_color = [0.9, 0.3, 0.3, 1]  # Red train
        self.corner_radius = 20
        self._front_dir = 1
        
        # Animation settings
        self.current_animation = None
        self._idle_bounce_anim = None
        self._brake_anim = None
        self._speed_trail_anim = None
        self.is_moving = False
        # Easing function for smooth movement
        # Options: 'in_out_quint' (smooth), 'in_out_cubic' (moderate), 
        #          'in_out_sine' (gentle), 'in_out_expo' (dramatic)
        self.easing_function = easing_function
        
        # Callback when train arrives at node
        self.on_arrival_callback: Optional[Callable] = None
        
        # Bind train position to actual position
        self.bind(train_x=self._update_position, train_y=self._update_position)
        self.bind(pos=self.draw, size=self.draw)
        self.bind(glow_alpha=self.draw, trail_alpha=self.draw, tint_strength=self.draw)
        self.bind(front_glow_alpha=self.draw)
        
        # Initial draw
        self.draw()
        self._start_idle_bounce()
    
    def set_path(self, line_view):
        """
        Set the metro line path for the train to follow
        
        Args:
            line_view: LineMapView instance with node positions
        """
        self.line_view = line_view
        
        # Start at first node
        if self.line_view and self.line_view.node_count > 0:
            first_pos = self.line_view.get_node_pos(0)
            if first_pos:
                self.train_x, self.train_y = first_pos
                self.current_node = 0
                self._update_position()
    
    def move_to_node(self, node_index: int, duration: float = 1.0):
        """
        Animate train movement to a specific node with smooth easing
        
        Uses ease-in-out interpolation over the duration for natural movement:
        - Accelerates smoothly from current position
        - Maintains speed in the middle
        - Decelerates smoothly to arrival point
        
        Args:
            node_index: Target node index
            duration: Animation duration in seconds (time_to_arrival)
        """
        if not self.line_view:
            print("Warning: No path set for train")
            return
        
        if node_index < 0 or node_index >= self.line_view.node_count:
            print(f"Warning: Node index {node_index} out of bounds")
            return
        
        # Get target position
        target_pos = self.line_view.get_node_pos(node_index)
        if not target_pos:
            return
        
        target_x, target_y = target_pos
        
        # Stop any current animation
        if self.current_animation:
            self.current_animation.cancel(self)
        
        self.is_moving = True
        self._stop_idle_bounce()

        self._front_dir = 1 if target_y >= self.train_y else -1

        distance = ((target_x - self.train_x) ** 2 + (target_y - self.train_y) ** 2) ** 0.5
        speed = distance / max(duration, 0.01)
        trail_intensity = max(0.0, min(0.5, (speed - 70) / 200))
        self.set_trail_intensity(trail_intensity, duration=0.2)
        front_glow = max(0.0, min(0.6, (speed - 110) / 160))
        self.set_front_glow(front_glow, duration=0.25)

        # Create smooth ease-in-out animation
        # The transition parameter controls the interpolation curve over duration
        self.current_animation = Animation(
            train_x=target_x,
            train_y=target_y,
            duration=duration,
            transition=self.easing_function  # Smooth ease-in-out interpolation
        )
        
        # Bind completion callback
        self.current_animation.bind(on_complete=lambda *args: self._on_arrival(node_index))
        
        # Start animation
        self.current_animation.start(self)
    
    def _on_arrival(self, node_index: int):
        """Called when train arrives at a node"""
        self.current_node = node_index
        self.is_moving = False
        self.set_trail_intensity(0.0, duration=0.35)
        self.set_front_glow(0.0, duration=0.3)
        
        # Trigger micro bounce effect
        self.play_arrival_bounce()
        
        if self.on_arrival_callback:
            self.on_arrival_callback(node_index)

        self._start_idle_bounce(delay=0.2)
    
    def play_arrival_bounce(self):
        """Play a subtle bounce effect when train arrives at station.
        
        Creates a quick downward compression then spring back for realistic stop.
        Total duration: ~180ms
        """
        # Cancel any existing bounce
        if hasattr(self, '_bounce_anim') and self._bounce_anim:
            self._bounce_anim.cancel(self)
        
        # Store original train position
        original_y = self.train_y
        
        self._play_brake_pulse()

        # Quick downward "squish" (compression on brake)
        bounce_down = Animation(
            train_y=original_y - 2,
            duration=0.06,
            transition='out_cubic'
        )
        
        # Spring back up slightly (overcompensate)
        bounce_up = Animation(
            train_y=original_y + 1,
            duration=0.05,
            transition='out_quad'
        )
        
        # Settle back to original position
        settle = Animation(
            train_y=original_y,
            duration=0.05,
            transition='in_out_quad'
        )
        
        # Chain animations: compress -> bounce -> settle
        self._bounce_anim = bounce_down + bounce_up + settle
        self._bounce_anim.start(self)

    def _play_brake_pulse(self):
        """Short brake squeeze to emphasize arrival."""
        if self._brake_anim:
            self._brake_anim.cancel(self)

        original_size = self.size
        original_pos = self.pos
        target_size = (original_size[0] * 1.04, original_size[1] * 0.92)
        offset_x = (target_size[0] - original_size[0]) / 2
        offset_y = (original_size[1] - target_size[1]) / 2
        target_pos = (original_pos[0] - offset_x, original_pos[1] + offset_y)

        squeeze = Animation(size=target_size, pos=target_pos, duration=0.08, transition='out_quad')
        release = Animation(size=original_size, pos=original_pos, duration=0.12, transition='in_out_quad')
        self._brake_anim = squeeze + release
        self._brake_anim.start(self)

    def _start_idle_bounce(self, delay=0.0):
        """Start a subtle idle bounce when the train is stationary."""
        if self.is_moving:
            return

        def start_anim(*args):
            if self.is_moving:
                return
            if self._idle_bounce_anim:
                self._idle_bounce_anim.cancel(self)
            base_y = self.train_y
            up = Animation(train_y=base_y + 2, duration=1.1, transition='in_out_sine')
            down = Animation(train_y=base_y - 2, duration=1.1, transition='in_out_sine')
            settle = Animation(train_y=base_y, duration=0.8, transition='out_sine')
            self._idle_bounce_anim = up + down + settle
            self._idle_bounce_anim.bind(on_complete=lambda *a: self._start_idle_bounce())
            self._idle_bounce_anim.start(self)

        if delay > 0:
            Clock.schedule_once(start_anim, delay)
        else:
            start_anim()

    def _stop_idle_bounce(self):
        """Stop idle bounce animation when train starts moving."""
        if self._idle_bounce_anim:
            self._idle_bounce_anim.cancel(self)
            self._idle_bounce_anim = None
    
    def set_on_arrival_callback(self, callback: Callable):
        """
        Set callback for when train arrives at a node
        
        Args:
            callback: Function with signature callback(node_index: int)
        """
        self.on_arrival_callback = callback
    
    def set_easing_function(self, easing: str):
        """
        Change the easing function for train movement
        
        Args:
            easing: Easing function name. Options:
                   - 'in_out_quint': Smooth, pronounced easing (default)
                   - 'in_out_cubic': Moderate easing
                   - 'in_out_sine': Gentle, sinusoidal easing
                   - 'in_out_expo': Dramatic, exponential easing
                   - 'in_out_quad': Subtle easing
                   - 'linear': No easing (constant speed)
        """
        self.easing_function = easing
    
    def _update_position(self, *args):
        """Update widget position based on train_x/y"""
        # Center the sprite on the train position
        self.x = self.train_x - self.width / 2
        self.y = self.train_y - self.height / 2
    
    def draw(self, *args):
        """Draw the train sprite"""
        self.canvas.clear()

        tint = max(0.0, min(1.0, self.tint_strength))
        base_color = self.train_color[:3]
        tint_color = self.tint_color[:3]
        blended = [
            base_color[i] * (1 - tint) + tint_color[i] * tint
            for i in range(3)
        ]
        blended_rgba = blended + [self.train_color[3]]

        with self.canvas:
            corner_radius = min(self.width, self.height) * 0.38

            if self.trail_alpha > 0.01:
                trail_dir = -1 if self._front_dir >= 0 else 1
                trail_offset = trail_dir * self.height * 0.22
                trail_length = self.height * 0.62
                trail_width = self.width * 1.18
                trail_x = self.center_x - trail_width / 2
                trail_y = self.center_y - trail_length / 2 + trail_offset

                Color(self.trail_color[0], self.trail_color[1], self.trail_color[2], self.trail_alpha * 0.22)
                RoundedRectangle(
                    pos=(trail_x, trail_y),
                    size=(trail_width, trail_length),
                    radius=[corner_radius]
                )

                Color(1.0, 0.95, 0.9, self.trail_alpha * 0.12)
                RoundedRectangle(
                    pos=(trail_x + 3, trail_y + 6),
                    size=(trail_width - 6, trail_length * 0.7),
                    radius=[corner_radius]
                )

            if self.glow_alpha > 0.01:
                Color(self.glow_color[0], self.glow_color[1], self.glow_color[2], self.glow_alpha * 0.6)
                RoundedRectangle(
                    pos=(self.x - 4, self.y - 4),
                    size=(self.width + 8, self.height + 8),
                    radius=[corner_radius + 4]
                )

            # Shadow
            Color(0, 0, 0, 0.3)
            shadow_offset = 2
            RoundedRectangle(
                pos=(self.x + shadow_offset, self.y - shadow_offset),
                size=self.size,
                radius=[corner_radius]
            )
            
            # Main body (darker base)
            darker_color = [c * 0.7 for c in blended] + [self.train_color[3]]
            Color(*darker_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[corner_radius]
            )
            
            # Top glossy part
            Color(*blended_rgba)
            gloss_height = self.height * 0.65
            RoundedRectangle(
                pos=(self.x, self.y + self.height - gloss_height),
                size=(self.width, gloss_height),
                radius=[corner_radius, corner_radius, 0, 0]
            )
            
            # Highlight (top shine)
            highlight_alpha = 0.5 + (tint * 0.4)
            highlight_color = [min(c * 1.4, 1.0) for c in blended] + [highlight_alpha]
            Color(*highlight_color)
            highlight_height = self.height * 0.2
            RoundedRectangle(
                pos=(self.x + 3, self.y + self.height - highlight_height - 3),
                size=(self.width - 6, highlight_height),
                radius=[corner_radius]
            )

            # Wrought-iron accent line
            Color(self.accent_color[0], self.accent_color[1], self.accent_color[2], 0.45)
            accent_x = self.x + self.width * 0.22
            Line(points=[accent_x, self.y + self.height * 0.18, accent_x, self.y + self.height * 0.86], width=1)
            
            # Windows (two circles)
            Color(0.9, 0.9, 1, 0.8)
            window_radius = 5
            window_y_top = self.y + self.height * 0.7
            window_y_bottom = self.y + self.height * 0.4
            
            # Top window
            Ellipse(
                pos=(self.center_x - window_radius, window_y_top - window_radius),
                size=(window_radius * 2, window_radius * 2)
            )
            
            # Bottom window
            Ellipse(
                pos=(self.center_x - window_radius, window_y_bottom - window_radius),
                size=(window_radius * 2, window_radius * 2)
            )

            if self.front_glow_alpha > 0.01:
                front_y = self.y + (self.height * 0.86 if self._front_dir >= 0 else self.height * 0.14)
                front_x = self.center_x
                Color(self.glass_glow_color[0], self.glass_glow_color[1], self.glass_glow_color[2], self.front_glow_alpha * 0.45)
                Ellipse(pos=(front_x - 14, front_y - 14), size=(28, 28))
                Color(self.glass_glow_color[0], self.glass_glow_color[1], self.glass_glow_color[2], self.front_glow_alpha * 0.25)
                Ellipse(pos=(front_x - 22, front_y - 22), size=(44, 44))
                Color(1.0, 1.0, 1.0, self.front_glow_alpha * 0.35)
                Ellipse(pos=(front_x - 6, front_y - 6), size=(12, 12))

    def pulse_glow(self, duration=0.3, peak=0.35):
        """Pulse a soft glow around the train."""
        if hasattr(self, '_glow_anim') and self._glow_anim:
            self._glow_anim.cancel(self)
        self.glow_alpha = 0.0
        self._glow_anim = Animation(glow_alpha=peak, duration=duration * 0.4, transition='out_quad')
        self._glow_anim += Animation(glow_alpha=0.0, duration=duration * 0.6, transition='in_quad')
        self._glow_anim.start(self)

    def set_trail_intensity(self, intensity, duration=0.25):
        """Animate trail intensity for streak feedback."""
        target = max(0.0, min(0.8, intensity))
        if hasattr(self, '_trail_anim') and self._trail_anim:
            self._trail_anim.cancel(self)
        self._trail_anim = Animation(trail_alpha=target, duration=duration, transition='in_out_quad')
        self._trail_anim.start(self)

    def set_front_glow(self, intensity, duration=0.2):
        """Animate a stained-glass glow at the front when moving fast."""
        target = max(0.0, min(0.75, intensity))
        if hasattr(self, '_front_glow_anim') and self._front_glow_anim:
            self._front_glow_anim.cancel(self)
        self._front_glow_anim = Animation(front_glow_alpha=target, duration=duration, transition='in_out_quad')
        self._front_glow_anim.start(self)

    def set_tint_strength(self, strength, duration=0.3):
        """Animate subtle tint shift for higher streaks."""
        target = max(0.0, min(0.4, strength))
        if hasattr(self, '_tint_anim') and self._tint_anim:
            self._tint_anim.cancel(self)
        self._tint_anim = Animation(tint_strength=target, duration=duration, transition='in_out_quad')
        self._tint_anim.start(self)
    
    def stop(self):
        """Stop any current animation"""
        if self.current_animation:
            self.current_animation.cancel(self)
            self.current_animation = None
