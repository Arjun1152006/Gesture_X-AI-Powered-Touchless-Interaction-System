import numpy as np

import time



class GestureRecognizerEnhanced:

    def __init__(self, config):

        self.config = config

        self.prev_hand_x = None

        self.prev_hand_y = None

        self.gesture_start_time = {}

        self.gesture_active = {}

       

    def recognize_gesture(self, lm_list, fingers, mode):

        if len(lm_list) < 21:

            self.prev_hand_x = None

            self.prev_hand_y = None

            return 'idle'



        current_time = time.time()

        allowed = ['switch_mode']

        if mode == 'mouse_mode':

            allowed += ['left_click', 'right_click', 'move', 'scroll']

        else:

            allowed += ['next_slide', 'previous_slide']



        for gesture_key, gesture_data in self.config.GESTURES.items():

            name = gesture_data.get('name', '').lower().replace(" ", "_")

            if name not in allowed: continue



            if self.match_gesture(lm_list, fingers, gesture_data):

                if gesture_key not in self.gesture_start_time:

                    self.gesture_start_time[gesture_key] = current_time

               

                hold_time = current_time - self.gesture_start_time[gesture_key]

                if hold_time >= gesture_data.get('min_hold', 0.05):

                    # Continuous gestures (move/scroll) don't use cooldowns

                    is_continuous = name in ['move', 'scroll']

                    last_act = self.gesture_active.get(gesture_key, 0)

                   

                    if is_continuous or (current_time - last_act > 0.5):

                        self.gesture_active[gesture_key] = current_time

                        return name

            else:

                self.gesture_start_time.pop(gesture_key, None)

                # Reset anchors when the specific gesture is lost

                if name in ['next_slide', 'previous_slide']: self.prev_hand_x = None

                if name == 'scroll': self.prev_hand_y = None



        return 'idle'



    def match_gesture(self, lm_list, fingers, gesture_data):
        name = gesture_data.get('name', '').lower().replace(" ", "_")
        # Landmark 9 (Middle Knuckle) is the most stable point for movement
        curr_x, curr_y = lm_list[9][1], lm_list[9][2]
        
        # Calculate dynamic hand size to make movement relative to distance from camera
        hand_size = np.hypot(lm_list[0][1] - lm_list[9][1], lm_list[0][2] - lm_list[9][2])

        try:
            # SCROLL: 3 Fingers Up
            if name == 'scroll':
                return fingers == [0, 1, 1, 1, 0]

            # --- MODIFIED PRESENTATION GESTURES ---
            elif name == 'next_slide':
                # Use "Peace/Victory" sign: Index and Middle up [0, 1, 1, 0, 0]
                # This is much easier to detect than a horizontal sweep
                return fingers == [0, 1, 1, 0, 0]

            elif name == 'previous_slide':
                return fingers == [0, 1, 0, 0, 1]
            # --------------------------------------

            elif name == 'left_click':
                dist = np.hypot(lm_list[4][1]-lm_list[8][1], lm_list[4][2]-lm_list[8][2])
                finger_curled = lm_list[8][2] > lm_list[6][2]
                return dist < (0.25 * hand_size)
            elif name == 'right_click':
                dist = np.hypot(lm_list[8][1] - lm_list[12][1], lm_list[8][2] - lm_list[12][2])
                return dist < (0.25 * hand_size)
            elif name == 'move':
                return fingers == [0, 1, 0, 0, 0]
            elif name == 'switch_mode':
                return fingers == [1, 1, 1, 1, 1]

        except Exception:
            return False
        return False