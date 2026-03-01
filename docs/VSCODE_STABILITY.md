# VS Code Stability & WSL Guide

## Recommended Extensions (Minimal Set)

✅ **Essential:**
- **Python** (ms-python.python) - Core language support
- **Pylance** (ms-python.vscode-pylance) - AI-powered IntelliSense (configurado conservador en settings.json)
- **debugpy** (ms-python.debugpy) - Python debugging

✅ **Optional (Low overhead):**
- **Kivy** extension (if available)
- **Android** extension (ms-vscode.extension-name)

## Extensions to AVOID During Long Builds

❌ **High Memory/CPU Cost:**
- **Copilot/GitHub Copilot** - Constant analysis
- **Live Share** - Network overhead
- **Remote-SSH** extensions - Extra layer
- **ESLint, Prettier** (if installed) - Not needed for Python/Kivy
- **C/C++ Intellisense** - Heavy analysis
- **Docker, Kubernetes** extensions - Extra processes
- **GitLens** - Aggressive repo scanning (use `git.autofetch = false` if keeping)
- **Thunder Client, REST Client** - Network tools, unnecessary
- **Any language packs** for unused languages
- **Theme extensions** with high refresh rates

## Disable Extensions During Build

### Option 1: VS Code Workspace Settings
Already configured in `.vscode/settings.json`:
```json
"extensions.ignoreRecommendations": false
```

### Option 2: Disable Specific Extensions in UI
1. Open Extensions sidebar (`Ctrl+Shift+X`)
2. Find extension → Click gear icon → **Disable (Workspace)**

### Option 3: Launch with Disabled Extensions

**Disable ALL extensions:**
```bash
code --disable-extensions .
```

**Disable specific extension:**
```bash
code --disable-extension publisher.extension-name .
```

**Example - disable Copilot during build:**
```bash
code --disable-extension GitHub.Copilot .
```

### Option 4: WSL-Specific (Recommended for Builds)

Open in WSL without extensions:
```bash
code --disable-extensions /mnt/c/Users/Usuario/Desktop/Tetris-Metro
```

Then in terminal tab inside VS Code (already in WSL):
```bash
./scripts/build_android_debug.sh
```

## Verify WSL Environment

### Quick Check - In Terminal

```bash
# Should output Ubuntu version
uname -a
cat /etc/os-release

# Confirm you're in WSL (not native Windows)
grep -i microsoft /proc/version
```

✅ **Expected output:**
```
...microsoft...  # Contains "microsoft" = You're in WSL
Ubuntu 22.04 LTS (or later)
```

### In VS Code

1. Click **Remote indicator** (bottom-left corner, should show `WSL: Ubuntu` or similar)
2. Or run in integrated terminal:
   ```bash
   echo "WSL Distribution: $(wsl.exe -l -v 2>/dev/null | grep Ubuntu || echo 'Check manually')"
   ```

## Build Process Recommendations

1. **Before starting build:**
   ```bash
   # Check memory
   ./tools/diag_memory.sh
   
   # Clean old artifacts
   ./scripts/clean_build_artifacts.sh
   ```

2. **During build:**
   - Keep only Python + Pylance enabled
   - Close other VS Code windows/tabs not being used
   - Avoid heavy file exploration (minimize file tree)

3. **Run build:**
   ```bash
   ./scripts/build_android_debug.sh
   ```

4. **Check logs after build:**
   - VS Code task: `Android: tail last build log`
   - Or manual: `tail -n 200 logs/buildozer_debug_*.log`

## WSL Memory Optimization

If builds still hit OOM:

1. **Check WSL memory limit:**
   ```bash
   free -h
   ```

2. **Increase WSL allocation** (on Windows, .wslconfig):
   ```ini
   [wsl2]
   memory=4GB
   swap=2GB
   ```

3. **Monitor during build:**
   ```bash
   watch -n 1 'free -h && echo "---" && ps aux --sort=-rss | head -5'
   ```

## Summary Checklist

- [ ] Confirm WSL Ubuntu with `uname -a`
- [ ] Python + Pylance only enabled by default
- [ ] `settings.json` configured (already done)
- [ ] `.vscode/extensions.json` present (already done)
- [ ] Heavy extensions disabled for builds
- [ ] Memory diagnostics available (`./tools/diag_memory.sh`)
- [ ] Build script ready (`./scripts/build_android_debug.sh`)
