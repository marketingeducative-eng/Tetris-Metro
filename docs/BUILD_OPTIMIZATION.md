# ⚡ Build Optimization Guide

## Técnicas Avanzadas para Builds Más Rápidos y Eficientes

---

## 🎯 Objetivos de Optimización

1. **Reducir tiempo de build** (30-50% mejora)
2. **Minimizar uso de memoria** (evitar OOM)
3. **Builds reproducibles** (mismos resultados siempre)
4. **APK más pequeño** (mejor instalación y rendimiento)

---

## 🚀 Optimizaciones de Configuración

### buildozer.spec Optimizado

#### Memoria y Performance

```ini
# === GRADLE OPTIMIZATION ===
# Balance entre velocidad y memoria
android.gradle_options = -Xmx2048m -Xms512m -XX:MaxMetaspaceSize=512m -XX:+UseG1GC -XX:+HeapDumpOnOutOfMemoryError

# Parallel builds (solo si tienes >8GB RAM)
# android.gradle_options = -Xmx3072m -Xms1024m --parallel --max-workers=2

# === SDK/NDK VERSIONS ===
# Versiones específicas para builds reproducibles
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# === ARQUITECTURAS ===
# Una arquitectura = build más rápido
# Desarrollo: solo arm64
android.archs = arm64-v8a

# Producción: múltiples arquitecturas (split APKs)
# android.archs = arm64-v8a,armeabi-v7a
# android.enable_split = 1

# === COMPILACIÓN ===
# Skip debug symbols en desarrollo
android.debug = 0

# Optimizaciones del compilador
# p4a.bootstrap = sdl2
# p4a.local_recipes = ./recipes
```

#### Assets y Recursos

```ini
# === ASSETS ===
# Solo incluir lo necesario
source.include_exts = py,png,jpg,kv,atlas,ogg,ttf

# Excluir directorios innecesarios
source.exclude_dirs = tests, docs, .vscode, tools, scripts, __pycache__, *.egg-info

# Excluir archivos de desarrollo
source.exclude_patterns = test_*, *.spec, *.md, .git*, .DS_Store, *.pyc, *.pyo

# === PERMISOS ===
# Solo los estrictamente necesarios (menos checks = build más rápido)
android.permissions = INTERNET,VIBRATE,WAKE_LOCK

# === FEATURES ===
# Declarar features explícitamente
android.features = android.hardware.touchscreen

# === ORIENTATION ===
# Fija para evitar lógica de rotación
orientation = portrait
fullscreen = 1
```

#### Requirements Optimizados

```ini
# === REQUIREMENTS ===
# Versiones específicas para reproducibilidad
requirements = python3,kivy==2.3.0,plyer

# Si necesitas más:
# requirements = python3,kivy==2.3.0,plyer,pillow,requests

# EVITAR librerías pesadas innecesarias:
# ❌ numpy, scipy, pandas (si no las usas)
# ❌ opencv (muy pesado)
# ✅ Solo lo que realmente necesitas
```

---

## 🖼️ Optimización de Assets

### Imágenes

#### Herramientas de Compresión

**pngquant (Lossy, excelente compresión):**
```bash
# Instalar: choco install pngquant (Windows)
pngquant --quality 65-80 --ext .png --force assets/**/*.png
```

**OptiPNG (Lossless):**
```bash
# Instalar: choco install optipng
optipng -o7 assets/**/*.png
```

**ImageMagick (Resize + Compress):**
```bash
# Resize a max 1024px manteniendo aspecto
magick mogrify -resize 1024x1024\> -quality 85 assets/**/*.jpg
```

#### Atlas Textures (Kivy)

Combinar múltiples imágenes en un atlas reduce draw calls:

```python
# En tu código Kivy
from kivy.atlas import Atlas

atlas = Atlas('assets/game.atlas')
sprite = atlas['piece_blue']
```

Crear atlas:
```python
# create_atlas.py
from kivy.atlas import Atlas

Atlas.create(
    'assets/game.atlas',
    ['assets/piece_blue.png', 'assets/piece_red.png', ...],
    512  # Tamaño del atlas
)
```

#### Directrices de Tamaño

| Tipo | Max Dimensiones | Max Tamaño |
|------|----------------|------------|
| Splash screen | 1080x1920 | 500KB |
| Background | 1080x1920 | 300KB |
| UI elements | 512x512 | 100KB |
| Icons | 256x256 | 50KB |
| Pieces/Sprites | 128x128 | 30KB |

### Audio

#### Conversión a OGG

**FFmpeg (mejor herramienta):**
```bash
# Instalar: choco install ffmpeg

# Música (stereo, calidad media)
ffmpeg -i music.wav -c:a libvorbis -q:a 4 music.ogg

# SFX (mono, calidad suficiente)
ffmpeg -i sound.wav -ac 1 -c:a libvorbis -q:a 3 sound.ogg

# Batch conversion
for %f in (*.wav) do ffmpeg -i "%f" -c:a libvorbis -q:a 4 "%~nf.ogg"
```

#### Directrices de Audio

| Tipo | Canales | Bitrate | Duración Max |
|------|---------|---------|--------------|
| Música | Stereo | 96-128 kbps | 2-3 min (loop) |
| SFX | Mono | 64-96 kbps | 1-2 seg |
| Ambiente | Stereo | 96 kbps | 30-60 seg |

---

## 🔧 Optimizaciones del Sistema

### Windows

#### PowerShell Performance

```powershell
# Disable Windows Defender durante build (temporal)
# ⚠️ Solo si confías en el código
Set-MpPreference -DisableRealtimeMonitoring $true

# Al terminar:
Set-MpPreference -DisableRealtimeMonitoring $false

# Aumentar prioridad del proceso (cuidado!)
# $process = Get-Process python
# $process.PriorityClass = 'High'
```

#### Environment Variables

```powershell
# En tu perfil o build script
$env:GRADLE_OPTS = "-Xmx2048m -Xms512m -Dorg.gradle.daemon=true -Dorg.gradle.parallel=true"
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONHASHSEED = "0"  # Determinismo
$env:PIP_NO_CACHE_DIR = "1"  # Menos disco
```

### Linux/WSL

#### Swap Optimization

```bash
# Configurar swappiness (0-100, default 60)
# Menor = menos swap, más RAM
sudo sysctl vm.swappiness=10

# Permanente
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
```

#### File Watchers

```bash
# Aumentar límite de file watchers
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

## 📦 Optimización del APK

### ProGuard (Minificación)

Activa en `buildozer.spec` para release:

```ini
[app:android.release]
# Minificación y ofuscación
android.enable_proguard = 1

# Archivo de reglas personalizado
android.proguard_file = proguard-rules.pro
```

Crea `proguard-rules.pro`:
```proguard
# Mantener clases de Kivy
-keep class org.kivy.** { *; }
-keep class org.renpy.** { *; }

# Optimizaciones
-optimizationpasses 5
-dontusemixedcaseclassnames
-dontskipnonpubliclibraryclasses
-dontpreverify
-verbose
```

### Split APKs por Arquitectura

```ini
# En buildozer.spec
android.archs = arm64-v8a,armeabi-v7a
android.enable_split = 1
```

Resultado:
- `app-arm64-v8a-release.apk` (moderna, más pequeña)
- `app-armeabi-v7a-release.apk` (legacy)

### Bundle (AAB) en lugar de APK

Para Google Play:

```ini
# En buildozer.spec
android.release_artifact = aab
```

Ventajas:
- 15-30% más pequeño
- Google Play lo optimiza automáticamente
- Requerido para nuevas apps en Play Store

---

## 🎯 Estrategias de Build

### Desarrollo: Iteración Rápida

```ini
# buildozer.spec para DEV
android.archs = arm64-v8a  # Solo una
android.debug = 0  # Sin symbols
android.minapi = 21
requirements = python3,kivy  # Mínimo
```

```powershell
# Build rápido (NO clean)
buildozer android debug
```

### Testing: Validación

```ini
# buildozer.spec para TEST
android.archs = arm64-v8a,armeabi-v7a
android.debug = 1  # Con debug
requirements = python3,kivy,plyer  # Completo
```

```powershell
# Build completo con validación
.\scripts\build_android.ps1 -Clean
```

### Producción: Release Optimizado

```ini
# buildozer.spec para PROD
android.archs = arm64-v8a,armeabi-v7a
android.enable_split = 1
android.enable_proguard = 1
android.release_artifact = aab
android.debug = 0
requirements = python3,kivy==2.3.0,plyer  # Versiones fijas
```

```powershell
# Build release
.\scripts\build_android.ps1 -Release -Clean
```

---

## 📊 Métricas y Benchmarks

### Medir Tiempos de Build

**Script de medición:**
```powershell
# measure_build.ps1
$start = Get-Date

.\scripts\build_android.ps1

$end = Get-Date
$duration = $end - $start

Write-Host "Build duration: $($duration.ToString('mm\:ss'))"
"Build,$start,$end,$($duration.TotalSeconds)" | Out-File -Append build_metrics.csv
```

### Comparar Optimizaciones

| Optimización | Tiempo Base | Tiempo Optimizado | Mejora |
|-------------|-------------|-------------------|--------|
| Single arch | 30 min | 20 min | 33% |
| Assets optimizados | 25 min | 22 min | 12% |
| No debug symbols | 25 min | 20 min | 20% |
| Gradle parallel | 25 min | 18 min | 28% |
| **Todas** | 30 min | **15 min** | **50%** |

### Tamaños de APK

| Configuración | Tamaño |
|--------------|--------|
| Debug, no optimizado | 35 MB |
| Debug, optimizado | 25 MB |
| Release, no optimizado | 30 MB |
| Release, optimizado | **18 MB** |
| AAB optimizado | **12 MB** |

---

## 🔬 Análisis Avanzado

### Perfilar Build de Gradle

```bash
# Agrega a gradle_options
--profile --scan

# Genera reporte en:
# build/reports/profile/profile-*.html
```

### Analizar Tamaño del APK

```bash
# Descargar APK Analyzer (Android Studio)
# O usar online: https://appetize.io/

# Desde línea de comandos
apkanalyzer apk summary app.apk
apkanalyzer apk file-size app.apk
```

### Cache Gradle

Gradle daemon acelera builds subsecuentes:

```ini
# buildozer.spec
android.gradle_options = -Dorg.gradle.daemon=true -Dorg.gradle.caching=true
```

---

## ✅ Checklist de Optimización

### Configuración
- [ ] Gradle memory settings optimizados
- [ ] Una sola arquitectura para dev
- [ ] Debug symbols desactivados (dev)
- [ ] Requirements mínimos
- [ ] Exclude dirs configurado

### Assets
- [ ] Imágenes comprimidas (PNG/JPG)
- [ ] Audio en OGG (no WAV)
- [ ] Atlas textures para sprites
- [ ] Sin assets innecesarios

### Sistema
- [ ] Al menos 8GB RAM
- [ ] 20GB+ disco libre
- [ ] Cache limpio periódicamente
- [ ] Aplicaciones pesadas cerradas

### Workflow
- [ ] Evitar clean innecesarios
- [ ] Usar build debug en dev
- [ ] Solo release para producción
- [ ] Validar antes de build

---

## 🎓 Tips Pro

1. **Incremental builds:** No hagas clean cada vez
2. **Cache is king:** Gradle y pip cachean, úsalo
3. **Profile primero:** Mide antes de optimizar
4. **Test en real:** Emulador != device real
5. **Automatiza:** Scripts > manual

---

**Última actualización:** 2026-02-28
