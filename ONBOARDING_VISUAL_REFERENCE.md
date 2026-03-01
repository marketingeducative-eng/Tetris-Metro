# Narrative Onboarding - Visual Flow Reference

```
┌─────────────────────────────────────────────────────────────┐
│                     GAME LAUNCH                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Check Settings    │
                    │ has_completed_    │
                    │ onboarding?       │
                    └───────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                  FALSE               TRUE
                    │                   │
                    ▼                   ▼
        ┌─────────────────────┐   ┌──────────────┐
        │  ONBOARDING FLOW    │   │ NORMAL FLOW  │
        │  (First Launch)     │   │ (Skip)       │
        └─────────────────────┘   └──────────────┘
                    │                   │
                    │                   ▼
                    │           Show Intro Banner
                    │                   │
                    │                   ▼
                    │           Show Tutorial
                    │                   │
                    │                   ▼
                    │           Start Game
                    │
                    ▼
        ┌─────────────────────────────────────────┐
        │  CINEMATIC SEQUENCE                     │
        ├─────────────────────────────────────────┤
        │  0.0s - 1.0s:  Fade in from black       │
        │                Ambient sound starts     │
        │                                         │
        │  1.5s - 2.7s:  "Acabes d'arribar..."   │
        │                [Fade in → hold → out]   │
        │                                         │
        │  3.4s - 4.6s:  "El metro serà..."      │
        │                [Fade in → hold → out]   │
        │                                         │
        │  5.3s - 6.5s:  "Per moure't..."        │
        │                [Fade in → hold → out]   │
        │                                         │
        │  7.2s - 8.0s:  "Avui és el teu..."     │
        │                [Fade in → stays]        │
        │                                         │
        │  8.5s:         Buttons fade in          │
        └─────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            PRIMARY BUTTON      SECONDARY BUTTON
          "Començar el teu    "Need help in
           primer dia"         English?"
                    │                   │
                    │                   ▼
                    │         ┌──────────────────┐
                    │         │ ENGLISH HELP     │
                    │         │ MODAL            │
                    │         ├──────────────────┤
                    │         │ • How to Play    │
                    │         │ • Instructions   │
                    │         │ • Gameplay note  │
                    │         └──────────────────┘
                    │                   │
                    │         "Start my first day
                    │          in Catalan"
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ ON COMPLETE       │
                    ├───────────────────┤
                    │ 1. Set flag=True  │
                    │ 2. Save settings  │
                    │ 3. Activate       │
                    │    first_day_mode │
                    │ 4. Reset progress │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ TRANSITION        │
                    ├───────────────────┤
                    │ • Fade out        │
                    │ • Show banner:    │
                    │   "El teu primer  │
                    │    dia a BCN"     │
                    │ • Show tutorial   │
                    │ • Start game      │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ FIRST DAY MODE    │
                    │ ACTIVE            │
                    └───────────────────┘
```

## Button Interaction Flow

```
┌────────────────────────────────────┐
│  PRIMARY BUTTON                    │
│  "Començar el teu primer dia"      │
│                                    │
│  Style:                            │
│  • Large (380x56px)                │
│  • Green background                │
│  • Bold white text                 │
│  • Prominent positioning           │
└────────────────────────────────────┘
                 │
                 ▼
      Complete Onboarding
      Activate First Day Mode
      Start Game


┌────────────────────────────────────┐
│  SECONDARY BUTTON                  │
│  "Need help in English?"           │
│                                    │
│  Style:                            │
│  • Smaller (280x42px)              │
│  • Subtle gray background          │
│  • Regular text                    │
│  • Below primary button            │
└────────────────────────────────────┘
                 │
                 ▼
      ┌────────────────────────────┐
      │  ENGLISH HELP MODAL        │
      │  ────────────────────────  │
      │  How to Play               │
      │                            │
      │  1. Next station shown     │
      │  2. Drag correct token     │
      │  3. Beat the train         │
      │                            │
      │  Note: Game is in Catalan  │
      │                            │
      │  [Start my first day in    │
      │   Catalan]                 │
      └────────────────────────────┘
                 │
                 ▼
      Complete Onboarding
      Activate First Day Mode
      Start Game
```

## Text Animation Pattern

```
Each narrative text follows this pattern:

Opacity
  1.0 ┤         ╭─────╮
      │        ╱       ╲
      │       ╱         ╲
  0.5 ┤      ╱           ╲
      │     ╱             ╲
      │    ╱               ╲
  0.0 ┼───╯                 ╰───
      └────────────────────────→ Time
      0  0.6  1.8  2.3      (seconds)
      
      Fade-in  Hold  Fade-out
      (0.6s)  (1.2s) (0.5s)
```

## Color Palette

```
Onboarding Overlay:
┌──────────────────────────────────────┐
│ Background: RGB(0, 0, 0) - Black     │
│ Text: RGB(242, 242, 242) - Off-white │
│ Primary Button: RGB(77, 230, 128)    │
│ Secondary Button: RGB(64, 71, 89)    │
└──────────────────────────────────────┘

English Help Modal:
┌──────────────────────────────────────┐
│ Background: RGB(31, 38, 56)          │
│ Border: RGB(77, 179, 230) - Blue     │
│ Text: RGB(230, 235, 242)             │
│ Button: RGB(77, 230, 128) - Green    │
└──────────────────────────────────────┘
```

## File Structure

```
Tetris-Metro/
├── core/
│   └── settings.py ........................ ✓ has_completed_onboarding
│
├── game_proxima_parada.py ................ ✓ Main implementation
│   ├── Renderer.show_onboarding_overlay()
│   ├── Renderer._show_english_help_modal()
│   └── ProximaParadaGame._show_onboarding()
│
├── test_onboarding.py .................... ✓ Integration test
├── onboarding_util.py .................... ✓ Flag management
├── ONBOARDING_IMPLEMENTATION.md .......... ✓ Full documentation
└── ONBOARDING_VISUAL_REFERENCE.md ........ ✓ This file
```

## Timing Diagram (Detailed)

```
Time (s) │ Event                           │ Duration │ Transition
─────────┼─────────────────────────────────┼──────────┼────────────
0.0      │ Overlay added, opacity=0        │          │
0.0-1.0  │ Fade in overlay → opacity=1     │ 1.0s     │ in_quad
1.0      │ Overlay fully visible (black)   │          │
         │                                  │          │
1.5      │ Text 1 fade-in starts           │          │
1.5-2.1  │ "Acabes d'arribar..." → 1.0     │ 0.6s     │ in_out_quad
2.1-2.7  │ Text 1 holds                    │ 0.6s     │
2.7-3.2  │ Text 1 fade-out → 0.0           │ 0.5s     │ in_out_quad
         │                                  │          │
3.4      │ Text 2 fade-in starts           │          │
3.4-4.0  │ "El metro serà..." → 1.0        │ 0.6s     │ in_out_quad
4.0-4.6  │ Text 2 holds                    │ 0.6s     │
4.6-5.1  │ Text 2 fade-out → 0.0           │ 0.5s     │ in_out_quad
         │                                  │          │
5.3      │ Text 3 fade-in starts           │          │
5.3-5.9  │ "Per moure't..." → 1.0          │ 0.6s     │ in_out_quad
5.9-6.5  │ Text 3 holds                    │ 0.6s     │
6.5-7.0  │ Text 3 fade-out → 0.0           │ 0.5s     │ in_out_quad
         │                                  │          │
7.2      │ Text 4 fade-in starts           │          │
7.2-8.0  │ "Avui és el teu..." → 1.0       │ 0.8s     │ in_out_quad
8.0+     │ Text 4 stays visible            │ ∞        │
         │                                  │          │
8.5      │ Buttons fade-in starts          │          │
8.5-9.3  │ Buttons → opacity=1             │ 0.8s     │ in_out_quad
9.3+     │ Interactive state               │ ∞        │ (user action)
```

## State Transitions

```
┌────────────────┐
│ Settings File  │
│ settings.json  │
└────────────────┘
        │
        ├─ has_completed_onboarding: false  (first launch)
        │
        │  [User completes onboarding]
        │
        └─ has_completed_onboarding: true   (persisted)


┌────────────────┐
│ Game State     │
└────────────────┘
        │
        ├─ first_day_mode: false            (before onboarding)
        │
        │  [Onboarding completed]
        │
        ├─ first_day_mode: true             (activated)
        ├─ first_day_progress: 0            (reset)
        └─ first_day_completed: false       (ready to start)
```

---

**Visual Reference Version**: 1.0
**Last Updated**: February 24, 2026
