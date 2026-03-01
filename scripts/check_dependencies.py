#!/usr/bin/env python3
"""
Dependency Checker for Buildozer Builds
Validates Python environment, Buildozer, and Android SDK/NDK setup.
"""
import sys
import subprocess
import shutil
from pathlib import Path
import platform

class DependencyChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def check_python(self):
        """Check Python version and installation."""
        print("🐍 Checking Python...")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3:
            self.errors.append("Python 3.x required")
        elif version.minor < 7:
            self.warnings.append(f"Python {version_str} is old (3.8+ recommended)")
        else:
            self.info.append(f"✓ Python {version_str}")
        
        # Check pip
        try:
            import pip
            self.info.append(f"✓ pip installed")
        except ImportError:
            self.errors.append("pip not found")
    
    def check_buildozer(self):
        """Check if buildozer is installed and working."""
        print("🔨 Checking Buildozer...")
        
        if not shutil.which('buildozer'):
            self.errors.append("buildozer not found in PATH")
            self.info.append("Install: pip install buildozer")
            return
        
        try:
            result = subprocess.run(
                ['buildozer', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.info.append(f"✓ Buildozer {version}")
            else:
                self.warnings.append("buildozer found but version check failed")
        except subprocess.TimeoutExpired:
            self.warnings.append("buildozer command timed out")
        except Exception as e:
            self.warnings.append(f"buildozer check failed: {e}")
    
    def check_cython(self):
        """Check Cython installation."""
        print("⚙️  Checking Cython...")
        
        try:
            import Cython
            self.info.append(f"✓ Cython {Cython.__version__}")
        except ImportError:
            self.warnings.append("Cython not installed (may be needed)")
            self.info.append("Install: pip install cython")
    
    def check_build_essentials(self):
        """Check for build essentials."""
        print("🔧 Checking build tools...")
        
        if platform.system() == 'Windows':
            # Check for Git
            if shutil.which('git'):
                self.info.append("✓ Git installed")
            else:
                self.warnings.append("Git not found (recommended)")
            
            # Check for Java
            if shutil.which('java'):
                try:
                    result = subprocess.run(
                        ['java', '-version'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    # Java version output goes to stderr
                    version_output = result.stderr.split('\n')[0]
                    self.info.append(f"✓ Java: {version_output}")
                except:
                    self.warnings.append("Java found but version check failed")
            else:
                self.warnings.append("Java not found (required by Gradle)")
                self.info.append("Install: OpenJDK 11 or newer")
        
        else:  # Linux/Mac
            required_tools = ['git', 'unzip', 'patch']
            for tool in required_tools:
                if shutil.which(tool):
                    self.info.append(f"✓ {tool} installed")
                else:
                    self.errors.append(f"{tool} not found")
    
    def check_buildozer_spec(self):
        """Check if buildozer.spec exists."""
        print("📄 Checking buildozer.spec...")
        
        workspace = Path(__file__).parent.parent
        spec_path = workspace / "buildozer.spec"
        
        if spec_path.exists():
            self.info.append(f"✓ buildozer.spec found")
            
            # Quick parse for package name
            with open(spec_path, 'r') as f:
                for line in f:
                    if line.startswith('package.name'):
                        pkg_name = line.split('=')[1].strip()
                        self.info.append(f"  Package: {pkg_name}")
                        break
        else:
            self.errors.append("buildozer.spec not found")
            self.info.append("Run: buildozer init")
    
    def check_required_packages(self):
        """Check for required Python packages."""
        print("📦 Checking Python packages...")
        
        required = {
            'kivy': 'Main framework',
            'plyer': 'Platform APIs',
            'android': 'Android bindings (optional)'
        }
        
        for package, description in required.items():
            try:
                __import__(package)
                self.info.append(f"✓ {package} - {description}")
            except ImportError:
                if package == 'android':
                    # android module only available on Android
                    pass
                else:
                    self.warnings.append(f"{package} not installed - {description}")
    
    def check_disk_space(self):
        """Check available disk space."""
        print("💿 Checking disk space...")
        
        try:
            import psutil
            workspace = Path(__file__).parent.parent
            disk = psutil.disk_usage(str(workspace))
            
            free_gb = disk.free / (1024**3)
            
            if free_gb < 10:
                self.warnings.append(f"Low disk space: {free_gb:.1f}GB free")
                self.info.append("Recommended: 20GB+ for Android builds")
            else:
                self.info.append(f"✓ Disk space: {free_gb:.1f}GB free")
        except ImportError:
            self.warnings.append("psutil not installed - cannot check disk space")
            self.info.append("Install: pip install psutil")
    
    def generate_report(self):
        """Generate final report."""
        print("\n" + "=" * 60)
        print("📊 DEPENDENCY CHECK REPORT")
        print("=" * 60)
        print()
        
        if self.errors:
            print("❌ ERRORS (Must Fix)")
            print("-" * 60)
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS (Should Review)")
            print("-" * 60)
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")
            print()
        
        if self.info:
            print("ℹ️  INFORMATION")
            print("-" * 60)
            for info_item in self.info:
                print(f"  {info_item}")
            print()
        
        # Overall status
        print("🎯 STATUS")
        print("-" * 60)
        if self.errors:
            print("❌ NOT READY: Fix errors before building")
            result = False
        elif self.warnings:
            print("⚠️  READY WITH WARNINGS: Review issues")
            result = True
        else:
            print("✅ READY: All dependencies OK")
            result = True
        
        print("=" * 60)
        return result

def main():
    """Main checker function."""
    print("=" * 60)
    print("🔍 BUILD ENVIRONMENT CHECKER")
    print("=" * 60)
    print()
    
    checker = DependencyChecker()
    
    # Run all checks
    checker.check_python()
    checker.check_buildozer()
    checker.check_cython()
    checker.check_build_essentials()
    checker.check_buildozer_spec()
    checker.check_required_packages()
    checker.check_disk_space()
    
    # Generate report
    result = checker.generate_report()
    
    return 0 if result else 1

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
