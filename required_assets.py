"""
Required Assets Configuration for Pròxima Parada

This list defines all assets that must be present for the game to function.
Used by asset_manager.validate_required_assets() at startup.

Place all assets in the data/ directory:
  data/
    sounds/
    fonts/
"""

# List of required assets relative to project root
REQUIRED_ASSETS = [
    # Add your required sound files here
    # 'data/sounds/bell.wav',
    # 'data/sounds/station_arrive.wav',
    # 'data/sounds/game_over.wav',
    
    # Add your required font files here
    # 'data/fonts/main.ttf',
]

# Optional: Assets that should be present but won't fail if missing
OPTIONAL_ASSETS = [
    # 'data/sounds/background_music.wav',
]


def get_required_assets():
    """Get the list of required assets."""
    return REQUIRED_ASSETS


def get_optional_assets():
    """Get the list of optional assets."""
    return OPTIONAL_ASSETS
