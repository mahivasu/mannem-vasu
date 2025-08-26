import pyttsx3
import speech_recognition as sr
import webbrowser
from googlesearch import search

engine = pyttsx3.init()
engine.setProperty("rate", 180)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening... Speak now.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        query = recognizer.recognize_google(audio)
        print("You (voice):", query)
        return query
    except:
        speak("Sorry, I couldn't understand.")
        return ""

def google_search(query):
    speak("Searching Google...")
    for result in search(query, num_results=1):
        speak("Here is what I found.")
        webbrowser.open(result)
        break

speak("🔊 Google-style Assistant Ready! Type or Speak. Say 'exit' to quit.")

while True:
    print("\nChoose input method:")
    print("1. Type")
    print("2. Speak")
    method = input("Enter 1 or 2: ")

    if method == "1":
        query = input("You (typed): ")
    elif method == "2":
        query = listen_voice()
    else:
        speak("Invalid option.")
        continue

    query = query.lower()

    if any(word in query for word in ["exit", "quit", "bye"]):
        speak("Goodbye! 👋")
        break

    if query:
        google_search(query)
