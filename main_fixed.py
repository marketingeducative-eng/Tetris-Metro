"""
Metro Tetris - Main Application
Mobile-first Tetris implementation with Kivy
"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from game.controller import GameController, GameState
from game.content_manager import ContentManager
from game.persistence import PersistenceManager

# Lock to portrait mode
Window.size = (360, 640)


class TetrisGame(FloatLayout):
    """Main game widget handling rendering and input"""
    
    score = NumericProperty(0)
    level = NumericProperty(1)
    high_score = NumericProperty(0)
    station_label = StringProperty("")
    is_paused = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize managers
        self.content_manager = ContentManager()
        self.persistence = PersistenceManager()
        
        # Load high score
        self.high_score = self.persistence.get_high_score()
        
        # Initialize controller
        self.controller = GameController(width=10, height=20)
        
        # Game rendering properties
        self.cell_size = 30
        self.offset_x = 30
        self.offset_y = 160
        
        # Gravity system
        self.gravity_timer = 0
        self.gravity_interval = 0.5  # seconds
        
        # Feedback message
        self.feedback_message = ""
        self.feedback_timer = 0
        self.feedback_duration = 1.5
        
        # Touch gesture tracking
        self.touch_start_pos = None
        self.touch_start_time = 0
        self.swipe_threshold = 50  # pixels
        self.tap_time_threshold = 0.2  # seconds
        
        # Create game canvas widget
        self.game_canvas = Widget(size_hint=(1, 1))
        self.add_widget(self.game_canvas)
        
        # Create HUD and overlays
        self._create_hud()
        self._create_overlays()
        
        # Bind keyboard events
        Window.bind(on_key_down=self.on_keyboard_down)
        
        # Schedule game loop at 60 FPS
        self.game_loop = Clock.schedule_interval(self.update, 1.0 / 60.0)
        
        self.game_canvas.bind(pos=self.redraw, size=self.redraw)
        
        # Initial HUD update
        self._update_hud()
    
    def _create_hud(self):
        """Create HUD labels for score, level and station"""
        # Score label
        self.score_label = Label(
            text='Score: 0',
            pos_hint={'x': 0.02, 'top': 0.99},
            size_hint=(None, None),
            size=(150, 25),
            font_size='15sp',
            halign='left',
            valign='top'
        )
        self.add_widget(self.score_label)
        
        # High score label
        self.high_score_label = Label(
            text=f'Best: {self.high_score}',
            pos_hint={'right': 0.98, 'top': 0.99},
            size_hint=(None, None),
            size=(150, 25),
            font_size='13sp',
            halign='right',
            valign='top',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.high_score_label)
        
        # Level label
        self.level_label = Label(
            text='Level: 1',
            pos_hint={'x': 0.02, 'top': 0.95},
            size_hint=(None, None),
            size=(150, 25),
            font_size='15sp',
            halign='left',
            valign='top'
        )
        self.add_widget(self.level_label)
        
        # Lines label
        self.lines_label = Label(
            text='Lines: 0/10',
            pos_hint={'right': 0.98, 'top': 0.95},
            size_hint=(None, None),
            size=(150, 25),
            font_size='13sp',
            halign='right',
            valign='top'
        )
        self.add_widget(self.lines_label)
        
        # Target line label
        self.target_line_label = Label(
            text='Objetivo: L1',
            pos_hint={'x': 0.02, 'top': 0.91},
            size_hint=(None, None),
            size=(200, 25),
            font_size='14sp',
            halign='left',
            valign='top',
            color=(1, 0.9, 0.3, 1)  # Yellow
        )
        self.add_widget(self.target_line_label)
        
        # Current station label (larger, prominent)
        self.station_label_widget = Label(
            text='',
            pos_hint={'x': 0.02, 'top': 0.87},
            size_hint=(0.96, None),
            size=(0, 30),
            font_size='13sp',
            halign='left',
            valign='top',
            color=(0.3, 0.8, 1, 1)  # Light blue
        )
        self.add_widget(self.station_label_widget)
        
        # Next piece station label
        self.next_station_label = Label(
            text='',
            pos_hint={'x': 0.02, 'top': 0.83},
            size_hint=(0.96, None),
            size=(0, 25),
            font_size='11sp',
            halign='left',
            valign='top',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(self.next_station_label)
        
        # Feedback label (auto-hide)
        self.feedback_label = Label(
            text='',
            pos_hint={'center_x': 0.5, 'top': 0.6},
            size_hint=(None, None),
            size=(300, 40),
            font_size='18sp',
            halign='center',
            valign='middle',
            color=(0.2, 1, 0.3, 1),  # Green
            bold=True,
            opacity=0
        )
        self.add_widget(self.feedback_label)
        
        # Pause button
        self.pause_button = Button(
            text='⏸',
            pos_hint={'right': 0.98, 'top': 0.87},
            size_hint=(None, None),
            size=(40, 40),
            font_size='20sp',
            background_color=(0.3, 0.3, 0.35, 1),
            color=(1, 1, 1, 1)
        )
        self.pause_button.bind(on_press=self.on_pause_button)
        self.add_widget(self.pause_button)
    
    def _create_overlays(self):
        """Create pause and game over overlays"""
        # Pause overlay
        self.pause_overlay = FloatLayout(size_hint=(1, 1), opacity=0)
        
        # Dark background
        with self.pause_overlay.canvas.before:
            Color(0, 0, 0, 0.7)
            self.pause_bg = Rectangle(pos=self.pause_overlay.pos, size=self.pause_overlay.size)
        self.pause_overlay.bind(pos=self._update_overlay_bg, size=self._update_overlay_bg)
        
        pause_title = Label(
            text='PAUSA',
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            font_size='32sp',
            bold=True
        )
        self.pause_overlay.add_widget(pause_title)
        
        resume_btn = Button(
            text='Continuar',
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            size_hint=(0.5, 0.1),
            font_size='18sp',
            background_color=(0.2, 0.7, 0.3, 1)
        )
        resume_btn.bind(on_press=self.on_resume_button)
        self.pause_overlay.add_widget(resume_btn)
        
        self.add_widget(self.pause_overlay)
        
        # Game Over overlay
        self.game_over_overlay = FloatLayout(size_hint=(1, 1), opacity=0)
        
        with self.game_over_overlay.canvas.before:
            Color(0, 0, 0, 0.8)
            self.game_over_bg = Rectangle(pos=self.game_over_overlay.pos, size=self.game_over_overlay.size)
        self.game_over_overlay.bind(pos=self._update_overlay_bg, size=self._update_overlay_bg)
        
        game_over_title = Label(
            text='GAME OVER',
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            font_size='32sp',
            bold=True,
            color=(1, 0.3, 0.3, 1)
        )
        self.game_over_overlay.add_widget(game_over_title)
        
        self.final_score_label = Label(
            text='Score: 0',
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            font_size='24sp'
        )
        self.game_over_overlay.add_widget(self.final_score_label)
        
        self.new_record_label = Label(
            text='NUEVO RÉCORD!',
            pos_hint={'center_x': 0.5, 'center_y': 0.52},
            font_size='16sp',
            color=(1, 0.9, 0.3, 1),
            bold=True,
            opacity=0
        )
        self.game_over_overlay.add_widget(self.new_record_label)
        
        retry_btn = Button(
            text='Reintentar',
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            size_hint=(0.5, 0.1),
            font_size='18sp',
            background_color=(0.2, 0.7, 0.3, 1)
        )
        retry_btn.bind(on_press=self.on_retry_button)
        self.game_over_overlay.add_widget(retry_btn)
        
        exit_btn = Button(
            text='Salir',
            pos_hint={'center_x': 0.5, 'center_y': 0.28},
            size_hint=(0.5, 0.1),
            font_size='18sp',
            background_color=(0.7, 0.2, 0.2, 1)
        )
        exit_btn.bind(on_press=self.on_exit_button)
        self.game_over_overlay.add_widget(exit_btn)
        
        self.add_widget(self.game_over_overlay)
    
    def _update_overlay_bg(self, instance, value):
        """Update overlay background rectangles"""
        if hasattr(self, 'pause_bg'):
            self.pause_bg.pos = self.pause_overlay.pos
            self.pause_bg.size = self.pause_overlay.size
        if hasattr(self, 'game_over_bg'):
            self.game_over_bg.pos = self.game_over_overlay.pos
            self.game_over_bg.size = self.game_over_overlay.size
    
    def _update_hud(self):
        """Update HUD labels with current game state"""
        self.score_label.text = f'Score: {self.controller.scoring.score}'
        self.level_label.text = f'Level: {self.controller.scoring.level}'
        
        # Lines progress
        lines_in_level = self.controller.scoring.lines_cleared % self.controller.scoring.LINES_PER_LEVEL
        self.lines_label.text = f'Lines: {lines_in_level}/{self.controller.scoring.LINES_PER_LEVEL}'
        
        # Target line
        if self.controller.order_track.target_line_id:
            line_info = self.content_manager.get_line_info(self.controller.order_track.target_line_id)
            if line_info:
                self.target_line_label.text = f'Objetivo: {line_info["name"]}'
            else:
                self.target_line_label.text = f'Objetivo: {self.controller.order_track.target_line_id}'
        
        # Current piece station
        if self.controller.current_piece and self.controller.current_piece.station_label:
            self.station_label_widget.text = f'▶ {self.controller.current_piece.station_label}'
        else:
            self.station_label_widget.text = ''
        
        # Next piece station
        if self.controller.next_piece and self.controller.next_piece.station_label:
            self.next_station_label.text = f'Següent: {self.controller.next_piece.station_label}'
        else:
            self.next_station_label.text = ''
        
        # Update high score display
        if self.controller.scoring.score > self.high_score:
            self.high_score = self.controller.scoring.score
            self.high_score_label.text = f'Best: {self.high_score}'
    
    def show_feedback(self, message):
        """Show temporary feedback message"""
        if message:
            self.feedback_message = message
            self.feedback_timer = self.feedback_duration
            self.feedback_label.text = message
            self.feedback_label.opacity = 1
    
    def update(self, dt):
        """Game loop at 60 FPS - handles gravity and rendering"""
        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_label.opacity = 0
        
        # Only update game logic if running
        if self.controller.state == GameState.RUNNING:
            # Accumulate time for gravity
            self.gravity_timer += dt
            
            # Update gravity interval based on level
            self.gravity_interval = self.controller.scoring.get_fall_speed()
            
            # Apply gravity when timer exceeds interval
            if self.gravity_timer >= self.gravity_interval:
                locked = not self.controller.move_down()
                self.gravity_timer = 0
                
                # Check for feedback after lock
                if locked:
                    feedback = self.controller.get_last_feedback()
                    if feedback:
                        self.show_feedback(feedback)
            
            # Update UI properties
            self.score = self.controller.scoring.score
            self.level = self.controller.scoring.level
            
            # Update HUD
            self._update_hud()
            
            # Redraw every frame
            self.redraw()
        
        elif self.controller.state == GameState.GAME_OVER:
            # Transition to game over overlay
            self._show_game_over()
            # Reset state to prevent repeated calls
            self.controller.state = GameState.PAUSED
    
    def redraw(self, *args):
        """Redraw the game board"""
        self.game_canvas.canvas.clear()
        with self.game_canvas.canvas:
            # Background
            Color(0.1, 0.1, 0.15, 1)
            Rectangle(pos=self.game_canvas.pos, size=self.game_canvas.size)
            
            # Draw grid
            self._draw_grid()
            
            # Draw locked pieces
            self._draw_board()
            
            # Draw current piece
            self._draw_current_piece()
            
            # Draw ghost piece (preview where piece will land)
            self._draw_ghost_piece()
    
    def _draw_grid(self):
        """Draw grid lines"""
        Color(0.3, 0.3, 0.35, 1)
        for x in range(self.controller.board.width + 1):
            px = self.offset_x + x * self.cell_size
            Line(points=[px, self.offset_y, 
                        px, self.offset_y + self.controller.board.height * self.cell_size], 
                 width=1)
        
        for y in range(self.controller.board.height + 1):
            py = self.offset_y + y * self.cell_size
            Line(points=[self.offset_x, py,
                        self.offset_x + self.controller.board.width * self.cell_size, py],
                 width=1)
    
    def _draw_board(self):
        """Draw locked pieces on board"""
        for y in range(self.controller.board.height):
            for x in range(self.controller.board.width):
                if self.controller.board.grid[y][x] != 0:
                    color_value = self.controller.board.grid[y][x]
                    self._draw_cell(x, y, color_value)
    
    def _draw_current_piece(self):
        """Draw the currently falling piece"""
        if self.controller.current_piece:
            piece = self.controller.current_piece
            for y, row in enumerate(piece.get_current_shape()):
                for x, cell in enumerate(row):
                    if cell:
                        px = piece.x + x
                        py = piece.y + y
                        if 0 <= py < self.controller.board.height:
                            self._draw_cell(px, py, piece.color)
    
    def _draw_ghost_piece(self):
        """Draw ghost piece showing where current piece will land"""
        if self.controller.current_piece:
            ghost_y = self.controller.get_ghost_y()
            piece = self.controller.current_piece
            
            Color(0.5, 0.5, 0.5, 0.3)
            for y, row in enumerate(piece.get_current_shape()):
                for x, cell in enumerate(row):
                    if cell:
                        px = self.offset_x + (piece.x + x) * self.cell_size
                        py = self.offset_y + (ghost_y + y) * self.cell_size
                        if ghost_y + y < self.controller.board.height:
                            Rectangle(pos=(px + 1, py + 1), 
                                    size=(self.cell_size - 2, self.cell_size - 2))
    
    def _draw_cell(self, grid_x, grid_y, color_id):
        """Draw a single cell"""
        colors = {
            1: (0, 1, 1, 1),      # Cyan - I
            2: (0, 0, 1, 1),      # Blue - J
            3: (1, 0.5, 0, 1),    # Orange - L
            4: (1, 1, 0, 1),      # Yellow - O
            5: (0, 1, 0, 1),      # Green - S
            6: (0.5, 0, 0.5, 1),  # Purple - T
            7: (1, 0, 0, 1),      # Red - Z
        }
        
        color = colors.get(color_id, (0.5, 0.5, 0.5, 1))
        Color(*color)
        
        px = self.offset_x + grid_x * self.cell_size
        py = self.offset_y + grid_y * self.cell_size
        
        # Main cell
        Rectangle(pos=(px + 1, py + 1), 
                 size=(self.cell_size - 2, self.cell_size - 2))
        
        # Highlight
        Color(color[0] * 1.3, color[1] * 1.3, color[2] * 1.3, 0.5)
        Line(rectangle=(px + 2, py + 2, self.cell_size - 4, self.cell_size - 4), width=1)
    
    def on_keyboard_down(self, window, key, *args):
        """Handle keyboard input"""
        if key in [276, 97]:  # Left arrow or A
            self.controller.move_left()
        elif key in [275, 100]:  # Right arrow or D
            self.controller.move_right()
        elif key in [274, 115]:  # Down arrow or S (soft drop)
            self.controller.move_down()
        elif key in [273, 119]:  # Up arrow or W (rotate)
            self.controller.rotate()
        elif key == 32:  # Space (hard drop)
            self.controller.hard_drop()
        elif key == 112:  # P (pause)
            self.controller.toggle_pause()
            self._update_pause_overlay()
        elif key == 114:  # R (restart)
            if self.controller.state == GameState.GAME_OVER:
                self.on_retry_button(None)
            else:
                self.controller.reset()
                self.gravity_timer = 0
                self._hide_overlays()
        
        self.redraw()
    
    def on_touch_down(self, touch):
        """Handle touch down - start gesture tracking"""
        if self.controller.state == GameState.GAME_OVER:
            return True
        
        # Record touch start for gesture detection
        self.touch_start_pos = touch.pos
        self.touch_start_time = Clock.get_time()
        
        return True
    
    def on_touch_up(self, touch):
        """Handle touch up - process gestures"""
        if self.controller.state == GameState.GAME_OVER or not self.touch_start_pos:
            return True
        
        # Calculate touch movement
        dx = touch.pos[0] - self.touch_start_pos[0]
        dy = touch.pos[1] - self.touch_start_pos[1]
        distance = (dx**2 + dy**2)**0.5
        duration = Clock.get_time() - self.touch_start_time
        
        # Detect gesture type
        if distance < self.swipe_threshold and duration < self.tap_time_threshold:
            # TAP - Rotate
            self.controller.rotate()
        
        elif distance >= self.swipe_threshold:
            # SWIPE - check direction
            abs_dx = abs(dx)
            abs_dy = abs(dy)
            
            if abs_dx > abs_dy:
                # Horizontal swipe
                if dx > 0:
                    # Swipe RIGHT
                    self.controller.move_right()
                else:
                    # Swipe LEFT
                    self.controller.move_left()
            else:
                # Vertical swipe
                if dy < 0:
                    # Swipe DOWN - soft drop or hard drop
                    if abs_dy > self.swipe_threshold * 2:
                        # Long swipe - hard drop
                        self.controller.hard_drop()
                    else:
                        # Short swipe - soft drop
                        for _ in range(3):
                            if not self.controller.move_down():
                                break
                else:
                    # Swipe UP - could be used for hold (future)
                    pass
        
        # Reset touch tracking
        self.touch_start_pos = None
        self.redraw()
        
        return True
    
    def on_pause_button(self, instance):
        """Handle pause button press"""
        self.controller.toggle_pause()
        self._update_pause_overlay()
    
    def on_resume_button(self, instance):
        """Handle resume button press"""
        self.controller.resume()
        self._update_pause_overlay()
    
    def on_retry_button(self, instance):
        """Handle retry button press"""
        # Save session data
        self.persistence.save_session(
            self.controller.scoring.score,
            self.controller.scoring.level,
            self.controller.scoring.lines_cleared
        )
        
        # Reset game
        self.controller.reset()
        self.gravity_timer = 0
        self._hide_overlays()
        self.redraw()
    
    def on_exit_button(self, instance):
        """Handle exit button press"""
        # Save session data
        self.persistence.save_session(
            self.controller.scoring.score,
            self.controller.scoring.level,
            self.controller.scoring.lines_cleared
        )
        
        # Exit app
        App.get_running_app().stop()
    
    def _update_pause_overlay(self):
        """Show/hide pause overlay"""
        if self.controller.is_paused():
            self.pause_overlay.opacity = 1
            self.pause_button.text = '▶'
        else:
            self.pause_overlay.opacity = 0
            self.pause_button.text = '⏸'
    
    def _show_game_over(self):
        """Show game over overlay"""
        # Update final score
        self.final_score_label.text = f'Score: {self.controller.scoring.score}'
        
        # Check and update high score
        is_new_record = self.persistence.update_high_score(self.controller.scoring.score)
        self.persistence.update_best_level(self.controller.scoring.level)
        self.persistence.add_lines_cleared(self.controller.scoring.lines_cleared)
        self.persistence.increment_game_count()
        
        # Show new record badge if applicable
        if is_new_record:
            self.new_record_label.opacity = 1
            self.high_score = self.controller.scoring.score
            self.high_score_label.text = f'Best: {self.high_score}'
        else:
            self.new_record_label.opacity = 0
        
        # Show overlay
        self.game_over_overlay.opacity = 1
    
    def _hide_overlays(self):
        """Hide all overlays"""
        self.pause_overlay.opacity = 0
        self.game_over_overlay.opacity = 0
        self.pause_button.text = '⏸'


class TetrisApp(App):
    """Main Kivy application"""
    
    def build(self):
        self.title = "Metro Tetris"
        game = TetrisGame()
        return game


if __name__ == "__main__":
    TetrisApp().run()
