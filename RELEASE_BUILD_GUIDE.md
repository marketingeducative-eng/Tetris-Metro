# GitHub Actions Release Build - Manual Execution Guide

## Overview

The **Android Release Build workflow** (`android-release.yml`) allows manual builds of release and debug APKs with custom version names.

## How to Trigger

### Method 1: GitHub Web UI (Recommended)

1. Go to your repository on GitHub
2. Click **"Actions"** tab
3. Select **"Android Release Build (Manual)"** from the left sidebar
4. Click **"Run workflow"** button (top right)
5. Fill in the inputs:
   - **version_name**: Enter version (e.g., `1.0.0`, `1.1.0-beta`, `2.0.0-rc1`)
   - **build_type**: Select from dropdown (`debug` or `release`, defaults to `release`)
6. Click **"Run workflow"** button
7. Monitor progress in the workflow run

### Method 2: GitHub CLI

```bash
gh workflow run android-release.yml \
  -f version_name="1.0.0" \
  -f build_type="release"
```

### Method 3: Direct API

```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/android-release.yml/dispatches \
  -d '{
    "ref":"main",
    "inputs":{
      "version_name":"1.0.0",
      "build_type":"release"
    }
  }'
```

## Workflow Behavior

### Inputs

| Input | Type | Required | Default | Example |
|-------|------|----------|---------|---------|
| `version_name` | String | ✅ Yes | — | `1.0.0`, `1.1.0-beta`, `2.0.0-rc1` |
| `build_type` | Choice | ✅ Yes | `release` | `debug` or `release` |

### Process

1. **Checkout** code from `main` branch
2. **Install** system dependencies and buildozer
3. **Update** `buildozer.spec` version **temporarily** (not committed to repo)
4. **Build** APK/AAB based on `build_type`
   - `debug`: outputs `.apk` 
   - `release`: outputs `.aab` (app bundle) and `.apk` (if configured)
5. **Upload** artifacts with naming convention:
   - `proxima-parada-{version_name}-{build_type}/{artifact}`
   - Example: `proxima-parada-1.0.0-release/`
6. **Generate** release notes with build metadata

### Key Features

- ✅ **No repo changes**: Version update is temporary (runner workspace only)
- ✅ **Flexible versions**: Use any semantic version format
- ✅ **Cached builds**: Reuses pip, buildozer, gradle caches for speed
- ✅ **Metadata tracking**: Includes commit hash, timestamp, run number
- ✅ **Long retention**: Artifacts kept for 90 days

## Artifacts Generated

After successful build, download from **"Actions" → Run → Artifacts**:

### For `release` build type
- `proxima-parada-1.0.0-release/` (app bundle and/or APK)
- `release-notes-1.0.0/` (build metadata)

### For `debug` build type
- `proxima-parada-1.0.0-debug/` (debug APK with symbols)
- `release-notes-1.0.0/` (build metadata)

### Release Notes Contents

```
Build Metadata
==============
Version: 1.0.0
Build Type: release
Built At: 2026-03-01 14:30:45 UTC
Commit: a1b2c3d4e5f6...
Branch: refs/heads/main
Workflow: Android Release Build (Manual)
Run: 42
```

## Installation on Device

### Debug APK
```bash
adb install bin/proxima-parada-debug.apk
```

### Release APK (if building with `release` type and APK output is configured)
```bash
adb install bin/proxima-parada-release.apk
```

## Troubleshooting

### Build fails: "No APK or AAB file found"
- Check logs for compilation errors
- Verify `buildozer.spec` is valid
- Ensure all required assets exist

### Version not updating in buildozer.spec
- Check the "Update version in buildozer.spec" step in logs
- Verify version format (e.g., no spaces or special chars)

### Artifacts not downloading
- Ensure workflow completed successfully (green checkmark)
- Check artifact retention hasn't expired (90 days)
- Use GitHub CLI: `gh run download RUN_ID -n artifact-name`

## Examples

### Release version 1.0.0
```
version_name: "1.0.0"
build_type: "release"
→ Produces: proxima-parada-1.0.0-release/{artifact}.aab
```

### Beta test version
```
version_name: "1.1.0-beta.1"
build_type: "debug"
→ Produces: proxima-parada-1.1.0-beta.1-debug/{artifact}.apk
```

### Release candidate
```
version_name: "2.0.0-rc1"
build_type: "release"
→ Produces: proxima-parada-2.0.0-rc1-release/{artifact}.aab
```

## Important Notes

⚠️ **Version Persistence**: Version changes are NOT committed to GitHub repo  
⚠️ **Branch Target**: Always builds from `main` branch  
✅ **Safe to Retry**: Can run workflow multiple times with different versions  
✅ **No Secrets Needed**: Only needs repository access (public or internal)

## Workflow File

Configuration: `.github/workflows/android-release.yml`

Key steps:
- System dependencies: `build-essential`, `openjdk-17-jdk`, etc.
- Cache strategy: pip, buildozer, gradle (speeds up builds ~3-5x)
- Post-build validation: Checks APK/AAB existence before upload
- Metadata capture: Commit hash, timestamp, workflow run number

---

**Last Updated**: 2026-03-01  
**Workflow File**: [.github/workflows/android-release.yml](.github/workflows/android-release.yml)
