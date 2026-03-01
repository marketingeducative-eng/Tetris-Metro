# Ken Burns Animation - Visual Reference Guide

## Animation Timeline

```
TIME         ZOOM    VISUAL STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0.00s   →   1.00x   ▣ Image at normal scale
            1.01x   ░░░░░░░░░░░░░░░░░░░░░░░░░ (zoming in...)
            1.02x   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
            1.05x   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
            1.08x   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
1.75s   →   1.08x   ▓ Peak zoom (1.75s elapsed)
            1.07x   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (zooming out...)
            1.05x   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
            1.02x   ░░░░░░░░░░░░░░░░░░░░░░░░░
            1.00x   ▣ Image back to normal
3.50s   →   1.00x   ▣ Animation complete
```

## Popup Layout

### Before Animation (Popup Opening)
```
┌─────────────────────────────────────────┐
│                                         │
│  ╔═════════════════════════════════╗   │
│  ║  ┌──────────────────────────┐   ║   │
│  ║  │                          │   ║   │
│  ║  │     IMAGE (120px)        │   ║   │
│  ║  │   Starts at 1.0x scale   │   ║   │
│  ║  │                          │   ║   │
│  ║  └──────────────────────────┘   ║   │
│  ║                                  ║   │
│  ║    SAGRADA FAMILIA              ║   │
│  ║    "Reserva entrada..."         ║   │
│  ║                                  ║   │
│  ║        [Continuar]              ║   │
│  ╚═════════════════════════════════╝   │
│                                         │
│     (Semi-transparent overlay)         │
└─────────────────────────────────────────┘
```

### During Animation (Peak Zoom at 1.75s)
```
┌─────────────────────────────────────────┐
│                                         │
│  ╔═════════════════════════════════╗   │
│  ║ ┌──────────────────────────────┐ ║   │
│  ║ │  IMAGE ZOOMED TO 1.08x       │ ║   │
│  ║ │ (Subtle zoom up in progress) │ ║   │
│  ║ │  Creates depth perception    │ ║   │
│  ║ └──────────────────────────────┘ ║   │
│  ║                                  ║   │
│  ║    SAGRADA FAMILIA              ║   │
│  ║    "Reserva entrada..."         ║   │
│  ║   (Stays readable below image)  ║   │
│  ║        [Continuar]              ║   │
│  ╚═════════════════════════════════╝   │
│                                         │
│     (Semi-transparent overlay)         │
└─────────────────────────────────────────┘
```

### After Animation (Zoom Out Complete at 3.5s)
```
┌─────────────────────────────────────────┐
│                                         │
│  ╔═════════════════════════════════╗   │
│  ║  ┌──────────────────────────┐   ║   │
│  ║  │                          │   ║   │
│  ║  │     IMAGE (120px)        │   ║   │
│  ║  │   Back to 1.0x scale     │   ║   │
│  ║  │                          │   ║   │
│  ║  └──────────────────────────┘   ║   │
│  ║                                  ║   │
│  ║    SAGRADA FAMILIA              ║   │
│  ║    "Reserva entrada..."         ║   │
│  ║                                  ║   │
│  ║        [Continuar]              ║   │
│  ╚═════════════════════════════════╝   ║
│                                         │
│    Animation complete - User can now    │
│         click Continuar to dismiss      │
└─────────────────────────────────────────┘
```

## Stations with Ken Burns Animation

```
┌─ BARCELONA METRO TOURIST STATIONS ──────────────────┐
│                                                      │
│ 1. CATALUNYA (L1, L2, L3)                           │
│    ✓ Image: https://images.unsplash.com/...         │
│    ✠ Zone: Eixample                                 │
│    ✠ Priority: 5/5 ⭐                              │
│    ✠ Tip: "Bon punt per orientar-te..."            │
│                                                      │
│ 2. PASSEIG DE GRÀCIA (L3, L4)                       │
│    ✓ Image: https://images.unsplash.com/...         │
│    ✠ Zone: Eixample                                 │
│    ✠ Priority: 5/5 ⭐                              │
│    ✠ Tip: "Passeja amunt i avall..."               │
│                                                      │
│ 3. SAGRADA FAMILIA (L2, L5)                         │
│    ✓ Image: https://images.unsplash.com/...         │
│    ✠ Zone: Eixample                                 │
│    ✠ Priority: 5/5 ⭐                              │
│    ✠ Tip: "Reserva entrada amb antelació..."       │
│                                                      │
│ 4. JAUME I (L4)                                     │
│    ✓ Image: https://images.unsplash.com/...         │
│    ✠ Zone: Ciutat Vella                             │
│    ✠ Priority: 5/5 ⭐                              │
│    ✠ Tip: "Perdre't pel Gòtic és el millor pla"   │
│                                                      │
│ 5. BARCELONETA (L4)                                 │
│    ✓ Image: https://images.unsplash.com/...         │
│    ✠ Zone: Ciutat Vella                             │
│    ✠ Priority: 5/5 ⭐                              │
│    ✠ Tip: "Ideal al capvespre per passejar..."     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Animation Parameters

```
┌────────────────────────────────────────────────────┐
│           KEN BURNS EFFECT SETTINGS                │
├────────────────────────────────────────────────────┤
│                                                    │
│  Duration Breakdown:                              │
│  ├─ Phase 1 (Zoom In):    1.75 seconds            │
│  └─ Phase 2 (Zoom Out):   1.75 seconds            │
│  └─ TOTAL:                3.50 seconds            │
│                                                    │
│  Zoom Parameters:                                 │
│  ├─ Start Scale:          1.00x                   │
│  ├─ Peak Scale:           1.08x (+8%)             │
│  ├─ End Scale:            1.00x                   │
│                                                    │
│  Easing Curve:            in_out_quad             │
│  ├─ Entry:  Accelerating then easing out          │
│  ├─ Exit:   Easing in then accelerating           │
│                                                    │
│  Image Layout:                                    │
│  ├─ Container Height:     120px                   │
│  ├─ Allow Stretch:        True (fills width)      │
│  ├─ Keep Ratio:           False (fills height)    │
│                                                    │
└────────────────────────────────────────────────────┘
```

## User Flow

```
START GAME
    ↓
SELECT LINE
    ↓
PLAY & MOVE TRAIN
    ↓
REACH TOURIST STATION
├─ Sagrada Familia? → YES
├─ Tourist Highlight? → YES
├─ Priority >= 4? → YES
└─ Has Tip Text? → YES
    ↓
SHOW POPUP
    ├─ Semi-transparent overlay appears
    ├─ Panel slides into center
    ├─ IMAGE LOADS at top
    └─ Text displays below image
    ↓
START KEN BURNS ANIMATION
    ├─ 0-1.75s: Image zooms from 1.0x → 1.08x
    │           (Smooth acceleration, subtle depth)
    │
    ├─ 1.75-3.5s: Image zooms from 1.08x → 1.0x
    │             (Smooth deceleration, return to normal)
    │
    └─ 3.5s+: Animation complete, player reads content
    ↓
PLAYER CLICKS "Continuar"
    ├─ Animation cancels cleanly
    ├─ References cleared (no memory leak)
    ├─ Popup fades out
    └─ Overlay removed
    ↓
GAME CONTINUES
    ↓
END
```

## Comparison: Before vs After

### Before Enhancement
```
┌──────────────────────────┐
│   TOURIST POPUP          │
│                          │
│  SAGRADA FAMILIA         │
│                          │
│  "Reserva entrada       │
│   amb antelació:        │
│   hi ha cues sovint"    │
│                          │
│   [Continuar]            │
└──────────────────────────┘
```

### After Enhancement  
```
┌──────────────────────────┐
│   TOURIST POPUP          │
│                          │
│  ┌────────────────────┐  │
│  │   BEAUTIFUL IMAGE  │  │ ← NEW!
│  │  (Zooming 1.0→1.08 │  │ ← NEW!
│  │   + Pan Animation) │  │ ← NEW!
│  └────────────────────┘  │
│                          │
│  SAGRADA FAMILIA         │
│  "Reserva entrada       │
│   amb antelació:        │
│   hi ha cues sovint"    │
│                          │
│   [Continuar]            │
└──────────────────────────┘
```

## Browser Developer Timeline

If implemented in web version, Chrome DevTools would show:

```
Timeline View:
├─ 0.00s ─ Tourist popup Mount
├─ 0.10s ─ Image load start (Unsplash fetch)
├─ 0.50s ─ Image load complete
├─ 0.50s ─ Animation start: scale=1.0
├─ 0.75s ─ Animation mid-phase 1: scale=1.04
├─ 1.75s ─ Animation peak: scale=1.08
├─ 2.50s ─ Animation mid-phase 2: scale=1.04
├─ 3.50s ─ Animation complete: scale=1.0
├─ 3.50s ─ (Player clicks Continuar)
├─ 3.51s ─ Animation cancel
├─ 3.55s ─ Popup unmount
└─ 3.60s ─ Game continues
```

## Memory Profile

```
ANIMATION LIFECYCLE
═════════════════════════════════

ON POPUP OPEN:
  └─ self._tourist_image_anim = Animation chain object
  └─ self._tourist_image_widget = Image widget reference
  └─ Memory: ~2MB (image cache)

DURING ANIMATION (3.5 seconds):
  └─ Animation frame updates 60x/sec
  └─ GPU handles rendering
  └─ Memory stable

ON POPUP CLOSE:
  ├─ anim.cancel(image_widget)  ← Stops animation
  ├─ self._tourist_image_anim = None  ← Clear reference
  ├─ self._tourist_image_widget = None  ← Clear reference  
  └─ Memory released
```

---

This visual guide helps understand the Ken Burns animation implementation at a glance.
