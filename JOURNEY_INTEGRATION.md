# Journey Overlay - Quick Integration Guide

## How to Trigger the Journey Overlay

### From Game Renderer
```python
# Assuming you have a Renderer instance
renderer.show_journey_overlay()

# With callback
renderer.show_journey_overlay(on_close_callback=lambda: print("Closed"))
```

### From Main Menu (Line Selection Screen)

Add a button to the line selection screen:

```python
# In the screen that shows available metro lines:
journey_icon = Button(
    text="📊",  # Stats icon
    size_hint=(None, None),
    size=(50, 50),
    pos_hint={'right': 0.95, 'top': 0.95},
    background_normal="",
    background_color=(0.2, 0.3, 0.4, 0.8),
    font_size='24sp'
)

def open_journey(*args):
    # Get renderer instance from game
    if hasattr(app.game_widget, 'renderer'):
        app.game_widget.renderer.show_journey_overlay()

journey_icon.bind(on_release=open_journey)
screen.add_widget(journey_icon)
```

### From Post-Game Screen

Add to the overlay shown after completing a line:

```python
# In the line completion overlay:
journey_button = Button(
    text="Veure el meu viatge",
    size_hint=(0.45, None),
    height=44,
    pos_hint={'x': 0.05, 'y': 0.1}
)

journey_button.bind(on_release=lambda *args: renderer.show_journey_overlay())
completion_panel.add_widget(journey_button)
```

### From Settings Menu

Add as a menu option:

```python
# In settings overlay or menu:
stats_option = Button(
    text="📊 El teu viatge",
    size_hint=(0.8, None),
    height=50
)

stats_option.bind(on_release=lambda *args: renderer.show_journey_overlay())
```

### Keyboard Shortcut (Optional)

Bind to a key for quick access:

```python
from kivy.core.window import Window

def on_keyboard(window, key, *args):
    if key == ord('j'):  # Press 'J' for Journey
        renderer.show_journey_overlay()
        return True
    return False

Window.bind(on_keyboard=on_keyboard)
```

## Example: Complete Integration

```python
class ProximaParadaGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # ... existing setup ...
        
        # Add journey button to main screen
        self.add_journey_button()
    
    def add_journey_button(self):
        """Add floating journey button to main UI"""
        journey_btn = Button(
            text="📊",
            size_hint=(None, None),
            size=(48, 48),
            pos_hint={'right': 0.97, 'top': 0.97},
            background_normal="",
            background_color=(0.25, 0.6, 0.85, 0.9),
            font_size='22sp'
        )
        
        def show_journey(*args):
            if hasattr(self, 'renderer') and self.renderer:
                self.renderer.show_journey_overlay()
        
        journey_btn.bind(on_release=show_journey)
        self.add_widget(journey_btn)
```

## Testing the Trigger

Quick test to verify it works:

```python
# In your main game file:
from kivy.core.window import Window

# Add temporary keyboard binding for testing
def test_journey(window, key, *args):
    if key == ord('t'):  # Press 'T' to test
        if hasattr(app, 'renderer'):
            app.renderer.show_journey_overlay()
        return True
    return False

Window.bind(on_keyboard=test_journey)

# Run game and press 'T' to test the overlay
```

## UI Placement Recommendations

### Minimal Integration (Recommended)
Place a small icon in the top-right corner:
- Position: `pos_hint={'right': 0.95, 'top': 0.95}`
- Size: 48×48px
- Icon: 📊 or 📈
- Background: Semi-transparent blue

### Menu Integration
Add to main menu as a full button:
- Position: Below "Play" and "Settings"
- Text: "El teu viatge"
- Icon: 📊 prefix
- Color: Accent green

### Post-Game Integration  
Show after line completion:
- Position: Bottom of completion overlay
- Text: "Veure progressió"
- Size: Half-width button
- Appears alongside "Next Line" / "Exit"

## Data Requirements

The overlay will automatically fetch from `ProgressManager`:
- ✓ Total score
- ✓ Completed lines
- ✓ Completed stations
- ✓ Earned badges
- ✓ First Day completion

**No additional setup required** - just call `show_journey_overlay()`.

---

**Quick Start**: Add this to your main screen:
```python
renderer.show_journey_overlay()
```
