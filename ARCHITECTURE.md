# Metro Tetris - Arquitectura Refactorizada

## 📁 Estructura del Proyecto

```
Tetris-Metro/
├── model/               # Lógica pura (sin Kivy)
│   ├── board.py         # Grid 10×20, validación de posiciones
│   ├── piece.py         # Tetrominos con datos de estación
│   ├── tetrominos.py    # Definiciones de 7 piezas
│   ├── rules.py         # Colisiones, rotación SRS, wall kicks
│   ├── scoring.py       # Puntuación, niveles, bonus
│   └── metro_content.py # Gestión de estaciones Metro BCN
│
├── ui/                  # Componentes Kivy
│   ├── board_view.py    # Render Canvas eficiente
│   ├── hud_view.py      # Labels de info (score, level, lines)
│   ├── overlays.py      # Pantallas pausa/game over
│   └── input_controller.py # Gestos táctiles + teclado
│
├── game/                # Orquestación
│   └── controller.py    # GameController (model + ui)
│
├── core/                # Infraestructura
│   ├── assets.py        # AssetManager (atlas/colores)
│   ├── logger.py        # Logging estructurado
│   └── performance.py   # Monitor FPS
│
├── data/
│   └── stations.json    # 20 estaciones Metro Barcelona
│
├── logs/                # Logs de juego (auto-creado)
├── main.py              # Entry point
└── buildozer.spec       # Configuración Android
```

## 🏗️ Arquitectura en Capas

### 1. **Model Layer** (Lógica Pura)
- ✅ **Cero dependencias de Kivy**
- Totalmente testeable con unit tests
- Separación clara de reglas del juego

**model/board.py**
- Grid 10×20 con validación de posiciones
- Lock de piezas y clear de líneas
- Métodos: `is_valid_position()`, `lock_piece()`, `clear_lines()`

**model/piece.py**
- Tetromino con 4 rotaciones
- Station data integrado (Metro BCN)
- Métodos: `rotate_clockwise()`, `get_cells()`, `clone()`

**model/rules.py**
- SRS (Super Rotation System) con wall kicks
- Cálculo de ghost piece
- Métodos: `try_rotate()`, `calculate_ghost_y()`

**model/scoring.py**
- Sistema de puntuación con multiplicadores
- Progresión de niveles (cada 10 líneas)
- Bonus × 1.5 si pieza coincide con línea objetivo
- Métodos: `calculate_score()`, `add_score()`, `get_fall_speed()`

**model/metro_content.py**
- Carga stations.json con fallback
- Selección por dificultad (A1/A2/B1)
- Weighted random por frecuencia (high/medium/low)

### 2. **UI Layer** (Componentes Kivy)

**ui/board_view.py** - Render Optimizado
- ✅ Canvas con instrucciones reutilizables
- ✅ Cache de estado para evitar redraws innecesarios
- ✅ Solo redibuja cuando cambia `board_grid`, `piece_cells`, o `ghost_cells`
- Soporte para texturas (AssetManager) con fallback a colores
- Métodos: `render()`, `_render_board()`, `_render_piece()`, `_render_ghost()`

**ui/hud_view.py**
- Labels creados una vez (no por frame)
- Update solo de texto cuando cambia estado
- Muestra: score, high score, level, lines (X/10), target line, station actual/next

**ui/overlays.py**
- `PauseOverlay`: pantalla semitransparente con botón "Continuar"
- `GameOverOverlay`: score final, badge "¡NUEVO RÉCORD!", botones retry/exit

**ui/input_controller.py**
- Detección de gestos: tap (rotate), swipe horizontal (move), swipe down (hard drop)
- Teclado: flechas/WASD, Space (drop), P (pause)
- Callbacks configurables

### 3. **Game Layer** (Orquestador)

**game/controller.py**
- Coordina model + ui
- GameState enum: RUNNING, PAUSED, GAME_OVER
- Gestiona gravedad, lock de piezas, scoring
- Persistencia con JsonStore (high score)
- Métodos: `move_left/right/down()`, `rotate()`, `hard_drop()`, `_lock_piece()`, `get_state_dict()`

### 4. **Core Layer** (Infraestructura)

**core/assets.py** - AssetManager
- Soporte para atlas Kivy (texturas desde PNG)
- Fallback a colores sólidos si no existe atlas
- 3 variantes: normal, highlight, shadow
- Ghost piece con alpha 0.3
- **PREPARADO PARA CANDY**: solo crear atlas con tiles candy

**core/logger.py**
- Logging estructurado a `logs/game.log`
- Niveles: DEBUG, INFO, WARNING, ERROR
- Formato: timestamp | level | message
- Método: `log_game_event(event_type, **data)`

**core/performance.py**
- FPS monitor con ventana de 5 segundos
- Solo activo en DEBUG_MODE
- Métodos: `frame_tick()`, `get_fps()`, `get_frame_time_ms()`

## 🚀 Optimizaciones de Rendimiento

### Render Eficiente (60 FPS)
1. **Canvas reutilizable**: instrucciones `Rectangle`, `Line`, `Color` se cachean
2. **State diffing**: solo redibuja cuando cambia `board_grid != cached_board`
3. **Grid estático**: líneas de grid dibujadas una sola vez en `_init_grid()`
4. **Precalcular posiciones**: `px = offset_x + x * cell_size` (sin recalcular cada frame)

### Limitación de Cálculos
- Ghost piece: solo recalcula si `current_piece` cambia
- HUD: solo actualiza text de labels (no recrea widgets)
- Feedback: timer automático (1.5s) para limpiar mensajes

### Gestión de Memoria
- `get_grid_copy()` solo cuando se renderiza (no cada frame)
- Instrucciones Canvas eliminadas antes de reemplazar (`canvas.remove()`)
- JsonStore lazy (solo guarda al batir high score)

## 🎨 Sistema de Assets (Preparado para Candy)

### Uso Actual (Fallback)
```python
assets = AssetManager()
color = assets.get_color(color_id)  # (r, g, b, a)
```

### Migración a Texturas Candy
1. Crear atlas Kivy:
```bash
# Crear directorio assets/
mkdir assets
# Añadir tiles: tile_1.png, tile_2.png, ..., tile_7.png (32×32)
# Generar atlas:
kivy-atlas assets/atlas 256 assets/*.png
```

2. AssetManager detecta automáticamente:
```python
# Si assets/atlas.atlas existe:
texture = assets.get_tile_texture(color_id)  # Texture
# Si no existe:
color = assets.get_color(color_id)  # Fallback
```

3. Modificar `ui/board_view.py` para usar texturas:
```python
# En _draw_cell():
texture = self.assets.get_tile_texture(color_id)
if texture:
    Rectangle(pos=(px, py), size=(cell_size, cell_size), texture=texture)
else:
    # Fallback actual
```

## 📊 Instrumentación

### Debug Mode
Activar en [main.py](main.py):
```python
DEBUG_MODE = True  # Muestra FPS en pantalla
```

### Logging
```python
logger.info("Evento del juego")
logger.log_game_event('GAME_OVER', score=1000, level=5)
logger.error("Error crítico", exc_info=True)
```

Logs guardados en: `logs/game.log`

### Performance Monitor
```python
perf = PerformanceMonitor()
perf.enable()  # Solo en DEBUG_MODE
perf.frame_tick()  # Cada frame
fps = perf.get_fps()  # Promedio últimos 5s
```

## 🎮 Flujo del Juego

```
main.py (TetrisApp)
    ↓
TetrisGame (FloatLayout)
    ├── AssetManager (texturas/colores)
    ├── GameLogger (logs estructurados)
    ├── PerformanceMonitor (FPS en debug)
    │
    ├── GameController (orquestador)
    │   ├── Board (grid 10×20)
    │   ├── Rules (SRS rotation)
    │   ├── ScoringSystem (puntos/niveles)
    │   └── MetroContentManager (stations.json)
    │
    ├── BoardView (Canvas render)
    ├── HUDView (labels info)
    ├── PauseOverlay
    ├── GameOverOverlay
    └── InputController (gestos/teclado)
```

### Game Loop (60 FPS)
```python
update(dt):
    1. perf.frame_tick()
    2. controller.update(dt)  # Fade feedback timer
    3. Check game state (RUNNING/PAUSED/GAME_OVER)
    4. Gravity timer += dt
    5. If timer >= fall_speed: move_down()
    6. render()  # Solo redibuja cambios
    7. hud.update(state_dict)
```

## 🎯 Puntos de Extensión

### 1. **Partículas** (post-refactor)
**Dónde añadir**: `ui/particles.py`
```python
class ParticleSystem:
    def emit(self, pos, count=10):
        # Crear partículas al limpiar líneas
        pass

# En game/controller.py _lock_piece():
if lines_cleared > 0:
    particles.emit(line_y_positions)
```

### 2. **Animaciones** (post-refactor)
**Dónde añadir**: `ui/animations.py`
```python
from kivy.animation import Animation

class GameAnimations:
    @staticmethod
    def line_clear(board_view, lines_indices):
        # Flash líneas antes de borrar
        anim = Animation(opacity=0, duration=0.3)
        anim.start(target)
```

### 3. **Power-ups** (extensión model)
**Dónde añadir**: `model/powerups.py`
```python
class PowerUp:
    def __init__(self, type='clear_line'):
        self.type = type
    
    def apply(self, board, controller):
        if self.type == 'clear_line':
            board.clear_lines(force=True)
```

### 4. **Modos de Juego** (extensión controller)
**Dónde añadir**: `game/modes.py`
```python
class MarathonMode:
    def __init__(self, controller):
        self.controller = controller
        self.target_lines = 150
```

### 5. **Sonido/Música** (core layer)
**Dónde añadir**: `core/audio.py`
```python
from kivy.core.audio import SoundLoader

class AudioManager:
    def __init__(self):
        self.sfx = {
            'move': SoundLoader.load('assets/move.wav'),
            'rotate': SoundLoader.load('assets/rotate.wav'),
            'lock': SoundLoader.load('assets/lock.wav'),
            'clear': SoundLoader.load('assets/clear.wav')
        }
```

## 📝 Cambios Principales vs Versión Anterior

### ✅ Mejoras Arquitecturales
1. **Separación de capas**: model (0 Kivy) / ui (widgets) / game (orquestador)
2. **Render optimizado**: Canvas con cache, solo redibuja cambios
3. **Asset system**: preparado para atlas de texturas candy
4. **Instrumentación**: logger + FPS monitor en debug

### ✅ Código Eliminado
- `game/board.py`, `game/piece.py`, `game/tetrominos.py` → movidos a `model/`
- `game/content_manager.py` → refactorizado como `model/metro_content.py`
- `game/persistence.py` → integrado en `game/controller.py` (JsonStore directo)
- `main_fixed.py` → reemplazado por `main.py` limpio

### ✅ Nuevos Módulos
- `model/rules.py`: SRS rotation con wall kicks
- `model/scoring.py`: sistema de puntuación extraído
- `ui/board_view.py`: render Canvas eficiente
- `ui/hud_view.py`: HUD como widget separado
- `ui/overlays.py`: pause/game over como widgets
- `ui/input_controller.py`: gestos + teclado
- `core/assets.py`: gestión de texturas/colores
- `core/logger.py`: logging estructurado
- `core/performance.py`: FPS monitor

### ✅ Compatibilidad Android
- Mantiene `buildozer.spec` original
- Portrait mode: 360×640
- Touch gestures optimizados
- JsonStore para persistencia offline

## 🔧 Ejecución

### Desarrollo (PC)
```bash
python main.py
```

### Debug Mode
```python
# En main.py:
DEBUG_MODE = True
```
Muestra FPS en esquina inferior izquierda.

### Build Android
```bash
buildozer android debug
buildozer android deploy run
```

## 📦 Dependencias

```
kivy>=2.3.0
```

## 🎓 Créditos

Metro Tetris para proyecto educativo "La Rosa de Barcelona"
- 20 estaciones Metro BCN (5 líneas: L1-L5)
- Dificultades A1/A2/B1 por nivel
- Bonus × 1.5 al hacer match con línea objetivo

---

**Versión**: 2.0 (Refactorizada)  
**Fecha**: 2026-02-08  
**Licencia**: Proyecto Educativo
