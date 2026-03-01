# Integración TTS en Tetris Metro

## Descripción

Se ha implementado un servicio de Text-to-Speech (TTS) en catalán para anunciar estaciones del metro durante el juego.

## Archivos Creados

### 1. `core/tts.py`
Servicio principal de TTS con soporte para:
- Android (usando `jnius` y Android TTS API)
- Desktop (modo mock para desarrollo)
- Configuración en catalán (`Locale("ca", "ES")`)

### 2. `test_tts.py`
Aplicación de prueba con interfaz Kivy para probar el TTS.

## Uso Básico

### Importación

```python
from core.tts import get_tts, speak, announce_station, announce_line
```

### Ejemplos de Uso

#### 1. Anunciar una estación
```python
from core.tts import announce_station

# Anunciar estación (interrumpe anuncio anterior)
announce_station("Liceu", interrupt=True)

# Añadir a cola sin interrumpir
announce_station("Catalunya", interrupt=False)
```

#### 2. Anunciar una línea
```python
from core.tts import announce_line

announce_line("Línia 3")
```

#### 3. Texto personalizado
```python
from core.tts import speak

speak("Benvingut al metro de Barcelona")
speak("Pròxima estació: Diagonal")
```

#### 4. Uso avanzado con instancia
```python
from core.tts import get_tts

tts = get_tts()

# Configurar velocidad (1.0 = normal, 0.5 = lento, 2.0 = rápido)
tts.set_speech_rate(1.2)

# Configurar tono (1.0 = normal)
tts.set_pitch(1.0)

# Anunciar estación + línea
tts.announce_sequence("Liceu", "Línia 3")

# Detener anuncio actual
tts.stop()

# Cerrar servicio
tts.shutdown()
```

## Integración en el Juego

### Ejemplo: Anunciar cuando se coloca una pieza

```python
# En game/controller.py o main_fixed.py

from core.tts import announce_station

class GameController:
    def lock_piece(self):
        """Lock piece to board"""
        # ... código existente ...
        
        # Anunciar estación cuando se bloquea
        if self.current_piece and self.current_piece.station_data:
            station_name = self.current_piece.station_data.get('name', '')
            if station_name:
                announce_station(station_name, interrupt=False)
        
        # ... resto del código ...
```

### Ejemplo: Anunciar en Order Track Mode

```python
# En game/order_track.py

from core.tts import get_tts

class OrderTrackManager:
    def __init__(self, ...):
        # ... código existente ...
        self.tts = get_tts()
    
    def check_piece(self, piece, board_x, board_y):
        """Check if placed piece is correct"""
        # ... código existente ...
        
        if is_correct:
            # Anunciar estación correcta
            self.tts.announce_station(station_name, interrupt=False)
        else:
            # Anunciar error (opcional)
            self.tts.speak("Estació incorrecta", interrupt=True)
```

### Ejemplo: Anunciar nueva línea

```python
# En game/order_track.py

def start_new_line(self, line_id=None):
    """Start tracking a new metro line"""
    # ... código existente ...
    
    if line_id:
        line_info = self.metro_lines.get(line_id)
        if line_info:
            # Anunciar nueva línea
            from core.tts import announce_line
            announce_line(f"Línia {line_id}")
```

## Configuración Android

### buildozer.spec

Asegúrate de tener estos permisos en `buildozer.spec`:

```ini
# Permisos
android.permissions = INTERNET

# No se necesitan permisos especiales para TTS básico
# El servicio TTS es parte del sistema Android
```

### Dependencias

El servicio usa `pyjnius` que viene incluido con Kivy en Android.

No se necesitan dependencias adicionales.

## Testing

### En Desktop

```bash
# El servicio funcionará en modo mock (solo logs)
python test_tts.py
```

### En Android

1. Compilar APK con buildozer
2. Instalar en dispositivo
3. Verificar que el dispositivo tenga:
   - Motor TTS instalado (Google TTS recomendado)
   - Idioma catalán descargado en el motor TTS

Para descargar catalán en Android:
- Ajustes → Sistema → Idioma → Text-to-speech
- Descargar paquete de voz catalán

## Características

- ✅ Soporte Android nativo
- ✅ Configuración en catalán (ca_ES)
- ✅ Control de interrupciones (QUEUE_FLUSH / QUEUE_ADD)
- ✅ Control de velocidad y tono
- ✅ Modo mock para desarrollo desktop
- ✅ Patrón singleton para gestión eficiente
- ✅ Integración simple con funciones de conveniencia
- ✅ Logging completo para debugging

## API Reference

### Funciones de Conveniencia

```python
speak(text: str, interrupt: bool = True) -> bool
announce_station(station_name: str, interrupt: bool = True)
announce_line(line_name: str, interrupt: bool = True)
get_tts() -> TTSService
shutdown_tts()
```

### Clase TTSService

```python
class TTSService:
    def __init__(self, language="ca", country="ES")
    def speak(self, text: str, interrupt: bool = True) -> bool
    def stop(self)
    def announce_station(self, station_name: str, interrupt: bool = True)
    def announce_line(self, line_name: str, interrupt: bool = True)
    def announce_sequence(self, station_name: str, line_name: str, interrupt: bool = True)
    def set_speech_rate(self, rate: float)
    def set_pitch(self, pitch: float)
    def shutdown(self)
    
    # Properties
    is_initialized: bool
    is_available: bool
    language: str
    country: str
```

## Notas

- El TTS es **asíncrono**: no bloquea el juego
- En modo `interrupt=True` usa `QUEUE_FLUSH` (interrumpe)
- En modo `interrupt=False` usa `QUEUE_ADD` (encola)
- El servicio se inicializa automáticamente al primer uso
- Usa `shutdown()` al cerrar la aplicación para liberar recursos
