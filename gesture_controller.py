import cv2
import numpy as np
import time
import config
from action_executor import ActionExecutor
from gesture_recognition import GestureRecognizerEnhanced
from hand_detection import HandDetectorEnhanced

# Try to import ML modules (optional)
try:
    from gesture_recognition import MLGestureRecognizer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ ML modules not found. Using rule-based recognition only.")

class GestureController:
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        
        # Initialize detectors
        self.detector = HandDetectorEnhanced()
        self.rule_recognizer = GestureRecognizerEnhanced(config)
        self.executor = ActionExecutor()
        
        # Initialize ML recognizer (optional)
        self.use_ml = False
        self.ml_recognizer = None
        self.load_ml_model()
        
        # Mode settings
        self.current_mode = 'mouse_mode'
        self.last_mode_switch = 0
        
        # For ML confidence tracking
        self.consecutive_predictions = []
        self.prediction_threshold = 3 
        
    def load_ml_model(self, model_path="gesture_models/default_model.pkl"):
        """Load ML model if available"""
        if not ML_AVAILABLE: return
        import os
        if os.path.exists(model_path):
            try:
                self.ml_recognizer = MLGestureRecognizer(model_path)
                self.use_ml = True
                print(f"✅ ML gesture model loaded")
            except Exception as e:
                print(f"❌ Failed to load ML model: {e}")
                self.use_ml = False
    
    def recognize_gesture(self, lm_list, fingers):
        """Recognize gesture using either ML or rule-based"""
        if len(lm_list) == 0: return 'idle', 0
        
        gesture, confidence = 'idle', 0
        
        if self.use_ml and self.ml_recognizer:
            ml_gesture, ml_confidence = self.ml_recognizer.recognize(lm_list)
            self.consecutive_predictions.append(ml_gesture)
            if len(self.consecutive_predictions) > self.prediction_threshold:
                self.consecutive_predictions.pop(0)
            
            if len(self.consecutive_predictions) == self.prediction_threshold:
                if all(p == ml_gesture for p in self.consecutive_predictions):
                    if ml_confidence > 0.7:
                        gesture, confidence = ml_gesture, ml_confidence
        
        if gesture == 'idle' or confidence < 0.5:
            rule_gesture = self.rule_recognizer.recognize_gesture(lm_list, fingers, self.current_mode)
            if rule_gesture != 'idle':
                gesture, confidence = rule_gesture, 0.8
        return gesture, confidence

    def execute_action(self, gesture, lm_list, img):
        """Processes the gesture and executes hardware commands via the executor."""
        
        # --- 1. MODE SWITCHING (Global Priority) ---
        if gesture == 'switch_mode':
            current_time = time.time()
            if current_time - self.last_mode_switch > 1.5:
                self.current_mode = 'presentation_mode' if self.current_mode == 'mouse_mode' else 'mouse_mode'
                self.last_mode_switch = current_time
                print(f"🔄 Mode Switched to: {self.current_mode}")
            return # Don't do other actions while switching

        # --- 2. MOUSE MODE LOGIC ---
        if self.current_mode == 'mouse_mode':
            # Handle Scrolling (Crucial: Reset scroll anchor if NOT scrolling)
            if gesture == 'scroll':
                # Use Middle Finger Tip (12) for scroll tracking
                self.executor.scroll(lm_list[12][2])
                cv2.putText(img, "Scrolling...", (img.shape[1]//2, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
            else:
                self.executor.reset_scroll() # Prevents "jumps" when returning to scroll

            # Action Prioritization
            if gesture == 'left_click':
                self.executor.left_click()
                cv2.circle(img, (lm_list[8][1], lm_list[8][2]), 15, (0, 255, 0), cv2.FILLED)
            
            elif gesture == 'right_click':
                self.executor.right_click()
                cv2.circle(img, (lm_list[12][1], lm_list[12][2]), 15, (0, 0, 255), cv2.FILLED)
            
            elif gesture == 'move' or gesture == 'idle':
                # Map Index Tip (8) to screen
                self.executor.move_mouse(lm_list[8][1], lm_list[8][2], img.shape[1], img.shape[0])

        # --- 3. PRESENTATION MODE LOGIC ---
        elif self.current_mode == 'presentation_mode':
            if gesture == 'next_slide':
                self.executor.next_slide()
                cv2.putText(img, "NEXT >>", (img.shape[1]-200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
            
            elif gesture == 'previous_slide':
                self.executor.previous_slide()
                cv2.putText(img, "<< PREV", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    def run(self):
        print(f"\n🚀 GestureX Active | Mode: {self.current_mode}")
        while True:
            success, img = self.cap.read()
            if not success: break
            
            img = cv2.flip(img, 1)
            img = self.detector.find_hands(img, draw=True)
            lm_list, bbox = self.detector.find_position(img)
            
            if len(lm_list) != 0:
                fingers = self.detector.fingers_up()
                gesture, confidence = self.recognize_gesture(lm_list, fingers)
                
                # Combined logic execution
                self.execute_action(gesture, lm_list, img)
                self.draw_info(img, gesture, confidence, fingers)
            
            # UI Overlays
            ml_status = f"ML: {'ON' if self.use_ml else 'OFF'}"
            cv2.putText(img, ml_status, (img.shape[1] - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if self.use_ml else (0, 0, 255), 2)
            cv2.imshow("GestureX - AI Touchless Control", img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'): break
            elif key == ord('m'): self.use_ml = not self.use_ml
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def draw_info(self, img, gesture, confidence, fingers):
        mode_text = f"MODE: {self.current_mode.upper()}"
        cv2.putText(img, mode_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        if confidence > 0:
            cv2.putText(img, f"GESTURE: {gesture}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

if __name__ == "__main__":
    controller = GestureController()
    controller.run()