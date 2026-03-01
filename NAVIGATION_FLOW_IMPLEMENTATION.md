# Navigation Flow Implementation Summary

**Date:** February 20, 2026  
**Task:** Close the "line completion" loop with clear CTAs and reliable navigation

## Changes Implemented

### 1. Screen Name Constants
**File:** `game_proxima_parada.py` (lines 33-36)

Added constants for reliable screen navigation:
```python
SCREEN_COVER = "cover"
SCREEN_LINES = "line_select"
SCREEN_GAME = "game"
```

### 2. Line Completion Overlay - 3 Buttons
**File:** `game_proxima_parada.py` (lines 1231-1380)

Updated `show_line_completed()` overlay with three action buttons (Catalan):

#### Primary Button: "Tornar a línies"
- **Color:** Blue (0.25, 0.7, 0.95)
- **Action:** Navigate to LineSelectScreen
- **Size:** 200x42 (prominent)
- **Position:** Center top of button area

#### Secondary Button: "Repetir línia"
- **Color:** Medium blue (0.35, 0.55, 0.75)
- **Action:** Restart current line (calls `reset_run()`)
- **Size:** 180x36
- **Position:** Left of button area

#### Tertiary Button: "Sortir"
- **Color:** Dark red (0.5, 0.35, 0.35)
- **Action:** Exit to CoverScreen
- **Size:** 120x36
- **Position:** Right of button area

**Navigation Flow:**
- Closes overlay first
- Uses FadeTransition (0.25s duration)
- Reliable screen manager navigation

### 3. Game Reset Method
**File:** `game_proxima_parada.py` (lines 1910-1962)

Added `reset_run()` method to `ProximaParadaGame` class:

**Functionality:**
- Cancels all scheduled Clock events (rounds, animations, timeouts)
- Resets all game state variables:
  - Position: `current_index=0`, `next_index=1`
  - Stats: `score=0`, `streak=0`, `mistakes=0`
  - Lives: `bonus_lives=0`
  - Flags: `game_over=False`, `has_attempted=False`
  - Tracking: `visited_stations` reset to {0}
- Clears UI elements (tokens, overlays)
- Resets train and line view to initial state
- Starts fresh intro sequence and first round

**Does NOT reset:**
- Selected line (`line_id`)
- Current settings (`practice_mode`, `direction_mode`, `subtitles_enabled`)

### 4. Game Over UI - Navigation Button
**File:** `game_proxima_parada.py` (lines 1547-1617)

Updated `show_game_over()` with navigation buttons:

#### "Tornar a línies" Button (Primary)
- **Color:** Blue (0.25, 0.7, 0.95)
- **Action:** Navigate to LineSelectScreen
- **Size:** 180x40
- **Position:** Bottom left of panel

#### "Jugar de nou" Button (Secondary)
- **Color:** Medium blue (0.35, 0.55, 0.75)
- **Action:** Restart current line (calls `reset_run()`)
- **Size:** 150x40
- **Position:** Bottom right of panel

**Implementation Details:**
- Navigation closes game over overlay first
- Uses FadeTransition for smooth screen changes
- Safe cleanup of pulse animation before navigation

### 5. ESC Key Behavior
**Files:** `ui/screens.py`

Complete ESC key flow:

#### CoverScreen (lines 342-345)
```python
def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
    if key == 27:  # ESC
        App.get_running_app().stop()  # Exit app
        return True
```

#### LineSelectScreen (lines 747-750)
```python
def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
    if key == 27:  # ESC
        self._go_back()  # Go to CoverScreen
        return True
```

#### GameScreen (lines 397-401)
```python
def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
    if key == 27 and self.manager:  # ESC
        self.manager.transition = FadeTransition(duration=0.25)
        self.manager.current = "line_select"  # Go to LineSelectScreen
        return True
```

## Navigation Flow Diagram

```
┌─────────────┐
│ CoverScreen │ ◄── ESC exits app
└──────┬──────┘
       │ "Jugar" button
       ▼
┌────────────────┐
│ LineSelectScreen│ ◄── ESC goes back to cover
└────────┬───────┘
         │ Select line
         ▼
    ┌──────────┐
    │GameScreen│ ◄── ESC goes to line select
    └────┬─────┘
         │
         ├─── Line Completed ────┐
         │                       │
         │  ┌────────────────────▼─────────────┐
         │  │ "Tornar a línies" → LineSelect   │
         │  │ "Repetir línia"   → reset_run()  │
         │  │ "Sortir"          → CoverScreen  │
         │  └──────────────────────────────────┘
         │
         └─── Game Over ────────┐
                                │
            ┌───────────────────▼───────────────┐
            │ "Tornar a línies" → LineSelect    │
            │ "Jugar de nou"    → reset_run()   │
            └───────────────────────────────────┘
```

## Testing Checklist

### Manual Test Flow 1: Line Completion → Line Selection
1. ✅ Start game and play until line completion
2. ✅ Verify "LÍNIA COMPLETADA" overlay appears with 3 buttons
3. ✅ Click "Tornar a línies"
4. ✅ Verify navigation to LineSelectScreen with progress updated
5. ✅ Select different line
6. ✅ Verify new line starts correctly

### Manual Test Flow 2: Line Completion → Repeat
1. ✅ Play line until completion
2. ✅ Click "Repetir línia" button
3. ✅ Verify game resets (score=0, streak=0, position=start)
4. ✅ Verify intro banner shows
5. ✅ Verify same line plays again

### Manual Test Flow 3: Line Completion → Exit
1. ✅ Play line until completion
2. ✅ Click "Sortir" button
3. ✅ Verify navigation to CoverScreen

### Manual Test Flow 4: Game Over → Line Selection
1. ✅ Play until game over (run out of lives)
2. ✅ Verify game over overlay shows with route map
3. ✅ Click "Tornar a línies"
4. ✅ Verify navigation to LineSelectScreen

### Manual Test Flow 5: Game Over → Retry
1. ✅ Play until game over
2. ✅ Click "Jugar de nou"
3. ✅ Verify game resets and restarts same line

### Manual Test Flow 6: ESC Keys
1. ✅ From GameScreen: Press ESC → goes to LineSelectScreen
2. ✅ From LineSelectScreen: Press ESC → goes to CoverScreen
3. ✅ From CoverScreen: Press ESC → exits app

## Implementation Notes

### Safety & Cleanup
- All Clock events are properly cancelled before reset
- Overlays are removed from widget tree before navigation
- FadeTransition provides smooth visual feedback
- No memory leaks from scheduled events

### User Experience
- Primary actions use prominent blue colors
- Secondary actions use muted colors
- Exit/destructive actions use red tones
- All text in Catalan for consistency
- Button hierarchy clear through size and color

### Code Organization
- Screen constants centralized at module level
- Navigation logic separated from game logic
- Clean separation between overlay UI and navigation
- Reusable reset method for consistency

## Known Limitations

1. **No confirmation dialog** for "Sortir" button (could exit accidentally)
2. **No animation** when resetting game (instant)
3. **Tourist popup during arrival** may delay line completion screen
4. **Settings not accessible** from line completion/game over overlays

## Future Enhancements

1. Add confirmation dialog for "Sortir" action
2. Add smooth fade-out/fade-in when resetting game
3. Show completion stats (time, accuracy) in overlay
4. Add "Compartir resultats" (share results) button
5. Add achievements/badges for line completion
6. Remember last played line for quick retry
7. Add "Continue" option to resume partial progress

## Files Modified

1. `game_proxima_parada.py` - Main game logic and overlays
2. `ui/screens.py` - GameScreen ESC behavior (already correct)

## Catalan UI Text

All button labels are in Catalan:
- "Tornar a línies" - Back to lines
- "Repetir línia" - Repeat line
- "Sortir" - Exit
- "Jugar de nou" - Play again
- "LÍNIA COMPLETADA" - Line completed
- "FI DEL TRAJECTE" - End of route
