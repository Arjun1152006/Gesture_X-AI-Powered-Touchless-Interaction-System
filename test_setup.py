#!/usr/bin/env python3
"""
GestureX - Installation Test Script
Run this to verify all libraries are properly installed
"""

import sys
import importlib

def test_import(module_name):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {module_name:15} - version {version}")
        return True
    except ImportError as e:
        print(f"❌ {module_name:15} - Not installed: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("GestureX - Installation Test")
    print("="*50)
    
    # Test Python version
    print(f"\n🐍 Python version: {sys.version}")
    
    # Test required libraries
    print("\n📦 Testing required libraries:")
    print("-" * 40)
    
    libraries = [
        'cv2',           # OpenCV
        'mediapipe',     # MediaPipe
        'numpy',         # NumPy
        'pyautogui',     # PyAutoGUI
        'PIL',           # Pillow
        'pynput'         # Pynput
    ]
    
    results = [test_import(lib) for lib in libraries]
    
    # Summary
    print("\n" + "="*50)
    if all(results):
        print("✅ SUCCESS! All libraries are installed correctly!")
        print("\nYou can now run: python main.py")
    else:
        print("❌ Some libraries are missing. Please run the installation command:")
        print("\npip install opencv-python mediapipe pyautogui numpy pillow pynput")
    print("="*50)

if __name__ == "__main__":
    main()