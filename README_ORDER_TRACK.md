# Metro Tetris - ORDER TRACK Mode

## Instal·lació Ràpida

### Requisits
- Python 3.7+
- Kivy 2.0+

### Instal·lar Dependències

```bash
# Crear entorn virtual (recomanat)
python -m venv .venv

# Activar entorn (Windows)
.venv\Scripts\activate

# Activar entorn (Linux/Mac)
source .venv/bin/activate

# Instal·lar Kivy
pip install kivy
```

### Execució

```bash
# Mode ORDER TRACK (nou)
python main_order_track.py

# Mode antic (si vols comparar)
python main_fixed.py
```

## Estructura del Projecte

```
Tetris-Metro/
├── main_order_track.py       # Aplicació principal amb nous modos
├── main_fixed.py              # Versió anterior
├── config.py                  # Configuració de paràmetres
├── MODOS_JUEGO.md            # Documentació completa dels modos
│
├── game/                      # Lògica del joc
│   ├── controller.py          # ✨ Actualitzat: Suporta modos A i B
│   ├── album_store.py         # ✨ Nou: Persistència de progrés
│   ├── order_track.py         # ✨ Nou: Gestor del Modo A
│   ├── direction_mission.py   # ✨ Nou: Gestor del Modo B
│   ├── board.py
│   ├── piece.py
│   └── tetrominos.py
│
├── ui/                        # Interfície d'usuari
│   ├── hud_view.py            # ✨ Actualitzat: Mini-mapa i progrés
│   ├── overlays.py            # ✨ Actualitzat: Nous overlays
│   ├── board_view.py
│   └── particles.py
│
├── model/                     # Model de dades
│   ├── metro_content.py
│   ├── scoring.py
│   └── rules.py
│
└── data/                      # Dades i persistència
    ├── stations.json          # Dades de les estacions
    ├── album_data.json        # ✨ Generat: Progrés del jugador
    └── game_data.json
```

## Característiques Noves ✨

### Modo A: ORDER TRACK
- Col·loca estacions en l'ordre correcte d'una línia de metro
- Validació en columnes "rail" (4-5)
- Sistema de ratxes amb bonus
- Mini-mapa amb 10 pròximes estacions
- Desbloqueig progressiu d'estacions

### Modo B: MISSIÓ DE DIRECCIÓ
- Mini-repte cada 5 encerts
- Tria la direcció correcta entre dues opcions
- Preguntes en català
- Bonus de +300 punts

### Sistema d'Àlbum
- Progrés guardat offline
- Estadístiques per estació
- Comptadors d'encerts/errors
- Notificacions de desbloqueig

## Controls

### Teclat
- `←` `→` : Moure peça
- `↑` : Rotar
- `↓` : Caiguda ràpida
- `Espai` : Caiguda instantània
- `P` : Pausa

### Tàctil (Mòbil)
- Toc curt: Rotar
- Lliscar esquerra/dreta: Moure
- Lliscar avall: Caiguda instantània

## Configuració Personalitzada

Edita `config.py` per ajustar:
- Columnes de la pista
- Freqüència de missions
- Bonificacions de puntuació
- Velocitat del joc
- Colors de les línies

## Dades JSON

### stations.json
Conté les línies de metro amb estacions ordenades:
```json
{
  "metro_lines": {
    "L1": {
      "name": "Línia 1",
      "stations": ["Fondo", "Santa Eulàlia", ...]
    }
  }
}
```

### album_data.json (auto-generat)
Guarda el progrés:
```json
{
  "line_L1": {
    "unlocked": ["Catalunya", "Sagrada Família"]
  },
  "stats_st_001": {
    "correct": 12,
    "wrong": 3
  }
}
```

## Troubleshooting

### Error: "No module named 'kivy'"
```bash
pip install kivy
```

### El joc va massa ràpid/lent
Ajusta a `config.py`:
```python
INITIAL_FALL_SPEED = 0.8  # Més lent
FALL_SPEED_DECREASE = 0.02  # Progressió més suau
```

### No es veu el mini-mapa
Comprova la resolució de la finestra a `main_order_track.py`:
```python
Window.size = (360, 640)  # Mode mòbil
```

## Crèdits

- Disseny del joc: Metro Tetris
- Dades de metro: TMB Barcelona
- Framework: Kivy
- Implementació ORDER TRACK: 2026

---

Per més informació: Consulta `MODOS_JUEGO.md`
