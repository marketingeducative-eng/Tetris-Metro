# Audio Event System - Quick Reference

## Import
```python
from core.audio import AudioService, AudioEvent
```

## Available Events

### UI Sounds
```python
AudioEvent.UI_CLICK          # Button clicks
AudioEvent.UI_PICK           # Token drag start
AudioEvent.UI_DROP           # Token drop
AudioEvent.UI_HOVER_TARGET   # Hover over valid drop zone
```

### Game SFX
```python
AudioEvent.SFX_CORRECT       # Correct answer
AudioEvent.SFX_WRONG         # Wrong answer
AudioEvent.SFX_INVALID_DROP  # Invalid token drop
AudioEvent.SFX_TIMEOUT       # Time ran out
```

### Train SFX
```python
AudioEvent.SFX_ARRIVAL_BRAKE # Train braking sound
AudioEvent.SFX_DOOR_OPEN     # Door opening
AudioEvent.SFX_DOOR_CLOSE    # Door closing
```

### Ambience Loops
```python
AudioEvent.AMB_TUNNEL        # Tunnel whoosh (looping)
AudioEvent.AMB_STATION       # Station ambience (looping)
```

### Special Events
```python
AudioEvent.SFX_GOAL_ANTICIPATION  # Near goal (3 stations away)
AudioEvent.SFX_GOAL_CELEBRATION   # Goal reached
AudioEvent.SFX_LINE_COMPLETED     # Line completed
```

## Usage Examples

### Basic Play
```python
audio = AudioService()
audio.play(AudioEvent.UI_CLICK)
```

### With Volume
```python
audio.play(AudioEvent.SFX_CORRECT, volume=0.6)
```

### With Cooldown (prevent spam)
```python
audio.play(
    AudioEvent.UI_PICK,
    volume=0.35,
    cooldown_ms=150  # 150ms minimum between plays
)
```

### With Priority (interrupt lower priority sounds)
```python
# High priority (interrupts lower)
audio.play(
    AudioEvent.SFX_ARRIVAL_BRAKE,
    volume=0.45,
    priority=2
)

# Low priority (gets interrupted)
audio.play(
    AudioEvent.UI_CLICK,
    volume=0.3,
    priority=0
)
```

### Allow Overlap
```python
# Multiple sounds can play simultaneously
audio.play(
    AudioEvent.UI_CLICK,
    volume=0.3,
    allow_overlap=True
)
```

### Complete Example
```python
# Button click with all parameters
self.audio.play(
    AudioEvent.UI_CLICK,
    volume=0.3,
    allow_overlap=True,
    cooldown_ms=120,
    priority=1
)
```

## Ambience System

### Set Ambience
```python
audio.set_ambience("tunnel")   # Start tunnel loop
audio.set_ambience("station")  # Switch to station (crossfades)
audio.set_ambience("none")     # Stop all ambience
```

### Characteristics
- **Non-overlapping**: Only one ambience plays at a time
- **Smooth crossfades**: 0.6s transition between modes
- **Auto-looping**: Continues until changed or stopped
- **Fade out**: Smooth volume decrease when stopping

## Legacy Methods (Still Supported)

```python
audio.play_station_announcement()    # Station chime
audio.play_tunnel_loop()             # Start tunnel ambience
audio.stop_tunnel_sound()            # Stop tunnel (fade out)
audio.play_bonus_life_sound()        # Bonus life jingle
audio.play_direction_mode_cue()      # Direction mode startup
audio.play_milestone_cue()           # Milestone celebration
audio.play_goal_anticipation_sound() # Near goal sound
audio.play_goal_celebration_sound()  # Goal reached sound
audio.play_line_completed()          # Line completed
```

## Common Patterns

### Button Feedback
```python
def _bind_button_feedback(self, button):
    def on_press(instance):
        Animation(opacity=0.85, duration=0.08).start(instance)
    
    def on_release(instance):
        Animation(opacity=1.0, duration=0.12).start(instance)
        self.audio.play(
            AudioEvent.UI_CLICK,
            volume=0.3,
            allow_overlap=True,
            cooldown_ms=120,
            priority=1
        )
    
    button.bind(on_press=on_press, on_release=on_release)
```

### Token Drag
```python
def on_drag_start(self, token):
    self.audio.play(
        AudioEvent.UI_PICK,
        volume=0.35,
        allow_overlap=True,
        cooldown_ms=150,
        priority=1
    )
```

### Hover Feedback
```python
def on_hover_target(self):
    self.audio.play(
        AudioEvent.UI_HOVER_TARGET,
        volume=0.25,
        allow_overlap=True,
        cooldown_ms=0,  # No cooldown for continuous feedback
        priority=0
    )
```

### Answer Validation
```python
if correct:
    self.audio.play(
        AudioEvent.SFX_CORRECT,
        volume=0.55,
        allow_overlap=False,
        cooldown_ms=150,
        priority=2
    )
else:
    self.audio.play(
        AudioEvent.SFX_WRONG,
        volume=0.55,
        allow_overlap=False,
        cooldown_ms=150,
        priority=2
    )
```

### Train Arrival Sequence
```python
# Brake
self.audio.play(AudioEvent.SFX_ARRIVAL_BRAKE, volume=0.45, priority=2)

# Door open (after 0.12s)
Clock.schedule_once(
    lambda dt: self.audio.play(AudioEvent.SFX_DOOR_OPEN, volume=0.45, priority=2),
    0.12
)

# Door close (after 1.2s)
Clock.schedule_once(
    lambda dt: self.audio.play(AudioEvent.SFX_DOOR_CLOSE, volume=0.45, priority=2),
    1.2
)
```

## Parameter Guidelines

### Volume
- **0.0 - 0.2**: Very quiet (ambience, subtle feedback)
- **0.2 - 0.4**: Quiet (UI feedback, hover sounds)
- **0.4 - 0.6**: Normal (game events, celebrations)
- **0.6 - 0.8**: Loud (important SFX, correct/wrong)
- **0.8 - 1.0**: Very loud (avoid, may be jarring)

### Cooldown (milliseconds)
- **0ms**: No cooldown (continuous feedback)
- **100-150ms**: Fast interaction (clicks, picks)
- **150-250ms**: Standard cooldown (drops, SFX)
- **500ms+**: Prevent frequent spam

### Priority
- **0**: Low (UI feedback, can be interrupted)
- **1**: Medium (button clicks, token events)
- **2**: High (game SFX, train sounds, interrupts others)
- **3+**: Critical (reserved for essential audio)

### Allow Overlap
- **True**: Multiple sounds can play (UI feedback)
- **False**: Only one sound plays (game SFX, important events)

## Best Practices

### ✓ DO
- Use AudioEvent constants (type-safe)
- Set appropriate cooldowns to prevent spam
- Use priority for important sounds
- Keep volume in reasonable range (0.2-0.6)
- Allow overlap for UI feedback
- Prevent overlap for game events

### ✗ DON'T
- Use hardcoded strings ("ui_click")
- Skip cooldowns on frequent events
- Use very high volumes (>0.8)
- Allow overlap on important SFX
- Chain rapid sounds without delays

## Troubleshooting

### Sound Not Playing
1. Check if sound file exists in `sounds/` folder
2. Verify AudioEvent is registered in AUDIO_EVENT_FILES
3. Check cooldown hasn't blocked playback
4. Verify priority isn't lower than active sound
5. Check if audio is enabled: `audio.enabled`

### Sound Too Quiet/Loud
- Adjust volume parameter (0.0 to 1.0)
- Check system volume settings
- Verify sound file amplitude

### Sound Spam
- Add cooldown_ms parameter
- Increase cooldown duration
- Use allow_overlap=False

### Sounds Cutting Off
- Check priority levels
- Use allow_overlap=True for concurrent sounds
- Increase cooldown on interrupting sounds

---

**Quick Start**: Just import AudioEvent and use `audio.play(AudioEvent.EVENT_NAME)` ✓
