#!/usr/bin/env python3
"""
Memory Profiler for Buildozer Builds
Monitors system memory and provides recommendations to avoid OOM errors.
"""
import os
import sys
import psutil
import json
from pathlib import Path

def get_memory_stats():
    """Get current memory statistics."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        "total_ram_gb": round(mem.total / (1024**3), 2),
        "available_ram_gb": round(mem.available / (1024**3), 2),
        "used_ram_gb": round(mem.used / (1024**3), 2),
        "ram_percent": mem.percent,
        "swap_total_gb": round(swap.total / (1024**3), 2),
        "swap_used_gb": round(swap.used / (1024**3), 2),
        "swap_percent": swap.percent
    }

def check_disk_space():
    """Check available disk space."""
    workspace = Path(__file__).parent.parent
    disk = psutil.disk_usage(str(workspace))
    
    return {
        "total_gb": round(disk.total / (1024**3), 2),
        "free_gb": round(disk.free / (1024**3), 2),
        "percent_used": disk.percent
    }

def analyze_buildozer_cache():
    """Analyze .buildozer cache size."""
    workspace = Path(__file__).parent.parent
    buildozer_dir = workspace / ".buildozer"
    
    if not buildozer_dir.exists():
        return {"exists": False, "size_mb": 0}
    
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(buildozer_dir):
        for file in files:
            try:
                file_path = Path(root) / file
                total_size += file_path.stat().st_size
                file_count += 1
            except (PermissionError, FileNotFoundError):
                pass
    
    return {
        "exists": True,
        "size_mb": round(total_size / (1024**2), 2),
        "size_gb": round(total_size / (1024**3), 2),
        "file_count": file_count
    }

def get_recommendations(mem_stats, disk_stats, cache_stats):
    """Provide recommendations based on current stats."""
    recommendations = []
    warnings = []
    
    # Memory checks
    if mem_stats["available_ram_gb"] < 2:
        warnings.append("⚠️  CRITICAL: Less than 2GB RAM available")
        recommendations.append("Close other applications before building")
        recommendations.append("Consider adding swap space")
    elif mem_stats["available_ram_gb"] < 4:
        warnings.append("⚠️  WARNING: Less than 4GB RAM available")
        recommendations.append("Close unnecessary applications")
    
    if mem_stats["ram_percent"] > 80:
        warnings.append("⚠️  WARNING: RAM usage above 80%")
        recommendations.append("Restart system or close applications")
    
    # Disk space checks
    if disk_stats["free_gb"] < 10:
        warnings.append("⚠️  CRITICAL: Less than 10GB disk space")
        recommendations.append("Clean up disk space before building")
        recommendations.append("Run clean_build script to remove old builds")
    elif disk_stats["free_gb"] < 20:
        warnings.append("⚠️  WARNING: Less than 20GB disk space")
        recommendations.append("Consider cleaning .buildozer cache")
    
    # Cache checks
    if cache_stats["exists"] and cache_stats["size_gb"] > 5:
        warnings.append(f"ℹ️  INFO: .buildozer cache is {cache_stats['size_gb']}GB")
        recommendations.append("Consider running clean_build.ps1 to reclaim space")
    
    return recommendations, warnings

def main():
    """Main profiler function."""
    print("=" * 60)
    print("🔍 MEMORY & DISK PROFILER FOR BUILDOZER")
    print("=" * 60)
    print()
    
    # Get stats
    mem_stats = get_memory_stats()
    disk_stats = check_disk_space()
    cache_stats = analyze_buildozer_cache()
    
    # Display Memory Info
    print("💾 MEMORY STATUS")
    print("-" * 60)
    print(f"Total RAM:      {mem_stats['total_ram_gb']} GB")
    print(f"Available RAM:  {mem_stats['available_ram_gb']} GB")
    print(f"Used RAM:       {mem_stats['used_ram_gb']} GB ({mem_stats['ram_percent']}%)")
    print(f"Swap Total:     {mem_stats['swap_total_gb']} GB")
    print(f"Swap Used:      {mem_stats['swap_used_gb']} GB ({mem_stats['swap_percent']}%)")
    print()
    
    # Display Disk Info
    print("💿 DISK STATUS")
    print("-" * 60)
    print(f"Total Space:    {disk_stats['total_gb']} GB")
    print(f"Free Space:     {disk_stats['free_gb']} GB")
    print(f"Used:           {disk_stats['percent_used']}%")
    print()
    
    # Display Cache Info
    print("📦 BUILDOZER CACHE")
    print("-" * 60)
    if cache_stats["exists"]:
        print(f"Cache Size:     {cache_stats['size_gb']} GB ({cache_stats['size_mb']} MB)")
        print(f"File Count:     {cache_stats['file_count']}")
    else:
        print("Cache Status:   No .buildozer directory found")
    print()
    
    # Get recommendations
    recommendations, warnings = get_recommendations(mem_stats, disk_stats, cache_stats)
    
    # Display warnings
    if warnings:
        print("⚠️  WARNINGS")
        print("-" * 60)
        for warning in warnings:
            print(warning)
        print()
    
    # Display recommendations
    if recommendations:
        print("📋 RECOMMENDATIONS")
        print("-" * 60)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print()
    else:
        print("✅ SYSTEM STATUS: GOOD")
        print("System has sufficient resources for building")
        print()
    
    # Build readiness assessment
    print("🎯 BUILD READINESS")
    print("-" * 60)
    
    can_build = True
    if mem_stats["available_ram_gb"] < 2 or disk_stats["free_gb"] < 10:
        can_build = False
        print("❌ NOT RECOMMENDED: System resources too low")
    elif mem_stats["available_ram_gb"] < 4 or disk_stats["free_gb"] < 20:
        print("⚠️  CAUTION: Build may succeed but monitor closely")
    else:
        print("✅ READY: System has adequate resources")
    
    print("=" * 60)
    
    return 0 if can_build else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
