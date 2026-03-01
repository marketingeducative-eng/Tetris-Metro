"""
Game Logger - Structured logging to file
"""
import logging
from pathlib import Path
from datetime import datetime


class GameLogger:
    """Structured logging for game events and errors"""
    
    def __init__(self, log_file='logs/game.log', debug_mode=False):
        """
        Initialize logger
        
        Args:
            log_file: Path to log file
            debug_mode: Enable debug level logging
        """
        self.log_file = log_file
        self.debug_mode = debug_mode
        
        # Create logs directory
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger('MetroTetris')
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        
        self.info("=" * 60)
        self.info(f"Game session started - Debug: {debug_mode}")
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        """Log error"""
        self.logger.error(message, exc_info=exc_info)
    
    def log_game_event(self, event_type, **data):
        """Log structured game event"""
        event_data = ' | '.join(f"{k}={v}" for k, v in data.items())
        self.info(f"{event_type}: {event_data}")
