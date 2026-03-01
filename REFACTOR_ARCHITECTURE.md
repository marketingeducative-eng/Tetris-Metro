# Game Loop Refactoring - Architecture Documentation

## Overview
The game has been refactored from a monolithic 684-line `ProximaParadaGame` class into a clean separation of concerns with three decoupled components.

## Key Features
- ✅ **Decoupled Architecture**: GameState (logic) / Renderer (UI) / InputController (events)
- ✅ **Bonus Life System**: Earn +1 life every 7 correct answers (max +2 lives)
- ✅ **Practice Mode**: Unlimited mistakes with separate high score tracking
- ✅ **Random Seed Support**: Reproducible game runs for testing
- ✅ **Dynamic Difficulty**: Time (3.2s→2.2s) and radius (50px→38px) scaling
- ✅ **High Score Persistence**: Separate files for normal and practice modes
- ✅ **Visual Feedback**: Success flash + glow animations + life indicators
- ✅ **Tutorial System**: 5-second onboarding overlay
- ✅ **Deterministic Validation**: Clock-based timeout handling

## Architecture

### 1. GameState (Logic Layer)
**Purpose**: Pure game logic and state management - no UI dependencies

**Responsibilities**:
- Game state tracking (score, streak, mistakes, high_score, indices)
- Round state management (waiting for answer, attempted, answered correctly)
- Difficulty calculations (travel duration, drop radius)
- Game logic processing (correct/wrong/timeout handlers)
- High score persistence (load/save JSON)

**Key Methods**:
- `calculate_travel_duration()` - Dynamic difficulty based on streak
- `calculate_drop_radius()` - Precision scaling based on streak
- `start_round(current_time)` - Initialize new round state
- `handle_correct_answer()` - Process correct answer, return feedback data
- `handle_wrong_answer()` - Process wrong answer, return feedback data
- `handle_timeout()` - Process timeout, return feedback data
- `check_game_over()` - Check win/loss conditions, save high score

**Benefits**:
- Testable in isolation (no Kivy dependencies)
- Pure functions return data dictionaries instead of directly manipulating UI
- Clear single responsibility

### 2. Renderer (UI Layer)
**Purpose**: All UI rendering and visual updates

**Responsibilities**:
- Widget creation and management (LineMapView, TrainSprite, Labels)
- Layout setup (background, HUD, token area)
- Visual updates (stats, next station, feedback messages)
- Animations (success flash, highlight node)
- Overlays (tutorial, game over)
- Token display management

**Key Methods**:
- `setup_all()` - Initialize all UI components
- `update_stats()` - Refresh HUD display
- `update_next_station(name)` - Update station label
- `show_feedback(message, color, duration)` - Temporary feedback
- `animate_success(node_index)` - Green burst animation
- `animate_highlight(node_index)` - Golden glow animation
- `move_train(target_index, duration)` - Train movement
- `show_tutorial(callback)` - Tutorial overlay
- `show_game_over(is_new_record)` - Game over screen

**Benefits**:
- All visual logic in one place
- Easy to modify UI without touching game logic
- Reusable rendering components

### 3. InputController (Event Layer)
**Purpose**: Event handling and input validation

**Responsibilities**:
- Token generation (correct + distractors)
- Token positioning (randomized to avoid bias)
- Drop validation (position, timing, correctness)
- Timeout scheduling and cancellation
- Input locking (one attempt per station)

**Key Methods**:
- `generate_tokens(on_drop_callback)` - Create 1 correct + 2 distractors
- `validate_drop(token, x, y)` - Check drop validity, return result
- `schedule_timeout(callback, duration)` - Set timeout timer
- `cancel_timeout()` - Cancel pending timeout

**Benefits**:
- Clean separation of input handling from game logic
- Deterministic drop validation using Clock.get_time()
- Encapsulated token management

### 4. ProximaParadaGame (Orchestrator)
**Purpose**: Coordinate the three components

**Responsibilities**:
- Create and initialize components
- Connect callbacks between components
- Orchestrate game flow
- Translate component outputs to appropriate actions

**Key Methods**:
- `__init__()` - Setup components and connect callbacks
- `_start_next_round()` - Coordinate round start across components
- `_on_token_dropped()` - Route drop events through validation
- `_handle_correct_answer()` - Coordinate correct answer response
- `_handle_wrong_answer()` - Coordinate wrong answer response
- `_handle_timeout()` - Coordinate timeout response
- `_on_train_arrived()` - Handle train arrival callback

**Benefits**:
- Thin orchestration layer
- Clear data flow between components
- Easy to understand game loop

## Data Flow

```
User Input → InputController.validate_drop()
          ↓
          Returns: 'correct' | 'wrong' | 'timeout' | None
          ↓
ProximaParadaGame._on_token_dropped()
          ↓
          Calls appropriate handler
          ↓
GameState.handle_XXX()
          ↓
          Returns: { 'message': str, 'bonus': int, ... }
          ↓
ProximaParadaGame coordinates:
  1. Renderer.animate_XXX()
  2. Renderer.show_feedback()
  3. Renderer.update_stats()
  4. Schedule next round
```

## Benefits of Refactoring

### 1. **Separation of Concerns**
- Logic, rendering, and input are completely decoupled
- Each component has a single, clear responsibility

### 2. **Testability**
- GameState can be unit tested without Kivy
- InputController validation logic is isolated
- Renderer methods can be tested with mock states

### 3. **Maintainability**
- Changes to game logic don't affect rendering
- UI redesigns don't touch game logic
- Input handling changes are isolated

### 4. **Readability**
- Each class is focused and understandable
- Clear boundaries between components
- Orchestrator shows high-level game flow

### 5. **Extensibility**
- Easy to add new game states
- Simple to add new UI elements
- Straightforward to add new input methods

## Implementation Details

### State Communication
Components communicate through:
- **Return values**: GameState methods return data dictionaries
- **Callbacks**: Renderer accepts callbacks for events
- **Direct calls**: Orchestrator calls component methods

### No Circular Dependencies
- GameState: No dependencies on other components
- Renderer: Only depends on GameState (read-only state access)
- InputController: Depends on GameState and Renderer (read-only)
- ProximaParadaGame: Depends on all three (orchestrates)

### Memory Management
- Renderer manages widget lifecycle
- GameState manages data only
- InputController manages event scheduling

## File Size Comparison
- **Before**: 684 lines in one monolithic class
- **After**: 
  - GameState: ~150 lines (pure logic)
  - Renderer: ~280 lines (UI only)
  - InputController: ~120 lines (events only)
  - ProximaParadaGame: ~80 lines (orchestration)
  - **Total**: ~630 lines (same functionality, better organized)

## Migration Notes
All existing features preserved:
- ✅ Game mechanics unchanged
- ✅ Dynamic difficulty (time + radius scaling)
- ✅ High score persistence
- ✅ Animations (success flash + glow highlight)
- ✅ Tutorial overlay
- ✅ Deterministic timeout validation
- ✅ Per-station validation lock
- ✅ Randomized token positions

## Bonus Life System

Players can earn extra lives through consistent performance:

**Mechanics**:
- Start with 3 base lives (mistake limit)
- Every 7 correct answers in a row → +1 bonus life 💚
- Maximum of 2 bonus lives (5 total lives)
- Wrong answer or timeout resets streak to 0
- Bonus lives extend the mistake threshold

**Progression**:
```
Streak  0: ❤️❤️❤️       (3 lives - starting)
Streak  7: ❤️❤️❤️💚     (4 lives - first bonus!)
Streak 14: ❤️❤️❤️💚💚   (5 lives - maximum!)
```

**HUD Display**:
- Lives shown with heart emojis
- Red hearts (❤️) = Base lives remaining
- Green hearts (💚) = Bonus lives from streaks
- Example: `Lives: ❤️❤️💚` = 2 base + 1 bonus life left

**Feedback**:
- Life granted message: "Correcte! +1100 💚+1 VIDA!"
- HUD updates immediately with new heart
- Provides strategic depth and comeback potential

**Implementation**:
- `GameState.bonus_lives` tracks earned lives
- `GameState.base_lives` = 3 (constant)
- Total lives = base_lives + bonus_lives
- Game over when mistakes >= total_lives

**Benefits**:
- Rewards consistent accuracy
- Provides forgiveness for late-game difficulty
- Creates comeback opportunities
- Adds strategic depth to gameplay

See `BONUS_LIVES_GUIDE.py` and `test_bonus_lives.py` for details.

## Testing Support

### Practice Mode
The game supports a practice mode flag for unlimited gameplay:

```python
# Practice mode - unlimited mistakes, separate stats
app = ProximaParadaApp(practice_mode=True)
app.run()

# Normal mode - 3 mistakes limit
app = ProximaParadaApp()
app.run()

# Combined: practice + reproducible
app = ProximaParadaApp(practice_mode=True, random_seed=42)
app.run()
```

**Features**:
- **No Game Over**: Mistakes never end the session
- **Separate Stats**: Uses `high_score_practice.json` 
- **Visual Indicators**: Blue title color + "[PRÀCTICA]" label
- **Error Counter**: Shows total (not X/3)
- **Same Difficulty**: Full streak-based scaling preserved

**Use Cases**:
- Learning station sequences
- Testing strategies
- Building muscle memory
- Warm-up before competitive play

### Random Seed for Reproducibility
The game now supports an optional `random_seed` parameter for reproducible runs:

```python
# Reproducible game for testing
app = ProximaParadaApp(random_seed=42)
app.run()

# Normal gameplay (random)
app = ProximaParadaApp()
app.run()
```

**Benefits**:
- **Reproducible Testing**: Same seed = same token sequences
- **Debugging**: Reproduce specific scenarios
- **Automated Testing**: Verify game behavior deterministically
- **Speedruns**: Record and verify optimal playthroughs

**Implementation**:
- Seed is passed from `ProximaParadaApp` → `ProximaParadaGame` → `InputController`
- `InputController` sets the seed in its constructor
- All randomization (token generation, position shuffling) uses the seeded RNG

**Testing Scripts**:
- `test_reproducibility.py`: Verifies same seed produces identical sequences
- `test_deterministic_game.py`: Example of running a reproducible game
- `test_practice_mode_logic.py`: Verifies practice mode behavior
- `test_practice_mode.py`: Launches practice mode game
- `MODES_COMPARISON.py`: Detailed feature comparison

## Future Improvements Enabled
This refactoring makes these additions easier:
- **Multiple game modes**: Just swap GameState implementations or use flags
- **Network multiplayer**: GameState can be synchronized
- **Replay system**: Record GameState method calls (now with reproducible seeds)
- **AI opponents**: Access GameState without UI (test with fixed seeds)
- **Different UIs**: Swap Renderer implementations
- **Accessibility**: Add alternative InputControllers
- **Regression testing**: Fix seed to catch behavior changes
- **Progressive difficulty**: Add more practice tiers or custom modes
