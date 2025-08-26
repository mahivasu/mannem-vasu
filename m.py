import speech_recognition as sr
import wikipedia
import wolframalpha
import random
import os
import subprocess
import webbrowser
import pyautogui
from datetime import datetime
from gtts import gTTS
import playsound
from pathlib import Path


WOLFRAM_APP_ID = "T5RT88-YQ8Q6J78AY"

DANGEROUS_MODE = False  
FORBIDDEN_PATHS = {
    str(Path("C:/")),
    str(Path("C:/Windows")),
    str(Path(os.environ.get("WINDIR", "C:/Windows"))),
}

KNOWN_PLACES = {
    "desktop": str(Path.home() / "Desktop"),
    "downloads": str(Path.home() / "Downloads"),
    "documents": str(Path.home() / "Documents"),
    "pictures": str(Path.home() / "Pictures"),
    "music": str(Path.home() / "Music"),
}
apps = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "whatsapp": "https://web.whatsapp.com/",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "youtube": "https://www.youtube.com",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}
def speak(text):
    print(f"[Assistant]: {text}")
    tts = gTTS(text=text, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)



recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("\n🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
        except sr.WaitTimeoutError:
            speak("I didn't hear anything, Spidey.")
            return None
    try:
        query = recognizer.recognize_google(audio)
        print(f"You: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry Spide, I didn't understand that.")
    except sr.RequestError:
        speak("Network error, Spidey.")
    return None



def open_any(name):
    if name in apps:
        target = apps[name]
        if target.endswith(".exe") and os.path.exists(target):
            subprocess.Popen(target)
            speak(f"Opening {name}, Spidey.")
            return
        else:
            webbrowser.open(target)
            speak(f"Opening {name}, Spidey.")
            return

    try:
        subprocess.Popen(name)
        speak(f"Opening {name}, Spidey.")
    except:
        speak(f"{name} not found locally. Searching online for you, Spidey.")
        webbrowser.open(f"https://www.google.com/search?q={name} download")


def open_random_app():
    app_name = random.choice(list(apps.keys()))
    open_any(app_name)


def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak(f"Searching for {query}, Spidey.")


def take_screenshot():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{ts}.png"
    pyautogui.screenshot(filename)
    speak(f"Screenshot saved as {filename}, Spidey.")



client = wolframalpha.Client(WOLFRAM_APP_ID)

def answer_question(query):
    try:
        res = client.query(query)
        answer = next(res.results).text
        speak(answer)
    except:
        try:
            summary = wikipedia.summary(query, sentences=2)
            speak(summary)
        except:
            speak("Let me search that on Google, Spidey.")
            search_web(query)



def execute(cmd):
    if not cmd:
        return

    if "Sam" in cmd:
        speak("Yes Spidey! I’m Samantha, your control assistant, always ready.")
        return

    if "shutdown" in cmd:
        speak("Shutting down your laptop, Spidey.")
        os.system("shutdown /s /t 5")
        return

    if "restart" in cmd or "reboot" in cmd:
        speak("Restarting your laptop, Spidey.")
        os.system("shutdown /r /t 5")
        return

    if "sleep" in cmd or "hibernate" in cmd:
        speak("Putting your laptop to sleep, Spidey.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return

    if "lock" in cmd or "lock screen" in cmd:
        speak("Lock screen on, Spide. Stay safe.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return

    if "random app" in cmd or "open any app" in cmd:
        speak("Choosing a random app for you, Spidey.")
        open_random_app()
        return

    if cmd.startswith("open "):
        open_any(cmd.replace("open ", "", 1).strip())
        return

    if cmd.startswith("search for "):
        search_web(cmd.replace("search for ", "", 1))
        return

    if "screenshot" in cmd:
        take_screenshot()
        return

    if "close window" in cmd:
        pyautogui.hotkey("alt", "f4")
        speak("Window closed, Spidey.")
        return

    if "switch window" in cmd:
        pyautogui.hotkey("alt", "tab")
        speak("Switched window, Spidey.")
        return

    if "time" in cmd:
        speak(datetime.now().strftime("It's %I:%M %p, Spide."))
        return

   
    answer_question(cmd)
    



if __name__ == "__main__":
    speak("Hello Spidey! I am your Samantha,Assistant.")

    while True:
        choice = input("\nDo you want to use Voice or Type? (v/t/q to quit): ").strip().lower()

        if choice == "q":
            speak("Goodbye Spidey! Have a great day.")
            break

        if choice == "v":
            command = listen()
            execute(command)

        elif choice == "t":
            command = input("Type your command: ").lower()
            execute(command)

        else:
            print("Invalid choice! Please enter 'v' for voice, 't' for text, or 'q' to quit.")
