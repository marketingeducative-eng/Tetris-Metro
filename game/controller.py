"""
GameController - Orchestrates model and UI
"""
from enum import Enum
from model import Board, Piece, Rules, ScoringSystem, MetroContentManager
from kivy.storage.jsonstore import JsonStore
from game.album_store import AlbumStore
from game.order_track import OrderTrackManager
from game.direction_mission import DirectionMission


class GameState(Enum):
    """Game states"""
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class GameMode(Enum):
    """Game modes"""
    ORDER_TRACK = "order_track"  # Main mode: place stations in order
    DIRECTION_MISSION = "direction_mission"  # Mini-challenge: choose direction


class GameController:
    """Coordinates game logic and state"""
    
    def __init__(self, width=10, height=20):
        """Initialize controller"""
        # Model layer
        self.board = Board(width, height)
        self.rules = Rules()
        self.scoring = ScoringSystem()
        self.content = MetroContentManager()
        
        # New game modes
        self.album = AlbumStore()
        self.order_track = OrderTrackManager(self.content, self.album)
        self.direction_mission = DirectionMission(self.content)
        
        # Game state
        self.state = GameState.RUNNING
        self.mode = GameMode.ORDER_TRACK
        self.current_piece = None
        self.next_piece = None
        
        # Persistence
        try:
            self.store = JsonStore('data/game_data.json')
        except:
            self.store = None
        
        # Feedback
        self.last_feedback = ""
        self.feedback_timer = 0
        
        # Station unlock notification
        self.station_unlock_notification = None
        self.unlock_notification_timer = 0
        
        # Animation callbacks
        self.on_piece_locked = None
        self.on_lines_cleared = None
        
        # Initialize
        self._init_game()
    
    def _init_game(self):
        """Initialize game pieces"""
        # Start ORDER TRACK mode
        self.mode = GameMode.ORDER_TRACK
        self.order_track.start_new_line()
        
        self.next_piece = self._create_piece()
        self._spawn_piece()
    
    def _create_piece(self):
        """Create piece with station data"""
        # Get difficulty based on level
        if self.scoring.level <= 3:
            difficulty = 'A1'
        elif self.scoring.level <= 6:
            difficulty = 'A2'
        else:
            difficulty = 'B1'
        
        station = self.content.get_random_station(difficulty)
        piece = Piece(station_data=station)
        
        # Center position
        piece.x = self.board.width // 2 - 1
        piece.y = 0
        
        return piece
    
    def _check_direction_mission_trigger(self):
        """Check if direction mission should trigger"""
        if self.mode == GameMode.ORDER_TRACK:
            progress = self.order_track.get_progress()
            if self.direction_mission.should_trigger(progress['correct_count']):
                # Trigger mission!
                success = self.direction_mission.start_mission(
                    self.order_track.target_line_id,
                    self.order_track.metro_lines
                )
                if success:
                    self.mode = GameMode.DIRECTION_MISSION
                    self.pause()  # Pause game briefly for mission
    
    def _spawn_piece(self):
        """Spawn next piece"""
        self.current_piece = self.next_piece
        self.next_piece = self._create_piece()
        
        # Check game over
        if not self.board.is_valid_position(self.current_piece):
            self.state = GameState.GAME_OVER
    
    def move_left(self):
        """Move piece left"""
        if self.state != GameState.RUNNING or not self.current_piece:
            return False
        
        self.current_piece.move(-1, 0)
        if not self.board.is_valid_position(self.current_piece):
            self.current_piece.move(1, 0)
            return False
        return True
    
    def move_right(self):
        """Move piece right"""
        if self.state != GameState.RUNNING or not self.current_piece:
            return False
        
        self.current_piece.move(1, 0)
        if not self.board.is_valid_position(self.current_piece):
            self.current_piece.move(-1, 0)
            return False
        return True
    
    def move_down(self):
        """
        Move piece down
        
        Returns:
            True if moved, False if locked
        """
        if self.state != GameState.RUNNING or not self.current_piece:
            return False
        
        self.current_piece.move(0, 1)
        if not self.board.is_valid_position(self.current_piece):
            self.current_piece.move(0, -1)
            self._lock_piece()
            return False
        return True
    
    def rotate(self):
        """Rotate piece with wall kicks"""
        if self.state != GameState.RUNNING or not self.current_piece:
            return False
        
        return self.rules.try_rotate(self.current_piece, self.board)
    
    def hard_drop(self):
        """Drop piece to bottom"""
        if self.state != GameState.RUNNING or not self.current_piece:
            return
        
        while self.move_down():
            pass
    
    def _lock_piece(self):
        """Lock piece and process lines"""
        if not self.current_piece:
            return
        
        # Get cells before locking (for animation)
        locked_cells = self.current_piece.get_cells()
        
        # Lock to board
        self.board.lock_piece(self.current_piece)
        
        # Trigger lock animation
        if self.on_piece_locked:
            self.on_piece_locked(locked_cells)
        
        # ORDER TRACK mode: check if piece is on rail
        if self.mode == GameMode.ORDER_TRACK:
            result = self.order_track.process_locked_piece(
                self.current_piece,
                self.current_piece.x
            )
            
            if result['on_rail']:
                if result['correct']:
                    # Correct station!
                    self.scoring.score += result['bonus_score']
                    self.last_feedback = result['feedback']
                    self.feedback_timer = 2.0
                    
                    # Show unlock notification if newly unlocked
                    if result['station_unlocked']:
                        station_data = self.current_piece.station_data
                        self.station_unlock_notification = {
                            'name': station_data.get('name', ''),
                            'lines': station_data.get('lines', [])
                        }
                        self.unlock_notification_timer = 2.0
                    
                    # Check for direction mission trigger
                    self._check_direction_mission_trigger()
                else:
                    # Wrong station
                    self.last_feedback = result['feedback']
                    self.feedback_timer = 2.0
        
        # Clear lines (classic Tetris mechanic still works)
        lines_cleared = self.board.clear_lines()
        
        # Base score for line clears
        if lines_cleared > 0:
            line_score = [0, 100, 300, 500, 800][min(lines_cleared, 4)]
            self.scoring.score += line_score
            
            # Trigger line clear animation
            if self.on_lines_cleared:
                line_indices = list(range(self.board.height - lines_cleared, self.board.height))
                self.on_lines_cleared(line_indices, lines_cleared)
        
        # Save high score
        self._save_high_score()
        
        # Spawn next piece
        self._spawn_piece()
    
    def pause(self):
        """Pause game"""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
    
    def resume(self):
        """Resume game"""
        if self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
    
    def toggle_pause(self):
        """Toggle pause"""
        if self.state == GameState.RUNNING:
            self.pause()
        elif self.state == GameState.PAUSED:
            self.resume()
    
    def reset(self):
        """Reset game"""
        self.board.clear()
        self.scoring.reset()
        self.state = GameState.RUNNING
        self.last_feedback = ""
        self.feedback_timer = 0
        
        self._init_game()
    
    def update(self, dt):
        """Update per frame"""
        # Fade feedback
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.last_feedback = ""
        
        # Fade unlock notification
        if self.unlock_notification_timer > 0:
            self.unlock_notification_timer -= dt
            if self.unlock_notification_timer <= 0:
                self.station_unlock_notification = None
        
        # Update game mode managers
        self.order_track.update(dt)
        self.direction_mission.update(dt)
    
    def get_ghost_y(self):
        """Get ghost piece Y position"""
        if not self.current_piece:
            return None
        return self.rules.calculate_ghost_y(self.current_piece, self.board)
    
    def get_high_score(self):
        """Get saved high score"""
        if self.album:
            return self.album.get_high_score()
        return 0
    
    def _save_high_score(self):
        """Save high score if beaten"""
        # Use album store for high score
        if self.album:
            self.album.save_high_score(self.scoring.score)
    
    def submit_direction_answer(self, option_index):
        """
        Submit answer to direction mission
        
        Args:
            option_index: 0 or 1 for option A or B
        """
        if self.mode != GameMode.DIRECTION_MISSION:
            return
        
        result = self.direction_mission.submit_answer(option_index)
        
        if result:
            # Add bonus score if correct
            if result['correct']:
                self.scoring.score += result['bonus_score']
            
            # Show feedback
            self.last_feedback = result['feedback']
            self.feedback_timer = 2.0
            
            # Return to ORDER TRACK mode
            self.mode = GameMode.ORDER_TRACK
            self.resume()
    
    def get_state_dict(self):
        """Get state for UI rendering"""
        current_label = ""
        next_label = ""
        
        if self.current_piece:
            current_label = self.content.format_station_label(self.current_piece.station_data)
        
        if self.next_piece:
            next_label = self.content.format_station_label(self.next_piece.station_data)
        
        # Get ORDER TRACK progress
        order_track_progress = self.order_track.get_progress()
        upcoming_stations = self.order_track.get_upcoming_stations(10)
        
        # Get direction mission data if active
        direction_mission_data = None
        if self.direction_mission.is_active():
            direction_mission_data = self.direction_mission.get_current_mission()
        
        return {
            'score': self.scoring.score,
            'high_score': self.get_high_score(),
            'level': self.scoring.level,
            'lines_progress': self.scoring.get_lines_progress(),
            'target_line': self.scoring.target_line,
            'current_station': current_label,
            'next_station': next_label,
            'feedback': self.last_feedback,
            'state': self.state,
            'mode': self.mode,
            
            # ORDER TRACK data
            'order_track': {
                'line_id': order_track_progress['line_id'],
                'line_name': order_track_progress['line_name'],
                'next_station': order_track_progress['next_station'],
                'progress': f"{order_track_progress['next_index']}/{order_track_progress['total_stations']}",
                'streak': order_track_progress['streak'],
                'upcoming_stations': upcoming_stations
            },
            
            # Direction mission data
            'direction_mission': direction_mission_data,
            
            # Station unlock notification
            'unlock_notification': self.station_unlock_notification
        }
