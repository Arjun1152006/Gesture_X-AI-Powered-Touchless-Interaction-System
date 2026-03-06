GestureX: AI-Powered Touchless Interaction System
GestureX is a sophisticated Human-Computer Interaction (HCI) tool that transforms hand gestures into system-level commands. By combining MediaPipe for hand tracking with Kalman Filter smoothing, it provides a buttery-smooth, touchless experience for controlling your mouse and presentations.
Features:
Precision Mouse Control: Map your index finger to the screen with advanced smoothing and sub-pixel accuracy.

Dual-Mode Operation: Seamlessly toggle between Mouse Mode and Presentation Mode.

Intelligent Smoothing: Utilizes Kalman Filters to eliminate camera jitter and provide stable cursor movement.

Gesture Prioritization: Built-in cooldowns and hold-time thresholds prevent accidental clicks or repeated actions.

Machine Learning Ready: Includes a modular classification system supporting Random Forest, SVM, and Neural Networks for custom gesture recognition.

Gesture Mapping
Global Commands
Switch Mode: Hold a full palm (5 fingers up) for 1 second.

Mouse Mode
Move Cursor: Index finger up.

Left Click: Pinch Thumb and Index finger.

Right Click: Pinch Index and Middle finger.

Scroll: Three fingers up (Index, Middle, Ring).

Presentation Mode
Next Slide: Peace sign (Index and Middle fingers up).

Previous Slide: Index and pinky finger up.

Modules required :
pip install opencv-python mediapipe pyautogui numpy scikit-learn pillow pynput
