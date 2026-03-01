# LineMapView Widget

## Descripción

`LineMapView` es un widget de Kivy que muestra una representación esquemática vertical de una línea de metro, con estaciones representadas como círculos a lo largo de una línea vertical.

## Características

✅ **Diseño vertical** - Optimizado para pantallas portrait  
✅ **Animación de pulso** - El slot activo pulsa suavemente (escala + alpha)  
✅ **Interacción táctil** - Detecta toques en los slots  
✅ **Sin assets** - Todo renderizado con Canvas (Line + Ellipse)  
✅ **Configurable** - Soporta 10-16+ estaciones con colores personalizados  

## API

### Métodos Principales

#### `set_line(line_id: str, line_color_hex: str, station_names: List[str])`
Configura la línea de metro a mostrar.

```python
line_map.set_line(
    line_id="L3",
    line_color_hex="#00923F",
    station_names=["Zona Universitària", "Palau Reial", ...]
)
```

#### `set_next_index(index: int)`
Establece qué estación es la activa (con animación de pulso).

```python
line_map.set_next_index(0)  # Primera estación activa
```

#### `get_slot_at(x: float, y: float) -> Optional[int]`
Obtiene el índice del slot en una posición dada.

```python
slot_index = line_map.get_slot_at(touch.x, touch.y)
if slot_index is not None:
    print(f"Tocaste la estación {slot_index}")
```

## Ejemplo de Uso

### Ejemplo Básico

```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from line_map_view import LineMapView

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        
        # Crear el widget
        line_map = LineMapView()
        
        # Configurar L3 con 12 estaciones
        line_map.set_line(
            line_id="L3",
            line_color_hex="#00923F",
            station_names=[
                "Zona Universitària",
                "Palau Reial",
                "Maria Cristina",
                "Les Corts",
                "Plaça del Centre",
                "Sants Estació",
                "Tarragona",
                "Espanya",
                "Poble Sec",
                "Paral·lel",
                "Drassanes",
                "Liceu"
            ]
        )
        
        # Activar la primer estación
        line_map.set_next_index(0)
        
        layout.add_widget(line_map)
        return layout

if __name__ == '__main__':
    MyApp().run()
```

### Integración con Cargador de Datos

```python
from data.metro_loader import load_metro_network
from pathlib import Path

# Cargar datos reales
data_path = Path("data/barcelona_metro_lines_stations.json")
network = load_metro_network(str(data_path))
l3 = network.get_line("L3")

# Usar primeras 12 estaciones
line_map.set_line(
    line_id=l3.id,
    line_color_hex=l3.color,
    station_names=l3.stations[:12]
)
```

## Propiedades Configurables

```python
# Radio de los círculos
line_map.slot_radius = 15

# Espaciado entre estaciones
line_map.slot_spacing = 50

# Grosor de la línea
line_map.line_width = 4

# Color de slots inactivos
line_map.inactive_color = (0.7, 0.7, 0.7, 0.5)

# Color del slot activo
line_map.active_color = (1, 0.3, 0.3, 1)
```

## Eventos

El widget detecta toques en los slots:

```python
def on_touch_down(self, touch):
    if self.line_map.collide_point(*touch.pos):
        slot_index = self.line_map.get_slot_at(touch.x, touch.y)
        if slot_index is not None:
            print(f"Tocaste: {self.line_map.station_names[slot_index]}")
```

## Demo

Ejecuta el ejemplo de prueba:

```bash
python test_line_map.py
```

La demo muestra:
- Línea L3 con 12 estaciones
- Botones para navegar entre estaciones
- Animación de pulso en la estación activa
- Detección de toques en los slots

## Estructura Visual

```
      ○  ← Slot inactivo (círculo vacío)
      ○
      ⦿  ← Slot activo (pulso animado)
      ○
      ○
      ○
```

La línea vertical conecta todos los slots, y el slot activo (indicado por `next_index`) tiene:
- Animación de pulso (escala 1.0 → 1.3)
- Cambio de opacidad (alpha 1.0 → 0.6)
- Halo resplandeciente
- Punto central blanco

## Integración en el Juego

Para integrar en Tetris Metro:

```python
# En el controller o vista principal
from line_map_view import LineMapView

class TetrisGame(Widget):
    def __init__(self):
        # ... código existente ...
        
        # Añadir mapa de línea
        self.line_map = LineMapView(
            size_hint=(None, None),
            size=(200, 600),
            pos=(10, 100)
        )
        self.add_widget(self.line_map)
        
        # Sincronizar con OrderTrackManager
        current_line = self.controller.order_track
        self.line_map.set_line(
            line_id=current_line.target_line_id,
            line_color_hex="#00923F",  # Color de la línea
            station_names=current_line.ordered_stations
        )
        
        # Actualizar índice cuando cambia
        self.line_map.set_next_index(current_line.next_index)
```

## Notas Técnicas

- **Renderizado**: Usa `kivy.graphics` (Canvas) exclusivamente
- **Animación**: `kivy.animation.Animation` con `t='in_out_sine'`
- **Layout**: Centrado vertical, escalable
- **Performance**: Eficiente, solo redibuja cuando cambia el estado
- **Touch detection**: Radio de tolerancia de 1.5x el tamaño del slot

## Archivos

- `line_map_view.py` - Widget principal
- `test_line_map.py` - Ejemplo de demostración
- `LINE_MAP_VIEW.md` - Esta documentación
