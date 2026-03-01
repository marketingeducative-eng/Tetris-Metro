# Navigation Quick Reference Card

## Button Actions Summary

### Line Completion Overlay ("LÍNIA COMPLETADA")

| Button | Text (Catalan) | Action | Screen Transition |
|--------|----------------|--------|-------------------|
| **Primary** | Tornar a línies | Navigate to line selection | Game → LineSelect |
| **Secondary** | Repetir línia | Restart current line | Reload GameScreen |
| **Tertiary** | Sortir | Exit to main menu | Game → Cover |

### Game Over Overlay ("FI DEL TRAJECTE")

| Button | Text (Catalan) | Action | Screen Transition |
|--------|----------------|--------|-------------------|
| **Primary** | Tornar a línies | Navigate to line selection | Game → LineSelect |
| **Secondary** | Jugar de nou | Restart current line | Reload GameScreen |

### ESC Key Behavior

| Screen | ESC Action | Destination |
|--------|-----------|-------------|
| **GameScreen** | Go back | → LineSelectScreen |
| **LineSelectScreen** | Go back | → CoverScreen |
| **CoverScreen** | Exit app | (Close application) |

## Code References

### Screen Constants
```python
SCREEN_COVER = "cover"
SCREEN_LINES = "line_select"
SCREEN_GAME = "game"
```

### Navigation Helper
```python
# Navigate to a screen
from kivy.app import App
from kivy.uix.screenmanager import FadeTransition

app = App.get_running_app()
manager = app.root
manager.transition = FadeTransition(duration=0.25)
manager.current = SCREEN_LINES  # or SCREEN_COVER, SCREEN_GAME
```

### Reset Current Line
```python
# From GameScreen
game_screen = manager.get_screen(SCREEN_GAME)
if game_screen.game_widget:
    game_screen.game_widget.reset_run()
```

## User Flow Examples

### Complete Line → Select Different Line
1. User completes a line
2. "LÍNIA COMPLETADA" overlay appears
3. Click "Tornar a línies"
4. LineSelectScreen shows with updated progress
5. User selects different line
6. New line loads and starts

### Complete Line → Retry Same Line
1. User completes a line
2. "LÍNIA COMPLETADA" overlay appears
3. Click "Repetir línia"
4. Game resets (score=0, position=start)
5. Intro banner shows
6. Same line starts again

### Game Over → Back to Lines
1. User runs out of lives
2. "FI DEL TRAJECTE" overlay with route map
3. Click "Tornar a línies"
4. LineSelectScreen shows
5. User can select any line

### Quick Navigation with ESC
1. Playing game
2. Press ESC → LineSelectScreen
3. Press ESC → CoverScreen
4. Press ESC → Exit app

## Implementation Files

| File | Key Functions |
|------|---------------|
| `game_proxima_parada.py` | `show_line_completed()`, `show_game_over()`, `reset_run()` |
| `ui/screens.py` | `GameScreen._on_keyboard()`, `LineSelectScreen._on_keyboard()` |

## Button Colors (RGBA)

| Button Type | Color | RGB |
|-------------|-------|-----|
| Primary (Blue) | Bright blue | (0.25, 0.7, 0.95, 1) |
| Secondary (Blue) | Medium blue | (0.35, 0.55, 0.75, 1) |
| Exit/Destructive | Dark red | (0.5, 0.35, 0.35, 1) |
| Success (Green) | Bright green | (0.3, 0.9, 0.5, 1) |

## Transition Settings

All screen transitions use:
- **Type:** FadeTransition
- **Duration:** 0.25 seconds
- **Easing:** Default (linear)

## Error Handling

All navigation functions include:
- Safe null checks for manager
- Exception handling for screen access
- Proper overlay cleanup before navigation
- Clock event cancellation

## Testing Commands

```bash
# Run navigation test
python test_navigation_flow.py

# Run game in practice mode (no game over)
python game_proxima_parada.py --practice

# Run game in direction mode
python game_proxima_parada.py --direction

# Run with both modes
python game_proxima_parada.py --practice --direction
```

## Common Issues & Solutions

### Issue: Navigation doesn't work
**Solution:** Ensure screen manager exists and has correct screen names
```python
if manager and hasattr(manager, "current"):
    manager.current = SCREEN_LINES
```

### Issue: Game doesn't reset properly
**Solution:** Ensure all Clock events are cancelled
```python
self.renderer.cancel_all_round_events()
self.input_controller.cancel_timeout()
self.cancel_game_events()
```

### Issue: Overlay stays visible after navigation
**Solution:** Remove overlay before navigating
```python
if overlay in self.parent.children:
    self.parent.remove_widget(overlay)
```

## Debug Tips

1. **Check screen names:**
   ```python
   print(manager.screen_names)  # ['cover', 'line_select', 'game']
   ```

2. **Verify current screen:**
   ```python
   print(manager.current)  # Current screen name
   ```

3. **Check game state:**
   ```python
   print(f"Score: {game_state.score}")
   print(f"Position: {game_state.current_index}/{len(line.stations)}")
   ```

4. **Monitor Clock events:**
   ```python
   print(f"Scheduled events: {len(self.scheduled_game_events)}")
   ```
