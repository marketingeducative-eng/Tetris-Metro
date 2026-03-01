"""
Board class - manages the game grid and piece placement
"""


class Board:
    """
    Game board managing the grid, collision detection and line clearing
    """
    
    def __init__(self, width=10, height=20):
        """
        Initialize game board
        
        Args:
            width: Number of columns (default 10)
            height: Number of rows (default 20)
        """
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
    
    def is_valid_position(self, piece):
        """
        Check if piece position is valid (no collisions)
        
        Args:
            piece: Piece instance to check
            
        Returns:
            True if position is valid, False otherwise
        """
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:  # If this cell is filled
                    x = piece.x + col_idx
                    y = piece.y + row_idx
                    
                    # Check boundaries
                    if x < 0 or x >= self.width:
                        return False
                    if y < 0 or y >= self.height:
                        return False
                    
                    # Check collision with locked pieces
                    if self.grid[y][x] != 0:
                        return False
        
        return True
    
    def lock_piece(self, piece):
        """
        Lock piece into the board grid
        
        Args:
            piece: Piece instance to lock
        """
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = piece.x + col_idx
                    y = piece.y + row_idx
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.grid[y][x] = piece.color
    
    def clear_lines(self):
        """
        Clear completed lines and return count
        
        Returns:
            Number of lines cleared
        """
        lines_cleared = 0
        y = self.height - 1
        
        while y >= 0:
            # Check if line is complete
            if all(cell != 0 for cell in self.grid[y]):
                # Remove this line
                del self.grid[y]
                # Add empty line at top
                self.grid.insert(0, [0 for _ in range(self.width)])
                lines_cleared += 1
                # Don't decrement y, check same row again
            else:
                y -= 1
        
        return lines_cleared
    
    def is_game_over(self):
        """
        Check if game is over (top row has locked pieces)
        
        Returns:
            True if game over, False otherwise
        """
        return any(cell != 0 for cell in self.grid[0])
    
    def clear(self):
        """Reset board to empty state"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
    
    def get_height_map(self):
        """
        Get height of each column (for AI or stats)
        
        Returns:
            List of heights for each column
        """
        heights = []
        for x in range(self.width):
            height = 0
            for y in range(self.height):
                if self.grid[y][x] != 0:
                    height = self.height - y
                    break
            heights.append(height)
        return heights
    
    def __repr__(self):
        """String representation for debugging"""
        lines = []
        for row in self.grid:
            line = ''.join(['█' if cell else '·' for cell in row])
            lines.append(line)
        return '\n'.join(lines)
