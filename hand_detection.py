import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import time

class HandDetectorEnhanced:
    def __init__(self, mode=False, max_hands=1, detection_con=0.8, track_con=0.8):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con,
            model_complexity=1  # 0 = Lite, 1 = Full (more accurate)
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.tip_ids = [4, 8, 12, 16, 20]
        
        # Smoothing filters
        self.position_history = deque(maxlen=5)  # For moving average
        self.kalman_filters = {}  # Kalman filters for each landmark
        
        # Handedness tracking
        self.hand_type = None
        
    def init_kalman(self, landmark_id):
        kalman = cv2.KalmanFilter(4, 2)
        kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                            [0, 1, 0, 0]], np.float32)
        kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                           [0, 1, 0, 1],
                                           [0, 0, 1, 0],
                                           [0, 0, 0, 1]], np.float32)
    
    # CHANGE THIS: Increase process noise to 1e-2 or 1e-3 for more smoothing
    # This tells the filter to ignore small "jitters" from the camera
        self.noise_factor = 1e-2
        kalman.processNoiseCov = np.eye(4, dtype=np.float32) * self.noise_factor
    
    # Measurement noise: how much you trust the camera (higher = smoother)
        kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.8
    
        return kalman
        
    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_rgb.flags.writeable = False
        self.results = self.hands.process(img_rgb)
        img_rgb.flags.writeable = True
        
        if self.results.multi_hand_landmarks:
            for idx, hand_lms in enumerate(self.results.multi_hand_landmarks):
                # Get hand type (left/right)
                if self.results.multi_handedness:
                    self.hand_type = self.results.multi_handedness[idx].classification[0].label
                
                if draw:
                    # Draw with custom styles
                    self.mp_draw.draw_landmarks(
                        img,
                        hand_lms,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_styles.get_default_hand_landmarks_style(),
                        self.mp_styles.get_default_hand_connections_style()
                    )
                    
                    # Draw hand type
                    if self.hand_type:
                        h, w, _ = img.shape
                        x = int(hand_lms.landmark[0].x * w)
                        y = int(hand_lms.landmark[0].y * h)
                        cv2.putText(img, f"{self.hand_type} Hand", (x, y-20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        return img
    
    def find_position(self, img, hand_no=0, draw=True, smooth=True):
        x_list = []
        y_list = []
        self.lm_list = []
        bbox = []
        
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            h, w, c = img.shape
            
            for id, lm in enumerate(my_hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                
                # Apply Kalman filter if enabled
                if smooth:
                    if id not in self.kalman_filters:
                        self.kalman_filters[id] = self.init_kalman(id)
                        self.kalman_filters[id].statePost = np.array([[np.float32(cx)], [np.float32(cy)], [0], [0]], np.float32)
                    kalman = self.kalman_filters[id]
                    measurement = np.array([[np.float32(cx)], [np.float32(cy)]])
                    kalman.correct(measurement)
                    prediction = kalman.predict()
        
                    cx = int(prediction[0][0])
                    cy = int(prediction[1][0])
                
                x_list.append(cx)
                y_list.append(cy)
                self.lm_list.append([id, cx, cy])
                
                if draw:
                    # Different colors for fingertips
                    color = (0, 255, 0) if id in self.tip_ids else (255, 0, 255)
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)
                    
                    # Draw landmark numbers (for debugging)
                    if id in self.tip_ids:
                        cv2.putText(img, str(id), (cx+10, cy-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Get bounding box
            bbox=[]
            if x_list:
                x_min, x_max = min(x_list), max(x_list)
                y_min, y_max = min(y_list), max(y_list)
                bbox = [x_min, y_min, x_max, y_max]
                
                if draw:
                    # Draw bounding box with hand type
                    cv2.rectangle(img, (int(x_min)-20, int(y_min)-20),
                                (int(x_max)+20, int(y_max)+20), (0, 255, 0), 2)
                    
                    # Draw hand type in bounding box
                    if self.hand_type:
                        cv2.putText(img, self.hand_type, (int(x_min), int(y_min)-30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return self.lm_list, bbox
    
    def fingers_up(self):
        """Robust finger detection for Left and Right hands"""
        fingers = []
        
        # Guard clause: ensure landmarks exist
        if not hasattr(self, 'lm_list') or len(self.lm_list) < 21:
            return [0, 0, 0, 0, 0]
        
        # --- THUMB LOGIC ---
        # Thumb is open if the tip (4) is further from the palm than the IP joint (3)
        # Note: In a flipped camera image, 'Right' and 'Left' can be tricky. 
        # Usually, tip.x < joint.x for Right hand thumb open.
        if self.hand_type == "Right":
            if self.lm_list[4][1] < self.lm_list[3][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        else:  # Left hand
            if self.lm_list[4][1] > self.lm_list[3][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        # --- OTHER FINGERS LOGIC (Index, Middle, Ring, Pinky) ---
        # We compare the Tip (y) with the PIP joint (y). 
        # If tip is higher (lower Y value) than PIP, the finger is up.
        for id in range(1, 5):
            tip_id = self.tip_ids[id]
            pip_id = tip_id - 2
            
            if self.lm_list[tip_id][2] < self.lm_list[pip_id][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def find_distance(self, p1, p2, img=None):
        """Enhanced distance calculation with error checking"""
        if len(self.lm_list) <= max(p1, p2):
            return 0, img, [0, 0, 0, 0, 0, 0]
        
        x1, y1 = self.lm_list[p1][1], self.lm_list[p1][2]
        x2, y2 = self.lm_list[p2][1], self.lm_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Calculate Euclidean distance
        length = np.hypot(x2 - x1, y2 - y1)
        
        # Calculate angle between points
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        
        if img is not None:
            # Draw line with color based on distance
            color = (0, 255, 0) if length < 30 else (0, 0, 255)
            cv2.line(img, (x1, y1), (x2, y2), color, 3)
            cv2.circle(img, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 8, (0, 255, 0), cv2.FILLED)
            
            # Show distance value
            cv2.putText(img, f"{int(length)}px", (cx-30, cy-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return length, img, [x1, y1, x2, y2, cx, cy]
    
    def get_hand_orientation(self):
        """Determine hand orientation (palm facing towards/away from camera)"""
        if len(self.lm_list) < 21:
            return "unknown"
        
        # Use wrist and MCP points to determine orientation
        wrist = self.lm_list[0]
        index_mcp = self.lm_list[5]
        pinky_mcp = self.lm_list[17]
        
        # Calculate palm center
        palm_center_x = (index_mcp[1] + pinky_mcp[1]) // 2
        palm_center_y = (index_mcp[2] + pinky_mcp[2]) // 2
        
        # Compare with wrist position
        if palm_center_y < wrist[2]:
            return "facing_up"
        else:
            return "facing_down"