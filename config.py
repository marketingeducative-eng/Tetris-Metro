# Configuració de Metro Tetris - ORDER TRACK

## Paràmetres de joc

### Mode cívic (desplegament municipal)
civic_mode = True

### Tema Modernisme 2.0 (toggle de desenvolupament)
modernisme_2_0_theme = True

### Pista (Rail)
RAIL_COLUMNS = [4, 5]  # Columnes on es validen les estacions

### Missions de Direcció
DIRECTION_MISSION_TRIGGER = 5  # Cada N encerts correctes
DIRECTION_MISSION_COOLDOWN = 3.0  # Segons entre missions

### Notificacions
STATION_UNLOCK_DURATION = 2.0  # Durada notificació desbloquejat (segons)
FEEDBACK_DURATION = 2.0  # Durada del feedback en pantalla

### Puntuacions
BASE_CORRECT_BONUS = 500  # Punts base per estació correcta
STREAK_BONUS_MULTIPLIER = 100  # Punts addicionals per ratxa
DIRECTION_MISSION_BONUS = 300  # Punts per missió de direcció correcta

### Velocitat de caiguda
INITIAL_FALL_SPEED = 0.5  # Segons entre caigudes (nivell 1)
FALL_SPEED_DECREASE = 0.03  # Reducció per nivell
MIN_FALL_SPEED = 0.1  # Velocitat mínima

### Visualització
CELL_SIZE = 28  # Píxels per cel·la
OFFSET_X = 30  # Desplaçament horitzontal del tauler
OFFSET_Y = 100  # Desplaçament vertical del tauler

### Mini-mapa
MINIMAP_STATIONS_COUNT = 10  # Estacions mostrades en el mini-mapa

### Colors de línies (hexadecimal)
LINE_COLORS = {
    'L1': '#E2001A',
    'L2': '#9B3FA0',
    'L3': '#00A651',
    'L4': '#FFCC00',
    'L5': '#004A98'
}
