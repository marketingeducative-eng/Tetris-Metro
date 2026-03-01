"""
Rules - Collision detection, rotation with wall kicks
"""

class Rules:
    """Game rules engine"""
    
    # SRS wall kick data
    WALL_KICKS = {
        'JLSTZ': {
            (0, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
            (1, 0): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
            (1, 2): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
            (2, 1): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
            (2, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
            (3, 2): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
            (3, 0): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
            (0, 3): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
        },
        'I': {
            (0, 1): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
            (1, 0): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
            (1, 2): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
            (2, 1): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
            (2, 3): [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
            (3, 2): [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
            (3, 0): [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
            (0, 3): [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
        }
    }
    
    @staticmethod
    def try_rotate(piece, board, clockwise=True):
        """
        Try to rotate piece with wall kicks
        
        Returns:
            True if rotation succeeded, False otherwise
        """
        old_rotation = piece.rotation
        
        # Rotate
        if clockwise:
            piece.rotate_clockwise()
        else:
            piece.rotate_counterclockwise()
        
        # Try basic position
        if board.is_valid_position(piece):
            return True
        
        # Try wall kicks
        kick_type = 'I' if piece.shape_type == 'I' else 'JLSTZ'
        kick_data = Rules.WALL_KICKS.get(kick_type, {})
        
        rotation_key = (old_rotation, piece.rotation)
        kicks = kick_data.get(rotation_key, [(0, 0)])
        
        for dx, dy in kicks:
            if board.is_valid_position(piece, dx, dy):
                piece.move(dx, dy)
                return True
        
        # Revert rotation
        piece.rotation = old_rotation
        return False
    
    @staticmethod
    def calculate_ghost_y(piece, board):
        """Calculate Y position where piece would land"""
        ghost = piece.clone()
        
        while board.is_valid_position(ghost):
            ghost.move(0, 1)
        
        ghost.move(0, -1)
        return ghost.y
