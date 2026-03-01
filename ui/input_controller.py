"""
InputController - Gesture detection and keyboard input
"""
from kivy.core.window import Window
import time


class InputController:
    """Handles touch gestures and keyboard input"""
    
    def __init__(self, on_move_left=None, on_move_right=None, on_rotate=None, 
                 on_hard_drop=None, on_pause=None):
        """
        Args:
            on_move_left: Callback for left movement
            on_move_right: Callback for right movement
            on_rotate: Callback for rotation
            on_hard_drop: Callback for hard drop
            on_pause: Callback for pause
        """
        self.on_move_left = on_move_left
        self.on_move_right = on_move_right
        self.on_rotate = on_rotate
        self.on_hard_drop = on_hard_drop
        self.on_pause = on_pause
        
        # Gesture detection
        self.touch_start_pos = None
        self.touch_start_time = None
        self.swipe_threshold = 50
        self.tap_time_threshold = 0.2
        
        # Bind keyboard
        Window.bind(on_keyboard=self._on_keyboard)
    
    def handle_touch_down(self, touch):
        """Handle touch start"""
        self.touch_start_pos = touch.pos
        self.touch_start_time = time.time()
    
    def handle_touch_up(self, touch):
        """Handle touch end - detect gesture"""
        if not self.touch_start_pos:
            return
        
        dx = touch.x - self.touch_start_pos[0]
        dy = touch.y - self.touch_start_pos[1]
        dt = time.time() - self.touch_start_time
        
        # Tap (rotation)
        if abs(dx) < 20 and abs(dy) < 20 and dt < self.tap_time_threshold:
            if self.on_rotate:
                self.on_rotate()
            return
        
        # Swipe
        if abs(dx) > abs(dy):
            # Horizontal swipe
            if abs(dx) > self.swipe_threshold:
                if dx > 0 and self.on_move_right:
                    self.on_move_right()
                elif dx < 0 and self.on_move_left:
                    self.on_move_left()
        else:
            # Vertical swipe
            if abs(dy) > self.swipe_threshold:
                if dy < 0 and self.on_hard_drop:  # Swipe down
                    self.on_hard_drop()
        
        self.touch_start_pos = None
        self.touch_start_time = None
    
    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle keyboard input"""
        # Movement
        if key == 276 or codepoint == 'a':  # Left arrow or A
            if self.on_move_left:
                self.on_move_left()
        elif key == 275 or codepoint == 'd':  # Right arrow or D
            if self.on_move_right:
                self.on_move_right()
        elif key == 273 or codepoint == 'w':  # Up arrow or W
            if self.on_rotate:
                self.on_rotate()
        elif key == 32:  # Space
            if self.on_hard_drop:
                self.on_hard_drop()
        
        # Pause
        elif codepoint == 'p':
            if self.on_pause:
                self.on_pause()
        
        return False
