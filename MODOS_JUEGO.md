# Metro Tetris - Modos de Juego

## Ejecutar el juego

```bash
python main_order_track.py
```

## Modo A: ORDER TRACK (Principal)

El modo principal del juego donde debes colocar estaciones en el orden correcto de una línea de metro.

### Mecánica

1. **Línea Objetivo**: El juego selecciona una línea de metro (L1, L2, L3, L4 o L5)
2. **Orden Secuencial**: Debes colocar las piezas con estaciones en el orden exacto de esa línea
3. **Pista (Rail)**: Las columnas centrales (4-5) son la "pista" donde se validan las estaciones
4. **Validación**: Cuando una pieza se bloquea tocando la pista:
   - ✅ **Correcta**: Si la estación coincide con la próxima esperada
     - Avanza al siguiente índice
     - Bonus de puntos: 500 + (racha × 100)
     - Feedback: "Correcte!"
     - Se desbloquea la estación en el álbum
   - ❌ **Incorrecta**: Si no es la estación esperada
     - No avanza (sin penalización dura)
     - Feedback: "Ara toca: [nombre_estación]"
     - Rompe la racha actual

### HUD (Información en Pantalla)

**Panel Central Superior:**
- Nombre de la línea objetivo (ej: "Línia 1")
- Próxima estación esperada (nombre grande)
- Progreso actual (ej: "12/27")

**Panel Izquierdo:**
- Puntuación actual
- Récord
- Nivel
- Racha actual

**Mini-mapa Derecho:**
- Lista de 10 próximas estaciones
- ✓ Marca verde = Estación completada
- → Flecha amarilla = Próxima estación
- Estaciones pendientes en gris

### Controles

**Teclado:**
- ← → : Mover pieza
- ↑ : Rotar pieza
- ↓ : Caída rápida
- Barra espaciadora: Caída instantánea
- P: Pausa

**Táctil (móvil):**
- Toque corto: Rotar
- Deslizar izquierda/derecha: Mover
- Deslizar abajo: Caída instantánea

## Modo B: MISSIÓ DE DIRECCIÓ (Mini-reto)

Cada 5 aciertos consecutivos en ORDER TRACK se dispara un mini-reto de dirección.

### Mecánica

1. **Trigger**: Se activa automáticamente cada 5 estaciones correctas
2. **Duración**: 3-5 segundos de pausa en el juego
3. **Pregunta**: Se muestra un texto en catalán:
   - "Vull anar a [destino] des de [origen]. Quina direcció?"
4. **Opciones**: Dos botones (A/B) con terminales de la línea:
   - Una opción correcta (terminal hacia el destino)
   - Una opción incorrecta (terminal opuesto)
5. **Respuesta**:
   - ✅ Correcta: +300 puntos bonus, feedback "Direcció correcta!"
   - ❌ Incorrecta: Feedback "Direcció: [correcta]" (sin penalización fuerte)

### Interfaz

El mini-reto aparece como overlay translúcido con:
- Panel central con título "MISSIÓ DE DIRECCIÓ"
- Texto de la pregunta en catalán
- Dos botones grandes (A y B) para seleccionar

## Álbum de Progreso

El juego guarda tu progreso offline en `data/album_data.json`:

### Datos Guardados

- **Estaciones desbloqueadas por línea**: Registro de todas las estaciones completadas
- **Estadísticas por estación**:
  - Contador de aciertos
  - Contador de fallos
- **Récord de puntuación**

### Notificación de Desbloqueo

Cuando desbloqueas una estación por primera vez:
- Overlay verde de 2 segundos
- Título: "ESTACIÓ DESBLOQUEJADA!"
- Nombre de la estación
- Líneas asociadas

## Arquitectura Técnica

### Nuevas Clases

1. **AlbumStore** (`game/album_store.py`)
   - Gestiona persistencia con JsonStore
   - Guarda/carga estaciones desbloqueadas
   - Estadísticas de aciertos/fallos
   - High score

2. **OrderTrackManager** (`game/order_track.py`)
   - Gestiona el modo ORDER TRACK
   - Carga listas ordenadas de estaciones desde JSON
   - Valida piezas en la pista
   - Controla progreso y racha

3. **DirectionMission** (`game/direction_mission.py`)
   - Genera misiones de dirección
   - Verifica respuestas
   - Controla cooldowns y triggers

4. **Overlays** (`ui/overlays.py`)
   - DirectionMissionOverlay: UI para mini-reto
   - StationUnlockOverlay: Notificación de desbloqueo

### GameController Actualizado

- Enum `GameMode` para alternar entre ORDER_TRACK y DIRECTION_MISSION
- Integración de AlbumStore, OrderTrackManager y DirectionMission
- Método `submit_direction_answer()` para responder misiones
- `get_state_dict()` extendido con datos de progreso

### HUDView Actualizado

- Panel central para info de ORDER TRACK
- Mini-mapa lateral con lista de estaciones
- Indicadores visuales (✓, →)
- Actualización dinámica de progreso

## Configuración

### Personalizar Pista (Rail)

En `OrderTrackManager`:
```python
self.rail_columns = [4, 5]  # Columnas que cuentan como pista
```

### Ajustar Trigger de Misión

En `DirectionMission`:
```python
self.trigger_interval = 5  # Cada N aciertos
```

### Duración de Notificaciones

En `StationUnlockOverlay.show()`:
```python
Clock.schedule_once(lambda dt: self.hide(), 2.0)  # 2 segundos
```

## Datos JSON

### stations.json

Estructura necesaria:
```json
{
  "metro_lines": {
    "L1": {
      "name": "Línia 1",
      "color": "#E2001A",
      "stations": ["Fondo", "Santa Eulàlia", ...]
    }
  },
  "stations_pool": [
    {
      "id": "st_001",
      "name": "Catalunya",
      "name_short": "Catalunya",
      "lines": ["L1", "L3"],
      "difficulty": "A1",
      "frequency": "high"
    }
  ]
}
```

## Rendimiento

- **Sin widgets por frame**: Todo se dibuja con Canvas directo
- **Overlays simples**: FloatLayout con Canvas
- **Labels pre-creados**: Se reutilizan en mini-mapa
- **Actualización selectiva**: Solo se redibuja cuando cambia estado

## Próximas Mejoras Sugeridas

1. **Frases "say_ca"**: Añadir textos de estación en `station_info.json`
2. **Animaciones**: Transiciones suaves en mini-mapa
3. **Sonidos**: Feedback audio para aciertos/fallos
4. **Estadísticas detalladas**: Pantalla de álbum completo
5. **Más líneas**: Añadir L6, L7, etc.
6. **Logros**: Sistema de achievements
7. **Modo libre**: Tetris clásico sin validación
