"""
BoardView - Candy-style Canvas rendering with juicy effects
"""
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Line, Ellipse, RoundedRectangle
from kivy.graphics import PushMatrix, PopMatrix, Scale, Translate
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.graphics.vertex_instructions import Triangle, Quad
import math


class BoardView(Widget):
    """Renders game board with candy-style tiles"""
    
    def __init__(self, cell_size=30, offset_x=0, offset_y=160, grid_height=20, **kwargs):
        super().__init__(**kwargs)
        
        self.cell_size = cell_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.grid_height = grid_height  # Needed to invert Y coordinates
        
        # Candy style settings
        self.tile_corner_radius = 6
        self.tile_padding = 2
        
        # Cached canvas instructions (for performance)
        self.grid_instructions = []
        self.board_instructions = {}  # Dict by (x, y) for reuse
        self.piece_instructions = []
        self.ghost_instructions = []
        
        # State cache to avoid redundant redraws
        self.cached_board = None
        self.cached_piece_cells = None
        self.cached_ghost_cells = None
        
        # Animation state
        self.animating_cells = set()
        
        self.assets = None  # Set externally
        
        # Background gradient
        with self.canvas.before:
            # Dark gradient background
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.pos, size=Window.size)
        
        self._init_grid()
    
    def set_asset_manager(self, asset_manager):
        """Set asset manager for textures/colors"""
        self.assets = asset_manager
    
    def _init_grid(self):
        """Initialize grid with subtle lines"""
        with self.canvas:
            # Very subtle grid lines
            Color(0.15, 0.15, 0.2, 0.3)
            
            # Vertical lines
            for x in range(11):
                line = Line(
                    points=[
                        self.offset_x + x * self.cell_size,
                        self.offset_y,
                        self.offset_x + x * self.cell_size,
                        self.offset_y + self.grid_height * self.cell_size
                    ],
                    width=1
                )
                self.grid_instructions.append(line)
            
            # Horizontal lines
            for y in range(self.grid_height + 1):
                line = Line(
                    points=[
                        self.offset_x,
                        self.offset_y + y * self.cell_size,
                        self.offset_x + 10 * self.cell_size,
                        self.offset_y + y * self.cell_size
                    ],
                    width=1
                )
                self.grid_instructions.append(line)
    
    def render(self, board_grid, current_piece, ghost_y=None):
        """
        Render board state
        
        Args:
            board_grid: 2D array of locked cells
            current_piece: Piece object
            ghost_y: Y position of ghost piece
        """
        # Update board if changed
        if board_grid != self.cached_board:
            self._render_board(board_grid)
            self.cached_board = [row[:] for row in board_grid]
        
        # Update ghost
        ghost_cells = None
        if current_piece and ghost_y is not None:
            ghost_cells = self._get_ghost_cells(current_piece, ghost_y)
        
        if ghost_cells != self.cached_ghost_cells:
            self._render_ghost(ghost_cells)
            self.cached_ghost_cells = ghost_cells
        
        # Update piece
        piece_cells = current_piece.get_cells() if current_piece else None
        if piece_cells != self.cached_piece_cells:
            self._render_piece(piece_cells)
            self.cached_piece_cells = piece_cells
    
    def _render_board(self, grid):
        """Render locked cells with candy style"""
        # Remove cells that no longer exist
        current_cells = set()
        for y, row in enumerate(grid):
            for x, cell_value in enumerate(row):
                if cell_value != 0:
                    current_cells.add((x, y))
        
        # Remove old instructions
        for key in list(self.board_instructions.keys()):
            if key not in current_cells:
                for instr in self.board_instructions[key]:
                    self.canvas.remove(instr)
                del self.board_instructions[key]
        
        # Draw new/updated cells
        with self.canvas:
            for y, row in enumerate(grid):
                for x, cell_value in enumerate(row):
                    if cell_value != 0 and (x, y) not in self.board_instructions:
                        self._draw_cell(x, y, cell_value, 'board')
    
    def _render_piece(self, cells):
        """Render current piece"""
        # Clear previous
        for instr in self.piece_instructions:
            self.canvas.remove(instr)
        self.piece_instructions.clear()
        
        if not cells:
            return
        
        # Draw cells
        with self.canvas:
            for cell in cells:
                self._draw_cell(cell['x'], cell['y'], cell['color'], 'piece')
    
    def _render_ghost(self, cells):
        """Render ghost piece with low alpha candy style"""
        # Clear previous
        for instr in self.ghost_instructions:
            self.canvas.remove(instr)
        self.ghost_instructions.clear()
        
        if not cells:
            return
        
        # Draw ghost with candy style but low alpha
        with self.canvas:
            for cell in cells:
                px = self.offset_x + cell['x'] * self.cell_size + self.tile_padding
                py = self.offset_y + cell['y'] * self.cell_size + self.tile_padding
                size = self.cell_size - self.tile_padding * 2
                
                # Semi-transparent candy tile
                base_color = self.assets.get_color(cell['color']) if self.assets else (1, 1, 1, 1)
                Color(base_color[0], base_color[1], base_color[2], 0.15)
                
                ghost_tile = RoundedRectangle(
                    pos=(px, py),
                    size=(size, size),
                    radius=[self.tile_corner_radius]
                )
                self.ghost_instructions.append(ghost_tile)
                
                # Ghost outline
                Color(1, 1, 1, 0.3)
                ghost_outline = Line(
                    rounded_rectangle=(px, py, size, size, self.tile_corner_radius),
                    width=1.5
                )
                self.ghost_instructions.append(ghost_outline)
    
    def _get_ghost_cells(self, piece, ghost_y):
        """Get ghost piece cells"""
        cells = []
        for cell in piece.get_cells():
            cells.append({
                'x': cell['x'],
                'y': ghost_y + (cell['y'] - piece.y),
                'color': cell['color']
            })
        return cells
    
    def _draw_cell(self, grid_x, grid_y, color_id, layer):
        """Draw candy-style rounded tile with volume effect"""
        if not self.assets:
            return
        
        px = self.offset_x + grid_x * self.cell_size + self.tile_padding
        # Invert Y: grid_y=0 should be at top, grid_y=19 at bottom
        py = self.offset_y + (self.grid_height - 1 - grid_y) * self.cell_size + self.tile_padding
        size = self.cell_size - self.tile_padding * 2
        
        with self.canvas:
            # Get base color
            base_color = self.assets.get_color(color_id)
            
            # Shadow (darker border at bottom)
            shadow_color = self.assets.get_color(color_id, 'shadow')
            Color(*shadow_color)
            shadow = RoundedRectangle(
                pos=(px + 1, py - 1),
                size=(size, size),
                radius=[self.tile_corner_radius]
            )
            
            # Main tile body
            Color(*base_color)
            main_tile = RoundedRectangle(
                pos=(px, py),
                size=(size, size),
                radius=[self.tile_corner_radius]
            )
            
            # Gradient effect (darker at bottom)
            darker = (base_color[0] * 0.7, base_color[1] * 0.7, base_color[2] * 0.7, base_color[3])
            Color(*darker)
            gradient_bottom = RoundedRectangle(
                pos=(px, py),
                size=(size, size * 0.4),
                radius=[self.tile_corner_radius]
            )
            
            # Highlight (glossy top)
            highlight_color = self.assets.get_color(color_id, 'highlight')
            Color(highlight_color[0], highlight_color[1], highlight_color[2], 0.4)
            highlight = RoundedRectangle(
                pos=(px + 2, py + size * 0.6),
                size=(size - 4, size * 0.3),
                radius=[self.tile_corner_radius - 2]
            )
            
            # Inner glow
            Color(1, 1, 1, 0.1)
            inner_glow = RoundedRectangle(
                pos=(px + 3, py + 3),
                size=(size - 6, size - 6),
                radius=[self.tile_corner_radius - 3]
            )
            
            # Store instructions
            instructions = [shadow, main_tile, gradient_bottom, highlight, inner_glow]
            
            if layer == 'board':
                key = (grid_x, grid_y)
                self.board_instructions[key] = instructions
            else:
                self.piece_instructions.extend(instructions)
    
    def animate_piece_lock(self, cells):
        """Squash & stretch animation when piece locks"""
        if not cells:
            return
        
        for cell in cells:
            x, y = cell['x'], cell['y']
            key = (x, y)
            
            if key in self.board_instructions:
                # Mark as animating
                self.animating_cells.add(key)
                
                # Schedule callback to remove from animating set
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.animating_cells.discard(key), 0.2)
    
    def flash_lines(self, line_indices):
        """Flash effect for cleared lines"""
        if not line_indices:
            return
        
        # Create flash rectangles
        flash_instructions = []
        
        with self.canvas:
            for line_y in line_indices:
                py = self.offset_y + line_y * self.cell_size
                
                # White flash
                Color(1, 1, 1, 0.8)
                flash = Rectangle(
                    pos=(self.offset_x, py),
                    size=(10 * self.cell_size, self.cell_size)
                )
                flash_instructions.append(flash)
        
        # Animate fade out
        def remove_flash(dt):
            for instr in flash_instructions:
                self.canvas.remove(instr)
        
        from kivy.clock import Clock
        Clock.schedule_once(remove_flash, 0.15)
    
    def clear_cache(self):
        """Force full redraw next render"""
        self.cached_board = None
        self.cached_piece_cells = None
        self.cached_ghost_cells = None
