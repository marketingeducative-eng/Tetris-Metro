# Sounds Directory

This directory contains audio files for game sound effects.

## Station Announcement Chime

The game will automatically use `station_chime.wav` if present in this directory for the station announcement sound effect.

If no `station_chime.wav` file is found, the game will generate a pleasant two-tone chime programmatically (E5 → C6).

### Custom Sound Requirements

To use a custom station announcement sound:

1. Name your file: `station_chime.wav`
2. Format: WAV format recommended
3. Duration: Keep it short (100-300ms) for best UX
4. Volume: The game will set volume to 40% automatically

### Sound Effect Timing

The station announcement chime plays when:
- A new station is revealed at the start of each round
- The "Pròxima parada:" label updates with the next station name

### Example Sounds

You can find free metro/transit chimes at:
- Freesound.org (search for "ding", "chime", "notification")
- BBC Sound Effects Library
- Metro/transit authority sound archives

### Generating Your Own

The built-in generator creates a pleasant two-tone chime:
- First tone: E5 (659.25 Hz) - 150ms
- Second tone: C6 (1046.50 Hz) - 150ms
- Total duration: 300ms
- Envelope: Sine fade in/out for smooth sound

You can modify the frequencies and duration in `core/audio.py` if desired.
