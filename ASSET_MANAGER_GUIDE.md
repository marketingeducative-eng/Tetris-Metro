"""
Asset Management System - Usage Guide
=====================================

This guide explains how to use the robust asset management system
for the Pròxima Parada game on both desktop and Android.

OVERVIEW
--------
The asset management system provides:
  ✓ Safe asset resolution for desktop and Android (APK)
  ✓ No hardcoded paths or working directory dependencies
  ✓ Runtime validation to catch missing assets early
  ✓ Detailed logging for debugging
  ✓ Production-ready error handling

PROJECT STRUCTURE
-----------------
After setup, your project should look like:

    main.py
    buildozer.spec
    asset_manager.py
    required_assets.py
    game_propera_parada.py
    data/
        sounds/
            bell.wav
            error.wav
            success.wav
        fonts/
            main.ttf
            mono.ttf


SETUP STEPS
-----------

1. Define Required Assets
   
   Edit required_assets.py and list all your assets:
   
       REQUIRED_ASSETS = [
           'data/sounds/bell.wav',
           'data/sounds/error.wav',
           'data/fonts/main.ttf',
       ]
   
   Place the actual files in the data/ directory structure.

2. Update buildozer.spec
   
   Ensure these lines are in your buildozer.spec:
   
       source.dir = .
       source.include_exts = py,png,jpg,kv,atlas,json,wav,ttf
   
   Add any additional file extensions used by your assets.

3. Assets are automatically validated at startup
   
   main.py calls validate_required_assets() before the app UI loads.
   If any assets are missing, the app fails gracefully with clear errors.


BASIC USAGE
-----------

In your game code, use asset_manager to load assets:

    from asset_manager import get_asset_path
    
    # Get the path to an asset
    sound_path = get_asset_path('data/sounds/bell.wav')
    
    # Use with Kivy
    from kivy.core.audio import SoundLoader
    sound = SoundLoader.load(sound_path)
    sound.play()
    
    # Use with fonts
    font_path = get_asset_path('data/fonts/main.ttf')
    
    from kivy.uix.label import Label
    label = Label(font_name=font_path, font_size='20sp')


RUNTIME VALIDATION
------------------

The system validates all required assets at startup:

    from asset_manager import validate_required_assets
    
    assets_to_check = [
        'data/sounds/critical_sound.wav',
        'data/fonts/main.ttf',
    ]
    
    try:
        validate_required_assets(assets_to_check)
        print("All assets ready!")
    except RuntimeError as e:
        print(f"Missing assets: {e}")
        sys.exit(1)


DEBUGGING
---------

List all available assets:

    from asset_manager import list_available_assets
    
    sounds = list_available_assets('data/sounds')
    for sound in sounds:
        print(sound)

Enable debug logging:

    import logging
    logging.getLogger('asset_manager').setLevel(logging.DEBUG)


ANDROID CONSIDERATIONS
-----------------------

When packaging for Android with Buildozer:

1. Assets must be in source.dir directory structure:
   ✓ data/sounds/ → included in APK
   ✓ data/fonts/ → included in APK

2. The asset_manager automatically detects Android environment:
   - Uses Kivy's resource system when available
   - Falls back to app directory resolution

3. buildozer.spec must include asset file types:
   
   source.include_exts = py,png,jpg,kv,atlas,json,wav,ttf,mp3,ogg

4. For audio/media files, ensure:
   - Files are in data/sounds/
   - File formats supported by platform (WAV, OGG, MP3)
   - buildozer.spec includes the extensions


TROUBLESHOOTING
---------------

Problem: "Asset not found: data/sounds/bell.wav"

  Solutions:
  1. Verify file exists: data/sounds/bell.wav
  2. Check file path is correct (case-sensitive on Linux/Android)
  3. Verify buildozer.spec includes the file type extension
  4. Check required_assets.py has correct relative path

Problem: Different behavior on desktop vs Android

  Solutions:
  1. Check asset paths are relative (no absolute paths)
  2. Verify assets exist in data/ subdirectories
  3. Remove any CWD-dependent code (chdir(), relative paths from CWD)
  4. Test with: python main.py on desktop, buildozer android debug on Android

Problem: Long startup time after asset validation

  Solutions:
  1. Only include necessary assets in REQUIRED_ASSETS
  2. Use list_available_assets() to debug what's being checked
  3. Move optional assets to OPTIONAL_ASSETS


EXAMPLES
--------

Example 1: Loading a sound
    
    from asset_manager import get_asset_path
    from kivy.core.audio import SoundLoader
    
    # Get asset path (works on desktop and Android)
    path = get_asset_path('data/sounds/bell.wav')
    
    # Load and play
    sound = SoundLoader.load(path)
    sound.play()


Example 2: Using a custom font

    from asset_manager import get_asset_path
    from kivy.uix.label import Label
    
    font_path = get_asset_path('data/fonts/main.ttf')
    label = Label(
        text='Score: 100',
        font_name=font_path,
        font_size='18sp'
    )


Example 3: Validating images at startup

    # In required_assets.py
    REQUIRED_ASSETS = [
        'data/images/icon.png',
        'data/images/background.jpg',
    ]
    
    # Validation happens automatically in main.py


Example 4: Conditional optional assets

    from asset_manager import list_available_assets
    
    # Get all available sounds
    sounds = list_available_assets('data/sounds')
    
    # Load only those that are actually present
    for sound_file in sounds:
        # Use sound_file...
        pass


API REFERENCE
-------------

asset_manager.get_asset_path(relative_path: str) -> str
    Resolve an asset path safely for desktop and Android.
    Raises RuntimeError if asset not found.
    
    Args:
        relative_path: Relative path to asset (e.g., 'data/sounds/bell.wav')
    Returns:
        Absolute path to asset
    Raises:
        RuntimeError: If asset not found
        ValueError: If path is invalid

asset_manager.validate_required_assets(required_assets: List[str]) -> None
    Validate that all required assets exist.
    Called automatically at app startup via main.py.
    
    Args:
        required_assets: List of relative asset paths
    Raises:
        RuntimeError: If any assets are missing

asset_manager.list_available_assets(directory: str = "data") -> List[str]
    List all available assets in a directory.
    
    Args:
        directory: Directory to scan (relative to app root)
    Returns:
        List of available asset paths

required_assets.get_required_assets() -> List[str]
    Get the list of required assets.
    
    Returns:
        List of required asset paths

required_assets.get_optional_assets() -> List[str]
    Get the list of optional assets.
    
    Returns:
        List of optional asset paths


BEST PRACTICES
--------------

✓ DO:
  - Keep all assets in data/ subdirectories
  - Use relative paths (data/sounds/file.wav)
  - Call validate_required_assets() at startup
  - Test on both desktop and Android
  - Use meaningful file names
  - Document asset requirements

✗ DON'T:
  - Use absolute paths (/full/path/to/file.wav)
  - Hardcode paths in game code
  - Rely on current working directory
  - Mix asset management approaches
  - Skip the startup validation
  - Use symlinks or non-standard structures


MIGRATION GUIDE (if updating existing code)
-------------------------------------------

If your project already has assets in different locations:

1. Create data/ directory structure
2. Move assets to data/sounds/ and data/fonts/
3. Update asset paths from:
   OLD: os.path.join(APP_DIR, 'sounds', 'bell.wav')
   NEW: get_asset_path('data/sounds/bell.wav')
4. Update all SoundLoader.load() calls
5. Update all font_name= properties
6. Test thoroughly on desktop first
7. Build and test on Android


PERFORMANCE NOTES
-----------------

- Asset validation happens once at startup
- Path resolution is cached by Kivy's resource system on Android
- No performance impact during gameplay
- Logging is debug-level and doesn't affect production

For optimal Android build size:
- Only include assets actually used by the game
- Compress audio files (OGG > MP3 > WAV)
- Use efficient font files
- Remove unused asset files before building
"""
