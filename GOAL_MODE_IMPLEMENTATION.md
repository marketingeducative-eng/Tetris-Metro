# Goal Mode Implementation Summary

## Overview
Implemented a comprehensive **Goal Mode** feature that allows players to set tourist destination goals and receive recommendations at Game Over.

## Features Implemented

### 1. Tag-to-Icon Mapping System
- **Location**: `game_proxima_parada.py` (lines 38-128)
- **Function**: `get_station_icon(tags)`
- Maps tourist tags to emoji/icons:
  - Gaudí → 🎨
  - Park Güell → 🏞️
  - Beach → 🏖️
  - Gòtic → 🏰
  - Camp Nou → ⚽
  - And 30+ more mappings

### 2. GameState Extensions
- **Location**: `game_proxima_parada.py` (GameState.__init__)
- New attributes:
  - `goal_mode`: Boolean flag for goal mode activation
  - `goal_station_id`: Normalized station ID of the goal (e.g., "SAGRADA_FAMILIA")
  - `goal_reached`: Boolean flag indicating goal achievement
- Modified `handle_correct_answer()` to detect goal completion

### 3. Tourist Recommendations UI
- **Location**: `game_proxima_parada.py` (show_game_over method)
- Expanded Game Over panel from 500→700px height
- Added "LLOCS D'INTERÈS" section showing 3 recommendations:
  - Each recommendation shows:
    - Icon based on location tags
    - Station name (bold)
    - One-liner description
    - "Jugar fins aquí" button (green)
- Recommendations filtered by:
  - Priority ≥ 3
  - Highlight = true
  - Present in current line's stations

### 4. Line Map Goal Marker
- **Location**: `line_map_view.py`
- New properties:
  - `goal_index`: Station index to mark as goal
  - `goal_pulse`: Animation property for pulsing effect
- New methods:
  - `_draw_goal_slot()`: Renders golden star marker with glow
  - `_start_goal_pulse()`: Continuous pulse animation (1.0 ↔ 1.2)
- Visual design:
  - Gold/yellow color scheme (different from active red)
  - Pulsing outer glow
  - White star shape in center
  - Slower pulse than active station (1.2s vs 0.8s)

### 5. Goal HUD Label
- **Location**: `game_proxima_parada.py` (_setup_hud)
- New label: `self.goal_label`
  - Shows "⭐ Objectiu: [Station Name]"
  - Gold color (1.0, 0.85, 0.2)
  - Positioned below direction label (if present)
- Method: `_update_goal_label()`
  - Updates label text and line map marker
  - Called during reset_run()

### 6. Goal Celebration Popup
- **Location**: `game_proxima_parada.py` (show_goal_celebration)
- Triggered when goal station is reached
- Panel features:
  - Large station icon (80sp)
  - "🎉 OBJECTIU ASSOLIT! 🎉" title with pulse animation
  - Station name (24sp bold)
  - Tourist tip/description
  - Final score and streak stats
  - Two buttons:
    - "Tornar a línies" (primary, blue)
    - "Continuar jugant" (secondary, green) - disables goal mode and continues
- Visual style:
  - Gold border (consistent with goal theme)
  - Pulsing title animation
  - Plays line completion sound

### 7. Reset Run with Goal Parameters
- **Location**: `game_proxima_parada.py` (reset_run method)
- Updated signature: `reset_run(goal_mode=False, goal_station_id=None)`
- Sets goal state on GameState
- Calls `_update_goal_label()` to refresh UI

## Data Flow

### Starting a Goal Run
1. Player clicks "Jugar fins aquí" in Game Over recommendations
2. `reset_run(goal_mode=True, goal_station_id="STATION_ID")` called
3. GameState updated with goal parameters
4. Goal label updated: "⭐ Objectiu: Station Name"
5. Line map marker set at goal station (golden star)
6. Game starts normally

### During Gameplay
1. Player progresses through stations
2. Goal marker visible on line map (pulsing gold star)
3. Goal label visible in HUD
4. Each correct answer checks: `current_station_id == goal_station_id`

### Reaching the Goal
1. `handle_correct_answer()` detects goal match
2. Sets `goal_reached = True`
3. Returns `goal_reached` in result dict
4. Game flow shows goal celebration popup
5. Player can either:
   - Return to line selection
   - Continue playing (goal mode disabled)

## Key Files Modified

1. **game_proxima_parada.py** (2700+ lines)
   - Added tag-to-icon mapping
   - Extended GameState
   - Updated show_game_over with recommendations
   - Added show_goal_celebration
   - Modified reset_run
   - Added _update_goal_label
   - Updated _handle_correct_answer

2. **line_map_view.py** (~460 lines)
   - Added goal_index and goal_pulse properties
   - Added _draw_goal_slot method
   - Added _start_goal_pulse method
   - Updated draw() to render goal markers

3. **data/tourist_ca.json** (exists - not modified, used for data)

## Testing Checklist

- [ ] Game Over shows 3 tourist recommendations
- [ ] Each recommendation has correct icon
- [ ] "Jugar fins aquí" button starts goal mode
- [ ] Goal label appears in HUD during goal mode
- [ ] Goal marker (golden star) visible on line map
- [ ] Goal marker pulses smoothly
- [ ] Reaching goal station triggers celebration popup
- [ ] Celebration shows correct station info and icon
- [ ] "Continuar jugant" button disables goal mode
- [ ] "Tornar a línies" navigates correctly
- [ ] Multiple goal runs work consecutively
- [ ] Goal mode compatible with practice/direction modes

## Visual Design Elements

### Color Scheme
- **Goal Marker**: Gold (1.0, 0.85, 0.2) with yellow glow
- **Goal Label**: Gold (1.0, 0.85, 0.2)
- **Celebration Border**: Gold (1.0, 0.85, 0.2)
- **Play Button**: Green (0.3, 0.75, 0.4)

### Animations
- Goal marker: Continuous pulse (1.0 ↔ 1.2, 1.2s cycle)
- Celebration title: Pulse (28sp ↔ 32sp, 0.6s cycle)

### Screen Navigation
```
Game Over (show recommendations)
    ↓ [Jugar fins aquí]
Game with Goal Mode (marker + label visible)
    ↓ [reach goal]
Goal Celebration Popup
    ↓ [Tornar a línies]  →  Line Selection Screen
    ↓ [Continuar jugant]  →  Continue current run (goal disabled)
```

## Future Enhancements (Optional)
- Sound effect specifically for goal reached
- Confetti/particle effects in celebration
- Progress bar showing distance to goal
- Goal history/achievements tracking
- Multiple goal selection
- Time challenge mode (reach goal in N stations)
