"""
Persistence Manager - handles local storage with JsonStore
"""
from kivy.storage.jsonstore import JsonStore
import os


class PersistenceManager:
    """
    Manages local data persistence using Kivy JsonStore
    Offline-first: all data stored locally
    """
    
    def __init__(self, store_path='data/game_data.json'):
        """
        Initialize persistence manager
        
        Args:
            store_path: Path to JsonStore file
        """
        self.store_path = store_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(store_path), exist_ok=True)
        
        # Initialize JsonStore
        self.store = JsonStore(store_path)
        
        # Initialize default values if not exist
        self._init_defaults()
    
    def _init_defaults(self):
        """Initialize default values if not present"""
        if not self.store.exists('game_stats'):
            self.store.put('game_stats',
                          high_score=0,
                          total_games=0,
                          total_lines_cleared=0,
                          best_level=1)
        
        if not self.store.exists('settings'):
            self.store.put('settings',
                          sound_on=True,
                          music_on=True,
                          vibration_on=True,
                          difficulty='medium')
        
        if not self.store.exists('session'):
            self.store.put('session',
                          last_played='',
                          last_score=0)
    
    # Game Stats
    def get_high_score(self):
        """Get current high score"""
        return self.store.get('game_stats')['high_score']
    
    def update_high_score(self, score):
        """Update high score if new score is higher"""
        current = self.get_high_score()
        if score > current:
            stats = self.store.get('game_stats')
            stats['high_score'] = score
            self.store.put('game_stats', **stats)
            return True
        return False
    
    def get_best_level(self):
        """Get best level reached"""
        return self.store.get('game_stats')['best_level']
    
    def update_best_level(self, level):
        """Update best level if higher"""
        current = self.get_best_level()
        if level > current:
            stats = self.store.get('game_stats')
            stats['best_level'] = level
            self.store.put('game_stats', **stats)
    
    def increment_game_count(self):
        """Increment total games played"""
        stats = self.store.get('game_stats')
        stats['total_games'] = stats.get('total_games', 0) + 1
        self.store.put('game_stats', **stats)
    
    def add_lines_cleared(self, lines):
        """Add to total lines cleared"""
        stats = self.store.get('game_stats')
        stats['total_lines_cleared'] = stats.get('total_lines_cleared', 0) + lines
        self.store.put('game_stats', **stats)
    
    def get_all_stats(self):
        """Get all game statistics"""
        return dict(self.store.get('game_stats'))
    
    # Settings
    def get_setting(self, key):
        """Get a specific setting value"""
        settings = self.store.get('settings')
        return settings.get(key)
    
    def set_setting(self, key, value):
        """Set a specific setting value"""
        settings = self.store.get('settings')
        settings[key] = value
        self.store.put('settings', **settings)
    
    def get_all_settings(self):
        """Get all settings"""
        return dict(self.store.get('settings'))
    
    def is_sound_on(self):
        """Check if sound is enabled"""
        return self.get_setting('sound_on')
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        current = self.is_sound_on()
        self.set_setting('sound_on', not current)
        return not current
    
    # Session
    def save_session(self, score, level, lines):
        """Save current session data"""
        from datetime import datetime
        self.store.put('session',
                      last_played=datetime.now().isoformat(),
                      last_score=score,
                      last_level=level,
                      last_lines=lines)
    
    def get_last_session(self):
        """Get last session data"""
        return dict(self.store.get('session'))
    
    # Clear data (for testing or reset)
    def clear_all_data(self):
        """Clear all stored data and reinitialize"""
        self.store.clear()
        self._init_defaults()
    
    def reset_stats(self):
        """Reset game statistics only"""
        self.store.put('game_stats',
                      high_score=0,
                      total_games=0,
                      total_lines_cleared=0,
                      best_level=1)
