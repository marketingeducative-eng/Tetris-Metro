"""
OrderTrackManager - Manages ORDER TRACK game mode
Players must place stations in the correct order for a metro line
"""
import json
from pathlib import Path


class OrderTrackManager:
    """
    Manages the ORDER TRACK game mode
    
    In this mode, players must place pieces with stations in the correct
    sequential order for a target metro line. A fixed "rail" area on the
    board determines when pieces are checked.
    """
    
    def __init__(self, content_manager, album_store, data_path='data/stations.json'):
        """
        Initialize Order Track Manager
        
        Args:
            content_manager: MetroContentManager instance
            album_store: AlbumStore instance for progress tracking
            data_path: Path to stations.json
        """
        self.content = content_manager
        self.album = album_store
        self.data_path = data_path
        
        # Rail configuration (columns that count as "on track")
        self.rail_columns = [4, 5]  # Middle columns by default
        
        # Current line progress
        self.target_line_id = None
        self.ordered_stations = []
        self.next_index = 0
        self.next_station_name = ""
        
        # Feedback state
        self.last_feedback = ""
        self.feedback_type = "neutral"  # "correct", "wrong", "neutral"
        self.feedback_timer = 0
        
        # Stats
        self.correct_count = 0
        self.wrong_count = 0
        self.streak = 0
        self.best_streak = 0
        
        # Load metro line data
        self._load_line_data()
    
    def _load_line_data(self):
        """Load metro line order data from JSON"""
        try:
            path = Path(self.data_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metro_lines = data.get('metro_lines', {})
                    print(f"Loaded {len(self.metro_lines)} metro lines")
            else:
                print(f"Warning: {self.data_path} not found")
                self.metro_lines = {}
        except Exception as e:
            print(f"Error loading metro lines: {e}")
            self.metro_lines = {}
    
    def start_new_line(self, line_id=None):
        """
        Start tracking a new metro line
        
        Args:
            line_id: Specific line to track (e.g., 'L1') or None for random
        """
        if not self.metro_lines:
            print("No metro lines available")
            return False
        
        # Select line
        if line_id and line_id in self.metro_lines:
            self.target_line_id = line_id
        else:
            # Random line
            import random
            self.target_line_id = random.choice(list(self.metro_lines.keys()))
        
        # Get ordered station list
        line_data = self.metro_lines[self.target_line_id]
        self.ordered_stations = line_data.get('stations', [])
        
        # Reset progress
        self.next_index = 0
        self._update_next_station()
        
        # Reset stats for this run
        self.streak = 0
        
        print(f"Started line {self.target_line_id} with {len(self.ordered_stations)} stations")
        return True
    
    def _update_next_station(self):
        """Update the next expected station"""
        if self.next_index < len(self.ordered_stations):
            self.next_station_name = self.ordered_stations[self.next_index]
        else:
            # Line completed!
            self.next_station_name = "COMPLETAT!"
    
    def check_piece_on_rail(self, piece, piece_x):
        """
        Check if a piece position intersects with the rail columns
        
        Args:
            piece: Game piece
            piece_x: Piece X position on board
            
        Returns:
            True if piece touches rail
        """
        # Get piece cells (relative to piece origin)
        shape = piece.shape
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    # Absolute column position
                    abs_col = piece_x + col_idx
                    if abs_col in self.rail_columns:
                        return True
        
        return False
    
    def process_locked_piece(self, piece, piece_x):
        """
        Process a locked piece and check if it matches expected station
        
        Args:
            piece: The locked piece
            piece_x: Piece X position
            
        Returns:
            dict with result info:
            {
                'on_rail': bool,
                'correct': bool,
                'station_unlocked': bool,
                'feedback': str,
                'bonus_score': int
            }
        """
        result = {
            'on_rail': False,
            'correct': False,
            'station_unlocked': False,
            'feedback': '',
            'bonus_score': 0
        }
        
        # Check if piece is on rail
        if not self.check_piece_on_rail(piece, piece_x):
            return result
        
        result['on_rail'] = True
        
        # Get station name from piece
        station_data = piece.station_data
        if not station_data:
            return result
        
        piece_station_name = station_data.get('name', '')
        station_id = station_data.get('id', '')
        
        # Check if it matches expected station
        if piece_station_name == self.next_station_name:
            # CORRECT!
            result['correct'] = True
            result['feedback'] = "Correcte!"
            result['bonus_score'] = 500 + (self.streak * 100)  # Streak bonus
            
            # Update stats
            self.correct_count += 1
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
            
            # Unlock in album
            if self.album:
                newly_unlocked = self.album.unlock_station(
                    self.target_line_id, 
                    piece_station_name
                )
                result['station_unlocked'] = newly_unlocked
                
                # Update station stats
                self.album.increment_station_stat(station_id, correct=True)
            
            # Advance to next station
            self.next_index += 1
            self._update_next_station()
            
            # Update feedback
            self.last_feedback = result['feedback']
            self.feedback_type = "correct"
            self.feedback_timer = 2.0
            
        else:
            # WRONG station
            result['correct'] = False
            result['feedback'] = f"Ara toca: {self.next_station_name}"
            
            # Update stats
            self.wrong_count += 1
            self.streak = 0  # Break streak
            
            # Track wrong attempt
            if self.album and station_id:
                self.album.increment_station_stat(station_id, correct=False)
            
            # Update feedback
            self.last_feedback = result['feedback']
            self.feedback_type = "wrong"
            self.feedback_timer = 2.0
        
        return result
    
    def get_progress(self):
        """Get current progress on line"""
        return {
            'line_id': self.target_line_id,
            'line_name': self.metro_lines.get(self.target_line_id, {}).get('name', ''),
            'next_index': self.next_index,
            'total_stations': len(self.ordered_stations),
            'next_station': self.next_station_name,
            'progress_percent': (self.next_index / len(self.ordered_stations) * 100) if self.ordered_stations else 0,
            'streak': self.streak,
            'best_streak': self.best_streak,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count
        }
    
    def get_upcoming_stations(self, count=12):
        """
        Get list of upcoming stations for mini-map display
        
        Args:
            count: Number of stations to return
            
        Returns:
            List of dicts with station info and completion status
        """
        upcoming = []
        
        for i in range(self.next_index, min(self.next_index + count, len(self.ordered_stations))):
            station_name = self.ordered_stations[i]
            is_unlocked = False
            
            if self.album:
                is_unlocked = self.album.is_station_unlocked(
                    self.target_line_id, 
                    station_name
                )
            
            upcoming.append({
                'name': station_name,
                'index': i,
                'is_next': (i == self.next_index),
                'is_unlocked': is_unlocked
            })
        
        return upcoming
    
    def update(self, dt):
        """Update per frame (for fading feedback)"""
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.last_feedback = ""
                self.feedback_type = "neutral"
    
    def is_line_complete(self):
        """Check if current line is completed"""
        return self.next_index >= len(self.ordered_stations)
    
    def set_rail_columns(self, columns):
        """Configure which columns count as the rail"""
        self.rail_columns = columns
