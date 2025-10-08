import cv2
import numpy as np
import face_recognition
import mediapipe as mp
import time
import platform
import os
import threading
import winsound   
import pyttsx3    
from plyer import notification 


def lock_screen():
    sysplat = platform.system()
    try:
        if sysplat == "Windows":
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        elif sysplat == "Darwin":
            os.system("""/System/Library/CoreServices/"Menu Extras"/User.menu/Contents/Resources/CGSession -suspend""")
        else:
            if os.system("gnome-screensaver-command -l") != 0:
                os.system("xdg-screensaver lock")
    except Exception as e:
        print("Lock failed:", e)

def show_notification():
    try:
        notification.notify(
            title="Privacy Guard ALERT",
            message="Stranger detected! Someone is looking at your screen!",
            timeout=5  
        )
    except Exception as e:
        print("Notification failed:", e)

def play_beeps():
    sysplat = platform.system()
    try:
        if sysplat == "Windows":
            for _ in range(3):   
                winsound.Beep(1000, 400)   
                time.sleep(0.2)
        else:
            os.system('play -nq -t alsa synth 0.4 sine 1000 repeat 3')
    except Exception as e:
        print("Beep failed:", e)

def speak_alert():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        for v in voices:
            if "female" in v.name.lower() or "zira" in v.name.lower():
                engine.setProperty("voice", v.id)
                break
        engine.say("Someone is looking at your screen")
        engine.runAndWait()
    except Exception as e:
        print("Voice failed:", e)

def alert_action():
    def run_alert():
        show_notification()  
        play_beeps()         
        speak_alert()        
        lock_screen()        
    threading.Thread(target=run_alert, daemon=True).start()


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=4,
                                  refine_landmarks=True, min_detection_confidence=0.5)


video = cv2.VideoCapture(0)
owner_embedding = None
OWNER_THRESHOLD = 0.5

last_alert_time = 0
ALERT_COOLDOWN = 3.0

print("Starting Privacy Guard...")

while True:
    ret, frame = video.read()
    if not ret:
        break
    small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
    rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    face_locs = face_recognition.face_locations(rgb_small)
    face_encs = face_recognition.face_encodings(rgb_small, face_locs)

    stranger_detected = False

    for i, enc in enumerate(face_encs):
        top, right, bottom, left = face_locs[i]
        scale = 2
        t, r, b, l = top*scale, right*scale, bottom*scale, left*scale

        name = "Unknown"
        if owner_embedding is None:
            owner_embedding = enc   
            name = "Owner"
            print("Owner enrolled automatically.")
        else:
            dist = face_recognition.face_distance([owner_embedding], enc)[0]
            if dist <= OWNER_THRESHOLD:
                name = "Owner"
            else:
                name = "Stranger"
                stranger_detected = True

        color = (0,255,0) if name=="Owner" else (0,0,255)
        cv2.rectangle(frame, (l,t), (r,b), color, 2)
        cv2.putText(frame, name, (l, t-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    now = time.time()
    if stranger_detected and (now - last_alert_time) > ALERT_COOLDOWN:
        last_alert_time = now
        cv2.putText(frame, "ALERT: Stranger detected!", (30,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)
        alert_action()

    cv2.imshow("Privacy Guard", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
