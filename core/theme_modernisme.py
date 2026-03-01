"""
Modernisme 2.0 Theme System
============================

Centralized visual identity inspired by Barcelona's modernista architecture:
- Urban-dark base palette with subtle stained-glass accents
- Geometric clarity with organic warmth
- Supports civic_mode for institutional presentation

Usage:
    from core.theme_modernisme import THEME, theme_color, apply_panel_style
    
    color = theme_color('primary', civic_mode=False)
    apply_panel_style(my_widget, variant='card', civic_mode=False)
"""

from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional
import math
import config as app_config


# ============================================================================
# CORE THEME DATA STRUCTURE
# ============================================================================

@dataclass
class ThemeColors:
    """Color palette with modernista-inspired accents"""
    # Base urban-dark palette
    background_deep: Tuple[float, float, float, float] = (0.04, 0.05, 0.07, 1.0)
    background_mid: Tuple[float, float, float, float] = (0.07, 0.09, 0.12, 1.0)
    background_raised: Tuple[float, float, float, float] = (0.12, 0.16, 0.22, 1.0)
    
    # Modernista accent colors (inspired by Gaudí's stained glass)
    primary: Tuple[float, float, float, float] = (0.3, 0.9, 0.5, 1.0)  # Vibrant green
    primary_glow: Tuple[float, float, float, float] = (0.3, 0.9, 0.5, 0.25)
    
    secondary: Tuple[float, float, float, float] = (0.25, 0.7, 0.95, 1.0)  # Mediterranean blue
    secondary_glow: Tuple[float, float, float, float] = (0.25, 0.7, 0.95, 0.15)
    
    accent_warm: Tuple[float, float, float, float] = (0.95, 0.75, 0.35, 1.0)  # Golden amber
    accent_cool: Tuple[float, float, float, float] = (0.65, 0.85, 0.95, 1.0)  # Sky blue
    
    # Status colors
    success: Tuple[float, float, float, float] = (0.25, 1.0, 0.7, 1.0)
    warning: Tuple[float, float, float, float] = (1.0, 0.7, 0.2, 1.0)
    error: Tuple[float, float, float, float] = (0.95, 0.25, 0.25, 1.0)
    
    # Text colors
    text_primary: Tuple[float, float, float, float] = (0.95, 0.96, 0.98, 1.0)
    text_secondary: Tuple[float, float, float, float] = (0.75, 0.8, 0.85, 1.0)
    text_tertiary: Tuple[float, float, float, float] = (0.5, 0.55, 0.62, 1.0)
    
    # Interactive states
    interactive_idle: Tuple[float, float, float, float] = (0.35, 0.55, 0.75, 1.0)
    interactive_hover: Tuple[float, float, float, float] = (0.45, 0.65, 0.85, 1.0)
    interactive_press: Tuple[float, float, float, float] = (0.25, 0.45, 0.65, 1.0)
    
    # Borders and dividers
    border_subtle: Tuple[float, float, float, float] = (0.2, 0.22, 0.26, 0.35)
    border_medium: Tuple[float, float, float, float] = (0.3, 0.35, 0.4, 0.6)
    border_strong: Tuple[float, float, float, float] = (0.5, 0.55, 0.6, 0.85)


@dataclass
class ThemeColorsCivic:
    """Calmer color palette for civic/institutional mode"""
    # Slightly lighter, more neutral base
    background_deep: Tuple[float, float, float, float] = (0.06, 0.07, 0.09, 1.0)
    background_mid: Tuple[float, float, float, float] = (0.09, 0.11, 0.14, 1.0)
    background_raised: Tuple[float, float, float, float] = (0.14, 0.18, 0.24, 1.0)
    
    # More subdued accents
    primary: Tuple[float, float, float, float] = (0.3, 0.75, 0.6, 1.0)
    primary_glow: Tuple[float, float, float, float] = (0.3, 0.75, 0.6, 0.15)
    
    secondary: Tuple[float, float, float, float] = (0.3, 0.6, 0.8, 1.0)
    secondary_glow: Tuple[float, float, float, float] = (0.3, 0.6, 0.8, 0.12)
    
    accent_warm: Tuple[float, float, float, float] = (0.75, 0.6, 0.4, 1.0)
    accent_cool: Tuple[float, float, float, float] = (0.6, 0.75, 0.85, 1.0)
    
    success: Tuple[float, float, float, float] = (0.3, 0.8, 0.65, 1.0)
    warning: Tuple[float, float, float, float] = (0.85, 0.65, 0.3, 1.0)
    error: Tuple[float, float, float, float] = (0.8, 0.35, 0.35, 1.0)
    
    text_primary: Tuple[float, float, float, float] = (0.88, 0.9, 0.93, 1.0)
    text_secondary: Tuple[float, float, float, float] = (0.68, 0.73, 0.78, 1.0)
    text_tertiary: Tuple[float, float, float, float] = (0.48, 0.53, 0.58, 1.0)
    
    interactive_idle: Tuple[float, float, float, float] = (0.4, 0.5, 0.65, 1.0)
    interactive_hover: Tuple[float, float, float, float] = (0.5, 0.6, 0.75, 1.0)
    interactive_press: Tuple[float, float, float, float] = (0.3, 0.4, 0.55, 1.0)
    
    border_subtle: Tuple[float, float, float, float] = (0.25, 0.27, 0.31, 0.3)
    border_medium: Tuple[float, float, float, float] = (0.35, 0.4, 0.45, 0.5)
    border_strong: Tuple[float, float, float, float] = (0.5, 0.55, 0.6, 0.75)


@dataclass
class ThemeTypography:
    """Typography scale and rules"""
    # Font family
    sans_serif: str = "Roboto"
    
    # Size scale (in sp)
    size_xs: str = "11sp"
    size_sm: str = "14sp"
    size_base: str = "16sp"
    size_lg: str = "18sp"
    size_xl: str = "22sp"
    size_2xl: str = "28sp"
    size_3xl: str = "36sp"
    size_4xl: str = "48sp"
    
    # Letter spacing (for uppercase labels)
    spacing_tight: float = -0.02
    spacing_normal: float = 0.0
    spacing_wide: float = 0.05
    spacing_wider: float = 0.1
    
    # Line heights (multipliers)
    leading_tight: float = 1.15
    leading_normal: float = 1.4
    leading_loose: float = 1.7


@dataclass
class ThemeGeometry:
    """Border radii and stroke styles"""
    # Corner radii (in pixels)
    radius_sharp: list = field(default_factory=lambda: [2])
    radius_sm: list = field(default_factory=lambda: [6])
    radius_md: list = field(default_factory=lambda: [12])
    radius_lg: list = field(default_factory=lambda: [18])
    radius_xl: list = field(default_factory=lambda: [24])
    radius_full: list = field(default_factory=lambda: [9999])
    
    # Stroke widths (in pixels)
    stroke_hairline: float = 0.5
    stroke_thin: float = 1.0
    stroke_medium: float = 2.0
    stroke_thick: float = 3.0
    stroke_bold: float = 4.0
    
    # Glow radii (for stained-glass effect)
    glow_subtle: float = 8.0
    glow_medium: float = 16.0
    glow_strong: float = 24.0


@dataclass
class ThemeTimings:
    """Animation duration and easing curves"""
    # Durations (in seconds)
    instant: float = 0.0
    fast: float = 0.15
    normal: float = 0.25
    slow: float = 0.4
    slower: float = 0.6
    
    # Easing curves (Kivy transition names)
    ease_in: str = "in_quad"
    ease_out: str = "out_quad"
    ease_in_out: str = "in_out_quad"
    ease_bounce: str = "out_bounce"
    ease_elastic: str = "out_elastic"
    
    # Civic mode is 20% slower for calmer feel
    civic_multiplier: float = 1.2


@dataclass
class ModernismeTheme:
    """Complete Modernisme 2.0 theme specification"""
    colors: ThemeColors = field(default_factory=ThemeColors)
    colors_civic: ThemeColorsCivic = field(default_factory=ThemeColorsCivic)
    typography: ThemeTypography = field(default_factory=ThemeTypography)
    geometry: ThemeGeometry = field(default_factory=ThemeGeometry)
    timings: ThemeTimings = field(default_factory=ThemeTimings)


# Global theme instance
THEME = ModernismeTheme()


# ============================================================================
# COLOR UTILITIES
# ============================================================================

def theme_color(name: str, civic_mode: bool = False, alpha_override: Optional[float] = None) -> Tuple[float, float, float, float]:
    """Get a color from the theme palette.
    
    Args:
        name: Color name (e.g., 'primary', 'text_primary', 'background_mid')
        civic_mode: Use calmer civic palette
        alpha_override: Override alpha channel (0.0-1.0)
    
    Returns:
        Tuple of (r, g, b, a) values
    
    Examples:
        >>> theme_color('primary')
        (0.3, 0.9, 0.5, 1.0)
        >>> theme_color('primary', civic_mode=True)
        (0.3, 0.75, 0.6, 1.0)
        >>> theme_color('text_primary', alpha_override=0.5)
        (0.95, 0.96, 0.98, 0.5)
    """
    colors = THEME.colors_civic if civic_mode else THEME.colors
    
    if not hasattr(colors, name):
        # Fallback to default colors if name not found
        print(f"Warning: Color '{name}' not found in theme, using text_primary")
        color = colors.text_primary
    else:
        color = getattr(colors, name)
    
    if alpha_override is not None:
        return (color[0], color[1], color[2], alpha_override)
    return color


def desaturate_color(color: Tuple[float, float, float, float], factor: float = 0.5) -> Tuple[float, float, float, float]:
    """Desaturate a color by blending toward grayscale.
    
    Args:
        color: RGBA tuple
        factor: Desaturation amount (0.0=no change, 1.0=full grayscale)
    
    Returns:
        Desaturated RGBA tuple
    """
    r, g, b, a = color
    avg = (r + g + b) / 3.0
    return (
        r * (1 - factor) + avg * factor,
        g * (1 - factor) + avg * factor,
        b * (1 - factor) + avg * factor,
        a
    )


def brighten_color(color: Tuple[float, float, float, float], factor: float = 0.2) -> Tuple[float, float, float, float]:
    """Brighten a color by blending toward white.
    
    Args:
        color: RGBA tuple
        factor: Brightening amount (0.0=no change, 1.0=white)
    
    Returns:
        Brightened RGBA tuple
    """
    r, g, b, a = color
    return (
        min(1.0, r + (1.0 - r) * factor),
        min(1.0, g + (1.0 - g) * factor),
        min(1.0, b + (1.0 - b) * factor),
        a
    )


# ============================================================================
# WIDGET STYLING UTILITIES
# ============================================================================

def apply_panel_style(widget, variant: str = "panel", civic_mode: bool = False, glow: bool = False) -> None:
    """Apply modernisme panel styling to a widget.
    
    Args:
        widget: Kivy widget to style (must have canvas context)
        variant: Style variant - "panel", "hud", "card", "overlay"
        civic_mode: Use calmer civic styling
        glow: Add subtle stained-glass glow effect
    
    Effects:
        - Sets background color and border
        - Applies appropriate corner radius
        - Adds optional glow layers
    """
    variant_configs = {
        "panel": {
            "bg_color": "background_raised",
            "border_color": "border_medium",
            "radius": THEME.geometry.radius_lg,
            "glow_radius": THEME.geometry.glow_medium if glow else 0,
        },
        "hud": {
            "bg_color": "background_mid",
            "border_color": "border_subtle",
            "radius": THEME.geometry.radius_sm,
            "glow_radius": 0,
        },
        "card": {
            "bg_color": "background_raised",
            "border_color": "border_strong",
            "radius": THEME.geometry.radius_md,
            "glow_radius": THEME.geometry.glow_subtle if glow else 0,
        },
        "overlay": {
            "bg_color": "background_deep",
            "border_color": "border_subtle",
            "radius": THEME.geometry.radius_xl,
            "glow_radius": THEME.geometry.glow_strong if glow else 0,
        },
    }
    
    config = variant_configs.get(variant, variant_configs["panel"])
    
    with widget.canvas.before:
        # Background
        Color(*theme_color(config["bg_color"], civic_mode=civic_mode))
        bg_rect = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=config["radius"]
        )
        
        # Border
        Color(*theme_color(config["border_color"], civic_mode=civic_mode))
        border_line = Line(
            rounded_rectangle=(
                widget.x, widget.y,
                widget.width, widget.height,
                *config["radius"]
            ),
            width=THEME.geometry.stroke_thin
        )
    
    # Bind updates
    def update_graphics(instance, value):
        bg_rect.pos = instance.pos
        bg_rect.size = instance.size
        border_line.rounded_rectangle = (
            instance.x, instance.y,
            instance.width, instance.height,
            *config["radius"]
        )
    
    widget.bind(pos=update_graphics, size=update_graphics)


def apply_button_style(button, variant: str = "primary", civic_mode: bool = False) -> Dict:
    """Generate button style dict compatible with Kivy Button.
    
    Args:
        button: Kivy Button widget
        variant: "primary", "secondary", "tertiary", "ghost"
        civic_mode: Use calmer styling
    
    Returns:
        Dict with style properties to apply to button
    
    Example:
        >>> btn = Button()
        >>> style = apply_button_style(btn, variant='primary')
        >>> btn.background_normal = ""
        >>> btn.background_color = style['background_color']
    """
    variant_configs = {
        "primary": {
            "bg_color": theme_color("primary", civic_mode=civic_mode),
            "text_color": theme_color("background_deep", civic_mode=civic_mode),
            "font_size": THEME.typography.size_base,
            "bold": True,
        },
        "secondary": {
            "bg_color": theme_color("secondary", civic_mode=civic_mode),
            "text_color": theme_color("text_primary", civic_mode=civic_mode),
            "font_size": THEME.typography.size_base,
            "bold": False,
        },
        "tertiary": {
            "bg_color": theme_color("interactive_idle", civic_mode=civic_mode),
            "text_color": theme_color("text_secondary", civic_mode=civic_mode),
            "font_size": THEME.typography.size_sm,
            "bold": False,
        },
        "ghost": {
            "bg_color": (0, 0, 0, 0),
            "text_color": theme_color("text_secondary", civic_mode=civic_mode),
            "font_size": THEME.typography.size_sm,
            "bold": False,
        },
    }
    
    config = variant_configs.get(variant, variant_configs["primary"])
    
    return {
        "background_color": config["bg_color"],
        "color": config["text_color"],
        "font_size": config["font_size"],
        "bold": config["bold"],
        "font_name": THEME.typography.sans_serif,
    }


def get_animation_duration(speed: str = "normal", civic_mode: bool = False) -> float:
    """Get animation duration from theme.
    
    Args:
        speed: "instant", "fast", "normal", "slow", "slower"
        civic_mode: Apply 20% slowdown for calmer feel
    
    Returns:
        Duration in seconds
    """
    durations = {
        "instant": THEME.timings.instant,
        "fast": THEME.timings.fast,
        "normal": THEME.timings.normal,
        "slow": THEME.timings.slow,
        "slower": THEME.timings.slower,
    }
    
    duration = durations.get(speed, THEME.timings.normal)
    
    if civic_mode:
        duration *= THEME.timings.civic_multiplier
    
    return duration


# ============================================================================
# DECORATIVE PATTERNS (OPTIONAL)
# ============================================================================

def draw_modernisme_frame(canvas, pos: Tuple[float, float], size: Tuple[float, float],
                         radius: int = 18, accent_color: Tuple[float, float, float, float] = None,
                         pattern: bool = False, civic_mode: bool = False) -> None:
    """Draw Modernisme 2.0 frame with wrought iron-inspired accents.
    
    Creates a sophisticated panel background with:
    - Dark rounded base rectangle
    - Thin inner stroke (wrought iron accent)
    - Subtle corner ornaments
    - Optional faint mosaic pattern fill (5-8% opacity)
    
    Args:
        canvas: Kivy canvas context
        pos: (x, y) position tuple
        size: (width, height) size tuple
        radius: Corner radius for rounded rectangle (default: 18)
        accent_color: Optional override for accent stroke color (RGBA tuple)
        pattern: If True, add subtle mosaic pattern fill
        civic_mode: Use subtler civic theme colors
    
    Example:
        with widget.canvas.before:
            draw_modernisme_frame(widget.canvas.before, widget.pos, widget.size, 
                                 radius=20, pattern=False, civic_mode=False)
    """
    if not getattr(app_config, "modernisme_2_0_theme", True):
        x, y = pos
        width, height = size
        base_color = (0.08, 0.09, 0.12, 0.9)
        border_color = (0.35, 0.38, 0.42, 0.55)
        Color(*base_color)
        RoundedRectangle(pos=pos, size=size, radius=[radius])
        Color(*border_color)
        Line(
            rounded_rectangle=(x + 1.5, y + 1.5, width - 3.0, height - 3.0, max(2, radius - 2)),
            width=1.0,
        )
        return

    x, y = pos
    width, height = size
    
    # Background: Deep dark base
    bg_color = theme_color("background_raised", civic_mode=civic_mode)
    Color(*bg_color)
    RoundedRectangle(pos=pos, size=size, radius=[radius])
    
    # Optional mosaic pattern fill (very subtle)
    if pattern:
        pattern_opacity = 0.05 if not civic_mode else 0.035
        pattern_color = theme_color("accent_warm", civic_mode=civic_mode, alpha_override=pattern_opacity)
        Color(*pattern_color)
        
        # Diagonal cross-hatch pattern (simplified mosaic)
        stripe_spacing = 24
        for i in range(0, int(width + height), stripe_spacing):
            # Diagonal lines from top-left to bottom-right
            start_x = x + i
            start_y = y
            end_x = x
            end_y = y + i
            
            if start_x > x + width:
                start_x = x + width
                start_y = y + (i - width)
            if end_y > y + height:
                end_y = y + height
                end_x = x + (i - height)
            
            Line(points=[start_x, start_y, end_x, end_y], 
                 width=THEME.geometry.stroke_hairline)
    
    # Wrought iron accent stroke (inner border)
    if accent_color is None:
        # Default: dark teal/graphite inspired by Barcelona wrought iron
        accent_color = theme_color("border_strong", civic_mode=civic_mode, alpha_override=0.6)
    
    Color(*accent_color)
    inset = 3
    Line(
        rounded_rectangle=(x + inset, y + inset, width - inset*2, height - inset*2, radius - inset),
        width=THEME.geometry.stroke_thin
    )
    
    # Subtle corner ornaments (inspired by wrought iron details)
    corner_ornament_color = theme_color("accent_warm", civic_mode=civic_mode, alpha_override=0.12)
    Color(*corner_ornament_color)
    
    corner_size = 10
    corner_inset = 8
    
    # Top-left ornament
    Line(points=[
        x + corner_inset, y + corner_inset + corner_size,
        x + corner_inset, y + corner_inset,
        x + corner_inset + corner_size, y + corner_inset
    ], width=THEME.geometry.stroke_hairline)
    
    # Top-right ornament
    Line(points=[
        x + width - corner_inset - corner_size, y + corner_inset,
        x + width - corner_inset, y + corner_inset,
        x + width - corner_inset, y + corner_inset + corner_size
    ], width=THEME.geometry.stroke_hairline)
    
    # Bottom-right ornament
    Line(points=[
        x + width - corner_inset, y + height - corner_inset - corner_size,
        x + width - corner_inset, y + height - corner_inset,
        x + width - corner_inset - corner_size, y + height - corner_inset
    ], width=THEME.geometry.stroke_hairline)
    
    # Bottom-left ornament
    Line(points=[
        x + corner_inset + corner_size, y + height - corner_inset,
        x + corner_inset, y + height - corner_inset,
        x + corner_inset, y + height - corner_inset - corner_size
    ], width=THEME.geometry.stroke_hairline)


def draw_stained_glass_glow(canvas, center_pos: Tuple[float, float], 
                            radius: float, color_name: str = "primary", 
                            civic_mode: bool = False) -> None:
    """Draw multi-layer glow effect inspired by stained glass.
    
    Args:
        canvas: Kivy canvas context
        center_pos: (x, y) center point
        radius: Glow radius in pixels
        color_name: Theme color name to use
        civic_mode: Use subtler glow
    """
    x, y = center_pos
    base_color = theme_color(color_name, civic_mode=civic_mode)
    
    # Three-layer glow with decreasing opacity
    layers = [
        (radius * 1.2, 0.08),
        (radius * 0.8, 0.15),
        (radius * 0.5, 0.25),
    ]
    
    if civic_mode:
        # Reduce glow intensity in civic mode
        layers = [(r, a * 0.6) for r, a in layers]
    
    with canvas:
        for layer_radius, layer_alpha in layers:
            Color(base_color[0], base_color[1], base_color[2], layer_alpha)
            Ellipse(
                pos=(x - layer_radius, y - layer_radius),
                size=(layer_radius * 2, layer_radius * 2)
            )


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_themed_animation(target_property: str, target_value, 
                           speed: str = "normal", civic_mode: bool = False,
                           easing: str = "ease_out") -> Animation:
    """Create an Animation with theme timing and easing.
    
    Args:
        target_property: Property to animate (e.g., 'opacity', 'x')
        target_value: Target value for the property
        speed: "instant", "fast", "normal", "slow", "slower"
        civic_mode: Apply civic timing multiplier
        easing: "ease_in", "ease_out", "ease_in_out", "ease_bounce", "ease_elastic"
    
    Returns:
        Configured Kivy Animation instance
    """
    duration = get_animation_duration(speed, civic_mode)
    
    easing_map = {
        "ease_in": THEME.timings.ease_in,
        "ease_out": THEME.timings.ease_out,
        "ease_in_out": THEME.timings.ease_in_out,
        "ease_bounce": THEME.timings.ease_bounce,
        "ease_elastic": THEME.timings.ease_elastic,
    }
    
    transition = easing_map.get(easing, THEME.timings.ease_out)
    
    return Animation(**{target_property: target_value}, duration=duration, transition=transition)


def get_text_style(size: str = "base", weight: str = "normal", 
                  color_type: str = "primary", civic_mode: bool = False) -> Dict:
    """Get complete text styling dict.
    
    Args:
        size: "xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl"
        weight: "normal", "bold"
        color_type: "primary", "secondary", "tertiary"
        civic_mode: Use civic color palette
    
    Returns:
        Dict with font_size, bold, color, font_name
    """
    size_map = {
        "xs": THEME.typography.size_xs,
        "sm": THEME.typography.size_sm,
        "base": THEME.typography.size_base,
        "lg": THEME.typography.size_lg,
        "xl": THEME.typography.size_xl,
        "2xl": THEME.typography.size_2xl,
        "3xl": THEME.typography.size_3xl,
        "4xl": THEME.typography.size_4xl,
    }
    
    color_map = {
        "primary": "text_primary",
        "secondary": "text_secondary",
        "tertiary": "text_tertiary",
    }
    
    return {
        "font_size": size_map.get(size, THEME.typography.size_base),
        "bold": weight == "bold",
        "color": theme_color(color_map.get(color_type, "text_primary"), civic_mode=civic_mode),
        "font_name": THEME.typography.sans_serif,
    }


# ============================================================================
# THEME INSPECTION
# ============================================================================

def print_theme_palette(civic_mode: bool = False) -> None:
    """Print all theme colors for inspection (useful for debugging)."""
    colors = THEME.colors_civic if civic_mode else THEME.colors
    mode_label = "CIVIC MODE" if civic_mode else "DEFAULT MODE"
    
    print(f"\n{'='*60}")
    print(f"MODERNISME 2.0 THEME PALETTE - {mode_label}")
    print(f"{'='*60}\n")
    
    for attr_name in dir(colors):
        if not attr_name.startswith('_'):
            color = getattr(colors, attr_name)
            if isinstance(color, tuple) and len(color) == 4:
                r, g, b, a = color
                print(f"{attr_name:20s}: rgba({r:.2f}, {g:.2f}, {b:.2f}, {a:.2f})")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # Demo and validation
    print("Modernisme 2.0 Theme System")
    print("="*60)
    
    # Test color retrieval
    print("\n[Color Tests]")
    print(f"Primary (default): {theme_color('primary')}")
    print(f"Primary (civic):   {theme_color('primary', civic_mode=True)}")
    print(f"With alpha override: {theme_color('primary', alpha_override=0.5)}")
    
    # Test animation timing
    print("\n[Animation Timing Tests]")
    print(f"Fast animation (default): {get_animation_duration('fast'):.3f}s")
    print(f"Fast animation (civic):   {get_animation_duration('fast', civic_mode=True):.3f}s")
    print(f"Normal animation (civic): {get_animation_duration('normal', civic_mode=True):.3f}s")
    
    # Test text styling
    print("\n[Text Style Tests]")
    style = get_text_style(size="xl", weight="bold", color_type="primary")
    print(f"XL Bold Primary: {style}")
    
    # Print full palettes
    print_theme_palette(civic_mode=False)
    print_theme_palette(civic_mode=True)
    
    print("\n✓ Theme system loaded successfully")
