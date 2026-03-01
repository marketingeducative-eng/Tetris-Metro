## HUD Refactor: Visual Hierarchy Enhancement

### Overview
Refactored the game HUD to establish clear visual hierarchy: dominant score display, animated streak highlights, and removal of travel duration for cleaner layout.

### Changes Implemented

#### 1. **Visually Dominant Score** ✓
- **Font Size**: 48sp (increased from 16sp) - largest element on HUD
- **Color**: Gold (1, 0.95, 0.4, 1) - warm, eye-catching
- **Position**: Top-left corner (x: 0.02, top: 0.92)
- **Size**: 200x60 px for prominence
- **Bold**: Yes

**Before:**
```
Score: 1250pts • High: 2000 • Streak: 5 • Lives: ❤️❤️❤️ • 15/27 • 2.3s
```

**After:**
```
[Large gold "1250"]  Ratxa: 5  High: 2000 • Lives: ❤️❤️❤️ • 15/27
```

#### 2. **Animated Streak Highlight** ✓
- **Trigger**: Automatically animates when streak increases and > 0
- **Animation Type**: Scale + Color Pulse
  - Scale: 20sp → 26sp (0.15s out_quad) → back to 20sp (0.2s in_out_quad)
  - Color: Orange (1, 0.6, 0.2, 1) → Bright yellow (1, 0.9, 0.3, 1) → back
- **Duration**: Total 0.35s for snappy feedback
- **Tracking**: `previous_streak` property tracks last value to detect increases

**Code Implementation:**
```python
def _animate_streak_highlight(self):
    """Animate streak label when it increases (scale + glow effect)"""
    # Scale bounce: 20sp → 26sp → 20sp
    # Color pulse: orange → bright yellow → orange
    # Provides strong visual feedback for streak gains
```

#### 3. **Travel Duration Hidden** ✓
- **Removed From Display**: No longer shown in HUD
- **Rationale**: 
  - Reduces visual clutter
  - Players focus on immediate feedback (score, streak, progress)
  - Duration is still calculated internally for game logic
- **Display Info (remaining)**:
  - Score (dominant, 48sp)
  - Streak (animated, 20sp)
  - High Score (secondary, 15sp)
  - Lives Remaining (secondary, 15sp)
  - Progress Counter (secondary, 15sp)

#### 4. **Clean, Balanced Layout** ✓
- **Three Tier Hierarchy**:
  1. **Tier 1 (Dominant)**: Score label (48sp, gold, left side)
  2. **Tier 2 (Important)**: Streak label (20sp, orange, animates, center-left)
  3. **Tier 3 (Supporting)**: Info label (15sp, gray, details on right)
- **Visual Spacing**: Each element has distinct x-position to avoid overlap
- **Color Coding**: 
  - Gold = Score (primary metric)
  - Orange = Streak (achievement/combo indicator)
  - Gray = Supporting info (secondary metrics)

### File Changes

**[game_proxima_parada.py](game_proxima_parada.py)**:

1. **Label Properties** (lines 260-267):
   - Replaced `self.stats_label` with three separate labels:
     - `self.score_label` (large, dominant)
     - `self.streak_label` (animatable, highlighted)
     - `self.info_label` (compact, secondary)
   - Added `self.previous_streak` for tracking streak increases

2. **UI Setup** (lines 420-455):
   - Score label: 48sp, bold, gold, top-left
   - Streak label: 20sp, bold, orange, center-left
   - Info label: 15sp, gray, compact format
   - Each positioned with `pos_hint` for responsive layout

3. **Update Method** (lines 518-556):
   - Refactored `update_stats()` to populate three labels separately
   - Detects streak increases and triggers animation
   - Removed `travel_duration` from display
   - Compact info format: "High: X • Lives: ❤️ • Progress: X/Y"

4. **Animation Method** (lines 558-602):
   - New `_animate_streak_highlight()` method
   - Scale animation: 20sp → 26sp → 20sp
   - Color animation: orange → bright yellow → orange
   - Chained animations for smooth transition
   - Provides strong visual feedback on streak gains

### Visual Hierarchy Summary

```
Tier 1 - DOMINANT SCORE
┌─────────────────────┐
│  1250 pts (48sp)    │ ← Primary focus, gold color
└─────────────────────┘

Tier 2 - STREAK (ANIMATED)
Ratxa: 5 [PULSES when increases]

Tier 3 - SUPPORTING INFO
High: 2000 • Lives: ❤️❤️❤️ • 15/27
```

### Testing Notes

- ✓ Game starts without errors
- ✓ Score displays correctly in large gold text
- ✓ Streak animates with scale + glow when increased
- ✓ Travel duration completely hidden from display
- ✓ Layout remains balanced with three-tier hierarchy
- ✓ Layout adapts to direction_mode toggle

### Benefits

1. **Clarity**: Users immediately know score is most important metric
2. **Feedback**: Animated streak provides clear reward signal for consecutive correct answers
3. **Focus**: Removing travel duration reduces cognitive load
4. **Balance**: Three-tier layout provides visual hierarchy without crowding
5. **Engagement**: Animation gives satisfying visual response to achievements
