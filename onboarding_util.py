"""
Utility script to manage onboarding flag for testing
"""
from core.settings import SettingsManager
import sys


def show_status():
    """Show current onboarding status"""
    settings = SettingsManager()
    flag = settings.get('has_completed_onboarding', False)
    print(f"\nCurrent onboarding status: {'COMPLETED' if flag else 'NOT COMPLETED'}")
    return flag


def reset_onboarding():
    """Reset onboarding flag to False (for testing)"""
    settings = SettingsManager()
    settings.set('has_completed_onboarding', False)
    print("\n✓ Onboarding flag reset to False")
    print("  Next game launch will show onboarding")


def complete_onboarding():
    """Set onboarding flag to True (skip onboarding)"""
    settings = SettingsManager()
    settings.set('has_completed_onboarding', True)
    print("\n✓ Onboarding flag set to True")
    print("  Next game launch will skip onboarding")


def main():
    print("=" * 50)
    print("ONBOARDING FLAG MANAGER")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python onboarding_util.py status   - Show current status")
        print("  python onboarding_util.py reset    - Reset flag (show onboarding)")
        print("  python onboarding_util.py complete - Complete flag (skip onboarding)")
        show_status()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    elif command == "reset":
        reset_onboarding()
        show_status()
    elif command == "complete":
        complete_onboarding()
        show_status()
    else:
        print(f"\nUnknown command: {command}")
        print("Use: status, reset, or complete")


if __name__ == '__main__':
    main()
