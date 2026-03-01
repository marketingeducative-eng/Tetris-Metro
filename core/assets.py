"""
Asset Manager - Texture atlas loading with fallback to solid colors
"""
from pathlib import Path


class AssetManager:
    """Manages game textures and visual assets"""
    
    # Color palette (fallback when no textures)
    FALLBACK_COLORS = {
        0: (0.15, 0.15, 0.15, 1),      # Empty
        1: (0.0, 0.8, 0.8, 1),          # I - Cyan
        2: (0.9, 0.8, 0.0, 1),          # O - Yellow
        3: (0.6, 0.2, 0.8, 1),          # T - Purple
        4: (0.0, 0.8, 0.2, 1),          # S - Green
        5: (0.9, 0.1, 0.1, 1),          # Z - Red
        6: (0.1, 0.3, 0.9, 1),          # J - Blue
        7: (0.9, 0.5, 0.1, 1)           # L - Orange
    }
    
    HIGHLIGHT_COLORS = {
        0: (0.2, 0.2, 0.2, 1),
        1: (0.2, 1.0, 1.0, 1),
        2: (1.0, 1.0, 0.3, 1),
        3: (0.8, 0.5, 1.0, 1),
        4: (0.3, 1.0, 0.5, 1),
        5: (1.0, 0.3, 0.3, 1),
        6: (0.3, 0.5, 1.0, 1),
        7: (1.0, 0.7, 0.3, 1)
    }
    
    SHADOW_COLORS = {
        0: (0.1, 0.1, 0.1, 1),
        1: (0.0, 0.4, 0.4, 1),
        2: (0.5, 0.4, 0.0, 1),
        3: (0.3, 0.1, 0.4, 1),
        4: (0.0, 0.4, 0.1, 1),
        5: (0.5, 0.05, 0.05, 1),
        6: (0.05, 0.15, 0.5, 1),
        7: (0.5, 0.25, 0.05, 1)
    }
    
    def __init__(self, atlas_path='assets/atlas.atlas'):
        """
        Initialize asset manager
        
        Args:
            atlas_path: Path to Kivy atlas file
        """
        self.atlas_path = atlas_path
        self.atlas = None
        self.use_textures = False
        
        self._load_atlas()
    
    def _load_atlas(self):
        """Try to load texture atlas"""
        try:
            from kivy.atlas import Atlas
            
            path = Path(self.atlas_path)
            if path.exists():
                self.atlas = Atlas(str(path))
                self.use_textures = True
                print(f"Atlas loaded: {self.atlas_path}")
            else:
                print(f"Atlas not found, using fallback colors")
                self.use_textures = False
        except Exception as e:
            print(f"Could not load atlas: {e}")
            self.use_textures = False
    
    def get_tile_texture(self, color_id):
        """
        Get texture for tile
        
        Args:
            color_id: 0-7 tetromino color ID
        
        Returns:
            Kivy texture or None (use color fallback)
        """
        if not self.use_textures or not self.atlas:
            return None
        
        texture_name = f'tile_{color_id}'
        return self.atlas.get(texture_name)
    
    def get_color(self, color_id, variant='normal'):
        """
        Get RGBA color tuple
        
        Args:
            color_id: 0-7
            variant: 'normal', 'highlight', 'shadow'
        
        Returns:
            (r, g, b, a) tuple
        """
        if variant == 'highlight':
            return self.HIGHLIGHT_COLORS.get(color_id, (1, 1, 1, 1))
        elif variant == 'shadow':
            return self.SHADOW_COLORS.get(color_id, (0, 0, 0, 1))
        else:
            return self.FALLBACK_COLORS.get(color_id, (0.5, 0.5, 0.5, 1))
    
    def get_ghost_color(self, color_id):
        """Get semi-transparent color for ghost piece"""
        color = self.get_color(color_id)
        return (color[0], color[1], color[2], 0.3)
