# Clean Buildozer Cache and Build Artifacts
# Helps resolve build issues and OOM by removing stale cache

param(
    [switch]$DeepClean,
    [switch]$KeepDownloads,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "🧹 BUILDOZER CACHE CLEANER" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

$totalFreed = 0

function Remove-SafePath {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        try {
            $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
                     Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            
            Write-Host "  📁 $Description" -ForegroundColor Cyan
            Write-Host "     Path: $Path" -ForegroundColor Gray
            Write-Host "     Size: $sizeMB MB" -ForegroundColor Gray
            
            if (-not $DryRun) {
                Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
                Write-Host "     ✅ Deleted" -ForegroundColor Green
                $script:totalFreed += $sizeMB
            } else {
                Write-Host "     [DRY RUN] Would delete" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "     ⚠️  Could not delete: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⏭️  $Description - Not found (already clean)" -ForegroundColor Gray
    }
    Write-Host ""
}

Push-Location $WorkspaceRoot

Write-Host "🔍 Scanning for cleanable cache..." -ForegroundColor Cyan
Write-Host ""

# 1. Python cache
Write-Host "1️⃣  Python Cache Files" -ForegroundColor Yellow
Write-Host "-" * 60

$pycacheDirs = Get-ChildItem -Path $WorkspaceRoot -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue
$pycFiles = Get-ChildItem -Path $WorkspaceRoot -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue

if ($pycacheDirs -or $pycFiles) {
    $totalSize = 0
    $totalSize += ($pycacheDirs | ForEach-Object { 
        (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue | 
         Measure-Object -Property Length -Sum).Sum 
    } | Measure-Object -Sum).Sum
    
    $totalSize += ($pycFiles | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($totalSize / 1MB, 2)
    
    Write-Host "  Found $($pycacheDirs.Count) __pycache__ dirs and $($pycFiles.Count) .pyc files" -ForegroundColor Cyan
    Write-Host "  Total size: $sizeMB MB" -ForegroundColor Gray
    
    if (-not $DryRun) {
        $pycacheDirs | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        $pycFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ Cleaned" -ForegroundColor Green
        $script:totalFreed += $sizeMB
    } else {
        Write-Host "  [DRY RUN] Would clean" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✅ No Python cache found" -ForegroundColor Green
}
Write-Host ""

# 2. Buildozer build artifacts
Write-Host "2️⃣  Buildozer Build Artifacts" -ForegroundColor Yellow
Write-Host "-" * 60

Remove-SafePath "$WorkspaceRoot\.buildozer\android\platform\build-*\build" "Build intermediates"
Remove-SafePath "$WorkspaceRoot\.buildozer\android\platform\build-*\dists\*\.gradle" "Gradle cache"
Remove-SafePath "$WorkspaceRoot\.buildozer\android\app" "App build cache"

# 3. Deep clean (optional)
if ($DeepClean) {
    Write-Host "3️⃣  Deep Clean (SDK/NDK kept, everything else removed)" -ForegroundColor Yellow
    Write-Host "-" * 60
    
    if (-not $KeepDownloads) {
        Remove-SafePath "$WorkspaceRoot\.buildozer\android\platform\build-*\packages" "Python packages"
    }
    
    # Remove entire platform except SDK/NDK
    $buildDirs = Get-ChildItem -Path "$WorkspaceRoot\.buildozer\android\platform" -Directory -Filter "build-*" -ErrorAction SilentlyContinue
    
    foreach ($buildDir in $buildDirs) {
        $dists = Join-Path $buildDir.FullName "dists"
        if (Test-Path $dists) {
            Remove-SafePath $dists "Distribution $($buildDir.Name)"
        }
    }
    
} else {
    Write-Host "3️⃣  Deep Clean: SKIPPED (use -DeepClean to enable)" -ForegroundColor Gray
    Write-Host "   Deep clean removes all build artifacts except SDK/NDK" -ForegroundColor DarkGray
    Write-Host ""
}

# 4. Logs
Write-Host "4️⃣  Build Logs" -ForegroundColor Yellow
Write-Host "-" * 60

$logFiles = Get-ChildItem -Path "$WorkspaceRoot\.buildozer" -File -Recurse -Include "*.log" -ErrorAction SilentlyContinue

if ($logFiles) {
    $logSize = ($logFiles | Measure-Object -Property Length -Sum).Sum
    $logSizeMB = [math]::Round($logSize / 1MB, 2)
    
    Write-Host "  Found $($logFiles.Count) log files ($logSizeMB MB)" -ForegroundColor Cyan
    
    if (-not $DryRun) {
        $logFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  ✅ Cleaned" -ForegroundColor Green
        $script:totalFreed += $logSizeMB
    } else {
        Write-Host "  [DRY RUN] Would clean" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✅ No log files found" -ForegroundColor Green
}
Write-Host ""

# 5. Workspace bin/ (if exists)
if (Test-Path "$WorkspaceRoot\bin") {
    Write-Host "5️⃣  Workspace bin/" -ForegroundColor Yellow
    Write-Host "-" * 60
    Remove-SafePath "$WorkspaceRoot\bin" "Local bin directory"
}

# Summary
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "📊 CLEANUP SUMMARY" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN: No files were actually deleted" -ForegroundColor Yellow
} else {
    Write-Host "✅ Total space freed: $totalFreed MB" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  • Run: python tools\build_validator.py" -ForegroundColor Gray
    Write-Host "  • Then: .\scripts\build_android.ps1" -ForegroundColor Gray
}

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan

Pop-Location
