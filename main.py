#!/usr/bin/env python3
"""
GestureX - AI-Powered Touchless Interaction System
Optimized Main Entry File
"""
import sys
import os
import traceback
# ============================================================
# SAFE MODULE IMPORT
# ============================================================
def check_required_files():
    required_files = [
        "gesture_controller.py",
        "hand_detection.py",
        "gesture_recognition.py",
        "action_executor.py",
        "gesture_manager.py",
        "config.py"
    ]
    missing = [f for f in required_files if not os.path.exists(f)]

    if missing:
        print("\n❌ Missing required files:")
        for f in missing:
            print(f"   - {f}")
        print("\nMake sure all project files are in the same directory.")
        sys.exit(1)
def safe_import():
    try:
        from gesture_controller import GestureController
        return GestureController
    except ImportError as e:
        print("\n❌ Import Error:")
        print(e)
        print("\nPossible Causes:")
        print("1. File name mismatch")
        print("2. Circular import")
        print("3. Running from wrong directory")
        sys.exit(1)
# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    print("\n" + "=" * 60)
    print("GestureX - AI Touchless Interaction System")
    print("=" * 60)
    # Ensure script is running from its own directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    check_required_files()
    GestureController = safe_import()

    print("\n📷 Initializing camera and hand detector...")

    try:
        controller = GestureController()

        print("\n✅ System ready!")
        print("\n📋 Instructions:")
        print("  - Show your hand clearly to the camera")
        print("  - Perform configured gestures")
        print("  - Press 'q' to quit")
        print("=" * 60 + "\n")

        controller.run()

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user.")

    except Exception as e:
        print("\n❌ Runtime Error Occurred:")
        print(str(e))
        print("\n🔎 Full Traceback:")
        traceback.print_exc()

        print("\nTroubleshooting Tips:")
        print("1. Ensure camera is connected and not used by another app.")
        print("2. Check proper lighting.")
        print("3. Delete __pycache__ folder and restart.")
        print("4. Reinstall dependencies if needed.")

        sys.exit(1)

    print("\n👋 GestureX stopped successfully. Goodbye!")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()