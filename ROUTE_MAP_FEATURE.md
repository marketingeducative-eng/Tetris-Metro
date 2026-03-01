"""
Game Over Route Map - Feature Summary

OVERVIEW
========
At game over, players see a visual representation of their journey along the L3 metro line,
highlighting which stations they successfully reached versus those they didn't.

IMPLEMENTATION
==============

1. TRACKING (GameState)
   - Added: `visited_stations` set to track station indices
   - Initialized with station 0 (starting position)
   - Updated in `handle_correct_answer()` when player succeeds
   - Persists throughout game session

2. GAME OVER DISPLAY (Renderer)
   - Panel size: 500x500px (increased from 400x300)
   - Layout: Stats on top, route map below
   - Shows: "Estacions: X/26" in stats section

3. ROUTE VISUALIZATION
   - Horizontal line representing L3
   - 26 nodes evenly spaced
   - Green (bright): Visited stations (radius 8px)
   - Gray (dim): Unvisited stations (radius 5px)
   - Terminal labels: Start and end station names

VISUAL DESIGN
=============

Stats Section (top 200px):
  ┌─────────────────────────────────────┐
  │     FI DEL TRAJECTE                 │
  │                                     │
  │  Puntuació: 1800                   │
  │  Rècord: 2500                      │
  │  Millor ratxa: 8                   │
  │  Estacions: 13/26                  │
  │                                     │
  │  RUTA COMPLETADA:                  │
  └─────────────────────────────────────┘

Route Map (bottom 250px):
  ┌─────────────────────────────────────┐
  │ Zona Universitària                  │
  │  ●●●●●●●●●●●●●○○○○○○○○○○○○○ Trinitat Nova │
  │   └─visited─┘  └─not visited─┘    │
  │                                     │
  └─────────────────────────────────────┘

● = Green node (visited, 8px radius)
○ = Gray node (not visited, 5px radius)

EXAMPLE SCENARIOS
=================

1. Early Game Over (5 stations):
   - Shows 5/26 in stats
   - 5 green nodes at start of line
   - Most of line remains gray
   - Demonstrates limited progress

2. Mid-Game (13 stations):
   - Shows 13/26 in stats
   - Half the line is green
   - Clear visual of 50% completion
   - Motivates to reach further next time

3. Late Game (20 stations):
   - Shows 20/26 in stats
   - Most nodes green, few gray at end
   - Player almost reached terminal
   - Strong sense of achievement

4. Full Completion (26 stations):
   - Shows 26/26 in stats
   - All nodes bright green
   - Perfect run visualization
   - Ultimate achievement display

TECHNICAL DETAILS
=================

Station Tracking:
  - Set data structure for O(1) lookup
  - Station indices (0-25) not names
  - Persists across game rounds
  - Not saved to disk (session only)

Route Drawing:
  - Uses Kivy canvas instructions
  - Responsive to panel size changes
  - CoreLabel for terminal text
  - Ellipse primitives for nodes

Node Positioning:
  - Spacing = (width - 20) / (num_stations - 1)
  - X position = start + (index * spacing)
  - Y position = center of route line
  - Evenly distributed across line

Colors:
  - Line: (0.3, 0.3, 0.35) dark gray
  - Visited: (0.3, 0.9, 0.4) bright green
  - Unvisited: (0.25, 0.25, 0.3) dim gray
  - Labels: (0.8, 0.8, 0.85) light gray

BENEFITS
========

1. Visual Achievement
   - Clear representation of progress
   - Satisfying to see green nodes
   - Motivates "beat my last run"

2. Educational Context
   - Shows L3 as a continuous route
   - Reinforces sequential station order
   - Geographic awareness of line length

3. Goal Clarity
   - Visualizes how far to terminal
   - Makes "reaching Trinitat Nova" concrete
   - Provides clear success metric

4. Replay Value
   - Compare different game attempts
   - See improvement over time
   - Challenge: reach further each game

TESTING
=======

Run visual test:
  python test_route_map_visual.py

Run unit tests:
  python test_route_map.py

Play actual game:
  python game_proxima_parada.py
  (Make mistakes to trigger game over)

FUTURE ENHANCEMENTS
===================

Potential additions:
  - Show exact station names on hover
  - Highlight longest continuous segment
  - Display total distance traveled
  - Compare to previous best run
  - Animate the route drawing
  - Color-code by line section
  - Show time spent at each station
