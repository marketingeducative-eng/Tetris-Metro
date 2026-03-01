"""
LineMapView - Widget to display a schematic metro line with animated active station
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.properties import NumericProperty, ListProperty, StringProperty, BooleanProperty
from kivy.animation import Animation
from kivy.clock import Clock
from typing import Optional, List, Tuple
import colorsys


class LineMapView(Widget):
    """
    Schematic metro line view with vertical layout
    Displays stations as circles along a vertical line
    """
    
    # Properties
    next_index = NumericProperty(0)
    line_color = ListProperty([0.5, 0.5, 0.5, 1])  # RGBA
    pulse_scale = NumericProperty(1.0)
    pulse_alpha = NumericProperty(1.0)
    
    # Glow highlight properties
    glow_index = NumericProperty(-1)  # Index to highlight (-1 = none)
    glow_alpha = NumericProperty(0.0)  # Glow intensity
    glow_scale = NumericProperty(1.0)  # Glow pulse scale
    
    # Success flash properties
    success_index = NumericProperty(-1)  # Index with success animation
    success_alpha = NumericProperty(0.0)  # Success flash intensity
    success_scale = NumericProperty(1.0)  # Success flash scale
    
    # Arrival flash properties (subtle node flash on train arrival)
    arrival_index = NumericProperty(-1)  # Index with arrival animation
    arrival_alpha = NumericProperty(0.0)  # Arrival flash intensity
    
    # Goal marker properties (for tourist destination mode)
    goal_index = NumericProperty(-1)  # Index of goal station (-1 = none)
    goal_pulse = NumericProperty(1.0)  # Pulse animation for goal

    # Zoom properties
    zoom_scale = NumericProperty(1.0)
    zoom_center_index = NumericProperty(-1)

    # Visual mode toggles
    mosaic_enabled = BooleanProperty(True)

    # Interchange station indices (double-ring motif)
    interchange_indices = ListProperty([])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Line data
        self.line_id = ""
        self.station_names = []
        self.num_slots = 0
        
        # Visual settings
        self.slot_radius = 15
        self.slot_spacing = 50
        self.line_width = 4
        self.inactive_color = (0.45, 0.48, 0.52, 0.45)
        self.active_color = (0.9, 0.4, 0.3, 1)

        # Modernisme 2.0 visual tuning
        self.curve_strength = 6  # Subtle curvature in px
        self.mosaic_opacity = 0.05
        
        # Slot positions (calculated on draw)
        self.slot_positions = []
        
        # Animation
        self.pulse_anim = None
        self.glow_anim = None
        self.success_anim = None
        self.goal_anim = None
        self._zoom_anim = None
        self.arrival_anim = None
        
        # Bind properties to redraw
        self.bind(pos=self.draw, size=self.draw)
        self.bind(next_index=self.draw)
        self.bind(pulse_scale=self.draw, pulse_alpha=self.draw)
        self.bind(glow_index=self.draw, glow_alpha=self.draw, glow_scale=self.draw)
        self.bind(success_index=self.draw, success_alpha=self.draw, success_scale=self.draw)
        self.bind(goal_index=self.draw, goal_pulse=self.draw)
        self.bind(zoom_scale=self.draw, zoom_center_index=self.draw)
        self.bind(arrival_index=self.draw, arrival_alpha=self.draw)
        self.bind(mosaic_enabled=self.draw, interchange_indices=self.draw)
        
        # Start pulse animation on next_index
        self.bind(next_index=self._restart_pulse)
        self.bind(goal_index=self._start_goal_pulse)
    
    def set_line(self, line_id: str, line_color_hex: str, station_names: List[str], interchange_indices: Optional[List[int]] = None):
        """
        Set the metro line to display
        
        Args:
            line_id: Line identifier (e.g., "L3")
            line_color_hex: Color in hex format (e.g., "#00923F")
            station_names: List of station names
        """
        self.line_id = line_id
        self.station_names = station_names
        self.num_slots = len(station_names)
        if interchange_indices is not None:
            self.interchange_indices = list(interchange_indices)
        
        # Convert hex color to RGBA and refine for saturated-but-soft tone
        self.line_color = self._refine_line_color(self._hex_to_rgba(line_color_hex))
        self.active_color = (
            min(self.line_color[0] * 1.08, 1.0),
            min(self.line_color[1] * 1.08, 1.0),
            min(self.line_color[2] * 1.08, 1.0),
            1.0,
        )
        
        # Reset next_index
        self.next_index = 0
        
        # Redraw
        self.draw()

    def set_interchange_indices(self, indices: List[int]):
        """Set which stations should render with the interchange double-ring motif."""
        self.interchange_indices = list(indices)
    
    def set_next_index(self, index: int):
        """
        Set the active slot index
        
        Args:
            index: Index of the next expected station (0-based)
        """
        if 0 <= index < self.num_slots:
            self.next_index = index
    
    def get_slot_at(self, x: float, y: float) -> Optional[int]:
        """
        Get the slot index at the given position
        
        Args:
            x: X coordinate (screen space)
            y: Y coordinate (screen space)
            
        Returns:
            Slot index or None if no slot at that position
        """
        for i, (slot_x, slot_y) in enumerate(self.slot_positions):
            # Check if point is within slot radius (with some tolerance)
            distance_sq = (x - slot_x) ** 2 + (y - slot_y) ** 2
            hit_radius = self.slot_radius * 1.5  # Add tolerance
            if distance_sq <= hit_radius ** 2:
                return i
        return None
    
    def get_node_pos(self, index: int) -> Optional[Tuple[float, float]]:
        """
        Get the position of a node/slot by index
        
        Args:
            index: Node index (0-based)
            
        Returns:
            (x, y) tuple or None if index out of bounds
        """
        if 0 <= index < len(self.slot_positions):
            return self.slot_positions[index]
        return None

    def zoom_to_node(self, node_index: int, zoom_factor: float = 1.2, duration: float = 0.4, punch: bool = False):
        """Smooth zoom toward a node with optional punch effect.
        
        Args:
            node_index: Target node index
            zoom_factor: Maximum zoom level (default: 1.2)
            duration: Animation duration in seconds
            punch: If True, adds a quick punch-zoom effect (for arrivals)
        """
        if not (0 <= node_index < self.num_slots):
            return

        if self._zoom_anim:
            self._zoom_anim.cancel(self)
        self.zoom_center_index = node_index

        if punch:
            # Punch effect: quick over-zoom then settle (max 250ms total)
            punch_duration = min(0.25, duration * 0.5)
            punch_zoom = zoom_factor * 1.08  # 8% overshoot
            
            # Quick punch
            zoom_punch = Animation(zoom_scale=punch_zoom, duration=punch_duration * 0.4, t='out_cubic')
            # Settle to target
            zoom_settle = Animation(zoom_scale=zoom_factor, duration=punch_duration * 0.6, t='in_out_quad')
            
            def start_return(*args):
                zoom_out = Animation(zoom_scale=1.0, duration=duration * 0.6, t='in_out_cubic')
                
                def clear_center(*args):
                    self.zoom_center_index = -1
                
                zoom_out.bind(on_complete=clear_center)
                self._zoom_anim = zoom_out
                zoom_out.start(self)
            
            zoom_seq = zoom_punch + zoom_settle
            zoom_seq.bind(on_complete=lambda *args: Clock.schedule_once(lambda dt: start_return(), 0.3))
            self._zoom_anim = zoom_seq
            zoom_seq.start(self)
        else:
            # Standard smooth zoom
            zoom_in = Animation(zoom_scale=zoom_factor, duration=duration, t='out_quad')
            
            def start_return(*args):
                zoom_out = Animation(zoom_scale=1.0, duration=duration, t='in_out_quad')
                
                def clear_center(*args):
                    self.zoom_center_index = -1
                
                zoom_out.bind(on_complete=clear_center)
                self._zoom_anim = zoom_out
                zoom_out.start(self)
            
            zoom_in.bind(on_complete=lambda *args: start_return())
            self._zoom_anim = zoom_in
            zoom_in.start(self)
    
    @property
    def node_count(self) -> int:
        """Get the total number of nodes"""
        return self.num_slots
    
    def draw(self, *args):
        """Draw the metro line schematic"""
        if self.num_slots == 0:
            return
        
        self.canvas.clear()
        
        with self.canvas:
            # Calculate layout
            center_x = self.x + self.width / 2
            total_height = (self.num_slots - 1) * self.slot_spacing
            start_y = self.y + (self.height - total_height) / 2
            
            # Store slot positions
            base_positions = []
            for i in range(self.num_slots):
                slot_y = start_y + i * self.slot_spacing
                base_positions.append((center_x, slot_y))

            self.slot_positions = base_positions

            if 0 <= self.zoom_center_index < self.num_slots:
                target_y = base_positions[self.zoom_center_index][1]
                center_y = self.y + self.height / 2
                zoomed_positions = []
                for slot_x, slot_y in base_positions:
                    dy = slot_y - target_y
                    zoomed_y = target_y + dy * self.zoom_scale
                    zoomed_y += (center_y - target_y)
                    zoomed_positions.append((slot_x, zoomed_y))
                self.slot_positions = zoomed_positions

            if self.mosaic_enabled:
                self._draw_mosaic_pattern(center_x, start_y, total_height)
            
            # Draw vertical line connecting all slots (subtle organic curvature)
            Color(*self.line_color)
            line_points = self._build_curved_line_points(self.slot_positions)
            Line(points=line_points, width=self.line_width, cap='round', joint='round')
            
            # Draw dashed line from current to goal (if goal mode active)
            if self.goal_index >= 0 and self.next_index != self.goal_index:
                self._draw_goal_path()
            
            # Draw slots (circles)
            for i, (slot_x, slot_y) in enumerate(self.slot_positions):
                if i == self.success_index and self.success_alpha > 0:
                    # Success slot with green flash (drawn over everything)
                    self._draw_success_slot(slot_x, slot_y)
                elif i == self.arrival_index and self.arrival_alpha > 0:
                    # Arrival flash (subtle white pulse)
                    self._draw_arrival_slot(slot_x, slot_y)
                elif i == self.next_index:
                    # Active slot with pulse animation
                    self._draw_active_slot(slot_x, slot_y)
                elif i == self.glow_index and self.glow_alpha > 0:
                    # Glowing slot (correct answer highlight)
                    self._draw_glow_slot(slot_x, slot_y)
                elif i == self.goal_index and self.goal_index >= 0:
                    # Goal marker (tourist destination)
                    self._draw_goal_slot(slot_x, slot_y)
                else:
                    # Inactive slot
                    self._draw_inactive_slot(slot_x, slot_y)

                if i in self.interchange_indices:
                    self._draw_interchange_rings(slot_x, slot_y)

    def _refine_line_color(self, rgba):
        r, g, b, a = rgba
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        s = min(1.0, s * 1.12)
        if l < 0.55:
            l = min(0.6, l * 1.08)
        r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
        return (r2, g2, b2, min(0.95, a))

    def _build_curved_line_points(self, positions: List[Tuple[float, float]]) -> List[float]:
        if len(positions) < 2:
            return [coord for pos in positions for coord in pos]

        total_segments = max(1, len(positions) - 1)
        line_points = [positions[0][0], positions[0][1]]

        for i in range(total_segments):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            mid_y = (y1 + y2) / 2

            t = (i + 0.5) / total_segments
            offset = self.curve_strength * (0.5 - abs(0.5 - t))
            mid_x = x1 + offset

            line_points.extend([mid_x, mid_y, x2, y2])

        return line_points

    def _draw_mosaic_pattern(self, center_x: float, start_y: float, total_height: float):
        """Draw a faint geometric mosaic pattern behind the line."""
        if self.mosaic_opacity <= 0:
            return

        Color(1.0, 1.0, 1.0, min(0.06, self.mosaic_opacity))

        tile = max(6, int(self.slot_radius * 0.45))
        step_y = self.slot_spacing * 0.8
        step_x = self.slot_radius * 1.6

        rows = int(total_height / step_y) + 2
        for row in range(rows):
            y = start_y + row * step_y
            for col in (-1, 1):
                x = center_x + col * step_x
                points = [
                    x, y + tile,
                    x + tile, y,
                    x, y - tile,
                    x - tile, y,
                    x, y + tile,
                ]
                Line(points=points, width=1)
    
    def _draw_inactive_slot(self, x: float, y: float):
        """Draw an inactive slot as a ceramic dot"""
        radius = self.slot_radius
        ring_color = (0.95, 0.97, 1.0)
        inner_color = (0.72, 0.75, 0.8, 0.9)
        self._draw_ceramic_dot(x, y, radius, inner_color, ring_color, ring_alpha=0.28)
    
    def _draw_success_slot(self, x: float, y: float):
        """Draw a success flash (green burst on correct answer)"""
        radius = self.slot_radius
        scaled_radius = radius * self.success_scale
        
        # Outer burst (bright green expanding)
        burst_color = (0.2, 1.0, 0.3, self.success_alpha * 0.5)
        Color(*burst_color)
        burst_radius = scaled_radius * 2.8
        Ellipse(pos=(x - burst_radius, y - burst_radius),
                size=(burst_radius * 2, burst_radius * 2))
        
        # Middle ring
        ring_color = (0.3, 1.0, 0.4, self.success_alpha * 0.8)
        Color(*ring_color)
        ring_radius = scaled_radius * 2.0
        Ellipse(pos=(x - ring_radius, y - ring_radius),
                size=(ring_radius * 2, ring_radius * 2))
        
        # Solid bright green circle
        Color(0.2, 1.0, 0.3, self.success_alpha)
        Ellipse(pos=(x - scaled_radius, y - scaled_radius),
                size=(scaled_radius * 2, scaled_radius * 2))
        
        # Bright white center flash
        Color(1, 1, 1, self.success_alpha)
        center_radius = scaled_radius * 0.6
        Ellipse(pos=(x - center_radius, y - center_radius),
                size=(center_radius * 2, center_radius * 2))
    
    def _draw_arrival_slot(self, x: float, y: float):
        """Draw a subtle arrival flash (white pulse when train arrives)"""
        radius = self.slot_radius
        
        # Soft white glow (outer layer)
        glow_color = (1.0, 1.0, 1.0, self.arrival_alpha * 0.3)
        Color(*glow_color)
        glow_radius = radius * 1.8
        Ellipse(pos=(x - glow_radius, y - glow_radius),
                size=(glow_radius * 2, glow_radius * 2))
        
        # Middle ring
        ring_color = (0.95, 0.97, 1.0, self.arrival_alpha * 0.5)
        Color(*ring_color)
        ring_radius = radius * 1.4
        Ellipse(pos=(x - ring_radius, y - ring_radius),
                size=(ring_radius * 2, ring_radius * 2))
        
        # Core circle (bright white)
        Color(1.0, 1.0, 1.0, self.arrival_alpha * 0.7)
        Ellipse(pos=(x - radius, y - radius),
                size=(radius * 2, radius * 2))

        ring_color = (0.96, 0.98, 1.0)
        inner_color = (0.85, 0.88, 0.92, min(1.0, 0.5 + self.arrival_alpha))
        self._draw_ceramic_dot(x, y, radius * 0.9, inner_color, ring_color, ring_alpha=0.25)
    
    def _draw_glow_slot(self, x: float, y: float):
        """Draw a glowing slot with scale pulse (correct answer highlight)"""
        radius = self.slot_radius
        scaled_radius = radius * self.glow_scale
        
        # Outer glow (bright yellow/gold) - scales with pulse
        glow_color = (1.0, 0.9, 0.3, self.glow_alpha * 0.8)
        Color(*glow_color)
        glow_radius = scaled_radius * 2.5
        Ellipse(pos=(x - glow_radius, y - glow_radius),
                size=(glow_radius * 2, glow_radius * 2))
        
        # Middle glow - scales with pulse
        glow_color2 = (1.0, 1.0, 0.5, self.glow_alpha)
        Color(*glow_color2)
        glow_radius2 = scaled_radius * 1.8
        Ellipse(pos=(x - glow_radius2, y - glow_radius2),
                size=(glow_radius2 * 2, glow_radius2 * 2))
        
        # Solid circle - scales with pulse
        Color(1.0, 0.85, 0.2, self.glow_alpha)
        Ellipse(pos=(x - scaled_radius, y - scaled_radius), 
                size=(scaled_radius * 2, scaled_radius * 2))
        
        # Center highlight - scales with pulse
        Color(1, 1, 1, self.glow_alpha)
        center_radius = scaled_radius * 0.5
        Ellipse(pos=(x - center_radius, y - center_radius),
                size=(center_radius * 2, center_radius * 2))

        ring_color = (1.0, 0.95, 0.7)
        inner_color = (1.0, 0.85, 0.25, min(1.0, 0.5 + self.glow_alpha * 0.5))
        self._draw_ceramic_dot(x, y, scaled_radius * 0.9, inner_color, ring_color, ring_alpha=0.3)
    
    def _draw_active_slot(self, x: float, y: float):
        """Draw the active slot with stained-glass glow and ceramic core"""
        base_radius = self.slot_radius
        pulsed_radius = base_radius * self.pulse_scale

        glow_colors = self._stained_glass_colors(self.line_color)
        glow_radii = (2.3, 1.7, 1.25)
        glow_alphas = (0.18, 0.28, 0.4)
        for color, scale, alpha in zip(glow_colors, glow_radii, glow_alphas):
            Color(color[0], color[1], color[2], self.pulse_alpha * alpha)
            glow_radius = pulsed_radius * scale
            Ellipse(pos=(x - glow_radius, y - glow_radius),
                size=(glow_radius * 2, glow_radius * 2))

        ring_color = self._shift_hue_color(self.line_color[:3], 0.03)
        inner_color = (self.active_color[0], self.active_color[1], self.active_color[2], 1.0)
        self._draw_ceramic_dot(x, y, pulsed_radius, inner_color, ring_color, ring_alpha=0.35)
    
    def _draw_goal_slot(self, x: float, y: float):
        """Draw a goal marker (destination indicator with pulsing star/flag)"""
        radius = self.slot_radius
        pulsed_radius = radius * self.goal_pulse
        
        # Outer glow (gold/yellow pulsing)
        glow_color = (1.0, 0.85, 0.2, 0.6 * self.goal_pulse)
        Color(*glow_color)
        glow_radius = pulsed_radius * 2.2
        Ellipse(pos=(x - glow_radius, y - glow_radius),
                size=(glow_radius * 2, glow_radius * 2))
        
        # Middle ring (bright gold)
        Color(1.0, 0.9, 0.3, 0.8)
        ring_radius = pulsed_radius * 1.5
        Ellipse(pos=(x - ring_radius, y - ring_radius),
                size=(ring_radius * 2, ring_radius * 2))
        
        # Base circle (golden)
        Color(1.0, 0.75, 0.0, 1.0)
        Ellipse(pos=(x - pulsed_radius, y - pulsed_radius),
                size=(pulsed_radius * 2, pulsed_radius * 2))
        
        # Inner highlight
        Color(1.0, 1.0, 0.7, 1.0)
        inner_radius = pulsed_radius * 0.6
        Ellipse(pos=(x - inner_radius, y - inner_radius),
                size=(inner_radius * 2, inner_radius * 2))
        
        # Draw a star shape in the center using Lines
        import math
        star_radius = pulsed_radius * 0.8
        star_points = []
        for i in range(10):  # 5 points, alternating outer and inner
            angle = (i * 36 - 90) * math.pi / 180  # Start from top
            r = star_radius if i % 2 == 0 else star_radius * 0.4
            star_points.extend([
                x + r * math.cos(angle),
                y + r * math.sin(angle)
            ])
        # Close the star
        star_points.extend([star_points[0], star_points[1]])
        
        Color(1.0, 1.0, 1.0, 1.0)
        Line(points=star_points, width=2, cap='round', joint='round')

    def _draw_ceramic_dot(self, x: float, y: float, radius: float, inner_color, ring_color, ring_alpha: float = 0.3):
        """Draw a ceramic dot with glazed ring and solid inner core."""
        shadow_offset = 1
        Color(0, 0, 0, 0.12)
        Ellipse(pos=(x - radius + shadow_offset, y - radius - shadow_offset),
                size=(radius * 2, radius * 2))

        Color(ring_color[0], ring_color[1], ring_color[2], ring_alpha)
        Ellipse(pos=(x - radius, y - radius), size=(radius * 2, radius * 2))

        inner_radius = radius * 0.72
        Color(*inner_color)
        Ellipse(pos=(x - inner_radius, y - inner_radius),
                size=(inner_radius * 2, inner_radius * 2))

        highlight_radius = inner_radius * 0.45
        Color(1.0, 1.0, 1.0, 0.12)
        Ellipse(pos=(x - highlight_radius * 0.7, y + highlight_radius * 0.2),
                size=(highlight_radius * 1.4, highlight_radius * 1.4))

    def _draw_interchange_rings(self, x: float, y: float):
        """Draw double-ring motif for interchange stations."""
        outer_radius = self.slot_radius * 1.05
        inner_radius = self.slot_radius * 0.8
        ring_color = (self.line_color[0], self.line_color[1], self.line_color[2], 0.7)

        Color(*ring_color)
        Line(circle=(x, y, outer_radius), width=1.4)
        Line(circle=(x, y, inner_radius), width=1.2)

    def _stained_glass_colors(self, rgba):
        r, g, b, _ = rgba
        warm = self._shift_hue_color((r, g, b), 0.04)
        cool = self._shift_hue_color((r, g, b), -0.05)
        rich = self._shift_hue_color((r, g, b), 0.12)
        return (warm, cool, rich)

    def _shift_hue_color(self, rgb, shift: float):
        h, l, s = colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])
        h = (h + shift) % 1.0
        s = min(1.0, s * 1.1)
        l = min(0.85, l * 1.05)
        return colorsys.hls_to_rgb(h, l, s)
    
    def _draw_goal_path(self):
        """Draw a subtle dashed line from current station to goal"""
        if self.goal_index < 0 or self.next_index >= len(self.slot_positions):
            return
        
        # Get positions
        current_pos = self.slot_positions[self.next_index]
        goal_pos = self.slot_positions[self.goal_index]
        
        # Draw dashed line
        Color(1.0, 0.85, 0.2, 0.5)  # Gold, semi-transparent
        
        # Calculate dash pattern
        x1, y1 = current_pos
        x2, y2 = goal_pos
        
        import math
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        num_dashes = int(distance / 15)  # Dash every 15 pixels
        
        if num_dashes < 2:
            return
        
        dash_points = []
        for i in range(num_dashes):
            t = i / (num_dashes - 1)
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            dash_points.extend([x, y])
        
        # Draw dashed line
        Line(points=dash_points, width=2, dash_offset=2, dash_length=8)
    
    def _restart_pulse(self, *args):
        """Restart the pulse animation for the active slot"""
        # Stop existing animation
        if self.pulse_anim:
            self.pulse_anim.cancel(self)
        
        # Create continuous pulse animation
        anim_out = Animation(pulse_scale=1.3, pulse_alpha=0.6, duration=0.8, t='in_out_sine')
        anim_in = Animation(pulse_scale=1.0, pulse_alpha=1.0, duration=0.8, t='in_out_sine')
        self.pulse_anim = anim_out + anim_in
        self.pulse_anim.repeat = True
        self.pulse_anim.start(self)
    
    def _start_goal_pulse(self, *args):
        """Start continuous pulse animation for the goal marker"""
        # Only start if goal_index is valid
        if self.goal_index < 0:
            if self.goal_anim:
                self.goal_anim.cancel(self)
            return
        
        # Stop existing animation
        if self.goal_anim:
            self.goal_anim.cancel(self)
        
        # Create continuous pulse animation (slower and more gentle than active slot)
        self.goal_pulse = 1.0
        anim_out = Animation(goal_pulse=1.2, duration=1.2, t='in_out_sine')
        anim_in = Animation(goal_pulse=1.0, duration=1.2, t='in_out_sine')
        self.goal_anim = anim_out + anim_in
        self.goal_anim.repeat = True
        self.goal_anim.start(self)
    
    def highlight_node(self, index: int, duration: float = 0.4):
        """Highlight a specific node with a glow animation and scale pulse
        
        Animates with subtle scale pulse (1.0 → 1.15 → 1.0) combined with glow
        
        Args:
            index: Node index to highlight
            duration: Duration of the glow effect in seconds
        """
        # Stop any existing glow animation
        if self.glow_anim:
            self.glow_anim.cancel(self)
        
        # Set the node to glow
        self.glow_index = index
        self.glow_alpha = 0.0
        self.glow_scale = 1.0
        
        # Fade in with scale pulse: fade + scale up → hold → fade out + scale down
        # Scale pulse: 1.0 → 1.15 → 1.0 for subtle breathing effect
        fade_in = Animation(
            glow_alpha=1.0, 
            glow_scale=1.15, 
            duration=duration * 0.3, 
            t='in_out_cubic'
        )
        fade_out = Animation(
            glow_alpha=0.0, 
            glow_scale=1.0, 
            duration=duration * 0.7, 
            t='in_out_cubic'
        )
        self.glow_anim = fade_in + fade_out
        
        # Reset glow_index and scale when done
        def reset_glow(*args):
            self.glow_index = -1
            self.glow_scale = 1.0
        self.glow_anim.bind(on_complete=reset_glow)
        
        self.glow_anim.start(self)
    
    def success_flash(self, index: int, duration: float = 0.3):
        """Flash a node with green success animation
        
        Args:
            index: Node index to flash
            duration: Duration of the flash effect in seconds
        """
        # Stop any existing success animation
        if self.success_anim:
            self.success_anim.cancel(self)
        
        # Set the node for success flash
        self.success_index = index
        self.success_alpha = 0.0
        self.success_scale = 1.0
        
        # Quick burst: scale up then fade out
        burst = Animation(success_alpha=1.0, success_scale=1.5, 
                         duration=duration * 0.25, t='out_cubic')
        fade = Animation(success_alpha=0.0, success_scale=1.8,
                        duration=duration * 0.75, t='in_cubic')
        self.success_anim = burst + fade
        
        # Reset success_index when done
        def reset_success(*args):
            self.success_index = -1
            self.success_scale = 1.0
        self.success_anim.bind(on_complete=reset_success)
        
        self.success_anim.start(self)
    
    def arrival_flash(self, index: int, duration: float = 0.2):
        """Flash a node with subtle white pulse on train arrival.
        
        Args:
            index: Node index to flash
            duration: Duration of the flash effect in seconds (default: 0.2s)
        """
        # Stop any existing arrival animation
        if self.arrival_anim:
            self.arrival_anim.cancel(self)
        
        # Set the node for arrival flash
        self.arrival_index = index
        self.arrival_alpha = 0.0
        
        # Quick pulse: fade in then out
        pulse_in = Animation(arrival_alpha=0.8, duration=duration * 0.3, t='out_quad')
        pulse_out = Animation(arrival_alpha=0.0, duration=duration * 0.7, t='in_quad')
        self.arrival_anim = pulse_in + pulse_out
        
        # Reset arrival_index when done
        def reset_arrival(*args):
            self.arrival_index = -1
        self.arrival_anim.bind(on_complete=reset_arrival)
        
        self.arrival_anim.start(self)
    
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
            # Default gray
            return (0.5, 0.5, 0.5, 1.0)
    
    def on_touch_down(self, touch):
        """Handle touch events"""
        if self.collide_point(*touch.pos):
            slot_index = self.get_slot_at(touch.x, touch.y)
            if slot_index is not None:
                print(f"Touched slot {slot_index}: {self.station_names[slot_index]}")
                return True
        return super().on_touch_down(touch)
