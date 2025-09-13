import cv2
import mediapipe as mp
import os
import webbrowser
import pyautogui
import datetime
import pyttsx3
import screen_brightness_control as sbc
import time

engine = pyttsx3.init()
voices = engine.getProperty("voices")
female_voice = None
for v in voices:
    if "female" in v.name.lower():
        female_voice = v.id
        break
if female_voice:
    engine.setProperty("voice", female_voice)
else:
    engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

log_file = "gesture_log.txt"
def log_action(action):
    with open(log_file, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {action}\n")

def fingers_up(hand_landmarks, hand_label):
    fingers = []
    tip_ids = [4, 8, 12, 16, 20]

    if hand_label == "Right":
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x <
                          hand_landmarks.landmark[tip_ids[0] - 1].x else 0)
    else:
        fingers.append(1 if hand_landmarks.landmark[tip_ids[0]].x >
                          hand_landmarks.landmark[tip_ids[0] - 1].x else 0)

    for id in range(1, 5):
        fingers.append(1 if hand_landmarks.landmark[tip_ids[id]].y <
                          hand_landmarks.landmark[tip_ids[id] - 2].y else 0)
    return fingers

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)

if cap.isOpened():
    speak("Camera Opened Spidey")
else:
    speak("Camera not found Spidey")
    exit()

last_action = None
last_time = 0
cooldown = 2
stable_gesture = None
stable_count = 0
required_stable_frames = 7


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            hand_label = handedness.classification[0].label
            fingers = fingers_up(hand_landmarks, hand_label)

            action, voice_text, command = None, None, None

           
            if hand_label == "Right":
                if fingers == [0,1,0,0,0]:
                    action, voice_text = "Locking Screen", "Locking Screen Spidey"
                    command = lambda: os.system("rundll32.exe user32.dll,LockWorkStation")

                elif fingers == [0,1,1,0,0]:
                    action, voice_text = "Opening YouTube", "Opening YouTube Spidey"
                    command = lambda: webbrowser.open("https://youtube.com")

                elif fingers == [0,1,1,1,0]:
                    action, voice_text = "Opening Chrome", "Opening Chrome Spidey"
                    command = lambda: os.system("start chrome")

                elif fingers == [0,1,1,1,1]:
                    action, voice_text = "Brightness Down", "Brightness Down Spidey"
                    command = lambda: sbc.set_brightness("-10")

                elif fingers == [1,1,1,1,1]:
                    action, voice_text = "Shutting Down", "Shutting Down Spidey"
                    command = lambda: os.system("shutdown /s /t 1")

           
            elif hand_label == "Left":
                if fingers == [0,1,0,0,0]:
                    action, voice_text = "Volume Up", "Volume Up Spidey"
                    command = lambda: [pyautogui.press("volumeup") for _ in range(5)]

                elif fingers == [0,1,1,0,0]:
                    action, voice_text = "Volume Down", "Volume Down Spidey"
                    command = lambda: [pyautogui.press("volumedown") for _ in range(5)]

                elif fingers == [0,1,1,1,0]:
                    action, voice_text = "Opening File Explorer", "Opening File Explorer Spidey"
                    command = lambda: os.system("explorer")

                elif fingers == [0,1,1,1,1]:
                    action, voice_text = "Opening Notepad", "Opening Notepad Spidey"
                    command = lambda: os.system("notepad")

                elif fingers == [1,1,1,1,1]:
                    action, voice_text = "Opening CMD", "Opening Command Prompt Spidey"
                    command = lambda: os.system("start cmd")

            
            if action:
                if action == stable_gesture:
                    stable_count += 1
                else:
                    stable_gesture = action
                    stable_count = 1

                if stable_count >= required_stable_frames:
                    if (action != last_action) or (time.time() - last_time > cooldown):
                        log_action(action)
                        speak(voice_text)
                        if command: command()
                        last_action = action
                        last_time = time.time()
                        stable_count = 0

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
