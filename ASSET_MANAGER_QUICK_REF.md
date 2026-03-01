# Asset Management System - Quick Reference

## Files Created/Modified

```
✅ asset_manager.py              - Core module (NEW)
✅ required_assets.py            - Configuration (NEW)
✅ main.py                       - Modified for validation
✅ ASSET_MANAGER_GUIDE.md        - Comprehensive guide (NEW)
✅ asset_manager_examples.py     - Code samples (NEW)
✅ ASSET_MANAGER_IMPLEMENTATION.md - Summary (NEW)
✅ data/sounds/                  - Sound directory (EXISTS)
✅ data/fonts/                   - Font directory (EXISTS)
```

## Essential Commands

```bash
# Test the asset system
python -c "from asset_manager import get_asset_path; print('✓ Asset manager loaded')"

# Run the game with asset validation
python main.py

# List available assets
python -c "from asset_manager import list_available_assets; print(list_available_assets('data'))"
```

## 3-Minute Setup

### 1. Add your assets
```bash
cp your_sound.wav data/sounds/
cp your_font.ttf data/fonts/
```

### 2. Update required_assets.py
```python
REQUIRED_ASSETS = [
    'data/sounds/your_sound.wav',
    'data/fonts/your_font.ttf',
]
```

### 3. Update buildozer.spec
```ini
source.include_exts = py,png,jpg,kv,atlas,json,wav,ttf,mp3,ogg
```

### 4. Use in game code
```python
from asset_manager import get_asset_path
from kivy.core.audio import SoundLoader

sound = SoundLoader.load(get_asset_path('data/sounds/your_sound.wav'))
sound.play()
```

### 5. Test
```
python main.py        # Desktop test
buildozer android run # Android test
```

## Usage Patterns

### Load Sound
```python
from asset_manager import get_asset_path
from kivy.core.audio import SoundLoader

path = get_asset_path('data/sounds/bell.wav')
sound = SoundLoader.load(path)
sound.play()
```

### Use Font
```python
from asset_manager import get_asset_path
from kivy.uix.label import Label

font = get_asset_path('data/fonts/main.ttf')
label = Label(font_name=font, text='Hello')
```

### Validate Assets
```python
from asset_manager import validate_required_assets

required = ['data/sounds/bell.wav', 'data/fonts/main.ttf']
validate_required_assets(required)  # Raises if missing
```

### List Available
```python
from asset_manager import list_available_assets

sounds = list_available_assets('data/sounds')
for sound in sounds:
    print(sound)
```

## Key Features

✅ **Desktop & Android** - Automatic detection
✅ **No Hardcoded Paths** - All relative
✅ **Startup Validation** - Catches issues early
✅ **Clear Errors** - Helpful failure messages
✅ **Logging** - Debug-friendly
✅ **APK-Safe** - Works in Android package
✅ **Production-Ready** - Error handling included

## File Locations After Setup

```
Tetris-Metro/
├── main.py (modified)
├── asset_manager.py (new)
├── required_assets.py (new)
├── asset_manager_examples.py (new)
├── game_propera_parada.py
├── buildozer.spec (update needed)
├── data/
│   ├── sounds/
│   │   ├── .gitkeep
│   │   ├── bell.wav (your files)
│   │   └── error.wav (your files)
│   ├── fonts/
│   │   ├── .gitkeep
│   │   ├── main.ttf (your files)
│   │   └── mono.ttf (your files)
│   └── (other data files)
├── ASSET_MANAGER_GUIDE.md (new)
├── ASSET_MANAGER_IMPLEMENTATION.md (new)
└── ...
```

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Asset not found" | Check file exists in data/sounds or data/fonts |
| Works on desktop but not Android | Update buildozer.spec include_exts |
| Can't import asset_manager | Ensure asset_manager.py is in project root |
| Startup is slow | Move non-critical assets to OPTIONAL_ASSETS |
| Different behavior | Check no absolute paths in game code |

## Startup Flow with Validation

```
python main.py
    ↓
Load asset_manager.py
    ↓
startup_validation()
    ├─ Check REQUIRED_ASSETS from required_assets.py
    ├─ Call validate_required_assets()
    └─ Log results
    ↓
All valid? → YES → Create app and run
    ↓ NO
Print clear error
sys.exit(1)
```

## Integration Checklist

- [ ] Asset files placed in data/sounds/ and data/fonts/
- [ ] required_assets.py updated with your files
- [ ] buildozer.spec has correct source.include_exts
- [ ] main.py has asset validation (auto-integrated)
- [ ] Game code uses get_asset_path()
- [ ] Tested with `python main.py`
- [ ] Tested on Android emulator/device

## Documentation Files

- **ASSET_MANAGER_GUIDE.md** - Full reference guide
- **asset_manager_examples.py** - Code examples & patterns
- **ASSET_MANAGER_IMPLEMENTATION.md** - What was created & why
- **THIS FILE** - Quick reference

## Next: Detailed Guides

Need more info? See:
- Setup: `ASSET_MANAGER_GUIDE.md` → SETUP STEPS
- Examples: `asset_manager_examples.py` → Copy patterns
- Troubleshooting: `ASSET_MANAGER_GUIDE.md` → TROUBLESHOOTING
- API: `ASSET_MANAGER_GUIDE.md` → API REFERENCE

## Support

```python
# Enable debug logging
import logging
logging.getLogger('asset_manager').setLevel(logging.DEBUG)

# List what's available
from asset_manager import list_available_assets
print(list_available_assets('data'))

# Test a specific asset
from asset_manager import get_asset_path
try:
    path = get_asset_path('data/sounds/test.wav')
    print(f"Found: {path}")
except RuntimeError as e:
    print(f"Error: {e}")
```

---

**Status**: ✅ Ready to Use

Start by adding your assets to data/ and updating required_assets.py!
