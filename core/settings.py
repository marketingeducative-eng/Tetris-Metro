"""
Settings Management - Load, save, and manage game settings
"""
import json
from pathlib import Path
from kivy.logger import Logger


class SettingsManager:
    """Manages game settings with JSON persistence"""
    
    DEFAULT_SETTINGS = {
        'practice_mode': False,
        'direction_mode': False,
        'subtitles_enabled': True,
        'language': 'ca',  # Default language: Catalan
        'has_completed_onboarding': False,  # First-launch onboarding flag
    }
    
    def __init__(self):
        self.settings_file = Path(__file__).parent.parent / "data" / "settings.json"
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._load_settings()
    
    def _load_settings(self):
        """Load settings from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    self.settings = {**self.DEFAULT_SETTINGS, **loaded}
            else:
                self.settings = self.DEFAULT_SETTINGS.copy()
                self._save_settings()  # Create file with defaults
            Logger.info(f"Settings: Loaded settings from {self.settings_file}")
        except Exception as e:
            Logger.warning(f"Settings: Error loading settings: {e}")
            self.settings = self.DEFAULT_SETTINGS.copy()
    
    def _save_settings(self):
        """Save settings to JSON file"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            Logger.info("Settings: Settings saved successfully")
        except Exception as e:
            Logger.warning(f"Settings: Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and persist"""
        self.settings[key] = value
        self._save_settings()
        Logger.info(f"Settings: {key} set to {value}")
    
    def toggle(self, key):
        """Toggle a boolean setting"""
        current = self.settings.get(key, False)
        new_value = not current
        self.set(key, new_value)
        return new_value
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._save_settings()
        Logger.info("Settings: All settings reset to defaults")
