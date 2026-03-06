import pyautogui
import time
import numpy as np

class ActionExecutor:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0 
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Movement Smoothing
        self.smoothening = 7  
        self.prev_x, self.prev_y_mouse = self.screen_width // 2, self.screen_height // 2
        
        # Cooldowns
        self.last_click_time = 0
        self.click_cooldown = 0.35
        self.last_slide_time = 0
        self.slide_cooldown = 1.0 # Stabilizes presentation slides
        
        self.prev_hand_y = None
        self.scroll_sensitivity = 4.0 

    def move_mouse(self, hand_x, hand_y, frame_width, frame_height):
        screen_x = np.interp(hand_x, [150, frame_width - 150], [0, self.screen_width])
        screen_y = np.interp(hand_y, [100, frame_height - 200], [0, self.screen_height])
        self.curr_x = self.prev_x + (screen_x - self.prev_x) / self.smoothening
        self.curr_y_mouse = self.prev_y_mouse + (screen_y - self.prev_y_mouse) / self.smoothening
        safe_x = np.clip(self.curr_x, 2, self.screen_width - 2)
        safe_y = np.clip(self.curr_y_mouse, 2, self.screen_height - 2)
        pyautogui.moveTo(int(safe_x), int(safe_y), _pause=False)
        self.prev_x, self.prev_y_mouse = self.curr_x, self.curr_y_mouse

    def left_click(self):
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.click(button='left')
            self.last_click_time = current_time
            return True
        return False

    def right_click(self):
        """FIXED: Uses explicit button parameter for better compatibility"""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            pyautogui.rightClick()
            self.last_click_time = current_time
            print("Action: Right Click")
            return True
        return False

    def scroll(self, hand_y):
        """FIXED: More sensitive scrolling logic"""
        if self.prev_hand_y is not None:
            diff = hand_y - self.prev_hand_y
            scroll_amount = int(diff * -self.scroll_sensitivity)
            if abs(scroll_amount) > 1: # Sensitive to slight movements
                pyautogui.scroll(scroll_amount)
        self.prev_hand_y = hand_y

    def reset_scroll(self):
        """Prevents vertical jumping when starting a new scroll"""
        self.prev_hand_y = None

    def next_slide(self):
        current_time = time.time()
        if current_time - self.last_slide_time > self.slide_cooldown:
            pyautogui.press('right')
            self.last_slide_time = current_time
            print("Action: Next Slide")

    def previous_slide(self):
        current_time = time.time()
        if current_time - self.last_slide_time > self.slide_cooldown:
            pyautogui.press('left')
            self.last_slide_time = current_time
            print("Action: Previous Slide")