# Direction Mode Feature

## Overview
Direction Mode adds an advanced gameplay layer that tests the player's understanding of metro line direction and terminal stations.

## Features Implemented

### 1. **Direction Awareness**
- HUD displays the terminal station: `➜ Direcció: Trinitat Nova`
- Shows the line's destination endpoint (from `line.endpoints['to']`)
- Helps players understand they're traveling in a specific direction along L3

### 2. **Visual Integration**
- Direction label appears below title in golden color: `(1, 0.9, 0.3, 1)`
- Title updates to show `[DIRECCIÓ]` tag
- All UI elements automatically reposition to accommodate direction info:
  - Station name moves from `top: 0.95` → `top: 0.92`
  - Stats move from `top: 0.87` → `top: 0.84`

### 3. **Tutorial Adaptation**
- Instructions change from 4 steps to 5 steps
- Adds: `"2. Confirma la direcció del tren"`
- Maintains Catalan language consistency

### 4. **High Score Separation**
- Direction mode games tracked separately
- File naming: `high_score_direction.json` vs `high_score.json`
- Combined modes: `high_score_practice_direction.json`
- Prevents mixing scores between game modes

## Usage

### Command Line
```bash
# Standard mode
python game_proxima_parada.py

# Direction mode
python game_proxima_parada.py --direction

# Combined with practice mode
python game_proxima_parada.py --direction --practice
```

### Programmatic
```python
from game_proxima_parada import ProximaParadaApp

# Enable direction mode
app = ProximaParadaApp(direction_mode=True)
app.run()

# With practice mode
app = ProximaParadaApp(practice_mode=True, direction_mode=True)
app.run()
```

### Test File
```bash
python test_direction_mode.py
```

## Technical Implementation

### Parameter Flow
```
main() 
  → ProximaParadaApp(direction_mode=True)
    → ProximaParadaGame(direction_mode=True)
      → GameState(direction_mode=True)
        → Renderer uses state.direction_mode for HUD
```

### Key Code Changes

#### GameState
```python
def __init__(self, metro_line, practice_mode=False, direction_mode=False):
    self.direction_mode = direction_mode
    
def get_direction_terminal(self):
    """Returns the 'to' endpoint - Trinitat Nova for L3"""
    return self.line.endpoints['to']
```

#### Renderer HUD
```python
if self.state.direction_mode:
    terminal_station = self.state.get_direction_terminal()
    self.direction_label = Label(
        text=f"➜ Direcció: {terminal_station}",
        font_size='18sp',
        bold=True,
        pos_hint={'top': 0.97},
        color=(1, 0.9, 0.3, 1)
    )
```

#### Dynamic Positioning
```python
# Adjust all labels based on direction mode presence
top_offset = 0.95 if not self.state.direction_mode else 0.92
stats_offset = 0.87 if not self.state.direction_mode else 0.84
```

## Barcelona L3 Context
- **Line**: L3 (Green Line)
- **Direction**: Zona Universitària → **Trinitat Nova** (26 stations)
- **Terminal Station**: Trinitat Nova (neighborhood in Sant Andreu district)

## Future Enhancements (Optional)
1. **Direction Confirmation Mechanic**: Require player to confirm they know which direction before selecting station
2. **Bidirectional Play**: Alternate between `'from'` and `'to'` endpoints each round
3. **Direction Hints**: Show intermediate station to help orient players
4. **Wrong Direction Penalty**: Extra life loss if player doesn't understand current direction

## Educational Value
- Teaches metro line topology beyond just station names
- Reinforces spatial awareness of Barcelona's metro network
- Prepares players for real navigation scenarios where direction matters
- Differentiates between "L3 to Trinitat Nova" vs "L3 to Zona Universitària"
