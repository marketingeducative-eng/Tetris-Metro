# 🏗️ Tetris Metro - Android Build Guide

## Guía Completa para Builds Reproducibles y Libres de OOM

---

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Configuración Inicial](#configuración-inicial)
3. [Proceso de Build](#proceso-de-build)
4. [Resolución de Problemas](#resolución-de-problemas)
5. [Optimizaciones](#optimizaciones)

---

## 🖥️ Requisitos del Sistema

### Hardware Mínimo
- **RAM:** 8GB (16GB recomendado)
- **Disco:** 20GB libres (50GB recomendado)
- **CPU:** Dual-core 2.0GHz (Quad-core recomendado)

### Software Requerido
- **Python:** 3.8 o superior
- **Java JDK:** OpenJDK 11 o 17
- **Git:** Para clonar repositorios
- **Buildozer:** pip install buildozer
- **Cython:** pip install cython

### Dependencias Python Adicionales
```bash
pip install psutil pillow
```

---

## ⚙️ Configuración Inicial

### 1. Validar el Entorno

Antes de hacer cualquier build, ejecuta el validador de dependencias:

```powershell
python scripts\check_dependencies.py
```

Este script verifica:
- ✅ Versión de Python
- ✅ Instalación de Buildozer
- ✅ Herramientas de compilación
- ✅ Espacio en disco
- ✅ Paquetes Python necesarios

### 2. Revisar Configuración de Memoria

Ejecuta el profiler de memoria:

```powershell
python tools\memory_profiler.py
```

Esto te mostrará:
- 💾 Memoria RAM disponible
- 💿 Espacio en disco libre
- 📦 Tamaño del cache de Buildozer

**Nota:** Si tienes menos de 4GB de RAM disponible, cierra otras aplicaciones antes de hacer el build.

### 3. Validar buildozer.spec

Valida tu configuración:

```powershell
python tools\build_validator.py
```

Este script revisa:
- Configuración de memoria Gradle
- Niveles de API
- Dependencias problemáticas
- Configuración de assets

---

## 🔨 Proceso de Build

### Build Automatizado (Recomendado)

El script de build incluye todas las validaciones y optimizaciones:

```powershell
# Build debug básico
.\scripts\build_android.ps1

# Build con limpieza previa
.\scripts\build_android.ps1 -Clean

# Build release
.\scripts\build_android.ps1 -Release

# Build sin validación (no recomendado)
.\scripts\build_android.ps1 -SkipValidation
```

### Pipeline Completo desde VS Code

Si usas VS Code, puedes ejecutar la tarea completa:

1. `Ctrl+Shift+P`
2. Buscar "Run Task"
3. Seleccionar "🔄 Full Build Pipeline"

Esto ejecuta en orden:
1. ✅ Check Build Environment
2. 🧹 Clean Build Cache
3. 📊 Memory Profile
4. ✅ Validate Config
5. 🖼️ Optimize Assets
6. 🏗️ Build Android

---

## 🔧 Resolución de Problemas

### Error: Out of Memory (OOM)

**Síntomas:**
```
OutOfMemoryError: Java heap space
FATAL EXCEPTION: Could not reserve enough space
```

**Soluciones:**

1. **Limpiar cache:**
   ```powershell
   .\scripts\clean_build.ps1
   ```

2. **Aumentar memoria Gradle:**
   Edita `buildozer.spec`:
   ```ini
   android.gradle_options = -Xmx2048m -Xms512m
   ```

3. **Cerrar aplicaciones:**
   Libera memoria RAM antes de hacer build

4. **Deep clean:**
   ```powershell
   .\scripts\clean_build.ps1 -DeepClean
   ```

Ver más: [OOM_TROUBLESHOOTING.md](OOM_TROUBLESHOOTING.md)

### Error: Build Fails Inconsistently

**Síntomas:**
- Build funciona a veces, falla otras veces
- Errores de "corrupted cache"

**Soluciones:**

1. **Habilitar builds determinísticos:**
   ```powershell
   $env:PYTHONHASHSEED = "0"
   ```
   (Ya incluido en `build_android.ps1`)

2. **Limpiar completamente:**
   ```powershell
   .\scripts\clean_build.ps1 -DeepClean
   ```

3. **Verificar versiones:**
   ```powershell
   python scripts\check_dependencies.py
   ```

### Error: SDK/NDK Download Issues

**Síntomas:**
```
Could not download SDK
Connection timed out
```

**Soluciones:**

1. **Verificar conexión:** Asegúrate de tener internet estable

2. **Descargar manualmente:** Si el problema persiste, descarga SDK manualmente y colócalo en `.buildozer/android/platform/`

3. **Reintentar con paciencia:** Los downloads pueden tardar mucho

---

## 🚀 Optimizaciones

### Optimizar Assets

Reduce el tamaño del APK y memoria necesaria:

```powershell
python tools\asset_optimizer.py
```

Este script identifica:
- 🖼️ Imágenes grandes sin comprimir
- 🔊 Archivos de audio WAV sin comprimir
- 📦 Assets que pueden optimizarse

### Configuración Óptima de buildozer.spec

Ver ejemplo completo en `.buildozer.spec.optimized`

**Puntos clave:**

```ini
# Memoria Gradle (crítico para evitar OOM)
android.gradle_options = -Xmx2048m -Xms512m -XX:MaxMetaspaceSize=512m

# API moderna para mejor rendimiento
android.api = 33
android.minapi = 21

# Solo incluir assets necesarios
source.include_exts = py,png,jpg,kv,atlas,ogg,ttf

# Permisos mínimos necesarios
android.permissions = INTERNET,VIBRATE

# Orientación fija para evitar bugs
orientation = portrait
```

### Builds Más Rápidos

1. **No hagas deep clean innecesariamente**
   - Solo limpia cuando haya errores
   - Cache aceleran builds subsecuentes

2. **Usa build debug durante desarrollo**
   - Release tarda mucho más
   - Solo usa release para distribución final

3. **Mantén assets optimizados**
   - Imágenes PNG comprimidas
   - Audio en OGG, no WAV
   - Sin videos pesados

---

## 📊 Métricas de Build

### Tiempos Esperados

| Tipo Build | Primera Vez | Subsecuente |
|-----------|-------------|-------------|
| Debug     | 20-45 min   | 5-15 min    |
| Release   | 30-60 min   | 10-20 min   |

### Tamaños Esperados

| Componente          | Tamaño    |
|--------------------|-----------|
| APK Debug          | 15-30 MB  |
| APK Release        | 10-20 MB  |
| Cache .buildozer   | 2-5 GB    |

---

## 🎯 Checklist Pre-Build

Antes de cada build:

- [ ] `python scripts\check_dependencies.py` - Todo OK
- [ ] `python tools\memory_profiler.py` - RAM suficiente
- [ ] `python tools\build_validator.py` - Config válida
- [ ] Cerrar aplicaciones pesadas (Chrome, etc)
- [ ] Al menos 10GB disco libre

---

## 📚 Referencias Adicionales

- [OOM_TROUBLESHOOTING.md](OOM_TROUBLESHOOTING.md) - Soluciones detalladas a problemas de memoria
- [BUILD_OPTIMIZATION.md](BUILD_OPTIMIZATION.md) - Técnicas avanzadas de optimización
- [buildozer.spec](../buildozer.spec) - Configuración actual
- [.buildozer.spec.optimized](../.buildozer.spec.optimized) - Configuración recomendada

---

## 🆘 Soporte

Si sigues teniendo problemas:

1. Revisa logs en `.buildozer/`
2. Ejecuta todos los diagnósticos
3. Prueba deep clean
4. Consulta la documentación oficial de Buildozer

---

**Última actualización:** 2026-02-28
