import cv2
import mediapipe as mp
import pyttsx3
import time
import numpy as np
from collections import deque

# ---------------- Setup ----------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

# Voice setup (female)
engine = pyttsx3.init()
voices = engine.getProperty("voices")
if len(voices) > 1:
    engine.setProperty("voice", voices[1].id)  # female
else:
    engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 150)

cap = cv2.VideoCapture(0)

# Word builder
current_word = ""
last_letter = ""
last_time = time.time()

# Dynamic gesture buffer
gesture_history = deque(maxlen=15)

# ---------------- Utility Functions ----------------
def vector_angle(a, b, c):
    ba = np.array([a.x - b.x, a.y - b.y])
    bc = np.array([c.x - b.x, c.y - b.y])
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
    return angle

def detect_sign(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    index_angle = vector_angle(landmarks[6], landmarks[7], landmarks[8])
    thumb_angle = vector_angle(landmarks[2], landmarks[3], landmarks[4])

    # Approx A-Z demo rules
    if index_tip.y < thumb_tip.y and middle_tip.y > index_tip.y:
        return "A"
    elif index_tip.y < thumb_tip.y and middle_tip.y < index_tip.y:
        return "B"
    elif ring_tip.y < thumb_tip.y and pinky_tip.y < ring_tip.y:
        return "C"
    elif index_angle < 30 and thumb_angle < 30:
        return "L"
    else:
        return "?"

# ---------------- Main Loop ----------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    text = "No Hand"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark
            text = detect_sign(landmarks)

            gesture_history.append(text)
            if len(set(gesture_history)) > 1 and "Z" in gesture_history:
                text = "Z"

            # Speak letter on C (space)
            if text == "C" and time.time() - last_time > 2.0:
                engine.say(current_word)
                engine.runAndWait()
                current_word = ""  # reset after speaking
                last_time = time.time()

            # Build word silently (no screen display)
            if text != "?" and text != last_letter:
                if time.time() - last_time > 1.0:
                    current_word += text
                    last_letter = text
                    last_time = time.time()

    # Show only detected Letter
    cv2.putText(frame, f"Letter: {text}", (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    cv2.imshow("Sign Language Detector", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC quit
        break

cap.release()
cv2.destroyAllWindows()
