"""
Scoring - Points calculation with metro line bonuses
"""

class ScoringSystem:
    """Handles score and level progression"""
    
    BASE_POINTS = {
        1: 100,   # Single
        2: 300,   # Double
        3: 500,   # Triple
        4: 800    # Tetris
    }
    
    LINE_BONUS_MULTIPLIER = 1.5
    LINES_PER_LEVEL = 10
    
    def __init__(self):
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.target_line = None
    
    def calculate_score(self, lines_cleared, piece_lines=None):
        """
        Calculate score for cleared lines
        
        Args:
            lines_cleared: Number of lines cleared (1-4)
            piece_lines: Metro lines from piece (for bonus)
        
        Returns:
            dict with 'points', 'bonus_applied', 'bonus_amount'
        """
        if lines_cleared == 0:
            return {'points': 0, 'bonus_applied': False, 'bonus_amount': 0}
        
        # Base score
        base = self.BASE_POINTS.get(lines_cleared, lines_cleared * 100)
        points = base * self.level
        
        # Check metro line bonus
        bonus_applied = False
        bonus_amount = 0
        
        if self.target_line and piece_lines and self.target_line in piece_lines:
            bonus_amount = int(points * (self.LINE_BONUS_MULTIPLIER - 1))
            points += bonus_amount
            bonus_applied = True
        
        return {
            'points': points,
            'bonus_applied': bonus_applied,
            'bonus_amount': bonus_amount
        }
    
    def add_score(self, lines_cleared, piece_lines=None):
        """Add score and update level"""
        result = self.calculate_score(lines_cleared, piece_lines)
        
        self.score += result['points']
        self.lines_cleared += lines_cleared
        
        # Level up
        new_level = (self.lines_cleared // self.LINES_PER_LEVEL) + 1
        if new_level > self.level:
            self.level = new_level
        
        return result
    
    def reset(self):
        """Reset scoring"""
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
    
    def get_fall_speed(self):
        """Get fall speed in seconds"""
        return max(0.1, 1.0 - (self.level - 1) * 0.05)
    
    def get_lines_progress(self):
        """Get lines cleared in current level (0-9)"""
        return self.lines_cleared % self.LINES_PER_LEVEL
