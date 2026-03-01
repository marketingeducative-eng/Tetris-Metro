# VS Code Workflow - Tetris Metro Android Build

## Pre-Build Checklist

1. **Check System Memory**
   ```
   Ctrl+Shift+P → Run Task → "WSL: Memory Check"
   ```
   - Available memory > 2GB recommended
   - If < 1GB: close other apps or wait

2. **Clean Old Build Artifacts** (optional but recommended)
   ```
   Ctrl+Shift+P → Run Task → "WSL: Clean Build Artifacts"
   ```
   - Frees disk space and improves build speed
   - Confirms each deletion interactively

3. **Open New Terminal** (integrated terminal)
   ```
   Ctrl+` (backtick)
   ```
   - Confirms you're in WSL (check prompt for `ubuntu` or `WSL:`)
   - Verify with: `echo $SHELL` → should show `/bin/bash`

---

## Building from VS Code

### Option A: Via Task (Recommended)
```
Ctrl+Shift+P → Run Task → "Android: Build Debug (safe log)"
```
- Displays output in dedicated panel (won't clutter editor)
- Auto-saves logs to `logs/buildozer_debug_*.log`
- Preserves exit code

### Option B: Via Terminal
```bash
./scripts/build_android_debug.sh
```
- Direct control and real-time feedback
- Same logging as Option A
- Can interrupt with `Ctrl+C`

### Option C: Direct Buildozer (Emergency)
```bash
buildozer -v android debug
```
- Requires manual environment setup
- Less logging (useful for debugging buildozer issues)

---

## Post-Build

**View Last Build Log**
```
Ctrl+Shift+P → Run Task → "Android: Tail Last Build Log"
```
- Shows last 200 lines of most recent build
- Quick error inspection

---

## VS Code Memory Issues

### Signs of OOM Risk
- ✗ Sluggish editor, input lag
- ✗ Red/yellow memory indicator (bottom bar)
- ✗ Extensions sidebar hangs
- ✗ Terminal freezes

### Immediate Actions
1. **Disable extensions temporarily**
   ```
   Ctrl+Shift+P → Extensions: Disable All Extensions (Workspace)
   ```
   - Or: `code --disable-extensions .`

2. **Stop file watching** (already optimized, but check)
   ```
   Ctrl+Shift+P → Stop File Watcher
   ```

3. **Close unused tabs and sidebars**
   - Explorer panel
   - Source Control
   - Extensions panel

4. **Restart VS Code** (nuclear option)
   ```bash
   pkill -f "code|electron"
   ```

### If Still High Memory
- Increase WSL memory limit (Windows `.wslconfig`):
  ```ini
  [wsl2]
  memory=4GB
  swap=2GB
  ```

---

## Terminal vs VS Code Builds

| Aspect | Terminal | VS Code Task |
|--------|----------|-------------|
| **Overhead** | Minimal | ~50MB (Electron) |
| **Logging** | Manual redirection | Auto-saved |
| **Interruption** | `Ctrl+C` direct | Panel close or `Ctrl+Shift+P` stop |
| **Real-time** | Full output | Filtered by panel settings |
| **Best for** | Low-memory systems | Development workflow |

**Recommendation**: Use **Terminal** for final builds on memory-constrained systems.

---

## OOM Prevention Best Practices

### Before Build
- [ ] Close VS Code → Terminal only (saves ~300MB)
- [ ] Close other applications (browsers, IDEs, etc.)
- [ ] Run `./tools/diag_memory.sh` to baseline memory
- [ ] Clean artifacts: `./scripts/clean_build_artifacts.sh`

### During Build
- [ ] Don't edit files while building
- [ ] Don't expand file explorer (forces re-indexing)
- [ ] Avoid Git operations (use terminal instead)
- [ ] Monitor via `watch -n 1 free -h` in separate terminal

### Build Configuration (buildozer.spec)
- Ensure `android.gradle_options = -Xmx2048m` (max heap)
- Don't increase NDK parallelism beyond 2 (`-j2`)
- Use `android.ndk_api = 21` (not latest)

### After Build
- Clean intermediate files: `./scripts/clean_build_artifacts.sh`
- Review logs for warnings: `./scripts/build_android_debug.sh` then "Android: Tail Last Build Log"
- Archive successful APK to external drive

---

## Quick Reference

```bash
# All-in-one pre-build + build (terminal)
./tools/diag_memory.sh && \
./scripts/clean_build_artifacts.sh && \
./scripts/build_android_debug.sh

# Emergency: low memory
code --disable-extensions . && \
./scripts/build_android_debug.sh

# Check specific errors
tail -n 500 logs/buildozer_debug_*.log | grep error
```

---

**Last Updated:** 2026-02-28  
**Environment:** WSL2 Ubuntu 22.04+ | VS Code 1.x+
