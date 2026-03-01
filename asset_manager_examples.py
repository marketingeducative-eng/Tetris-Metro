"""
Asset Manager Integration Examples

This file demonstrates practical usage patterns for integrating the
asset management system with your Kivy game code.

Copy patterns from here into your game code.
"""

# ============================================================================
# EXAMPLE 1: Loading Sounds
# ============================================================================

from kivy.core.audio import SoundLoader
from asset_manager import get_asset_path


class SoundManager:
    """Manages game sounds using the asset manager."""
    
    def __init__(self):
        self.sounds = {}
    
    def load_sound(self, sound_name: str, relative_path: str):
        """
        Load a sound file safely.
        
        Args:
            sound_name: Internal name (e.g., 'bell', 'error')
            relative_path: Path relative to project root (e.g., 'data/sounds/bell.wav')
        """
        try:
            path = get_asset_path(relative_path)
            sound = SoundLoader.load(path)
            self.sounds[sound_name] = sound
            print(f"✓ Loaded sound: {sound_name}")
            return sound
        except RuntimeError as e:
            print(f"❌ Failed to load sound {sound_name}: {e}")
            return None
    
    def play_sound(self, sound_name: str):
        """Play a previously loaded sound."""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            print(f"Warning: Sound '{sound_name}' not loaded")


# Usage
sound_mgr = SoundManager()
sound_mgr.load_sound('bell', 'data/sounds/bell.wav')
sound_mgr.load_sound('error', 'data/sounds/error.wav')

# Later in game code:
# sound_mgr.play_sound('bell')


# ============================================================================
# EXAMPLE 2: Using Custom Fonts
# ============================================================================

from kivy.uix.label import Label
from kivy.uix.button import Button
from asset_manager import get_asset_path


def create_styled_label(text: str, font_size: str = '16sp') -> Label:
    """
    Create a label with custom font.
    
    Args:
        text: Label text
        font_size: Font size (e.g., '16sp')
    
    Returns:
        Configured Label widget
    """
    try:
        font_path = get_asset_path('data/fonts/main.ttf')
        return Label(
            text=text,
            font_name=font_path,
            font_size=font_size
        )
    except RuntimeError as e:
        print(f"Warning: Could not load custom font, using default: {e}")
        return Label(text=text, font_size=font_size)


def create_styled_button(text: str) -> Button:
    """
    Create a button with custom font.
    
    Args:
        text: Button text
    
    Returns:
        Configured Button widget
    """
    try:
        font_path = get_asset_path('data/fonts/main.ttf')
        btn = Button(
            text=text,
            font_name=font_path,
            font_size='16sp'
        )
        return btn
    except RuntimeError:
        return Button(text=text)


# Usage
title = create_styled_label('Pròxima Parada', font_size='24sp')
play_button = create_styled_button('Play')


# ============================================================================
# EXAMPLE 3: Preloading Assets in App __init__
# ============================================================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from asset_manager import validate_required_assets, get_asset_path


class GameApp(App):
    """Game application with asset preloading."""
    
    def on_start(self):
        """Called when the app starts (after Kivy initialization)."""
        print("🎮 Game starting - loading assets...")
        
        try:
            # Validate critical assets
            self.validate_assets()
            
            # Preload sounds
            self.load_game_sounds()
            
            # Preload fonts
            self.load_game_fonts()
            
            print("✓ All assets ready")
            return True
        
        except Exception as e:
            print(f"❌ Asset loading failed: {e}")
            return False
    
    def validate_assets(self):
        """Validate all required assets exist."""
        required = [
            'data/sounds/bell.wav',
            'data/sounds/error.wav',
            'data/fonts/main.ttf',
        ]
        validate_required_assets(required)
    
    def load_game_sounds(self):
        """Preload all game sounds."""
        self.sound_mgr = SoundManager()
        
        sound_files = {
            'bell': 'data/sounds/bell.wav',
            'error': 'data/sounds/error.wav',
            # Add more...
        }
        
        for name, path in sound_files.items():
            self.sound_mgr.load_sound(name, path)
    
    def load_game_fonts(self):
        """Cache font paths."""
        self.fonts = {
            'main': get_asset_path('data/fonts/main.ttf'),
        }


# ============================================================================
# EXAMPLE 4: Handling Missing Assets Gracefully
# ============================================================================

class RobustAssetLoader:
    """Asset loader with fallbacks for missing files."""
    
    @staticmethod
    def load_sound_with_fallback(path: str, fallback_sound=None):
        """
        Load a sound, returning fallback if asset missing.
        
        Args:
            path: Asset path
            fallback_sound: Sound to use if primary fails
        
        Returns:
            Sound object or fallback_sound
        """
        try:
            resolved_path = get_asset_path(path)
            return SoundLoader.load(resolved_path)
        except RuntimeError:
            print(f"Warning: Asset '{path}' not found, using fallback")
            return fallback_sound
    
    @staticmethod
    def load_font_with_fallback(path: str):
        """
        Load a font, returning default system font if asset missing.
        
        Args:
            path: Asset path
        
        Returns:
            Font path string (absolute or system default)
        """
        try:
            return get_asset_path(path)
        except RuntimeError:
            print(f"Warning: Font '{path}' not found, using system default")
            return ""  # Empty string = use Kivy default


# ============================================================================
# EXAMPLE 5: Dynamic Asset Discovery
# ============================================================================

import os
from asset_manager import list_available_assets, get_asset_path


class DynamicAssetLoader:
    """Loads assets dynamically from directory."""
    
    @staticmethod
    def load_all_sounds():
        """Load all available sounds."""
        sounds = {}
        available = list_available_assets('data/sounds')
        
        for asset_path in available:
            try:
                full_path = get_asset_path(asset_path)
                sound_name = os.path.basename(asset_path).replace('.wav', '')
                sound = SoundLoader.load(full_path)
                sounds[sound_name] = sound
                print(f"Loaded: {sound_name}")
            except Exception as e:
                print(f"Skipped: {asset_path} ({e})")
        
        return sounds
    
    @staticmethod
    def get_available_fonts():
        """Get list of available fonts."""
        fonts = {}
        available = list_available_assets('data/fonts')
        
        for asset_path in available:
            try:
                full_path = get_asset_path(asset_path)
                font_name = os.path.basename(asset_path).replace('.ttf', '')
                fonts[font_name] = full_path
            except Exception as e:
                print(f"Skipped font: {asset_path}")
        
        return fonts


# ============================================================================
# EXAMPLE 6: Asset Manager as Singleton
# ============================================================================

class AssetManagerSingleton:
    """Global asset manager (singleton pattern)."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.sounds = {}
        self.fonts = {}
        self._initialized = True
        self._load_assets()
    
    def _load_assets(self):
        """Load all assets at initialization."""
        print("Initializing Asset Manager...")
        
        # Load sounds
        sound_files = [
            'data/sounds/bell.wav',
            'data/sounds/error.wav',
        ]
        for path in sound_files:
            try:
                self.sounds[os.path.basename(path)] = SoundLoader.load(
                    get_asset_path(path)
                )
            except RuntimeError:
                pass
        
        # Load fonts
        try:
            self.fonts['main'] = get_asset_path('data/fonts/main.ttf')
        except RuntimeError:
            self.fonts['main'] = ''
    
    def get_sound(self, name: str):
        """Get a loaded sound."""
        return self.sounds.get(name)
    
    def get_font(self, name: str = 'main') -> str:
        """Get a font path."""
        return self.fonts.get(name, '')
    
    def play_sound(self, name: str):
        """Play a sound."""
        sound = self.get_sound(name)
        if sound:
            sound.play()


# Usage:
# assets = AssetManagerSingleton()
# assets.play_sound('bell')
# label = Label(font_name=assets.get_font('main'))


# ============================================================================
# EXAMPLE 7: Testing Asset Configuration
# ============================================================================

def test_assets():
    """Test that all required assets are properly configured."""
    from required_assets import get_required_assets
    
    print("\n📋 Asset Configuration Test")
    print("=" * 50)
    
    required = get_required_assets()
    print(f"Required assets: {len(required)}")
    
    for asset in required:
        try:
            path = get_asset_path(asset)
            print(f"  ✓ {asset}")
        except RuntimeError as e:
            print(f"  ✗ {asset} - NOT FOUND")
    
    print("=" * 50)
    
    # List what's available
    print("\nAvailable assets:")
    available = list_available_assets('data')
    for asset in available:
        print(f"  - {asset}")
    
    print()


# Run this to test:
# if __name__ == '__main__':
#     test_assets()


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

"""
Before deploying to Android:

✓ Asset structure created:
  - data/sounds/ populated with .wav/.ogg files
  - data/fonts/ populated with .ttf files

✓ required_assets.py updated:
  - REQUIRED_ASSETS list includes all critical assets
  - OPTIONAL_ASSETS list includes non-critical files

✓ buildozer.spec updated:
  - source.include_exts includes all file types
  - Includes: wav, ttf, mp3, ogg, png, jpg, etc.

✓ main.py uses asset validation:
  - startup_validation() called before app.run()
  - Handles validation failures gracefully

✓ Game code uses asset_manager:
  - get_asset_path() for all asset loading
  - No hardcoded absolute paths
  - No reliance on current working directory

✓ Tested on desktop:
  - python main.py runs without path errors
  - All sounds and fonts load correctly
  - Asset validation passes

✓ Tested on Android (emulator/device):
  - buildozer android debug worked
  - App installed and started
  - All assets loaded correctly from APK

✓ Deployment ready:
  - buildozer android release built successfully
  - APK tested on physical device
  - No file not found errors in logs
"""
