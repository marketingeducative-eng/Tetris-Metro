# CI Build Readiness Checklist

## Summary
This document tracks the changes made to prepare the Tetris-Metro (Pròxima Parada) project for Linux CI builds with Buildozer.

## ✅ Completed Tasks

### 1. buildozer.spec Configuration
**Status: FIXED**

#### Changes Applied:
- ✅ **Removed absolute paths** (lines 65-66):
  - Commented out `android.sdk_path` and `android.ndk_path` to use Buildozer defaults
  - CI runners can now use their own SDK/NDK installations
  
- ✅ **Extended source.include_exts**:
  - **Before**: `py,png,jpg,kv,atlas,json`
  - **After**: `py,png,jpg,jpeg,kv,atlas,json,ttf,otf,wav,ogg,mp3,md`
  - Added: `jpeg`, `ttf`, `otf`, `wav`, `ogg`, `mp3`, `md`
  - **Rationale**: Audio files and fonts are referenced in code (core/audio.py, required_assets.py)

#### Verified Configuration:
- ✅ package.name: `metrotetris`
- ✅ package.domain: `org.larosa`
- ✅ requirements: `python3,kivy,pyjnius>=1.4.0` (minimal, correct)
- ✅ android.permissions: `VIBRATE`
- ✅ android.archs: `arm64-v8a` (optimized for speed)
- ✅ android.api: 31
- ✅ android.minapi: 21 (good compatibility)

### 2. Assets Directory
**Status: CREATED**

#### Changes Applied:
- ✅ Created `assets/` directory
- ✅ Added placeholder `cover_proxima_parada.png` (1x1 black pixel PNG)
- ✅ Added `assets/.gitkeep` with documentation note

**Note**: The cover image is used in [ui/screens.py](ui/screens.py#L707) for the title screen background. The placeholder prevents runtime errors; replace with production asset (recommended: 1080x1920 portrait).

### 3. Path Analysis
**Status: VERIFIED**

#### Runtime Assets:
All asset references use **relative paths**:
- `data/barcelona_metro_lines_stations.json` ✅
- `data/stations.json` ✅
- `data/sounds/*.wav` (directory exists, currently empty) ✅
- `data/fonts/*.ttf` (directory exists, currently empty) ✅
- `assets/cover_proxima_parada.png` ✅ (placeholder created)

No absolute paths or local environment dependencies found in Python code.

### 4. Dependencies Review
**Status: VERIFIED**

#### Current requirements:
```
python3,kivy,pyjnius>=1.4.0
```

#### Analysis:
- **Kivy**: Core framework ✅
- **pyjnius**: Required for Android TTS (TextToSpeech API) ✅
- **No heavy libraries**: No numpy, scipy, pandas, PIL (good for CI performance) ✅

All imports in the codebase are satisfied by:
- Python stdlib (json, math, random, pathlib, etc.)
- Kivy and its sub-modules
- Local modules (core/, game/, ui/, data/)

## 🚀 CI Build Command

The project is now ready for CI with:

```bash
buildozer -v android debug
```

### Expected CI Environment:
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8+
- **Buildozer**: Latest stable
- **Required system packages**:
  - `build-essential`
  - `git`
  - `zip, unzip`
  - `openjdk-11-jdk` (or 17)
  - `python3-pip`
  - `autoconf, libtool, pkg-config`
  - `zlib1g-dev, libncurses5-dev, libffi-dev, libssl-dev`

### CI Setup Example (GitHub Actions):

```yaml
name: Android Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential git zip unzip \
            openjdk-11-jdk \
            autoconf libtool pkg-config \
            zlib1g-dev libncurses5-dev \
            libffi-dev libssl-dev
      
      - name: Install Buildozer
        run: |
          pip install --upgrade buildozer cython
      
      - name: Build APK
        run: |
          buildozer -v android debug
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: apk-debug
          path: bin/*.apk
```

## 📋 Production Readiness Notes

### Assets to Add (Optional):
1. **Cover Image**: Replace `assets/cover_proxima_parada.png` with production artwork
2. **Audio Files**: Add to `data/sounds/` as needed:
   - UI sounds (ui_click.wav, ui_pick.wav, ui_drop.wav, etc.)
   - SFX sounds (sfx_correct.wav, sfx_wrong.wav, etc.)
   - Ambient sounds (amb_tunnel.wav)
3. **Fonts**: Add custom fonts to `data/fonts/` if needed (.ttf files)

### Current Fallbacks:
- **Audio**: Code uses AudioService which gracefully handles missing sound files
- **Images**: Missing assets show as blank/black (no crashes)
- **Fonts**: Kivy uses default fonts if custom fonts are missing

## 🔍 Verification

### Pre-Commit Checks:
```bash
# Validate buildozer.spec
python tools/build_validator.py

# Check for absolute paths
grep -r "/home/" buildozer.spec || echo "✓ No absolute paths"

# Verify assets exist
ls -la assets/
ls -la data/sounds/
ls -la data/fonts/
```

### Test Build Locally:
```bash
# Clean build
buildozer android clean

# Debug build (verbose)
buildozer -v android debug

# Check output
ls -lh bin/*.apk
```

## 📝 Commit History

### Commit 1: Remove absolute paths from buildozer.spec
**Changes**:
- Commented out `android.sdk_path` and `android.ndk_path`
- Added note explaining CI-friendly approach

**Rationale**: Absolute paths to `/home/xavi_delgado/` are local environment-specific and break CI builds.

### Commit 2: Extend source.include_exts for all runtime assets
**Changes**:
- Added file extensions: `jpeg,ttf,otf,wav,ogg,mp3,md`

**Rationale**: Audio files and fonts are referenced in code but weren't included in buildozer packaging.

### Commit 3: Create assets directory with placeholder
**Changes**:
- Created `assets/` directory
- Added placeholder `cover_proxima_parada.png`
- Added `.gitkeep` with documentation

**Rationale**: [ui/screens.py](ui/screens.py#L707) references this image; placeholder prevents runtime errors in CI.

## ✨ Result

**The project is now CI-ready and can build successfully with:**
```bash
buildozer -v android debug
```

**Key improvements**:
- ✅ No local environment dependencies
- ✅ All runtime assets accounted for
- ✅ Proper file extension coverage
- ✅ Graceful fallbacks for optional assets
- ✅ Minimal requirements (fast CI builds)
- ✅ Clear documentation for production assets
- ✅ GitHub Actions workflow configured ([.github/workflows/android-debug.yml](.github/workflows/android-debug.yml))
- ✅ .gitignore created to exclude local venv and build artifacts

## 🚀 GitHub Actions Workflows

### Automatic Debug Builds

**File**: [.github/workflows/android-debug.yml](.github/workflows/android-debug.yml)

**Trigger**: Automatically on every push/PR to `main`

**Features**:
- Automatic pipeline: every commit to `main` triggers build
- Caches: pip, buildozer, gradle (speeds up builds)
- System dependencies: all required packages for Android builds
- Robust error handling: fails if APK not found
- Debug step: lists `bin/` directory contents
- Artifact upload: retains APK for 30 days
- Uses latest stable actions (checkout@v4, cache@v4, etc.)

**First build**: ~15-30 minutes (downloads Android SDK/NDK)  
**Cached builds**: ~5-10 minutes

### Manual Release Builds

**File**: [.github/workflows/android-release.yml](.github/workflows/android-release.yml)

**Trigger**: Manual via GitHub UI (workflow_dispatch)

**Features**:
- Custom version name input (e.g., `1.0.0`, `1.1.0-beta`)
- Build type selector: debug or release
- Updates `buildozer.spec` temporarily (no repo commits)
- Caches same as debug builds
- Artifact naming includes version: `proxima-parada-{version}-{type}`
- Metadata capture: commit hash, timestamp, branch
- Artifacts retained for 90 days (vs 30 for debug)

**Usage**: See [RELEASE_BUILD_GUIDE.md](RELEASE_BUILD_GUIDE.md) for detailed instructions

**How to invoke**:
1. Go to GitHub → Actions → "Android Release Build (Manual)"
2. Click "Run workflow"
3. Enter version name (e.g., `1.0.0`) and select build type
4. Click "Run workflow"

---

**Date**: 2026-03-01  
**Engineer**: Build/Release Engineer  
**Project**: Tetris-Metro (Pròxima Parada)
