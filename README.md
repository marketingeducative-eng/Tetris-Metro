# Metro Tetris - Mobile Tetris Game

Implementación minimalista de Tetris en Python/Kivy para Android con controles táctiles optimizados.

## Estructura del proyecto

```
Tetris-Metro/
├── main.py                 # Aplicación principal Kivy
├── game/
│   ├── __init__.py
│   ├── board.py           # Clase Board (grid, colisiones, line clear)
│   ├── piece.py           # Clase Piece (tetrominos con rotación)
│   ├── controller.py      # GameController (lógica, scoring)
│   └── tetrominos.py      # Definiciones de piezas
├── buildozer.spec         # Configuración para build Android
└── README.md
```

## Características implementadas

### Core Game
- **Grid**: 10×20 células (estándar Tetris)
- **Piezas**: 7 tetrominos clásicos (I, J, L, O, S, T, Z)
- **Rotación**: Sistema SRS con wall kicks básicos
- **Colisiones**: Detección precisa de límites y piezas bloqueadas
- **Line Clear**: Eliminación automática de líneas completas
- **Scoring**: Puntuación por líneas (100/300/500/800) + hard drop bonus
- **Niveles**: Incremento cada 10 líneas con aumento de velocidad

### Controles

#### Teclado (desktop testing)
- **←/→ o A/D**: Mover izquierda/derecha
- **↓ o S**: Soft drop (caída rápida)
- **↑ o W**: Rotar
- **Espacio**: Hard drop (caída instantánea)
- **R**: Reiniciar partida

#### Táctil (móvil)
Pantalla dividida en 3 zonas verticales:
- **Inferior (33%)**: Controles de movimiento
  - Izquierda: mover left
  - Centro: soft drop
  - Derecha: mover right
- **Medio (33-66%)**: Rotar pieza
- **Superior (66%+)**: Hard drop

### Visualización
- Grid con líneas visibles
- Colores diferenciados por pieza
- **Ghost piece**: Vista previa transparente de dónde caerá la pieza
- Highlights en cada celda bloqueada
- HUD con score y nivel

## Ejecutar en desktop (desarrollo)

```bash
python main.py
```

## Build para Android

```bash
# Primera vez: instalar buildozer
pip install buildozer

# Build APK debug
buildozer android debug

# Build y deploy en device conectado
buildozer android debug deploy run

# Ver logs
buildozer android logcat
```

## Requisitos

- Python 3.8+
- Kivy 2.0+
- Para Android: Buildozer, Android SDK/NDK

## Clases principales

### Board
- `is_valid_position(piece)`: Validación de colisiones
- `lock_piece(piece)`: Fijar pieza al grid
- `clear_lines()`: Detectar y eliminar líneas completas
- `is_game_over()`: Check fila superior

### Piece
- Representa un tetromino con posición (x,y) y rotación
- `rotate_clockwise()`: Rotar 90°
- `get_cells()`: Celdas ocupadas
- `clone()`: Copia para ghost piece

### GameController
- Estado del juego completo
- `move_left/right/down()`: Movimientos con validación
- `rotate()`: Rotación con wall kicks
- `hard_drop()`: Caída instantánea
- `get_ghost_position()`: Calcular posición de aterrizaje
- `reset()`: Reiniciar partida

## Próximas mejoras

- [ ] Música y efectos de sonido
- [ ] Sistema de hold piece
- [ ] Preview de siguiente pieza más visible
- [ ] Animaciones de line clear
- [ ] Menú principal
- [ ] Guardar high score
- [ ] Vibración en mobile
- [ ] Partículas en combos

## Licencia

MIT
