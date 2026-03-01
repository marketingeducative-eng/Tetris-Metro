# Build Android APK with OOM Prevention
# This script implements memory-safe build practices for Buildozer

param(
    [switch]$Clean,
    [switch]$Release,
    [switch]$SkipValidation,
    [string]$BuildozerSpec = "buildozer.spec"
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "🏗️  TETRIS METRO - ANDROID BUILD SCRIPT (OOM-Safe)" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Step 1: Pre-build validation
if (-not $SkipValidation) {
    Write-Host "📋 Step 1/6: Validating build configuration..." -ForegroundColor Cyan
    python "$WorkspaceRoot\tools\build_validator.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build validation failed. Fix errors and try again." -ForegroundColor Red
        Write-Host "   Use -SkipValidation to bypass (not recommended)" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Validation passed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⚠️  Skipping validation (as requested)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 2: Memory check
Write-Host "💾 Step 2/6: Checking system memory..." -ForegroundColor Cyan
python "$WorkspaceRoot\tools\memory_profiler.py"
$memoryStatus = $LASTEXITCODE
if ($memoryStatus -ne 0) {
    Write-Host ""
    Write-Host "⚠️  WARNING: System memory is low" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y') {
        Write-Host "Build cancelled by user" -ForegroundColor Yellow
        exit 0
    }
}
Write-Host ""

# Step 3: Clean build (if requested)
if ($Clean) {
    Write-Host "🧹 Step 3/6: Cleaning build cache..." -ForegroundColor Cyan
    & "$WorkspaceRoot\scripts\clean_build.ps1"
    Write-Host "✅ Clean completed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⏭️  Step 3/6: Skipping clean (use -Clean to enable)" -ForegroundColor Gray
    Write-Host ""
}

# Step 4: Set memory-safe environment variables
Write-Host "⚙️  Step 4/6: Configuring build environment..." -ForegroundColor Cyan

# Java/Gradle memory settings
$env:GRADLE_OPTS = "-Xmx2048m -Xms512m -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError"
$env:_JAVA_OPTIONS = "-Xmx2048m -Xms512m"

# Python memory optimization
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONHASHSEED = "0"  # Deterministic builds

# Buildozer settings
$env:BUILDOZER_WARN_ON_ROOT = "0"
$env:USE_SDK_WRAPPER = "1"

# Build output optimization
$env:TERM = "dumb"  # Prevent colored output issues

Write-Host "  ✓ GRADLE_OPTS: $env:GRADLE_OPTS" -ForegroundColor Gray
Write-Host "  ✓ Memory limits: 2GB max heap" -ForegroundColor Gray
Write-Host "✅ Environment configured" -ForegroundColor Green
Write-Host ""

# Step 5: Build
Write-Host "🔨 Step 5/6: Starting Buildozer build..." -ForegroundColor Cyan
Write-Host "  This may take 15-45 minutes depending on system" -ForegroundColor Gray
Write-Host ""

Push-Location $WorkspaceRoot

try {
    # Determine build mode
    $buildMode = if ($Release) { "release" } else { "debug" }
    
    Write-Host "Building in $buildMode mode..." -ForegroundColor Yellow
    Write-Host ""
    
    # Run buildozer with memory monitoring
    $buildStartTime = Get-Date
    
    if ($Release) {
        buildozer android release
    } else {
        buildozer android debug
    }
    
    $buildResult = $LASTEXITCODE
    $buildEndTime = Get-Date
    $buildDuration = $buildEndTime - $buildStartTime
    
    Write-Host ""
    
    if ($buildResult -eq 0) {
        Write-Host "✅ Build completed successfully!" -ForegroundColor Green
        Write-Host "   Duration: $($buildDuration.ToString('mm\:ss'))" -ForegroundColor Gray
        Write-Host ""
        
        # Step 6: Locate APK
        Write-Host "📦 Step 6/6: Locating APK..." -ForegroundColor Cyan
        
        $apkPattern = if ($Release) { "*-release*.apk" } else { "*-debug*.apk" }
        $apkPath = Get-ChildItem -Path "$WorkspaceRoot\.buildozer\android\platform\build-*\dists\*\build\outputs\apk" -Filter $apkPattern -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        
        if ($apkPath) {
            $apkSize = [math]::Round($apkPath.Length / 1MB, 2)
            Write-Host "✅ APK found: $($apkPath.FullName)" -ForegroundColor Green
            Write-Host "   Size: $apkSize MB" -ForegroundColor Gray
            
            # Copy to workspace root for easy access
            $outputName = "tetris-metro-$buildMode.apk"
            Copy-Item $apkPath.FullName "$WorkspaceRoot\$outputName" -Force
            Write-Host "   Copied to: $outputName" -ForegroundColor Green
        } else {
            Write-Host "⚠️  APK built but location could not be determined" -ForegroundColor Yellow
            Write-Host "   Check .buildozer/android/platform/build-*/dists/" -ForegroundColor Gray
        }
        
    } else {
        Write-Host "❌ Build failed with exit code $buildResult" -ForegroundColor Red
        Write-Host ""
        Write-Host "Common solutions:" -ForegroundColor Yellow
        Write-Host "  1. Run: .\scripts\clean_build.ps1" -ForegroundColor Gray
        Write-Host "  2. Check: python .\tools\memory_profiler.py" -ForegroundColor Gray
        Write-Host "  3. Review: buildozer.spec configuration" -ForegroundColor Gray
        Write-Host "  4. See: .\docs\OOM_TROUBLESHOOTING.md" -ForegroundColor Gray
    }
    
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Build script completed" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

exit $buildResult
