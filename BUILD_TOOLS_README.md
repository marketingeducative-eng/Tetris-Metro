# 🛠️ Build Tools & Configuration

## Sistema de Build Reproducible y OOM-Safe para Tetris Metro

Este directorio contiene herramientas y configuración para hacer builds de Android reproducibles y libres de errores de memoria (OOM).

---

## 📁 Estructura

```
Tetris-Metro/
├── .vscode/
│   ├── settings.json          # Configuración del workspace
│   └── tasks.json             # Tareas de build (Ctrl+Shift+P > Run Task)
│
├── tools/                      # Herramientas de diagnóstico
│   ├── memory_profiler.py     # Analiza memoria RAM/disco
│   ├── build_validator.py     # Valida buildozer.spec
│   └── asset_optimizer.py     # Optimiza assets del juego
│
├── scripts/                    # Scripts de build
│   ├── build_android.ps1      # Build OOM-safe automatizado
│   ├── clean_build.ps1        # Limpia cache de build
│   └── check_dependencies.py  # Verifica entorno de build
│
├── docs/                       # Documentación completa
│   ├── BUILD_GUIDE.md         # Guía completa de builds
│   ├── OOM_TROUBLESHOOTING.md # Soluciones a errores OOM
│   └── BUILD_OPTIMIZATION.md  # Optimizaciones avanzadas
│
├── buildozer.spec             # Configuración actual
├── .buildozer.spec.optimized  # Configuración recomendada
└── build.config.json          # Configuración centralizada
```

---

## 🚀 Quick Start

### 1. Validar Entorno

Antes de tu primer build:

```powershell
# Verificar dependencias
python scripts\check_dependencies.py

# Verificar memoria disponible
python tools\memory_profiler.py

# Validar configuración
python tools\build_validator.py
```

### 2. Primer Build

```powershell
# Build debug con todas las validaciones
.\scripts\build_android.ps1
```

### 3. Builds Subsecuentes

```powershell
# Build normal (usa cache)
.\scripts\build_android.ps1

# Build limpio (si hay errores)
.\scripts\build_android.ps1 -Clean

# Build release (para producción)
.\scripts\build_android.ps1 -Release
```

---

## 🔧 Herramientas

### Memory Profiler

Analiza memoria RAM, disco y cache de Buildozer:

```powershell
python tools\memory_profiler.py
```

**Muestra:**
- 💾 RAM total y disponible
- 💿 Espacio en disco
- 📦 Tamaño del cache .buildozer
- ⚠️ Warnings si recursos insuficientes
- ✅ Recomendaciones

### Build Validator

Valida la configuración de buildozer.spec:

```powershell
python tools\build_validator.py
```

**Revisa:**
- Memory settings de Gradle
- Versiones de API
- Dependencias problemáticas
- Configuración de assets
- Permisos

### Asset Optimizer

Analiza assets y recomienda optimizaciones:

```powershell
python tools\asset_optimizer.py
```

**Identifica:**
- 🖼️ Imágenes grandes sin comprimir
- 🔊 Audio WAV sin comprimir
- 📦 Assets que ocupan mucho espacio

### Build Script (PowerShell)

Script principal de build con validaciones integradas:

```powershell
# Sintaxis
.\scripts\build_android.ps1 [-Clean] [-Release] [-SkipValidation]

# Ejemplos
.\scripts\build_android.ps1                    # Debug normal
.\scripts\build_android.ps1 -Clean             # Debug con limpieza
.\scripts\build_android.ps1 -Release           # Release
.\scripts\build_android.ps1 -Release -Clean    # Release limpio
```

**Proceso:**
1. Valida configuración
2. Verifica memoria
3. Limpia cache (si -Clean)
4. Configura environment OOM-safe
5. Ejecuta build
6. Copia APK al workspace

### Clean Script

Limpia cache de build para resolver problemas:

```powershell
# Limpieza básica (Python cache + build intermediates)
.\scripts\clean_build.ps1

# Deep clean (casi todo excepto SDK/NDK)
.\scripts\clean_build.ps1 -DeepClean

# Ver qué se borraría sin borrar (dry run)
.\scripts\clean_build.ps1 -DryRun

# Deep clean manteniendo downloads
.\scripts\clean_build.ps1 -DeepClean -KeepDownloads
```

---

## 📋 VS Code Tasks

Si usas VS Code, accede a las tareas con `Ctrl+Shift+P` > "Run Task":

- 🔍 **Check Build Environment** - Verifica dependencias
- 🧹 **Clean Build Cache** - Limpia cache
- 📊 **Memory Profile** - Analiza memoria
- ✅ **Validate Build Config** - Valida configuración
- 🖼️ **Optimize Assets** - Optimiza assets
- 🏗️ **Build Android (OOM-Safe)** - Build completo
- 🔄 **Full Build Pipeline** - Todo el flujo

---

## 📖 Documentación

### [BUILD_GUIDE.md](docs/BUILD_GUIDE.md)

Guía completa de builds:
- Requisitos del sistema
- Configuración inicial
- Proceso de build paso a paso
- Resolución de problemas comunes
- Optimizaciones

### [OOM_TROUBLESHOOTING.md](docs/OOM_TROUBLESHOOTING.md)

Soluciones detalladas para errores de memoria:
- Tipos de OOM y cómo identificarlos
- Soluciones específicas por tipo
- Prevención de OOM
- Configuración óptima
- Casos extremos

### [BUILD_OPTIMIZATION.md](docs/BUILD_OPTIMIZATION.md)

Técnicas avanzadas de optimización:
- Optimización de buildozer.spec
- Compresión de assets
- Configuración del sistema
- Reducción de tamaño del APK
- Aceleración de builds

---

## ⚙️ Configuración

### build.config.json

Configuración centralizada en JSON con:
- Perfiles de build (dev/test/prod)
- Settings de memoria
- Thresholds de validación
- Optimizaciones
- Scripts disponibles
- Troubleshooting

### .buildozer.spec.optimized

Configuración recomendada de Buildozer:
- Memory settings óptimos
- APIs modernas
- Assets optimizados
- Comentarios explicativos

Para usar:
```powershell
# Backup del actual
Copy-Item buildozer.spec buildozer.spec.backup

# Usar optimizado
Copy-Item .buildozer.spec.optimized buildozer.spec

# O comparar y ajustar manualmente
code --diff buildozer.spec .buildozer.spec.optimized
```

---

## 🐛 Troubleshooting

### Build Falla con OOM

```powershell
# 1. Limpiar cache
.\scripts\clean_build.ps1 -DeepClean

# 2. Verificar memoria
python tools\memory_profiler.py

# 3. Cerrar aplicaciones pesadas

# 4. Reintentar
.\scripts\build_android.ps1
```

### Build Inconsistente

```powershell
# Habilitar builds determinísticos
$env:PYTHONHASHSEED = "0"

# Limpiar y rebuild
.\scripts\clean_build.ps1 -DeepClean
.\scripts\build_android.ps1
```

### APK Muy Grande

```powershell
# 1. Optimizar assets
python tools\asset_optimizer.py

# 2. Usar split APKs
# Edita buildozer.spec:
# android.archs = arm64-v8a,armeabi-v7a
# android.enable_split = 1

# 3. Considerar AAB en lugar de APK
# android.release_artifact = aab
```

---

## 📊 Métricas Esperadas

### Tiempos de Build

| Tipo | Primera Vez | Subsecuente |
|------|-------------|-------------|
| Debug | 20-45 min | 5-15 min |
| Release | 30-60 min | 10-20 min |

### Tamaños

| Archivo | Tamaño Esperado |
|---------|----------------|
| APK Debug | 15-30 MB |
| APK Release | 10-20 MB |
| Cache .buildozer | 2-5 GB |

### Recursos Mínimos

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| RAM | 6 GB | 12 GB |
| Disco | 15 GB | 30 GB |
| RAM Disponible | 4 GB | 6 GB |

---

## ✅ Workflow Recomendado

### Desarrollo Diario

```powershell
# Build rápido sin clean (usa cache)
.\scripts\build_android.ps1
```

### Después de Cambios Grandes

```powershell
# Build con limpieza y validación
.\scripts\build_android.ps1 -Clean
```

### Antes de Release

```powershell
# 1. Optimizar assets
python tools\asset_optimizer.py

# 2. Validar todo
python scripts\check_dependencies.py
python tools\build_validator.py

# 3. Build release limpio
.\scripts\build_android.ps1 -Release -Clean
```

---

## 🎓 Tips

1. **No hagas clean sin motivo** - Cache acelera builds
2. **Usa debug para desarrollo** - Release es más lento
3. **Monitorea memoria** - Evita OOM antes que ocurra
4. **Optimiza assets** - Menor APK, build más rápido
5. **Lee los logs** - Buildozer es verboso pero útil

---

## 🆘 Soporte

Si tienes problemas:

1. **Ejecuta diagnósticos:**
   ```powershell
   python scripts\check_dependencies.py
   python tools\memory_profiler.py
   python tools\build_validator.py
   ```

2. **Lee la documentación:**
   - [BUILD_GUIDE.md](docs/BUILD_GUIDE.md)
   - [OOM_TROUBLESHOOTING.md](docs/OOM_TROUBLESHOOTING.md)

3. **Intenta deep clean:**
   ```powershell
   .\scripts\clean_build.ps1 -DeepClean
   ```

4. **Revisa logs:**
   - `.buildozer/` contiene logs detallados
   - Busca "Error", "FAILED", "OutOfMemory"

---

## 📝 Notas Importantes

⚠️ **IMPORTANTE:** Estos scripts NO modifican el código del juego.

Solo crean/modifican:
- ✅ Archivos de configuración (.vscode/, build.config.json)
- ✅ Scripts de build (scripts/, tools/)
- ✅ Documentación (docs/)
- ✅ Configuraciones de Buildozer (.buildozer.spec.optimized)

NO tocan:
- ❌ Ningún .py del juego
- ❌ Assets del juego
- ❌ Lógica de la aplicación

---

**Creado:** 2026-02-28  
**Versión:** 1.0.0  
**Autor:** Build Tools Team
