"""
Piece - Tetromino with position and metro station data
"""
import random
from .tetrominos import SHAPES, COLORS, SHAPE_TYPES


class Piece:
    """Tetromino piece with rotation and position"""
    
    def __init__(self, station_data=None, shape_type=None):
        """
        Args:
            station_data: Metro station info dict
            shape_type: Override shape (default: random)
        """
        self.shape_type = shape_type or random.choice(SHAPE_TYPES)
        self.shapes = SHAPES[self.shape_type]
        self.color = COLORS[self.shape_type]
        self.rotation = 0
        self.x = 0
        self.y = 0
        
        # Metro content
        self.station_data = station_data or {}
        self.station_label = self._format_station_label()
    
    def _format_station_label(self):
        """Format station name + lines"""
        if not self.station_data:
            return ""
        
        name = self.station_data.get('name_short', self.station_data.get('name', ''))
        lines = self.station_data.get('lines', [])
        
        if lines:
            return f"{name} ({', '.join(lines)})"
        return name
    
    def get_current_shape(self):
        """Get matrix for current rotation"""
        return self.shapes[self.rotation]
    
    def get_cells(self):
        """Get absolute positions of all filled cells"""
        shape = self.get_current_shape()
        cells = []
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != 0:
                    cells.append({
                        'x': self.x + col_idx,
                        'y': self.y + row_idx,
                        'color': self.color
                    })
        
        return cells
    
    def rotate_clockwise(self):
        """Rotate to next state"""
        self.rotation = (self.rotation + 1) % len(self.shapes)
    
    def rotate_counterclockwise(self):
        """Rotate to previous state"""
        self.rotation = (self.rotation - 1) % len(self.shapes)
    
    def move(self, dx, dy):
        """Move piece by delta"""
        self.x += dx
        self.y += dy
    
    def clone(self):
        """Create copy of piece"""
        copy = Piece(station_data=self.station_data, shape_type=self.shape_type)
        copy.rotation = self.rotation
        copy.x = self.x
        copy.y = self.y
        return copy
