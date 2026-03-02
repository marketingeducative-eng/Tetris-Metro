"""
AlbumStore - Manages persistent progress tracking
Tracks unlocked stations, stats, and high scores
"""
from pathlib import Path


class AlbumStore:
    """Persistent album and progress tracking"""
    
    def __init__(self, store_path='data/album_data.json'):
        """Initialize album store"""
        self.store_path = store_path
        try:
            from kivy.storage.jsonstore import JsonStore  # noqa: PLC0415
            self.store = JsonStore(store_path)
        except Exception:
            self.store = None
            print(f"Warning: Could not create album store at {store_path}")
    
    def unlock_station(self, line_id, station_name):
        """
        Unlock a station in the album
        
        Args:
            line_id: Metro line (e.g., 'L1')
            station_name: Station name
            
        Returns:
            True if newly unlocked, False if already unlocked
        """
        if not self.store:
            return False
        
        key = f"line_{line_id}"
        
        # Get existing unlocked stations for this line
        if self.store.exists(key):
            data = self.store.get(key)
            unlocked = data.get('unlocked', [])
        else:
            unlocked = []
        
        # Check if already unlocked
        if station_name in unlocked:
            return False
        
        # Add to unlocked list
        unlocked.append(station_name)
        self.store.put(key, unlocked=unlocked)
        return True
    
    def is_station_unlocked(self, line_id, station_name):
        """Check if station is unlocked"""
        if not self.store:
            return False
        
        key = f"line_{line_id}"
        if not self.store.exists(key):
            return False
        
        data = self.store.get(key)
        unlocked = data.get('unlocked', [])
        return station_name in unlocked
    
    def get_unlocked_stations(self, line_id):
        """Get list of unlocked stations for a line"""
        if not self.store:
            return []
        
        key = f"line_{line_id}"
        if not self.store.exists(key):
            return []
        
        data = self.store.get(key)
        return data.get('unlocked', [])
    
    def get_station_stats(self, station_id):
        """Get success/fail stats for a station"""
        if not self.store:
            return {'correct': 0, 'wrong': 0}
        
        key = f"stats_{station_id}"
        if not self.store.exists(key):
            return {'correct': 0, 'wrong': 0}
        
        data = self.store.get(key)
        return {
            'correct': data.get('correct', 0),
            'wrong': data.get('wrong', 0)
        }
    
    def increment_station_stat(self, station_id, correct=True):
        """Increment correct or wrong counter for a station"""
        if not self.store:
            return
        
        key = f"stats_{station_id}"
        stats = self.get_station_stats(station_id)
        
        if correct:
            stats['correct'] += 1
        else:
            stats['wrong'] += 1
        
        self.store.put(key, correct=stats['correct'], wrong=stats['wrong'])
    
    def get_high_score(self):
        """Get saved high score"""
        if not self.store:
            return 0
        
        if self.store.exists('high_score'):
            data = self.store.get('high_score')
            return data.get('value', 0)
        return 0
    
    def save_high_score(self, score):
        """Save high score if it's higher"""
        if not self.store:
            return False
        
        current = self.get_high_score()
        if score > current:
            self.store.put('high_score', value=score)
            return True
        return False
    
    def get_progress_summary(self, line_id):
        """Get progress summary for a line"""
        unlocked = self.get_unlocked_stations(line_id)
        return {
            'total_unlocked': len(unlocked),
            'stations': unlocked
        }
    
    def reset_line_progress(self, line_id):
        """Reset progress for a specific line"""
        if not self.store:
            return
        
        key = f"line_{line_id}"
        if self.store.exists(key):
            self.store.delete(key)
    
    def reset_all(self):
        """Reset all progress (dangerous!)"""
        if not self.store:
            return
        
        # Clear store file
        try:
            path = Path(self.store_path)
            if path.exists():
                path.unlink()
            # Recreate empty store
            self.store = JsonStore(self.store_path)
        except Exception as e:
            print(f"Error resetting album: {e}")
