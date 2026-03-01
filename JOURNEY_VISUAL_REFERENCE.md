# Journey Overlay - Visual Reference

## Layout Preview

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                   El teu viatge                          ║
║              Progressió i assoliments                    ║
║                                                           ║
║   ┌──────────┐    ┌──────────┐    ┌──────────┐         ║
║   │  12,500  │    │    2     │    │    47    │         ║
║   │  Punts   │    │  Línies  │    │Estacions │         ║
║   │  totals  │    │  fetes   │    │          │         ║
║   └──────────┘    └──────────┘    └──────────┘         ║
║      (Gold)         (Green)        (Blue)                ║
║                                                           ║
║          🏆 Medalles aconseguides                        ║
║                                                           ║
║     ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                 ║
║     │ 🎨  │  │ 🏛️  │  │  ⚽  │  │ 🌊  │                 ║
║     └─────┘  └─────┘  └─────┘  └─────┘                 ║
║                                                           ║
║     ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                 ║
║     │ 🏰  │  │ 🎭  │  │ 🖼️  │  │ 🏖️  │                 ║
║     └─────┘  └─────┘  └─────┘  └─────┘                 ║
║                                                           ║
║     ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                 ║
║     │ ⛰️  │  │ 🚶  │  │ 🛍️  │  │ 🥘  │                 ║
║     └─────┘  └─────┘  └─────┘  └─────┘                 ║
║                                                           ║
║              12 de 24 medalles                           ║
║                                                           ║
║       🗺️ El teu primer dia a Barcelona                   ║
║                ✓ Completat!                              ║
║                                                           ║
║            ┌──────────────────┐                          ║
║            │ Tornar al mapa   │                          ║
║            └──────────────────┘                          ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

## Color Scheme

### Panel
- **Outer border**: Green accent (#30E650, 60% opacity)
- **Background**: Dark blue-gray (#191E28)
- **Inner panel**: Darker blue-gray (#141A23)

### Text Colors
- **Title "El teu viatge"**: Bright green (#30E650)
- **Subtitle**: Light gray (#99B3CC)
- **Total score number**: Gold (#FFF266)
- **Lines completed**: Green (#30E650)
- **Stations count**: Light blue (#66B3FF)
- **Section headers**: Near-white (#E6E9F2)
- **Status text**: Variable (green for complete, gray for in-progress)

### Elements
- **Badge backgrounds**: Dark gray (#262D38, 80% opacity)
- **Button**: Blue (#3F99D9)
- **Button text**: White

## Dimensions

- **Panel**: 560px × 540px
- **Title**: 32sp, bold
- **Stats numbers**: 36sp, bold
- **Stats captions**: 13sp
- **Section headers**: 18sp (badges), 16sp (First Day)
- **Badge grid**: 60px per badge with 20px spacing
- **Button**: 50% width, 44px height

## States

### Empty State
```
┌─────────────────────────────────────┐
│        El teu viatge                │
│   Progressió i assoliments          │
│                                     │
│   [0]      [0]        [0]           │
│  Punts   Línies   Estacions         │
│                                     │
│  🏆 Medalles aconseguides           │
│                                     │
│  Encara no has aconseguit           │
│      cap medalla                    │
│                                     │
│  🗺️ El teu primer dia a Barcelona   │
│       En progrés...                 │
│                                     │
│    [Tornar al mapa]                 │
└─────────────────────────────────────┘
```

### Partial Progress
```
┌─────────────────────────────────────┐
│        El teu viatge                │
│   Progressió i assoliments          │
│                                     │
│   [5,420]   [1]      [18]           │
│   Punts   Línies  Estacions         │
│                                     │
│  🏆 Medalles aconseguides           │
│                                     │
│     [🎨]  [🏛️]  [⚽]  [ ]            │
│     [ ]   [ ]   [ ]   [ ]            │
│                                     │
│         3 de 24 medalles            │
│                                     │
│  🗺️ El teu primer dia a Barcelona   │
│       En progrés...                 │
│                                     │
│    [Tornar al mapa]                 │
└─────────────────────────────────────┘
```

### Complete Progress
```
┌─────────────────────────────────────┐
│        El teu viatge                │
│   Progressió i assoliments          │
│                                     │
│  [52,830]  [12]     [156]           │
│   Punts   Línies  Estacions         │
│                                     │
│  🏆 Medalles aconseguides           │
│                                     │
│  [🎨][🏛️][⚽][🌊][🏰][🎭][🖼️][🏖️]   │
│  [⛰️][🚶][🛍️][🥘][🏗️][🗿][🌳][👁️]   │
│                                     │
│        24 de 24 medalles            │
│                                     │
│  🗺️ El teu primer dia a Barcelona   │
│          ✓ Completat!               │
│                                     │
│    [Tornar al mapa]                 │
└─────────────────────────────────────┘
```

## Animation

### On Open
1. **Overlay fade-in**: 0s to 88% opacity
2. **Panel slide-up**: Slight upward motion (8px)
3. **Duration**: ~200ms with ease-out

### On Close
1. **Panel fade-out**: 88% to 0% opacity  
2. **Duration**: ~150ms with ease-in

### Button Press
1. **Opacity drop**: 100% → 85% (80ms)
2. **Release bounce**: 85% → 100% (120ms)
3. **Click sound**: UI_CLICK event

## Responsive Behavior

- **Centered**: Always centered on screen
- **Fixed size**: 560×540px (doesn't scale)
- **Overlay**: Full-screen semi-transparent background
- **Click outside**: Dismisses overlay
- **Button click**: Dismisses overlay

## Badge Grid Layout

- **Columns**: 4 badges per row
- **Rows**: Up to 3 rows (12 badges max shown)
- **Badge size**: 60×60px
- **Horizontal spacing**: 20px between badges
- **Vertical spacing**: 20px between rows
- **Grid centering**: Centered within badge container
- **Overflow**: Shows first 12 badges if more earned

## Typography Hierarchy

```
1. Title (32sp, bold, green)
   └─ "El teu viatge"

2. Subtitle (15sp, italic, gray)
   └─ "Progressió i assoliments"

3. Stat Numbers (36sp, bold, colored)
   ├─ Total score (gold)
   ├─ Lines completed (green)
   └─ Total stations (blue)

4. Stat Captions (13sp, gray)
   ├─ "Punts totals"
   ├─ "Línies fetes"  
   └─ "Estacions"

5. Section Headers (18sp/16sp, bold, white)
   ├─ "🏆 Medalles aconseguides" (18sp)
   └─ "🗺️ El teu primer dia a Barcelona" (16sp)

6. Status/Count (13sp-14sp, gray/colored)
   ├─ "X de Y medalles"
   ├─ "✓ Completat!" (green)
   └─ "En progrés..." (gray)

7. Button (16sp, bold, white)
   └─ "Tornar al mapa"
```

## Spacing Guide

```
Top margin:     4% (from panel top)
Title:          96% (y position)
Subtitle:       88%
Stats row:      75%
Badge header:   58%
Badge grid:     53%-23%
Badge count:    22%
First Day:      18%
Button:         3% (from bottom)
```

## Visual Hierarchy

**Priority 1** (Largest/Brightest):
- Total score number (36sp, gold)

**Priority 2** (Large/Colored):
- Title "El teu viatge" (32sp, green)
- Stat numbers (36sp, colored)

**Priority 3** (Medium/White):
- Section headers (18sp, 16sp)
- Button (16sp)

**Priority 4** (Small/Gray):
- Subtitle (15sp)
- Captions (13sp)
- Counts (13sp)

**Priority 5** (Icons):
- Badge emojis (32sp)
- Section icons (included in headers)

---

**Visual Style**: Minimal, elegant, game-consistent  
**Design Language**: Metro-inspired, urban dark theme  
**Accent Color**: Green (#30E650) matching game brand
