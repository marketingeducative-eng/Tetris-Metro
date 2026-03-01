"""
StationToken - Draggable candy-style station widget
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle, PushMatrix, PopMatrix, Scale, Rotate, Ellipse
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.core.text import Label as CoreLabel
from typing import Callable, Optional, Tuple


class StationToken(Widget):
    """
    Draggable station token with candy-style appearance
    Represents a metro station that can be dragged and dropped
    """
    
    # Properties
    station_id = StringProperty("")
    name_ca = StringProperty("")
    line_color = ListProperty([0.5, 0.5, 0.5, 1])  # RGBA
    is_dragging = BooleanProperty(False)
    scale_value = NumericProperty(1.0)  # For entrance animation
    rotation = NumericProperty(0.0)  # Subtle rotation in degrees
    is_hovered = BooleanProperty(False)
    target_hover_alpha = NumericProperty(0.0)
    touch_padding = NumericProperty(12.0)
    
    def __init__(self, station_id: str, name_ca: str, line_color_hex: str, **kwargs):
        """
        Initialize station token
        
        Args:
            station_id: Unique identifier for the station
            name_ca: Station name in Catalan
            line_color_hex: Color in hex format (e.g., "#00923F")
        """
        # Set default size if not provided
        if 'size' not in kwargs and 'size_hint' not in kwargs:
            kwargs['size_hint'] = (None, None)
            kwargs['size'] = (180, 50)
        
        super().__init__(**kwargs)
        
        # Set properties
        self.station_id = station_id
        self.name_ca = name_ca
        self.line_color = self._hex_to_rgba(line_color_hex)
        
        # Drag state
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.original_pos = None
        self.original_parent = None
        
        # Callback for drop event
        self.on_drop_callback: Optional[Callable] = None
        self.on_drag_start_callback: Optional[Callable] = None
        self.on_drag_move_callback: Optional[Callable] = None
        self.on_drag_end_callback: Optional[Callable] = None
        self._drag_started = False
        self._drag_scale_anim = None
        
        # Visual settings
        self.corner_radius = 22
        self.shadow_offset = 3
        self.padding = 12
        self._hover_anim = None
        self._target_hover_anim = None
        
        # Bind properties to redraw
        self.bind(pos=self.draw, size=self.draw)
        self.bind(is_dragging=self.draw)
        self.bind(is_hovered=self.draw)
        self.bind(target_hover_alpha=self.draw)
        self.bind(scale_value=self.draw)
        self.bind(rotation=self.draw)
        
        # Initial draw
        self.draw()
    
    def set_on_drop_callback(self, callback: Callable):
        """
        Set callback for drop event
        
        Args:
            callback: Function with signature callback(token, x, y)
        """
        self.on_drop_callback = callback

    def set_on_drag_start_callback(self, callback: Callable):
        """Set callback for drag start event."""
        self.on_drag_start_callback = callback

    def set_on_drag_move_callback(self, callback: Callable):
        """Set callback for drag move event."""
        self.on_drag_move_callback = callback

    def set_on_drag_end_callback(self, callback: Callable):
        """Set callback for drag end event."""
        self.on_drag_end_callback = callback

    def _set_drag_scale(self, target_scale: float, duration: float):
        from kivy.animation import Animation

        if self._drag_scale_anim:
            self._drag_scale_anim.cancel(self)
        self._drag_scale_anim = Animation(
            scale_value=target_scale,
            duration=duration,
            transition="out_quad",
        )
        self._drag_scale_anim.start(self)

    def set_target_hover(self, active: bool, duration: float = 0.12):
        from kivy.animation import Animation

        target = 0.9 if active else 0.0
        if self._target_hover_anim:
            self._target_hover_anim.cancel(self)
        self._target_hover_anim = Animation(
            target_hover_alpha=target,
            duration=duration,
            transition="out_quad",
        )
        self._target_hover_anim.start(self)

    def _set_hovered(self, active: bool):
        if self.is_hovered == active:
            return
        self.is_hovered = active
    
    def draw(self, *args):
        """Draw the modernisme token"""
        self.canvas.clear()
        
        with self.canvas:
            # Apply scale transformation from center
            PushMatrix()
            
            # Calculate center point
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            
            # Translate to center, rotate, scale, translate back
            from kivy.graphics import Translate
            Translate(center_x, center_y, 0)
            Rotate(angle=self.rotation, origin=(0, 0))
            Scale(self.scale_value, self.scale_value, 1)
            Translate(-center_x, -center_y, 0)
            
            # Shadow (if not dragging)
            if not self.is_dragging:
                Color(0, 0, 0, 0.3)
                shadow_x = self.x + self.shadow_offset
                shadow_y = self.y - self.shadow_offset
                RoundedRectangle(
                    pos=(shadow_x, shadow_y),
                    size=self.size,
                    radius=[self.corner_radius]
                )

            glow_active = self.is_dragging or self.is_hovered
            if glow_active:
                Color(self.line_color[0], self.line_color[1], self.line_color[2], 0.18)
                RoundedRectangle(
                    pos=(self.x - 6, self.y - 6),
                    size=(self.width + 12, self.height + 12),
                    radius=[self.corner_radius + 6]
                )

            # Ceramic tile base
            base_color = [c * 0.78 for c in self.line_color[:3]] + [self.line_color[3]]
            Color(*base_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.corner_radius]
            )

            # Layered tile highlight
            top_tint = [min(c * 1.08, 1.0) for c in self.line_color[:3]] + [0.95]
            Color(*top_tint)
            gloss_height = self.height * 0.55
            RoundedRectangle(
                pos=(self.x, self.y + self.height - gloss_height),
                size=(self.width, gloss_height),
                radius=[self.corner_radius, self.corner_radius, 0, 0]
            )

            # Subtle gradient band
            band_color = [min(c * 1.2, 1.0) for c in self.line_color[:3]] + [0.35]
            Color(*band_color)
            band_height = self.height * 0.18
            RoundedRectangle(
                pos=(self.x + 6, self.y + self.height - band_height - 8),
                size=(self.width - 12, band_height),
                radius=[self.corner_radius]
            )

            # Thin inner border
            inner_inset = 3
            Color(1, 1, 1, 0.35)
            RoundedRectangle(
                pos=(self.x + inner_inset, self.y + inner_inset),
                size=(self.width - inner_inset * 2, self.height - inner_inset * 2),
                radius=[max(2, self.corner_radius - inner_inset)]
            )

            # Vitrail halo ring when hovering correct target
            if self.target_hover_alpha > 0.01:
                halo_radius = max(self.width, self.height) * 0.55
                Color(0.6, 0.9, 1.0, self.target_hover_alpha * 0.35)
                Ellipse(
                    pos=(self.center_x - halo_radius, self.center_y - halo_radius),
                    size=(halo_radius * 2, halo_radius * 2)
                )
                Color(0.75, 0.95, 1.0, self.target_hover_alpha * 0.18)
                halo_radius2 = halo_radius * 1.2
                Ellipse(
                    pos=(self.center_x - halo_radius2, self.center_y - halo_radius2),
                    size=(halo_radius2 * 2, halo_radius2 * 2)
                )
            
            # Draw text (inside transformation)
            self._draw_text_to_canvas()
            
            # Restore transformation matrix
            PopMatrix()
    
    def _draw_text_to_canvas(self):
        """Draw station name text directly to current canvas context"""
        text = self.name_ca
        font_size = 16
        letter_spacing = 0.6

        glyphs = []
        total_width = 0
        max_height = 0
        for ch in text:
            label = CoreLabel(
                text=ch,
                font_size=font_size,
                color=(1, 1, 1, 1),
                bold=True,
                font_name="Roboto"
            )
            label.refresh()
            glyphs.append(label)
            total_width += label.texture.width + letter_spacing
            max_height = max(max_height, label.texture.height)

        if glyphs:
            total_width -= letter_spacing

        text_x = self.x + (self.width - total_width) / 2
        text_y = self.y + (self.height - max_height) / 2

        Color(1, 1, 1, 1)
        cursor_x = text_x
        for label in glyphs:
            Rectangle(
                pos=(cursor_x, text_y),
                size=label.texture.size,
                texture=label.texture
            )
            cursor_x += label.texture.width + letter_spacing
    
    def on_touch_down(self, touch):
        """Handle touch down - start drag"""
        if self.collide_point(*touch.pos):
            # Store drag offset
            self.drag_offset_x = touch.x - self.x
            self.drag_offset_y = touch.y - self.y
            
            # Store original position and parent
            self.original_pos = (self.x, self.y)
            self.original_parent = self.parent
            
            # Mark as dragging
            self.is_dragging = True
            self.opacity = 0.85
            self.scale_value = 0.98
            self._set_drag_scale(1.03, 0.12)
            touch.grab(self)

            if not self._drag_started:
                self._drag_started = True
                if self.on_drag_start_callback:
                    self.on_drag_start_callback(self)
            
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch move - drag token"""
        if touch.grab_current is self:
            # Move token with touch
            self.x = touch.x - self.drag_offset_x
            self.y = touch.y - self.drag_offset_y
            if self.on_drag_move_callback:
                self.on_drag_move_callback(self, touch.x, touch.y)
            return True
        if self.collide_point(*touch.pos):
            self._set_hovered(True)
        else:
            self._set_hovered(False)
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up - drop token"""
        if touch.grab_current is self:
            touch.ungrab(self)
            self.is_dragging = False
            self._drag_started = False
            self.opacity = 1.0
            self._set_drag_scale(1.0, 0.12)
            self._set_hovered(False)

            if self.on_drag_end_callback:
                self.on_drag_end_callback(self, touch.x, touch.y)
            
            # Trigger drop callback
            if self.on_drop_callback:
                self.on_drop_callback(self, touch.x, touch.y)
            
            return True
        self._set_hovered(False)
        return super().on_touch_up(touch)

    def collide_point(self, x, y):
        pad = self.touch_padding
        return (self.x - pad <= x <= self.right + pad) and (self.y - pad <= y <= self.top + pad)
    
    def reset_position(self):
        """Reset to original position"""
        if self.original_pos:
            self.pos = self.original_pos
    
    def _hex_to_rgba(self, hex_color: str) -> Tuple[float, float, float, float]:
        """Convert hex color to RGBA tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b, 1.0)
        elif len(hex_color) == 8:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            a = int(hex_color[6:8], 16) / 255.0
            return (r, g, b, a)
        else:
            return (0.5, 0.5, 0.5, 1.0)
