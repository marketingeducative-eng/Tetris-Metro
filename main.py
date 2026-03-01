"""
Pròxima Parada - Barcelona Metro Game
Main entry point launches only ProximaParada
"""
import os
import sys
import logging
import faulthandler
import threading

# Enable faulthandler to dump stack traces on crash or hang
faulthandler.enable(all_threads=True)

def dump_later():
    """Dump stack traces of all threads after 5 seconds (for debugging hangs)"""
    print("🔍 FAULTHANDLER: Dumping all thread stacks after 5s...", flush=True)
    faulthandler.dump_traceback()

# Start timer to dump traces (helps detect hangs during startup)
threading.Timer(5.0, dump_later).start()

def cp(msg):
    print(f"✅ CP: {msg}", flush=True)

cp("main.py start")

# Reduce Kivy console spam
os.environ['KIVY_NO_CONSOLELOG'] = '1'

# Configure logging before importing other modules
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(levelname)s: %(message)s'
)

cp("before importing asset_manager")
from asset_manager import validate_required_assets
cp("after importing asset_manager")

cp("before importing required_assets")
from required_assets import get_required_assets
cp("after importing required_assets")

cp("before importing game_propera_parada (main kivy app)")
from game_propera_parada import ProximaParadaApp
cp("after importing game_propera_parada")


def startup_validation():
    """
    Perform startup validation checks.
    
    This function runs before the app UI loads to ensure the app
    is in a valid state. If validation fails, the app exits gracefully.
    
    Returns:
        bool: True if validation passed, False otherwise
    """
    print("🔍 Starting up asset validation...")
    
    try:
        required_assets = get_required_assets()
        
        if required_assets:
            print(f"📦 Validating {len(required_assets)} required asset(s)...")
            validate_required_assets(required_assets)
            print("✓ Asset validation passed")
        else:
            print("ℹ️ No required assets configured")
        
        return True
    
    except RuntimeError as e:
        print(f"❌ Asset validation failed:")
        print(f"   {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during startup validation:")
        print(f"   {str(e)}")
        return False


if __name__ == '__main__':
    cp("entering __main__ block")
    print("🚇 Launching Pròxima Parada - Barcelona Metro Game...")
    
    # Validate assets before creating the app
    cp("before startup_validation()")
    if not startup_validation():
        print("⛔ App terminating due to validation failure")
        sys.exit(1)
    cp("after startup_validation()")
    
    # Parse command-line arguments for game modes
    direction_mode = '--direction' in sys.argv
    practice_mode = '--practice' in sys.argv
    
    # Create and run the app
    cp("before creating ProximaParadaApp instance")
    app = ProximaParadaApp(
        practice_mode=practice_mode,
        direction_mode=direction_mode
    )
    cp("after creating ProximaParadaApp instance")
    
    print("✓ App initialized. Starting...")
    cp("before app.run()")
    app.run()
    cp("after app.run()")
    
    print("🛑 Game ended")


