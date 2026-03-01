# Train Movement Easing Animation

## Overview

The train sprite now uses **smooth ease-in-out interpolation** for natural, realistic movement between stations. Instead of linear movement at constant speed, the train now:

1. **Starts slowly** (ease-in) - Gradual acceleration from the current station
2. **Accelerates smoothly** - Reaches peak speed in the middle of the journey
3. **Slows down** (ease-out) - Gradual deceleration before arriving at the target station

## Implementation

### Default Easing Function

The train now uses **quintic easing (`in_out_quint`)** by default, which provides:
- Very smooth acceleration and deceleration curves
- More pronounced easing effect than cubic
- Natural, comfortable motion

### Easing Over `time_to_arrival`

The easing function is applied over the entire `duration` parameter (typically `time_to_arrival` from game logic):
- The animation interpolates position from start to end over the full duration
- The easing function modulates the interpolation curve
- Time progression is non-linear, creating the smooth effect

### Available Easing Functions

You can customize the easing function when creating a train or change it dynamically:

```python
# Create train with specific easing
train = TrainSprite(easing_function='in_out_sine')

# Change easing function later
train.set_easing_function('in_out_expo')
```

#### Easing Options:

| Function | Description | Visual Effect |
|----------|-------------|---------------|
| `in_out_quint` | Quintic (smooth) | Very smooth, pronounced easing (default) |
| `in_out_cubic` | Cubic (moderate) | Moderate smoothness, balanced |
| `in_out_sine` | Sinusoidal (gentle) | Gentle, natural sine wave motion |
| `in_out_expo` | Exponential (dramatic) | Dramatic acceleration/deceleration |
| `in_out_quad` | Quadratic (subtle) | Subtle easing effect |
| `linear` | No easing | Constant speed (old behavior) |

## Code Changes

### TrainSprite Class (`train_sprite.py`)

1. **Constructor** - Added `easing_function` parameter with default `'in_out_quint'`
2. **move_to_node()** - Enhanced documentation explaining the ease-in-out interpolation over time_to_arrival
3. **set_easing_function()** - New method to change easing function dynamically
4. **Animation** - Uses `t=self.easing_function` parameter in Kivy Animation

### Key Code Section:

```python
# Create smooth ease-in-out animation
# The 't' parameter controls the interpolation curve over time_to_arrival
self.current_animation = Animation(
    train_x=target_x,
    train_y=target_y,
    duration=duration,  # time_to_arrival from game logic
    t=self.easing_function  # Smooth ease-in-out interpolation
)
```

## Testing

### Run the Easing Comparison Demo

To see the different easing functions in action side-by-side:

```bash
python test_easing_comparison.py
```

This demo shows 5 trains moving simultaneously with different easing functions, making it easy to compare the visual effects.

### Run the Standard Train Demo

To test the enhanced smooth movement with default easing:

```bash
python test_train.py
```

## Technical Details

### How Kivy Animation Easing Works

Kivy's `Animation` class uses the `t` parameter to specify an easing/transition function:
- Takes progress value from 0 to 1 (linear time)
- Returns interpolated value from 0 to 1 (eased time)
- The return value determines the actual position along the path

For `in_out_quint`:
- Progress 0.0 → Output ~0.0 (slow start)
- Progress 0.5 → Output ~0.5 (mid-speed)
- Progress 1.0 → Output ~1.0 (slow arrival)

The output curve is non-linear, creating the smooth acceleration/deceleration effect.

## Usage in Game

The game controller calls `move_train()` with the calculated `travel_duration`:

```python
# In game logic
travel_duration = self.state.calculate_travel_duration()
self.renderer.move_train(target_index, travel_duration)

# In renderer
def move_train(self, target_index, duration):
    self.train.move_to_node(target_index, duration=duration)
```

The `duration` parameter is the `time_to_arrival`, and the easing function automatically applies smooth interpolation over this time period.

## Benefits

1. **More realistic** - Trains in real life don't move at constant speed
2. **Smoother visually** - Gradual acceleration/deceleration is easier on the eyes
3. **Professional feel** - Modern games use easing for all animations
4. **Customizable** - Easy to experiment with different easing functions
5. **No performance impact** - Kivy's Animation handles interpolation efficiently

## Backward Compatibility

To get the old linear movement behavior, simply set the easing function to `'linear'`:

```python
train.set_easing_function('linear')
```

Or create the train with linear easing:

```python
train = TrainSprite(easing_function='linear')
```
