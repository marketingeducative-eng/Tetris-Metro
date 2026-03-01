"""
Board - Pure grid data structure (no rendering)
"""

class Board:
    """Grid that holds locked cells"""
    
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
    
    def is_valid_position(self, piece, offset_x=0, offset_y=0):
        """Check if piece fits at given position"""
        for cell in piece.get_cells():
            x = cell['x'] + offset_x
            y = cell['y'] + offset_y
            
            # Out of bounds
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            
            # Collision with locked cell
            if self.grid[y][x] != 0:
                return False
        
        return True
    
    def lock_piece(self, piece):
        """Lock piece cells into grid"""
        for cell in piece.get_cells():
            x, y = cell['x'], cell['y']
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = cell['color']
    
    def clear_lines(self):
        """Remove full lines and return count"""
        lines_cleared = 0
        y = self.height - 1
        
        while y >= 0:
            if all(cell != 0 for cell in self.grid[y]):
                # Remove line
                del self.grid[y]
                # Add empty line at top
                self.grid.insert(0, [0 for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
        
        return lines_cleared
    
    def clear(self):
        """Reset grid"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
    
    def get_grid_copy(self):
        """Return copy of grid for rendering"""
        return [row[:] for row in self.grid]
