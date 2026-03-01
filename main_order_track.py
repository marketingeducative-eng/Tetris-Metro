"""
Metro Tetris - ORDER TRACK Mode
Main application with integrated game modes
"""
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color, Line, RoundedRectangle
from kivy.properties import NumericProperty

from game.controller import GameController, GameState, GameMode
from ui.hud_view import HUDView
from ui.overlays import PauseOverlay, GameOverOverlay, DirectionMissionOverlay, StationUnlockOverlay

# Mobile portrait mode
Window.size = (360, 640)


class TetrisGame(FloatLayout):
    """Main game widget with ORDER TRACK mode"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Game controller with new modes
        self.controller = GameController(width=10, height=20)
        
        # Rendering config
        self.cell_size = 28
        self.offset_x = 30
        self.offset_y = 100
        
        # Gravity system
        self.gravity_timer = 0
        self.gravity_interval = 0.5
        
        # Touch controls
        self.touch_start_pos = None
        self.touch_start_time = 0
        self.swipe_threshold = 50
        self.tap_time_threshold = 0.2
        
        # Create game canvas
        self.game_canvas = Widget(size_hint=(1, 1))
        self.add_widget(self.game_canvas)
        
        # Create UI
        self.hud = HUDView()
        self.add_widget(self.hud)
        
        # Create overlays
        self.pause_overlay = PauseOverlay(on_resume=self.resume_game)
        self.add_widget(self.pause_overlay)
        
        self.game_over_overlay = GameOverOverlay(
            on_retry=self.restart_game,
            on_exit=self.exit_game
        )
        self.add_widget(self.game_over_overlay)
        
        self.direction_mission_overlay = DirectionMissionOverlay(
            on_answer=self.on_direction_answer
        )
        self.add_widget(self.direction_mission_overlay)
        
        self.station_unlock_overlay = StationUnlockOverlay()
        self.add_widget(self.station_unlock_overlay)
        
        # Bind keyboard
        Window.bind(on_key_down=self.on_keyboard_down)
        
        # Start game loop
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        
        self.game_canvas.bind(pos=self.redraw, size=self.redraw)
        
        # Initial update
        self._update_ui()
    
    def update(self, dt):
        """Game loop at 60 FPS"""
        # Update controller
        self.controller.update(dt)
        
        # Check for game over
        if self.controller.state == GameState.GAME_OVER:
            self._show_game_over()
            return
        
        # Check for direction mission
        if self.controller.mode == GameMode.DIRECTION_MISSION:
            mission_data = self.controller.direction_mission.get_current_mission()
            if mission_data and not self.direction_mission_overlay.visible:
                self.direction_mission_overlay.show(mission_data)
        
        # Check for station unlock notification
        unlock_notif = self.controller.station_unlock_notification
        if unlock_notif and not self.station_unlock_overlay.visible:
            self.station_unlock_overlay.show(
                unlock_notif['name'],
                unlock_notif['lines']
            )
        
        # Apply gravity if running
        if self.controller.state == GameState.RUNNING:
            self.gravity_timer += dt
            
            # Adjust fall speed by level
            self.gravity_interval = max(0.1, 0.5 - (self.controller.scoring.level * 0.03))
            
            if self.gravity_timer >= self.gravity_interval:
                self.controller.move_down()
                self.gravity_timer = 0
        
        # Update UI
        self._update_ui()
        
        # Redraw
        self.redraw()
    
    def _update_ui(self):
        """Update HUD with controller state"""
        state = self.controller.get_state_dict()
        self.hud.update(state)
    
    def redraw(self, *args):
        """Redraw game board"""
        self.game_canvas.canvas.clear()
        with self.game_canvas.canvas:
            # Background
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.game_canvas.pos, size=self.game_canvas.size)
            
            # Draw rail columns (visual indicator)
            self._draw_rail()
            
            # Draw grid
            self._draw_grid()
            
            # Draw locked board
            self._draw_board()
            
            # Draw ghost piece
            self._draw_ghost_piece()
            
            # Draw current piece
            self._draw_current_piece()
    
    def _draw_rail(self):
        """Draw the rail area (columns 4-5)"""
        rail_cols = self.controller.order_track.rail_columns
        
        # Highlight rail columns
        Color(0.15, 0.25, 0.35, 0.3)
        for col in rail_cols:
            px = self.offset_x + col * self.cell_size
            Rectangle(
                pos=(px, self.offset_y),
                size=(self.cell_size, self.controller.board.height * self.cell_size)
            )
    
    def _draw_grid(self):
        """Draw grid lines"""
        Color(0.25, 0.25, 0.3, 1)
        width = self.controller.board.width
        height = self.controller.board.height
        
        for x in range(width + 1):
            px = self.offset_x + x * self.cell_size
            Line(
                points=[px, self.offset_y, px, self.offset_y + height * self.cell_size],
                width=1
            )
        
        for y in range(height + 1):
            py = self.offset_y + y * self.cell_size
            Line(
                points=[self.offset_x, py, self.offset_x + width * self.cell_size, py],
                width=1
            )
    
    def _draw_board(self):
        """Draw locked pieces"""
        for y in range(self.controller.board.height):
            for x in range(self.controller.board.width):
                cell = self.controller.board.grid[y][x]
                if cell != 0:
                    self._draw_cell(x, y, cell)
    
    def _draw_current_piece(self):
        """Draw falling piece"""
        piece = self.controller.current_piece
        if not piece:
            return
        
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = piece.x + x
                    py = piece.y + y
                    if 0 <= py < self.controller.board.height:
                        self._draw_cell(px, py, piece.color)
    
    def _draw_ghost_piece(self):
        """Draw ghost piece"""
        piece = self.controller.current_piece
        if not piece:
            return
        
        ghost_y = self.controller.get_ghost_y()
        if ghost_y is None:
            return
        
        Color(0.5, 0.5, 0.5, 0.25)
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    px = self.offset_x + (piece.x + x) * self.cell_size
                    py = self.offset_y + (ghost_y + y) * self.cell_size
                    if ghost_y + y < self.controller.board.height:
                        Rectangle(
                            pos=(px + 1, py + 1),
                            size=(self.cell_size - 2, self.cell_size - 2)
                        )
    
    def _draw_cell(self, x, y, color):
        """Draw a single cell"""
        px = self.offset_x + x * self.cell_size
        py = self.offset_y + y * self.cell_size
        
        # Main cell color
        Color(*self._parse_color(color))
        Rectangle(pos=(px + 1, py + 1), size=(self.cell_size - 2, self.cell_size - 2))
        
        # Highlight
        Color(1, 1, 1, 0.15)
        Rectangle(pos=(px + 2, py + self.cell_size - 4), size=(self.cell_size - 4, 2))
    
    def _parse_color(self, color):
        """Parse color value to RGB"""
        if isinstance(color, (list, tuple)):
            return color
        
        # Default colors by type
        color_map = {
            1: (0.0, 0.8, 0.8, 1),  # I
            2: (0.0, 0.0, 1.0, 1),  # J
            3: (1.0, 0.5, 0.0, 1),  # L
            4: (1.0, 1.0, 0.0, 1),  # O
            5: (0.0, 1.0, 0.0, 1),  # S
            6: (0.5, 0.0, 0.5, 1),  # T
            7: (1.0, 0.0, 0.0, 1),  # Z
        }
        
        return color_map.get(color, (0.7, 0.7, 0.7, 1))
    
    # Input handling
    
    def on_keyboard_down(self, window, key, *args):
        """Handle keyboard input"""
        if self.controller.state == GameState.PAUSED:
            return
        
        # Arrow keys
        if key == 276:  # Left
            self.controller.move_left()
        elif key == 275:  # Right
            self.controller.move_right()
        elif key == 274:  # Down
            self.controller.move_down()
            self.gravity_timer = 0
        elif key == 273:  # Up
            self.controller.rotate()
        elif key == 32:  # Space
            self.controller.hard_drop()
            self.gravity_timer = 0
        elif key == 112:  # P
            self.toggle_pause()
    
    def on_touch_down(self, touch):
        """Handle touch start"""
        # Check if touch is on overlays first
        if self.direction_mission_overlay.visible:
            return super().on_touch_down(touch)
        
        if self.pause_overlay.visible or self.game_over_overlay.visible:
            return super().on_touch_down(touch)
        
        self.touch_start_pos = touch.pos
        self.touch_start_time = Clock.get_time()
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        """Handle touch end - swipe gestures"""
        if not self.touch_start_pos:
            return super().on_touch_up(touch)
        
        if self.controller.state == GameState.PAUSED:
            return super().on_touch_up(touch)
        
        dx = touch.pos[0] - self.touch_start_pos[0]
        dy = touch.pos[1] - self.touch_start_pos[1]
        dt = Clock.get_time() - self.touch_start_time
        
        # Tap (quick touch)
        if dt < self.tap_time_threshold and abs(dx) < 20 and abs(dy) < 20:
            self.controller.rotate()
        # Swipe left
        elif dx < -self.swipe_threshold:
            self.controller.move_left()
        # Swipe right
        elif dx > self.swipe_threshold:
            self.controller.move_right()
        # Swipe down (fast drop)
        elif dy < -self.swipe_threshold:
            self.controller.hard_drop()
            self.gravity_timer = 0
        
        self.touch_start_pos = None
        return super().on_touch_up(touch)
    
    # Game control methods
    
    def toggle_pause(self):
        """Toggle pause"""
        if self.controller.state == GameState.RUNNING:
            self.controller.pause()
            self.pause_overlay.show()
        elif self.controller.state == GameState.PAUSED:
            self.controller.resume()
            self.pause_overlay.hide()
    
    def resume_game(self):
        """Resume from pause"""
        self.controller.resume()
        self.pause_overlay.hide()
    
    def restart_game(self):
        """Restart game"""
        self.controller.reset()
        self.game_over_overlay.hide()
        self.gravity_timer = 0
    
    def exit_game(self):
        """Exit application"""
        App.get_running_app().stop()
    
    def _show_game_over(self):
        """Show game over overlay"""
        score = self.controller.scoring.score
        high_score = self.controller.get_high_score()
        is_new_record = score > high_score
        
        self.game_over_overlay.show(score, is_new_record)
    
    def on_direction_answer(self, option_index):
        """Handle direction mission answer"""
        self.controller.submit_direction_answer(option_index)
        self.direction_mission_overlay.hide()


class MetroTetrisApp(App):
    """Main application"""
    
    def build(self):
        return TetrisGame()


if __name__ == '__main__':
    MetroTetrisApp().run()
