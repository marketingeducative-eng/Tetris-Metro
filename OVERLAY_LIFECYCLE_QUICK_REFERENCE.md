# Overlay Lifecycle Quick Reference

## When to Use This Pattern

Use the overlay lifecycle pattern when creating any new overlay or modal popup that:
- Temporarily blocks game interaction
- Needs to be dismissed by user action
- Contains animations or scheduled events
- Binds touch/click event handlers

## Implementation Checklist

### ✅ Step 1: Add Overlay Tracking Attribute

In `Renderer.__init__()`:
```python
self.your_overlay = None
```

### ✅ Step 2: Add Duplicate Prevention

At the start of your show method:
```python
def show_your_overlay(self):
    # Prevent duplication
    if self.your_overlay:
        self._log_overlay("Already showing", "your_overlay")
        return
    
    self._log_overlay("Show", "your_overlay")
```

### ✅ Step 3: Create Overlay with Touch Handler (Optional)

If your overlay needs touch-outside-to-close:
```python
overlay = FloatLayout(size_hint=(1, 1))

def on_overlay_touch(instance, touch):
    if overlay.collide_point(*touch.pos):
        if not panel.collide_point(*touch.pos):
            close_overlay()
            return True
    return False

# Store handler for cleanup
overlay._touch_handler = on_overlay_touch
overlay.bind(on_touch_down=on_overlay_touch)
```

### ✅ Step 4: Define Close Handler

```python
def close_overlay(*args):
    # 1. Unbind touch handler if exists
    if self.your_overlay and hasattr(self.your_overlay, '_touch_handler'):
        self.your_overlay.unbind(on_touch_down=self.your_overlay._touch_handler)
    
    # 2. Cancel specific animations (if needed)
    if hasattr(self, '_your_animation') and self._your_animation:
        self._your_animation.cancel(...)
        self._your_animation = None
    
    # 3. Use centralized cleanup
    self._cleanup_overlay('your_overlay')
    
    # 4. Execute callback
    if on_close_callback:
        on_close_callback()
```

### ✅ Step 5: Store and Add Overlay

```python
self.your_overlay = overlay
self.parent.add_widget(overlay)
```

### ✅ Step 6: Handle Scheduled Events (Optional)

If your overlay schedules Clock events:

**Track the event:**
```python
# In __init__
self._your_event = None

# When scheduling
self._your_event = Clock.schedule_once(some_function, 2.0)
```

**Update `_cleanup_overlay()`:**
```python
elif overlay_name == 'your_overlay' and self._your_event:
    self._your_event.cancel()
    self._your_event = None
```

## Complete Example

```python
# Step 1: Add attribute in __init__
def __init__(self, ...):
    self.example_overlay = None
    self._example_fade_event = None

# Step 2-5: Create show method
def show_example_overlay(self, on_close_callback=None):
    # Prevent duplication
    if self.example_overlay:
        self._log_overlay("Already showing", "example_overlay")
        return
    
    self._log_overlay("Show", "example_overlay")
    
    # Create overlay
    overlay = FloatLayout(size_hint=(1, 1))
    # ... add UI elements ...
    
    # Touch handler (optional)
    def on_example_touch(instance, touch):
        if overlay.collide_point(*touch.pos):
            if not panel.collide_point(*touch.pos):
                close_overlay()
                return True
        return False
    
    overlay._touch_handler = on_example_touch
    overlay.bind(on_touch_down=on_example_touch)
    
    # Close handler
    def close_overlay(*args):
        # Unbind touch handler
        if self.example_overlay and hasattr(self.example_overlay, '_touch_handler'):
            self.example_overlay.unbind(on_touch_down=self.example_overlay._touch_handler)
        
        # Cleanup
        self._cleanup_overlay('example_overlay')
        
        if on_close_callback:
            on_close_callback()
    
    # Bind close button
    close_button.bind(on_release=close_overlay)
    
    # Store and add
    self.example_overlay = overlay
    self.parent.add_widget(overlay)

# Step 6: Update _cleanup_overlay if needed
def _cleanup_overlay(self, overlay_name):
    # ... existing code ...
    
    elif overlay_name == 'example_overlay' and self._example_fade_event:
        self._example_fade_event.cancel()
        self._example_fade_event = None
```

## Common Patterns

### Pattern: Timed Auto-Dismiss

```python
def auto_dismiss(dt):
    close_overlay()

self._example_fade_event = Clock.schedule_once(auto_dismiss, 5.0)
```

### Pattern: Pulse Animation

```python
def pulse_widget(dt):
    Animation(opacity=1.0, duration=0.3).start(widget)
    Animation(opacity=0.6, duration=0.3).start(widget)

self._example_pulse_event = Clock.schedule_interval(pulse_widget, 0.6)
```

### Pattern: Touch-Outside-to-Close

```python
def on_overlay_touch(instance, touch):
    if overlay.collide_point(*touch.pos):
        if not panel.collide_point(*touch.pos):
            # Clicked outside panel
            close_overlay()
            return True
    return False

overlay._touch_handler = on_overlay_touch
overlay.bind(on_touch_down=on_overlay_touch)
```

### Pattern: Button with Callback

```python
def close_overlay(*args):
    self._cleanup_overlay('your_overlay')
    if on_close_callback:
        on_close_callback()

close_button.bind(on_release=close_overlay)
```

## Testing Your Overlay

Use `test_overlay_lifecycle.py` as a template:

```python
def _test_your_overlay(self, renderer):
    print("\n=== Testing Your Overlay ===")
    print(f"Before: your_overlay = {renderer.your_overlay}")
    
    # First call should succeed
    renderer.show_your_overlay(lambda: print("Closed"))
    print(f"After show: your_overlay = {renderer.your_overlay}")
    
    # Second call should log "Already showing"
    renderer.show_your_overlay(lambda: None)
    
    # Close after delay
    def close_overlay(dt):
        print("Closing...")
        # Trigger your close method here
        print(f"After close: your_overlay = {renderer.your_overlay}")
    
    Clock.schedule_once(close_overlay, 2)
```

## Debug Checklist

If you see issues:

- [ ] Added overlay attribute in `__init__`?
- [ ] Check for duplication at start of show method?
- [ ] Called `_log_overlay()` for show and cleanup?
- [ ] Stored touch handler on overlay object?
- [ ] Unbound touch handler before cleanup?
- [ ] Cancelled animations before cleanup?
- [ ] Added event cancellation to `_cleanup_overlay()` if needed?
- [ ] Called `_cleanup_overlay()` instead of manual removal?
- [ ] Reset any modified state (camera position, audio, etc.)?

## What NOT to Do

❌ **Manual Cleanup**
```python
# DON'T DO THIS
if overlay in self.parent.children:
    self.parent.remove_widget(overlay)
self.your_overlay = None
```

✅ **Use Centralized Cleanup**
```python
# DO THIS
self._cleanup_overlay('your_overlay')
```

---

❌ **Forget to Unbind**
```python
# DON'T DO THIS
overlay.bind(on_touch_down=handler)
# ... later ...
self._cleanup_overlay('your_overlay')  # Handler still bound!
```

✅ **Unbind Before Cleanup**
```python
# DO THIS
if self.your_overlay and hasattr(self.your_overlay, '_touch_handler'):
    self.your_overlay.unbind(on_touch_down=self.your_overlay._touch_handler)
self._cleanup_overlay('your_overlay')
```

---

❌ **Skip Duplication Check**
```python
# DON'T DO THIS
def show_your_overlay(self):
    overlay = FloatLayout()  # Creates duplicate!
    # ...
```

✅ **Always Check First**
```python
# DO THIS
def show_your_overlay(self):
    if self.your_overlay:
        self._log_overlay("Already showing", "your_overlay")
        return
    # ...
```

## Related Documentation

- Full implementation details: [OVERLAY_LIFECYCLE_HARDENING.md](OVERLAY_LIFECYCLE_HARDENING.md)
- Test suite: [test_overlay_lifecycle.py](test_overlay_lifecycle.py)
- Example overlays:
  - Tutorial: lines 1116-1228
  - Settings: lines 1230-1383
  - Tourist: lines 1543-1703
  - Journey: lines 2006-2315
  - Onboarding: lines 2317-2493
  - Line Completed: lines 2596-2743
