# Overlay Lifecycle Hardening

**Status**: ✅ Complete  
**Date**: 2025  
**Affected File**: `game_proxima_parada.py`

## Overview

Comprehensive hardening of overlay lifecycle management to prevent duplication, animation leaks, event leaks, and resource cleanup issues across all six overlay types in the game.

## Problem Statement

Before hardening, overlays suffered from:

1. **Duplication**: Multiple instances of the same overlay could exist simultaneously
2. **Animation Leaks**: Animations continued running after overlay removal
3. **Event Leaks**: Scheduled Clock events persisted after cleanup
4. **Touch Handler Leaks**: Event handlers not unbound, causing memory leaks
5. **Camera Shake Leaks**: Parent widget position not reset after shake effect
6. **Inconsistent Cleanup**: Each overlay had different cleanup patterns

## Solution Architecture

### Core Infrastructure

#### 1. Overlay Tracking Attributes
```python
# Lines 186-193
self.tutorial_overlay = None
self.settings_overlay = None
self.tourist_overlay = None
self.journey_overlay = None
self.onboarding_overlay = None
self.line_completed_overlay = None
```

#### 2. Event Tracking
```python
self._tutorial_dismiss_event = None
self._camera_shake_event = None
self._line_completed_pulse_event = None
```

#### 3. Debug Logging
```python
def _log_overlay(self, action, name):
    """Log overlay lifecycle events for debugging"""
    print(f"[Overlay] {action}: {name}")
```

#### 4. Centralized Cleanup
```python
def _cleanup_overlay(self, overlay_name):
    """Safely cleanup an overlay and its resources
    
    - Stops all animations on overlay
    - Removes widget from parent
    - Clears overlay reference
    - Cancels related scheduled events
    """
    overlay = getattr(self, overlay_name, None)
    if not overlay:
        return
    
    self._log_overlay("Cleanup", overlay_name)
    
    # Stop all animations
    Animation.stop_all(overlay)
    
    # Remove from parent
    if overlay in self.parent.children:
        self.parent.remove_widget(overlay)
    
    # Clear reference
    setattr(self, overlay_name, None)
    
    # Clear related events
    if overlay_name == 'tutorial_overlay' and self._tutorial_dismiss_event:
        self._tutorial_dismiss_event.cancel()
        self._tutorial_dismiss_event = None
    elif overlay_name == 'line_completed_overlay' and self._line_completed_pulse_event:
        self._line_completed_pulse_event.cancel()
        self._line_completed_pulse_event = None
```

## Implementation Details

### Tutorial Overlay
**Lines**: 1116-1228

**Hardening**:
- ✅ Duplicate prevention at entry (line 1119-1121)
- ✅ Track dismiss event (line 1218)
- ✅ Cancel event in _cleanup_overlay()
- ✅ Use _cleanup_overlay() in dismiss_tutorial() (line 1228)

```python
def show_tutorial(self, line):
    if self.tutorial_overlay:
        self._log_overlay("Already showing", "tutorial_overlay")
        return
    
    self._log_overlay("Show", "tutorial_overlay")
    # ... create overlay ...
    self._tutorial_dismiss_event = Clock.schedule_once(auto_dismiss, 10)
```

### Settings Overlay
**Lines**: 1230-1383

**Hardening**:
- ✅ Duplicate prevention at entry (line 1233-1237)
- ✅ Store touch handler on overlay (line 1370-1372)
- ✅ Unbind touch handler in dismiss_settings() (line 1380-1382)
- ✅ Use _cleanup_overlay() (line 1383)

```python
def show_settings_overlay(self, on_close_callback):
    if self.settings_overlay:
        self._log_overlay("Already showing", "settings_overlay")
        return
    
    self._log_overlay("Show", "settings_overlay")
    # ... create overlay ...
    overlay._touch_handler = on_settings_touch
    overlay.bind(on_touch_down=on_settings_touch)

def dismiss_settings(self):
    if self.settings_overlay:
        if hasattr(self.settings_overlay, '_touch_handler'):
            self.settings_overlay.unbind(on_touch_down=self.settings_overlay._touch_handler)
    self._cleanup_overlay('settings_overlay')
```

### Tourist Overlay
**Lines**: 1543-1703

**Hardening**:
- ✅ Duplicate prevention at entry (line 1546-1550)
- ✅ Track Ken Burns animation (stored as _tourist_image_anim)
- ✅ Track image widget (stored as _tourist_image_widget)
- ✅ Cancel animations in dismiss_tourist_popup() (line 1691-1695)
- ✅ Use _cleanup_overlay() (line 1703)
- ✅ Refactored close_popup to call dismiss_tourist_popup() (line 1668-1671)

```python
def show_tourist_popup(self, station, on_close_callback):
    if self.tourist_overlay:
        self._log_overlay("Already showing", "tourist_overlay")
        return
    
    self._log_overlay("Show", "tourist_overlay")
    # ... Ken Burns animation ...
    
def dismiss_tourist_popup(self):
    # Cancel Ken Burns animation
    if hasattr(self, '_tourist_image_anim') and self._tourist_image_anim:
        try:
            self._tourist_image_anim.cancel(self._tourist_image_widget)
        except Exception:
            pass
        self._tourist_image_anim = None
    self._tourist_image_widget = None
    self._cleanup_overlay('tourist_overlay')
```

### Journey Overlay
**Lines**: 2006-2315

**Hardening**:
- ✅ Duplicate prevention at entry (line 2009-2014)
- ✅ Store touch handler on overlay (line 2311-2312)
- ✅ Unbind touch handler in close_overlay() (line 2303-2306)
- ✅ Use _cleanup_overlay() (line 2306)

```python
def show_journey_overlay(self, on_close_callback=None):
    if hasattr(self, 'journey_overlay') and self.journey_overlay:
        self._log_overlay("Already showing", "journey_overlay")
        return
    
    self._log_overlay("Show", "journey_overlay")
    # ... create overlay ...
    overlay._touch_handler = on_journey_touch
    overlay.bind(on_touch_down=on_journey_touch)
    
    def close_overlay(*args):
        if self.journey_overlay and hasattr(self.journey_overlay, '_touch_handler'):
            self.journey_overlay.unbind(on_touch_down=self.journey_overlay._touch_handler)
        self._cleanup_overlay('journey_overlay')
        if on_close_callback:
            on_close_callback()
```

### Onboarding Overlay
**Lines**: 2317-2493

**Hardening**:
- ✅ Duplicate prevention at entry (line 2320-2327)
- ✅ Sets ambience to "station" (appropriate for game state)
- ✅ Use _cleanup_overlay() in complete_onboarding() (line 2478)

```python
def show_onboarding_overlay(self):
    if self.onboarding_overlay:
        self._log_overlay("Already showing", "onboarding_overlay")
        return
    
    self._log_overlay("Show", "onboarding_overlay")
    # ... narrative sequence ...
    self.audio.set_ambience("station", volume=0.3)
    
    def complete_onboarding(*args):
        self._cleanup_overlay('onboarding_overlay')
        # Mark onboarding as complete
```

### Line Completed Overlay
**Lines**: 2596-2743

**Hardening**:
- ✅ Duplicate prevention at entry (line 2599-2604)
- ✅ Track pulse animation event (line 2701-2703)
- ✅ Cancel pulse event in _cleanup_overlay()
- ✅ Consolidated cleanup in close_overlay_and_navigate() (line 2707-2709)
- ✅ Consolidated cleanup in repeat_line() (line 2720-2722)

```python
def show_line_completed(self, total_stations, on_close_callback=None):
    if self.line_completed_overlay:
        self._log_overlay("Already showing", "line_completed_overlay")
        return
    
    self._log_overlay("Show", "line_completed_overlay")
    # ... create overlay ...
    self._line_completed_pulse_event = self.events.schedule_interval(pulse_title, 0.6)
    
    def close_overlay_and_navigate(target_screen):
        self._cleanup_overlay('line_completed_overlay')
        # Navigate...
    
    def repeat_line(*args):
        self._cleanup_overlay('line_completed_overlay')
        # Reset game...
```

### Camera Shake
**Lines**: 1422-1447

**Hardening**:
- ✅ Track shake event (line 1426-1429)
- ✅ Always reset parent position after shake (line 1445)

```python
def _camera_shake(self, parent, magnitude=3, duration=0.15):
    # Cancel previous shake
    if self._camera_shake_event:
        try:
            self._camera_shake_event.cancel()
        except:
            pass
    
    # Perform shake...
    
    def reset_position(dt):
        parent.pos = (0, 0)  # Always reset
        Clock.schedule_once(cleanup_event, 0)
    
    self._camera_shake_event = Clock.schedule_once(reset_position, duration)
```

## Duplication Prevention Pattern

All overlays follow this pattern:

```python
def show_OVERLAY_TYPE(self, ...):
    # 1. Check if overlay exists
    if self.OVERLAY_TYPE_overlay:
        self._log_overlay("Already showing", "OVERLAY_TYPE_overlay")
        return
    
    # 2. Log show action
    self._log_overlay("Show", "OVERLAY_TYPE_overlay")
    
    # 3. Create overlay
    overlay = FloatLayout(...)
    # ... setup overlay ...
    
    # 4. Store reference
    self.OVERLAY_TYPE_overlay = overlay
    self.parent.add_widget(overlay)
```

## Cleanup Pattern

All overlays use centralized cleanup:

```python
def close_overlay(*args):
    # 1. Unbind touch handlers (if applicable)
    if self.overlay and hasattr(self.overlay, '_touch_handler'):
        self.overlay.unbind(on_touch_down=self.overlay._touch_handler)
    
    # 2. Cancel specific animations (if applicable)
    if self._specific_animation:
        self._specific_animation.cancel(...)
    
    # 3. Use centralized cleanup
    self._cleanup_overlay('overlay_name')
    
    # 4. Execute callback (if applicable)
    if on_close_callback:
        on_close_callback()
```

## Testing

### Test Coverage
All six overlay types tested for:
1. Duplication prevention
2. Animation cleanup
3. Event cancellation
4. Touch handler unbinding
5. Camera shake position reset

### Test Script
`test_overlay_lifecycle.py` provides:
- Individual overlay tests
- Rapid cycle tests (5 open/close cycles per overlay)
- Camera shake position validation
- Debug log verification
- Final state check (all overlays should be None)

### Running Tests
```bash
python test_overlay_lifecycle.py
```

### Expected Console Output
```
[Overlay] Show: tutorial_overlay
[Overlay] Already showing: tutorial_overlay  # Duplication prevented
[Overlay] Cleanup: tutorial_overlay

[Overlay] Show: settings_overlay
[Overlay] Already showing: settings_overlay
[Overlay] Cleanup: settings_overlay

# ... similar for all overlays ...

=== Final State Check ===
tutorial_overlay: None
settings_overlay: None
tourist_overlay: None
journey_overlay: None
onboarding_overlay: None
line_completed_overlay: None
✓ All overlays properly cleaned up
```

## Debug Logging

All overlay lifecycle events are logged:

```python
[Overlay] Show: overlay_name           # Overlay opened
[Overlay] Already showing: overlay_name # Duplication prevented
[Overlay] Cleanup: overlay_name        # Overlay cleaned up
```

## Benefits

1. **Memory Safety**: No leaked widgets, animations, or event handlers
2. **Consistency**: All overlays follow same lifecycle pattern
3. **Debuggability**: Clear logging shows overlay state changes
4. **Maintainability**: Centralized cleanup reduces code duplication
5. **Robustness**: Handles edge cases (rapid clicks, animator timing, etc.)

## Migration Notes

### Before
```python
# Manual cleanup (error-prone)
if overlay in self.parent.children:
    self.parent.remove_widget(overlay)
self.some_overlay = None
# Event cleanup often forgotten
```

### After
```python
# Centralized cleanup (safe and complete)
self._cleanup_overlay('some_overlay')
# Handles: animations, events, parent removal, reference clearing
```

## Future Considerations

1. **Generic Overlay Manager**: Consider extracting overlay management into a separate OverlayManager class
2. **Stack-based Overlays**: Support multiple overlays with Z-order management
3. **Transition Animations**: Add fade-in/fade-out for all overlays
4. **Accessibility**: Add keyboard navigation and screen reader support

## Related Files

- **Implementation**: `game_proxima_parada.py` (lines 186-2743)
- **Test Suite**: `test_overlay_lifecycle.py`
- **Documentation**: `OVERLAY_LIFECYCLE_HARDENING.md` (this file)

## Summary

All six overlay types now use consistent, safe lifecycle management:
- ✅ Tutorial overlay
- ✅ Settings overlay
- ✅ Tourist overlay
- ✅ Journey overlay
- ✅ Onboarding overlay
- ✅ Line completed overlay
- ✅ Camera shake (position reset)

Zero leaks. Zero duplication. Zero position drift.
