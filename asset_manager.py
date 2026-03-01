"""
Asset Management System for Kivy Android Project

This module provides safe, Android-compatible asset resolution.
Works seamlessly on both desktop and APK environments.

Key functions:
  - get_asset_path(): Resolves asset paths safely
  - validate_required_assets(): Verifies assets exist at startup
"""

import os
import sys
import time
import traceback
import logging
from pathlib import Path
from typing import List, Optional

# Configure logging for asset management
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[AssetManager] %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def cp(msg):
    print(f"✅ CP: {msg}", flush=True)


def _is_android() -> bool:
    """
    Detect if the app is running on Android.
    
    Returns:
        bool: True if running in Android environment
    """
    try:
        from jnius import autoclass  # type: ignore[import-not-found]
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        return True
    except (ImportError, AttributeError):
        return False


def _get_app_data_dir() -> str:
    """
    Get the application root directory (desktop only).
    
    IMPORTANT: This function should NOT be used on Android to access assets.
    On Android, assets in the APK must be accessed via resource_find() only.
    
    On Android: May be called after app creation for non-asset data
    On Desktop: Returns directory where main.py is located
    
    Returns:
        str: Absolute path to app root directory
        
    Raises:
        RuntimeError: If app directory cannot be determined
    """
    if _is_android():
        # Do NOT try App.get_running_app() - it's None during early startup
        # Android assets must use resource_find() only, not this function
        raise RuntimeError(
            "_get_app_data_dir() cannot be used on Android. "
            "Use get_asset_path() or resource_find() instead."
        )
    
    # Desktop: Get directory where main.py is located
    if hasattr(sys, 'frozen'):
        # PyInstaller executable
        return os.path.dirname(sys.executable)
    
    # Normal Python script - use main module's directory
    main_module = sys.modules.get('__main__')
    if main_module and hasattr(main_module, '__file__') and main_module.__file__:
        return os.path.dirname(os.path.abspath(main_module.__file__))
    
    # Cannot determine app directory - must raise, not fallback to CWD
    raise RuntimeError(
        "Cannot determine app directory. "
        "main.__file__ is not available. "
        "Ensure the script is run directly as 'python main.py'."
    )


def get_asset_path(relative_path: str) -> str:
    """
    Resolve an asset path safely, working on both desktop and Android.
    
    This function properly handles asset resolution in different environments:
    - Desktop: Resolves relative to the app root directory (where main.py is)
    - Android (APK): Uses Kivy's resource system (ONLY method for APK assets)
    
    Args:
        relative_path: Relative path to the asset (e.g., 'data/sounds/bell.wav')
    
    Returns:
        str: Absolute path to the asset
    
    Raises:
        RuntimeError: If the asset cannot be found
        ValueError: If relative_path is empty or invalid
    
    Examples:
        >>> path = get_asset_path('data/sounds/button_click.wav')
        >>> path = get_asset_path('data/fonts/Arial.ttf')
    """
    if not relative_path or not isinstance(relative_path, str):
        error_msg = f"Invalid asset path: {relative_path!r}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Normalize the path
    relative_path = relative_path.strip()
    
    if _is_android():
        # On Android: ONLY use Kivy's resource finder
        # APK assets are compressed in the APK, NOT on filesystem
        # resource_find() is the ONLY reliable method
        try:
            from kivy.resources import resource_find
            absolute_path = resource_find(relative_path)
            if absolute_path and os.path.exists(absolute_path):
                logger.debug(f"Asset found: {relative_path} -> {absolute_path}")
                return absolute_path
        except Exception as e:
            logger.error(f"resource_find failed: {e}")
        
        # resource_find() did not find the asset
        error_msg = (
            f"Asset not found on Android: {relative_path!r}\n"
            f"The APK may be missing assets or buildozer.spec is incomplete.\n"
            f"Ensure source.include_exts includes the asset file type."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    else:
        # On desktop: resolve relative to app directory
        app_dir = _get_app_data_dir()  # Raises if it cannot determine directory
        absolute_path = os.path.join(app_dir, relative_path)
        
        if os.path.exists(absolute_path):
            logger.debug(f"Asset found: {relative_path} -> {absolute_path}")
            return absolute_path
        
        # Asset not found on desktop
        error_msg = (
            f"Asset not found: {relative_path!r}\n"
            f"Searched in: {app_dir}\n"
            f"Expected path: {absolute_path}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def validate_required_assets(required_assets: List[str]) -> None:
    """
    Validate that all required assets exist at runtime.
    
    This function should be called during app startup to ensure
    all necessary assets are present before the app attempts to use them.
    
    Args:
        required_assets: List of relative asset paths to validate
                        (e.g., ['data/sounds/bell.wav', 'data/fonts/Arial.ttf'])
    
    Raises:
        RuntimeError: If any required assets are missing
    
    Examples:
        >>> required = [
        ...     'data/sounds/bell.wav',
        ...     'data/sounds/error.wav',
        ...     'data/fonts/main.ttf'
        ... ]
        >>> validate_required_assets(required)
    """
    if not required_assets:
        logger.debug("No assets to validate")
        return
    
    missing_assets = []
    found_assets = []
    
    logger.info(f"Validating {len(required_assets)} required asset(s)...")
    
    for asset_path in required_assets:
        try:
            resolved = get_asset_path(asset_path)
            logger.debug(f"✓ Found: {asset_path}")
            found_assets.append(asset_path)
        except (RuntimeError, ValueError) as e:
            logger.warning(f"✗ Missing: {asset_path}")
            missing_assets.append(asset_path)
    
    # Summary
    logger.info(f"Asset validation: {len(found_assets)}/{len(required_assets)} found")
    
    if missing_assets:
        error_msg = (
            f"Asset validation failed: {len(missing_assets)} asset(s) missing:\n"
            + "\n".join(f"  - {asset}" for asset in missing_assets) +
            f"\n\nPlease ensure all required assets are present in the data/ directory."
        )
        logger.critical(error_msg)
        raise RuntimeError(error_msg)
    
    logger.info("✓ All required assets validated successfully")


def list_available_assets(directory: str = "data") -> List[str]:
    """
    List all available assets in a directory.
    
    NOTE: This function only works on desktop.
    On Android, APK assets cannot be listed via filesystem.
    
    Args:
        directory: Directory to scan (relative to app root)
    
    Returns:
        List of available asset paths (desktop only)
        
    Raises:
        RuntimeError: If called on Android
    """
    if _is_android():
        raise RuntimeError(
            "list_available_assets() only works on desktop. "
            "APK assets cannot be listed via filesystem."
        )
    
    app_dir = _get_app_data_dir()  # Raises if unable to determine directory
    full_dir = os.path.join(app_dir, directory)
    
    if not os.path.isdir(full_dir):
        logger.warning(f"Directory not found: {full_dir}")
        return []
    
    assets = []
    for root, dirs, files in os.walk(full_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, app_dir)
            assets.append(rel_path)
    
    logger.debug(f"Found {len(assets)} assets in {directory}/")
    return sorted(assets)


if __name__ == "__main__":
    # Quick test
    logger.info("Asset Manager Module Loaded")
    logger.info(f"Running on Android: {_is_android()}")
    logger.info(f"App data directory: {_get_app_data_dir()}")
