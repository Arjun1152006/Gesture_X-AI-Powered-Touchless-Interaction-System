# ============================================
# GESTUREX - ADVANCED CONFIGURATION
# Optimized for Maximum Accuracy & Custom Gestures
# ============================================
import pyautogui
import os
import json
import numpy as np

# ----------------------
# CAMERA SETTINGS
# ----------------------
CAMERA_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FPS = 60  # High FPS for smoother gesture tracking

# ----------------------
# HAND DETECTION SETTINGS
# ----------------------
DETECTION_CONFIDENCE = 0.8  # Increased for maximum accuracy
TRACKING_CONFIDENCE = 0.8
MAX_HANDS = 1

# ----------------------
# GESTURE THRESHOLDS
# ----------------------
PINCH_THRESHOLD = 35         # Distance for clicks
SWIPE_THRESHOLD = 65         # Pixels per frame for slide changes
SMOOTHENING = 4           # Balance between lag and jitter
SCROLL_SENSITIVITY = 2.0     

# ----------------------
# SCREEN RESOLUTION
# ----------------------
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# ----------------------
# GESTURE DEFINITIONS (Optimized)
# ----------------------
# Finger Arrays: [Thumb, Index, Middle, Ring, Pinky] (1=Up, 0=Down)
GESTURES = {
    # --- MOUSE MODE ---
    'MOVE': {
        'name': 'move',
        'fingers': [0, 1, 0, 0, 0],  # Index finger up
        'min_hold': 0.05,
        'cooldown': 0.01
    },
    'LEFT_CLICK': {
        'name': 'left_click',
        'type': 'pinch',
        'fingers': [4, 8],           # THUMB (4) + INDEX (8)
        'threshold': PINCH_THRESHOLD,
        'min_hold': 0.1,
        'cooldown': 0.3
    },
    'RIGHT_CLICK': {
        'name': 'right_click',
        'type': 'pinch',
        'fingers': [8, 12],          # INDEX (8) + MIDDLE (12)
        'threshold': PINCH_THRESHOLD,
        'min_hold': 0.1,
        'cooldown': 0.3
    },
    'SCROLL': {
        'name': 'scroll',
        'fingers': [0, 1, 1, 1, 0],  # 3 FINGERS UP
        'min_hold': 0.05,
        'cooldown': 0.05
    },
    
    # --- PRESENTATION MODE ---
    'NEXT_SLIDE': {
        'name': 'next_slide',
        'type': 'swipe',
        'fingers': [0, 1, 1, 0, 0], 
        'min_hold': 0.15,
    },
    'PREV_SLIDE': {
        'name': 'previous_slide',
        'type': 'swipe',
        'fingers': [0, 1, 0, 0, 1],  
        'min_hold': 0.15,
    },

    # --- GLOBAL ---
    'SWITCH_MODE': {
        'name': 'switch_mode',
        'fingers': [1, 1, 1, 1, 1],  # Full Palm
        'min_hold': 1.0,             # Hold for 1s to switch
        'cooldown': 1.5
    }
}

# ----------------------
# HAND LANDMARK REFERENCE
# ----------------------
# 
HAND_LANDMARKS = {
    'WRIST': 0, 'THUMB_TIP': 4, 'INDEX_TIP': 8, 
    'MIDDLE_TIP': 12, 'RING_TIP': 16, 'PINKY_TIP': 20
}

# ----------------------
# CONFIGURATION MANAGER
# ----------------------
class GestureConfig:
    def __init__(self, config_file="custom_gestures.json"):
        self.config_file = config_file
        self.gestures = self.load_gestures()
        
    def load_gestures(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_gestures()
        return self.get_default_gestures()
    
    def save_gestures(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.gestures, f, indent=4)
    
    def get_default_gestures(self):
        """Standard optimized mapping for logic synchronization"""
        return {
            "mouse_mode": {
                "left_click": {"fingers": [4, 8], "type": "pinch"},
                "right_click": {"fingers": [8, 12], "type": "pinch"},
                "scroll": {"fingers": [0, 1, 1, 1, 0]}
            },
            "presentation_mode": {
                "next_slide": {"fingers": [0, 1, 1, 1, 1], "type": "swipe"}
            },
            "global": {
                "switch_mode": {"fingers": [1, 1, 1, 1, 1]}
            }
        }