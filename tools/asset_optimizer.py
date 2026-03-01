#!/usr/bin/env python3
"""
Asset Optimizer for Buildozer Builds
Analyzes and provides recommendations for optimizing game assets to reduce memory usage.
"""
import sys
from pathlib import Path
from PIL import Image
import os

class AssetOptimizer:
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.recommendations = []
        self.stats = {
            "total_images": 0,
            "total_audio": 0,
            "total_size_mb": 0,
            "large_images": [],
            "uncompressed_audio": []
        }
    
    def scan_images(self):
        """Scan image files and check for optimization opportunities."""
        print("🖼️  Scanning images...")
        
        image_exts = ['.png', '.jpg', '.jpeg', '.bmp']
        assets_dirs = [
            self.workspace / 'assets',
            self.workspace / 'images',
            self.workspace / 'graphics'
        ]
        
        for assets_dir in assets_dirs:
            if not assets_dir.exists():
                continue
            
            for img_path in assets_dir.rglob('*'):
                if img_path.suffix.lower() in image_exts:
                    self.stats["total_images"] += 1
                    self._check_image(img_path)
    
    def _check_image(self, img_path):
        """Check individual image for optimization."""
        try:
            size_mb = img_path.stat().st_size / (1024 * 1024)
            self.stats["total_size_mb"] += size_mb
            
            # Check if image is too large
            if size_mb > 0.5:  # 500KB threshold
                try:
                    with Image.open(img_path) as img:
                        width, height = img.size
                        mode = img.mode
                        
                        issue = {
                            "path": str(img_path.relative_to(self.workspace)),
                            "size_mb": round(size_mb, 2),
                            "dimensions": f"{width}x{height}",
                            "mode": mode
                        }
                        
                        # Specific recommendations
                        if size_mb > 2:
                            issue["severity"] = "high"
                            issue["recommendation"] = "Critical: Reduce resolution or compress"
                        elif size_mb > 1:
                            issue["severity"] = "medium"
                            issue["recommendation"] = "Consider resizing or optimizing"
                        else:
                            issue["severity"] = "low"
                            issue["recommendation"] = "Minor optimization possible"
                        
                        # Check if 32-bit when could be 8-bit
                        if mode == 'RGBA' and width * height > 512 * 512:
                            issue["alpha_warning"] = "Large RGBA image - check if alpha needed"
                        
                        self.stats["large_images"].append(issue)
                        
                except Exception as e:
                    print(f"  Warning: Could not analyze {img_path.name}: {e}")
        
        except Exception as e:
            pass
    
    def scan_audio(self):
        """Scan audio files for optimization opportunities."""
        print("🔊 Scanning audio files...")
        
        audio_exts = {
            '.wav': 'uncompressed',
            '.ogg': 'compressed',
            '.mp3': 'compressed',
            '.m4a': 'compressed'
        }
        
        assets_dirs = [
            self.workspace / 'assets',
            self.workspace / 'audio',
            self.workspace / 'sounds',
            self.workspace / 'music'
        ]
        
        for assets_dir in assets_dirs:
            if not assets_dir.exists():
                continue
            
            for audio_path in assets_dir.rglob('*'):
                if audio_path.suffix.lower() in audio_exts:
                    self.stats["total_audio"] += 1
                    self._check_audio(audio_path, audio_exts)
    
    def _check_audio(self, audio_path, audio_exts):
        """Check individual audio file."""
        try:
            size_mb = audio_path.stat().st_size / (1024 * 1024)
            self.stats["total_size_mb"] += size_mb
            
            ext = audio_path.suffix.lower()
            compression = audio_exts.get(ext, 'unknown')
            
            # Flag uncompressed audio
            if compression == 'uncompressed':
                issue = {
                    "path": str(audio_path.relative_to(self.workspace)),
                    "size_mb": round(size_mb, 2),
                    "type": ext,
                    "recommendation": "Convert to OGG for better compression"
                }
                self.stats["uncompressed_audio"].append(issue)
            
            # Flag very large compressed audio
            elif size_mb > 5:
                issue = {
                    "path": str(audio_path.relative_to(self.workspace)),
                    "size_mb": round(size_mb, 2),
                    "type": ext,
                    "recommendation": "Very large audio file - reduce bitrate or duration"
                }
                self.stats["uncompressed_audio"].append(issue)
        
        except Exception:
            pass
    
    def generate_report(self):
        """Generate optimization report."""
        print("\n" + "=" * 60)
        print("📊 ASSET OPTIMIZATION REPORT")
        print("=" * 60)
        print()
        
        # Summary
        print("📈 SUMMARY")
        print("-" * 60)
        print(f"Total Images:    {self.stats['total_images']}")
        print(f"Total Audio:     {self.stats['total_audio']}")
        print(f"Total Size:      {round(self.stats['total_size_mb'], 2)} MB")
        print()
        
        # Large images
        if self.stats["large_images"]:
            print("🖼️  LARGE IMAGES (Optimization Recommended)")
            print("-" * 60)
            
            # Sort by size
            sorted_images = sorted(
                self.stats["large_images"],
                key=lambda x: x["size_mb"],
                reverse=True
            )
            
            for i, img in enumerate(sorted_images[:10], 1):  # Top 10
                severity_icon = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }
                icon = severity_icon.get(img["severity"], "⚪")
                
                print(f"{i}. {icon} {img['path']}")
                print(f"   Size: {img['size_mb']} MB | {img['dimensions']} | {img['mode']}")
                print(f"   → {img['recommendation']}")
                if "alpha_warning" in img:
                    print(f"   ⚠️  {img['alpha_warning']}")
                print()
            
            if len(sorted_images) > 10:
                print(f"   ... and {len(sorted_images) - 10} more images")
                print()
        
        # Audio files
        if self.stats["uncompressed_audio"]:
            print("🔊 AUDIO FILES (Optimization Needed)")
            print("-" * 60)
            
            for i, audio in enumerate(self.stats["uncompressed_audio"], 1):
                print(f"{i}. {audio['path']}")
                print(f"   Size: {audio['size_mb']} MB | {audio['type']}")
                print(f"   → {audio['recommendation']}")
                print()
        
        # Recommendations
        print("💡 OPTIMIZATION RECOMMENDATIONS")
        print("-" * 60)
        
        recommendations = []
        
        if self.stats["large_images"]:
            recommendations.append("1. Resize large images to actual display size")
            recommendations.append("2. Convert RGBA to RGB if alpha not needed")
            recommendations.append("3. Use PNG compression tools (pngquant, oxipng)")
            recommendations.append("4. Consider WebP format for better compression")
        
        if self.stats["uncompressed_audio"]:
            recommendations.append("5. Convert WAV files to OGG format")
            recommendations.append("6. Use lower bitrate for background music (96-128 kbps)")
            recommendations.append("7. Keep sound effects short and compressed")
        
        if not recommendations:
            recommendations.append("✅ Assets are reasonably optimized")
        
        for rec in recommendations:
            print(f"  {rec}")
        
        print()
        print("=" * 60)
        
        # Return status
        has_issues = bool(self.stats["large_images"] or self.stats["uncompressed_audio"])
        return 0 if not has_issues else 1

def main():
    """Main optimizer function."""
    workspace = Path(__file__).parent.parent
    
    print("=" * 60)
    print("🎨 ASSET OPTIMIZER FOR ANDROID BUILD")
    print("=" * 60)
    print(f"Workspace: {workspace}")
    print()
    
    optimizer = AssetOptimizer(workspace)
    
    try:
        optimizer.scan_images()
        optimizer.scan_audio()
        return optimizer.generate_report()
    except ImportError as e:
        if 'PIL' in str(e):
            print("❌ ERROR: Pillow not installed")
            print("Install with: pip install Pillow")
            return 1
        raise

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
