from flask import Flask, render_template, Response, request, redirect
import pyautogui
import keyboard
import webbrowser
import os
import cv2
import numpy as np
import pyttsx3
import threading
import time
import speech_recognition as sr
import json

app = Flask(__name__)

# ----------------- Password -----------------
DASHBOARD_PASSWORD = "ironman"

# ----------------- Female Voice Setup -----------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # female voice
engine.setProperty('rate', 150)

# ----------------- Voice Recognition -----------------
voice_commands = []

def listen_voice():
    r = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            cmd = r.recognize_google(audio)
            voice_commands.append(cmd.lower())
        except:
            continue

threading.Thread(target=listen_voice, daemon=True).start()

# ----------------- Macro System -----------------
macros = {
    "open_work": ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", "https://mail.google.com"],
    "open_fun": ["https://youtube.com", "https://netflix.com"]
}

# ----------------- Screen Capture -----------------
def capture_screen():
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/screen')
def screen():
    return Response(capture_screen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ----------------- Login -----------------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        pwd = request.form.get('password')
        if pwd==DASHBOARD_PASSWORD:
            return redirect('/dashboard')
        else:
            return "Incorrect Password"
    return render_template('login.html')

# ----------------- Dashboard -----------------
@app.route('/dashboard')
def dashboard():
    return render_template('ironman_final_dashboard.html', macros=macros)

@app.route('/action', methods=['POST'])
def action():
    command = request.form.get('command')
    data = request.form.get('data')

    if command == 'move':
        x, y = map(int, data.split(','))
        pyautogui.moveRel(x, y)
    elif command == 'click':
        pyautogui.click(button=data)
    elif command == 'type':
        keyboard.write(data)
    elif command == 'open_url':
        webbrowser.open(data)
    elif command == 'open_app':
        os.startfile(data)
    elif command == 'shutdown':
        os.system("shutdown /s /t 5")
    elif command == 'restart':
        os.system("shutdown /r /t 5")
    elif command == 'speak':
        engine.say(data)
        engine.runAndWait()
    elif command == 'macro':
        for item in macros[data]:
            if item.startswith("http"):
                webbrowser.open(item)
            else:
                os.startfile(item)
    elif command == 'media':
        if data == 'play':
            keyboard.press_and_release('play/pause media')
        elif data == 'next':
            keyboard.press_and_release('next track')
        elif data == 'prev':
            keyboard.press_and_release('prev track')
    return 'OK'

# ----------------- Voice Command Executor -----------------
def execute_voice():
    while True:
        if voice_commands:
            cmd = voice_commands.pop(0)
            if 'open youtube' in cmd:
                webbrowser.open('https://youtube.com')
                engine.say("Opening YouTube")
                engine.runAndWait()
            elif 'shutdown' in cmd:
                os.system("shutdown /s /t 5")
            elif 'restart' in cmd:
                os.system("shutdown /r /t 5")
            elif 'type' in cmd:
                text = cmd.replace('type ', '')
                keyboard.write(text)
            elif 'say' in cmd:
                text = cmd.replace('say ', '')
                engine.say(text)
                engine.runAndWait()
        time.sleep(1)

threading.Thread(target=execute_voice, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
