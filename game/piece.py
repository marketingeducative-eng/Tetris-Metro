"""
Piece class - represents a single Tetromino piece
"""
import random
from game.tetrominos import TETROMINOS, PIECE_TYPES


class Piece:
    """
    Represents a Tetromino piece with position, shape and rotation
    """
    
    def __init__(self, piece_type=None, x=3, y=0, station_data=None):
        """
        Initialize a piece
        
        Args:
            piece_type: Type of piece (I, J, L, O, S, T, Z) or None for random
            x: Starting x position (grid column)
            y: Starting y position (grid row)
            station_data: Dictionary with station information or None
        """
        if piece_type is None:
            piece_type = random.choice(PIECE_TYPES)
        
        self.type = piece_type
        self.rotation = 0
        self.x = x
        self.y = y
        
        # Get piece data from definitions
        piece_data = TETROMINOS[piece_type]
        self.shapes = piece_data['shape']
        self.color = piece_data['color']
        
        # Station label
        self.station_data = station_data
        self.station_label = self._format_station_label()
    
    @property
    def shape(self):
        """Get current rotated shape"""
        return self.shapes[self.rotation]
    
    def rotate_clockwise(self):
        """Rotate piece 90 degrees clockwise"""
        self.rotation = (self.rotation + 1) % len(self.shapes)
    
    def rotate_counterclockwise(self):
        """Rotate piece 90 degrees counterclockwise"""
        self.rotation = (self.rotation - 1) % len(self.shapes)
    
    def move(self, dx, dy):
        """
        Move piece by delta
        
        Args:
            dx: Change in x position
            dy: Change in y position
        """
        self.x += dx
        self.y += dy
    
    def get_cells(self):
        """
        Get list of occupied cell positions
        
        Returns:
            List of (x, y) tuples representing filled cells
        """
        cells = []
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    cells.append((self.x + col_idx, self.y + row_idx))
        return cells
    
    def _format_station_label(self):
        """Format station data into display label"""
        if not self.station_data:
            return ""
        
        name = self.station_data.get('name_short', self.station_data.get('name', ''))
        lines = self.station_data.get('lines', [])
        
        if lines:
            return f"{name} ({', '.join(lines)})"
        return name
    
    def clone(self):
        """
        Create a copy of this piece
        
        Returns:
            New Piece instance with same properties
        """
        new_piece = Piece(self.type, self.x, self.y, self.station_data)
        new_piece.rotation = self.rotation
        return new_piece
    
    def __repr__(self):
        station = self.station_label if self.station_label else "no label"
        return f"Piece({self.type}, {station}, x={self.x}, y={self.y}, rot={self.rotation})"
