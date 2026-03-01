# 🆘 OOM Troubleshooting Guide

## Soluciones Completas para Errores "Out of Memory"

---

## 🔍 Identificar el Tipo de OOM

Los errores OOM pueden ocurrir en diferentes etapas del build:

### 1. OOM durante Gradle Build

**Síntomas:**
```
* What went wrong:
Execution failed for task ':compileDebugJavaWithJavac'.
> java.lang.OutOfMemoryError: Java heap space
```

**Causa:** Heap de Java insuficiente

**Solución:**

Edita `buildozer.spec`:
```ini
android.gradle_options = -Xmx2048m -Xms512m -XX:MaxMetaspaceSize=512m
```

Si persiste, intenta:
```ini
android.gradle_options = -Xmx3072m -Xms1024m -XX:MaxMetaspaceSize=768m
```

⚠️ **Advertencia:** Valores muy altos (>4GB) pueden fallar en sistemas con poca RAM.

---

### 2. OOM durante Compilación de Cython

**Síntomas:**
```
Memory error
Unable to allocate memory for object
gcc killed (signal 9)
```

**Causa:** Sistema sin RAM suficiente para compilar extensiones

**Soluciones:**

1. **Añadir Swap (Linux/WSL):**
   ```bash
   # Crear 4GB swap
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

2. **Cerrar aplicaciones:**
   - Chrome/Firefox (pueden usar 2-4GB)
   - IDEs adicionales
   - Juegos/streamers

3. **Build en partes:**
   - Compila dependencias primero
   - Luego el proyecto principal

---

### 3. OOM durante Download/Extract SDK

**Síntomas:**
```
MemoryError: Unable to allocate array
Error extracting SDK files
```

**Causa:** Descompresión de archivos grandes

**Soluciones:**

1. **Limpiar cache y reintentar:**
   ```powershell
   .\scripts\clean_build.ps1 -DeepClean
   .\scripts\build_android.ps1
   ```

2. **Descargar SDK manualmente:**
   - Descarga desde [developer.android.com](https://developer.android.com/studio)
   - Coloca en `.buildozer/android/platform/android-sdk/`

---

### 4. OOM en Python durante Build

**Síntomas:**
```
MemoryError
Python process killed
```

**Causa:** Script de build usando demasiada memoria

**Soluciones:**

1. **Optimizar assets primero:**
   ```powershell
   python tools\asset_optimizer.py
   ```

2. **Usar Python 64-bit:**
   - Verifica: `python -c "import sys; print(sys.maxsize)"`
   - Si < 2^31, estás usando 32-bit (límite 2GB)

3. **Compilar sin debug symbols:**
   ```ini
   # En buildozer.spec
   android.debug = 0
   ```

---

## 🛠️ Soluciones Generales

### Nivel 1: Quick Fix

```powershell
# 1. Limpiar cache básico
.\scripts\clean_build.ps1

# 2. Verificar memoria disponible
python tools\memory_profiler.py

# 3. Build con validación
.\scripts\build_android.ps1
```

### Nivel 2: Intermediate Fix

```powershell
# 1. Deep clean
.\scripts\clean_build.ps1 -DeepClean

# 2. Optimizar assets
python tools\asset_optimizer.py

# 3. Validar config
python tools\build_validator.py

# 4. Build con config optimizada
Copy-Item .buildozer.spec.optimized buildozer.spec
.\scripts\build_android.ps1
```

### Nivel 3: Nuclear Option

```powershell
# 1. Borrar TODO
Remove-Item -Recurse -Force .buildozer, bin

# 2. Reiniciar sistema (liberar toda la RAM)

# 3. Build limpio
.\scripts\build_android.ps1 -Clean
```

---

## 💡 Prevención de OOM

### Configuración Óptima de buildozer.spec

```ini
# === CONFIGURACIÓN ANTI-OOM ===

# Memoria Gradle (CRÍTICO)
android.gradle_options = -Xmx2048m -Xms512m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError

# API moderna (mejor gestión de memoria)
android.api = 33
android.minapi = 21

# Compilación en release (menos memoria debug info)
# Pero más lenta - usar solo para producción
# android.release = 1

# Arquitecturas específicas (no universal)
# Reduce memoria y tiempo
android.archs = arm64-v8a

# Incluir solo assets necesarios
source.include_exts = py,png,jpg,kv,ogg,ttf
source.exclude_dirs = tests, docs, .vscode, tools, scripts

# Permisos mínimos
android.permissions = INTERNET,VIBRATE,WAKE_LOCK
```

### Optimización de Assets

**Imágenes:**
```bash
# Comprimir PNGs (herramientas externas)
pngquant --quality 65-80 input.png -o output.png
optipng -o7 image.png
```

**Audio:**
```bash
# Convertir WAV a OGG
ffmpeg -i input.wav -c:a libvorbis -q:a 4 output.ogg

# Para efectos cortos, mono es suficiente
ffmpeg -i input.wav -ac 1 -c:a libvorbis -q:a 3 output.ogg
```

**Directrices:**
- Imágenes: Max 1024x1024 para texturas
- Imágenes UI: Max 512x512
- Audio música: OGG 96-128 kbps
- Audio SFX: OGG 64-96 kbps, mono

---

## 📊 Monitoreo de Memoria

### Durante el Build

Abre otro terminal y monitorea:

```powershell
# Ver memoria cada 2 segundos
while ($true) { 
    Get-Process | Where-Object {$_.Name -like "*java*" -or $_.Name -like "*python*"} | 
    Select-Object Name, @{N='RAM (MB)';E={[math]::Round($_.WorkingSet64/1MB,2)}} | 
    Format-Table -AutoSize
    Start-Sleep 2 
}
```

### Logs de Gradle

Si Gradle hace OOM, debería crear un heap dump:

```
.buildozer/android/platform/build-*/java_pid*.hprof
```

Puedes analizarlo con herramientas como Eclipse MAT.

---

## 🎯 Diagnóstico Paso a Paso

### 1. Recopilar Información

```powershell
# Info del sistema
python tools\memory_profiler.py > diagnostico.txt

# Info de la config
python tools\build_validator.py >> diagnostico.txt

# Info de dependencias
python scripts\check_dependencies.py >> diagnostico.txt
```

### 2. Identificar el Paso que Falla

Ejecuta build y anota en qué punto falla:

- [ ] Descarga de SDK/NDK
- [ ] Instalación de requirements
- [ ] Compilación de Cython
- [ ] Gradle build (dex, merge, compile)
- [ ] Empaquetado final

### 3. Aplicar Solución Específica

Según el paso, aplica la solución correspondiente de las secciones anteriores.

---

## 🚨 Casos Extremos

### Sistema con 4GB RAM o Menos

**Realidad:** Buildozer necesita mucha RAM. Con 4GB es muy difícil.

**Opciones:**

1. **Swap agresivo (Linux/WSL):**
   ```bash
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```
   ⚠️ Será MUY lento (horas)

2. **Build en la nube:**
   - GitHub Actions
   - Google Cloud Build
   - AWS CodeBuild

3. **Usar máquina virtual:**
   - VM con más RAM asignada

### Build Funciona en PC A pero no en PC B

**Checklist de diferencias:**

```powershell
# En ambos PCs:
python --version
java -version
buildozer --version
python -c "import sys; print(sys.maxsize)"  # 32 vs 64 bit

# Comparar configs
python tools\build_validator.py
```

Diferencias comunes:
- Python 32-bit vs 64-bit
- Versiones diferentes de Java
- RAM disponible diferente

---

## 📚 Referencias

### Configuración Java/Gradle

- `-Xmx`: Memoria máxima heap
- `-Xms`: Memoria inicial heap
- `-XX:MaxMetaspaceSize`: Memoria para metadatos de clases
- `-XX:+HeapDumpOnOutOfMemoryError`: Crear dump al fallar

### Herramientas Útiles

- **Process Explorer (Windows):** Monitoreo detallado
- **htop (Linux):** Monitor de procesos
- **jconsole:** Monitor de JVM
- **MAT (Memory Analyzer Tool):** Analizar heap dumps

---

## ✅ Checklist de Prevención

Antes de CADA build:

- [ ] RAM disponible > 4GB
- [ ] Disco libre > 15GB
- [ ] Cache limpio (si build anterior falló)
- [ ] Aplicaciones pesadas cerradas
- [ ] Config validada (`build_validator.py`)
- [ ] Gradle memory settings correctos

---

**¿Aún tienes problemas?**

1. Ejecuta: `.\scripts\clean_build.ps1 -DeepClean -DryRun`
2. Revisa qué se va a borrar
3. Ejecuta sin `-DryRun`
4. Reinicia el sistema
5. Intenta build de nuevo

Si NADA funciona: considera builds en la nube o aumentar RAM física.

---

**Última actualización:** 2026-02-28
