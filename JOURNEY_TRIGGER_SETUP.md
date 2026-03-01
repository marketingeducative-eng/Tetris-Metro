# Adding Journey Button to Main Screen

## Quick Implementation

To add the journey overlay trigger to your main screen, add this code to your line selection screen or main menu:

```python
def add_journey_button_to_main_screen(self):
    """Add floating 'Journey' button to main screen (top-right corner)"""
    journey_icon = Button(
        text="📊",  # Stats/chart icon
        size_hint=(None, None),
        size=(48, 48),
        pos_hint={'right': 0.96, 'top': 0.97},
        background_normal="",
        background_color=(0.25, 0.6, 0.85, 0.9),  # Blue, semi-transparent
        font_size='22sp',
        color=(1, 1, 1, 1)
    )
    
    # Bind to show journey overlay
    def show_journey(*args):
        if hasattr(self, 'renderer') and self.renderer:
            self.renderer.show_journey_overlay()
    
    journey_icon.bind(on_release=show_journey)
    
    # Optional: Add visual feedback
    def on_press(*args):
        from kivy.animation import Animation
        Animation(opacity=0.7, duration=0.08).start(journey_icon)
    
    def on_release_anim(*args):
        from kivy.animation import Animation
        Animation(opacity=1.0, duration=0.12).start(journey_icon)
    
    journey_icon.bind(on_press=on_press, on_release=on_release_anim)
    
    # Add to screen
    self.add_widget(journey_icon)
    return journey_icon
```

## Alternative: Minimal Icon Only

For a truly subtle approach, use this minimalist version:

```python
# Ultra-minimal: Just the emoji
journey_icon = Label(
    text="📊",
    font_size='28sp',
    size_hint=(None, None),
    size=(44, 44),
    pos_hint={'right': 0.97, 'top': 0.98},
    color=(0.5, 0.7, 0.9, 0.8)  # Subtle blue-gray
)

# Make it clickable
def on_touch_down_journey(instance, touch):
    if instance.collide_point(*touch.pos):
        # Show journey overlay
        if hasattr(self, 'renderer'):
            self.renderer.show_journey_overlay()
        return True
    return False

journey_icon.bind(on_touch_down=on_touch_down_journey)
self.add_widget(journey_icon)
```

## Full Example: Integration into Main App

```python
class ProximaParadaApp(App):
    def build(self):
        # ... existing app setup ...
        
        # Add journey button after renderer is initialized
        if hasattr(self, 'renderer'):
            self.add_journey_trigger()
        
        return root
    
    def add_journey_trigger(self):
        """Add journey overlay trigger to main UI"""
        # Create button
        btn = Button(
            text="📊",
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={'right': 0.96, 'top': 0.97},
            background_normal="",
            background_color=(0.25, 0.6, 0.85, 0.9)
        )
        
        # Bind action
        btn.bind(on_release=lambda *args: self.renderer.show_journey_overlay())
        
        # Add to root
        self.root.add_widget(btn)
```

## Positioning Options

### Top-Right (Recommended)
```python
pos_hint={'right': 0.96, 'top': 0.97}
```
- Out of the way
- Standard UI pattern
- Easy to find

### Top-Left
```python
pos_hint={'x': 0.02, 'top': 0.97}
```
- Alternative position
- Left-handed friendly

### Bottom-Right
```python
pos_hint={'right': 0.96, 'y': 0.02}
```
- Near other controls
- iOS pattern

### Center-Bottom (Menu Style)
```python
pos_hint={'center_x': 0.5, 'y': 0.05}
size=(200, 50)
text="📊 El teu viatge"
```
- More prominent
- Menu-style button
- Full text label

## Recommended: Main Menu Integration

Add to your line selection screen as a menu option:

```python
class LineSelectionScreen(FloatLayout):
    def build_ui(self):
        # ... existing menu buttons ...
        
        # Journey button (below other options)
        journey_btn = Button(
            text="📊 El teu viatge",
            size_hint=(0.6, None),
            height=55,
            pos_hint={'center_x': 0.5, 'y': 0.15},
            background_normal="",
            background_color=(0.15, 0.25, 0.35, 1),
            font_size='18sp',
            bold=True
        )
        
        journey_btn.bind(on_release=self.show_journey)
        self.add_widget(journey_btn)
    
    def show_journey(self, *args):
        """Show journey overlay"""
        if hasattr(self.app, 'renderer'):
            self.app.renderer.show_journey_overlay()
```

## Testing the Button

Quick test after adding:

```python
# Run app
# Look for the icon in top-right corner
# Click it
# Should see "El teu viatge" overlay
# Click "Tornar al mapa" or outside to close
```

## Styling Variants

### Subtle (Recommended for Minimal UI)
```python
background_color=(0.25, 0.6, 0.85, 0.7)  # Low opacity
font_size='20sp'
```

### Prominent (Recommended for Menus)
```python
background_color=(0.3, 0.9, 0.5, 1)  # Bright green
font_size='22sp'
bold=True
```

### Matching Game Theme
```python
background_color=(0.08, 0.10, 0.14, 0.95)  # Dark like panels
border=(2, 0.3, 0.9, 0.5, 1)  # Green border (requires custom drawing)
```

## Complete Working Example

Drop this into your main game file:

```python
from kivy.uix.button import Button
from kivy.animation import Animation

def init_journey_ui(game_screen, renderer):
    """
    Initialize journey overlay UI element.
    
    Args:
        game_screen: The main game widget/screen
        renderer: Renderer instance with show_journey_overlay method
    """
    # Create button
    btn = Button(
        text="📊",
        size_hint=(None, None),
        size=(48, 48),
        pos_hint={'right': 0.96, 'top': 0.97},
        background_normal="",
        background_color=(0.25, 0.6, 0.85, 0.9),
        font_size='22sp'
    )
    
    # Press/release animation
    def on_press(*args):
        Animation(opacity=0.7, duration=0.08).start(btn)
    
    def on_release(*args):
        Animation(opacity=1.0, duration=0.12).start(btn)
    
    # Show overlay action
    def show_journey(*args):
        renderer.show_journey_overlay()
    
    # Bind events
    btn.bind(on_press=on_press)
    btn.bind(on_release=on_release)
    btn.bind(on_release=show_journey)
    
    # Add to screen
    game_screen.add_widget(btn)
    
    return btn

# Usage:
# journey_button = init_journey_ui(self.root, self.renderer)
```

## Troubleshooting

**Button not appearing?**
- Check `pos_hint` values (should be 0-1 range)
- Verify button is added to correct parent widget
- Check z-index (add button last so it's on top)

**Button appears but nothing happens?**
- Verify `renderer` instance exists
- Check `show_journey_overlay` method exists
- Add debug print in callback

**Button looks wrong?**
- Adjust `background_color` for visibility
- Check `font_size` (platform-dependent)
- Verify parent widget size

---

**Quick Start:**
```python
# Add this after renderer initialization:
journey_btn = Button(text="📊", size_hint=(None,None), size=(48,48), pos_hint={'right':0.96,'top':0.97})
journey_btn.bind(on_release=lambda *a: renderer.show_journey_overlay())
self.add_widget(journey_btn)
```
