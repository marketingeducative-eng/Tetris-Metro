#!/usr/bin/env python3
"""
Build Validator for Buildozer
Validates buildozer.spec configuration to prevent common OOM and build issues.
"""
import sys
import re
from pathlib import Path
import json

class BuildValidator:
    def __init__(self, spec_path):
        self.spec_path = Path(spec_path)
        self.errors = []
        self.warnings = []
        self.info = []
        self.config = {}
        
    def read_spec(self):
        """Read and parse buildozer.spec file."""
        if not self.spec_path.exists():
            self.errors.append(f"buildozer.spec not found at {self.spec_path}")
            return False
        
        with open(self.spec_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    self.config[key.strip()] = value.strip()
        
        return True
    
    def validate_memory_settings(self):
        """Validate memory-related settings."""
        print("🔍 Validating Memory Settings...")
        
        # Check gradle memory
        gradle_options = self.config.get('android.gradle_options', '')
        
        if 'Xmx' not in gradle_options:
            self.warnings.append("No Xmx (max heap) set in gradle_options")
            self.info.append("Recommended: android.gradle_options = -Xmx2048m -Xms512m")
        else:
            # Extract Xmx value
            match = re.search(r'-Xmx(\d+)([mMgG])', gradle_options)
            if match:
                size, unit = match.groups()
                size = int(size)
                if unit.lower() == 'm' and size < 1536:
                    self.warnings.append(f"Xmx={size}m may be too low (recommended: 2048m)")
                elif unit.lower() == 'm' and size > 4096:
                    self.warnings.append(f"Xmx={size}m may cause OOM on low-memory systems")
                else:
                    self.info.append(f"✓ Gradle heap size: {size}{unit}")
        
        # Check if using NDK (memory-intensive)
        ndk_path = self.config.get('android.ndk_path', '')
        if ndk_path:
            self.info.append("⚠️  NDK build detected - requires more memory")
    
    def validate_build_settings(self):
        """Validate general build settings."""
        print("🔍 Validating Build Settings...")
        
        # Check parallel builds
        accept_sdk_license = self.config.get('android.accept_sdk_license', 'False')
        if accept_sdk_license.lower() != 'true':
            self.warnings.append("android.accept_sdk_license not set to True")
        
        # Check API levels
        api_level = self.config.get('android.api', '')
        if api_level:
            try:
                api = int(api_level)
                if api < 21:
                    self.warnings.append(f"API level {api} is very old (consider >= 21)")
                elif api >= 21:
                    self.info.append(f"✓ API level: {api}")
            except ValueError:
                self.errors.append(f"Invalid API level: {api_level}")
        
        # Check minapi
        minapi = self.config.get('android.minapi', '')
        if minapi:
            try:
                min_api = int(minapi)
                if min_api < 21:
                    self.info.append(f"ℹ️  Min API {min_api} - consider 21+ for modern features")
            except ValueError:
                pass
    
    def validate_dependencies(self):
        """Validate requirements and dependencies."""
        print("🔍 Validating Dependencies...")
        
        requirements = self.config.get('requirements', '')
        if not requirements:
            self.warnings.append("No requirements specified")
            return
        
        req_list = [r.strip() for r in requirements.split(',')]
        self.info.append(f"✓ Found {len(req_list)} requirements")
        
        # Check for known memory-heavy libraries
        heavy_libs = ['numpy', 'scipy', 'pandas', 'matplotlib', 'opencv']
        found_heavy = [lib for lib in heavy_libs if lib in requirements.lower()]
        
        if found_heavy:
            self.warnings.append(f"Memory-intensive libraries detected: {', '.join(found_heavy)}")
            self.info.append("Consider pre-compiling or using lighter alternatives")
    
    def validate_assets(self):
        """Validate source.include_exts and assets."""
        print("🔍 Validating Assets Configuration...")
        
        include_exts = self.config.get('source.include_exts', '')
        if include_exts:
            exts = [e.strip() for e in include_exts.split(',')]
            self.info.append(f"✓ Including {len(exts)} file types: {', '.join(exts[:5])}...")
        
        # Check for potential large files
        if 'mp4' in include_exts or 'avi' in include_exts or 'mov' in include_exts:
            self.warnings.append("Video files in include_exts - ensure they're compressed")
        
        if 'wav' in include_exts:
            self.warnings.append("WAV files detected - consider converting to OGG/MP3")
    
    def validate_permissions(self):
        """Validate Android permissions."""
        print("🔍 Validating Permissions...")
        
        permissions = self.config.get('android.permissions', '')
        if permissions:
            perm_list = [p.strip() for p in permissions.split(',')]
            self.info.append(f"✓ {len(perm_list)} permissions requested")
            
            # Check for excessive permissions
            if len(perm_list) > 10:
                self.warnings.append(f"Many permissions ({len(perm_list)}) - may affect approval")
    
    def generate_report(self):
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("📊 BUILD VALIDATION REPORT")
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
        print("🎯 VALIDATION STATUS")
        print("-" * 60)
        if self.errors:
            print("❌ FAILED: Fix errors before building")
            result = False
        elif self.warnings:
            print("⚠️  PASSED WITH WARNINGS: Review issues before building")
            result = True
        else:
            print("✅ PASSED: Configuration looks good")
            result = True
        
        print("=" * 60)
        return result

def main():
    """Main validation function."""
    workspace = Path(__file__).parent.parent
    spec_path = workspace / "buildozer.spec"
    
    print("=" * 60)
    print("✅ BUILDOZER CONFIGURATION VALIDATOR")
    print("=" * 60)
    print(f"Checking: {spec_path}")
    print()
    
    validator = BuildValidator(spec_path)
    
    if not validator.read_spec():
        print("❌ Failed to read buildozer.spec")
        return 1
    
    # Run all validations
    validator.validate_memory_settings()
    validator.validate_build_settings()
    validator.validate_dependencies()
    validator.validate_assets()
    validator.validate_permissions()
    
    # Generate report
    result = validator.generate_report()
    
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
