import datetime
import os
import random
from typing import Optional

import pyautogui
import pyjokes
import pyttsx3
import speech_recognition as sr
import wikipedia
from openai import OpenAI
import webbrowser as wb

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)


def speak(audio) -> None:
    engine.say(audio)
    engine.runAndWait()


def speak_in_chunks(text: str, chunk_size: int = 150) -> None:
    """Speak a long response in manageable chunks."""
    for start in range(0, len(text), chunk_size):
        speak(text[start:start + chunk_size])


def time() -> None:
    """Tells the current time."""
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is")
    speak(current_time)
    print("The current time is", current_time)


def date() -> None:
    """Tells the current date."""
    now = datetime.datetime.now()
    speak("The current date is")
    speak(f"{now.day} {now.strftime('%B')} {now.year}")
    print(f"The current date is {now.day}/{now.month}/{now.year}")


def wishme() -> None:
    """Greets the user based on the time of day."""
    speak("Welcome back, sir!")
    print("Welcome back, sir!")

    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        speak("Good morning!")
        print("Good morning!")
    elif 12 <= hour < 16:
        speak("Good afternoon!")
        print("Good afternoon!")
    elif 16 <= hour < 24:
        speak("Good evening!")
        print("Good evening!")
    else:
        speak("Good night, see you tomorrow.")

    assistant_name = load_name()
    speak(f"{assistant_name} at your service. Please tell me how may I assist you.")
    print(f"{assistant_name} at your service. Please tell me how may I assist you.")


def screenshot() -> None:
    """Takes a screenshot and saves it."""
    img = pyautogui.screenshot()
    img_path = os.path.expanduser("~\\Pictures\\screenshot.png")
    img.save(img_path)
    speak(f"Screenshot saved as {img_path}.")
    print(f"Screenshot saved as {img_path}.")

def takecommand() -> Optional[str]:
    """Takes microphone input from the user and returns it as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1

        try:
            audio = r.listen(source, timeout=5)  # Listen with a timeout
        except sr.WaitTimeoutError:
            speak("Timeout occurred. Please try again.")
            return None

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(query)
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return None
    except Exception as e:
        speak(f"An error occurred: {e}")
        print(f"Error: {e}")
        return None

def play_music(song_name=None) -> None:
    """Plays music from the user's Music directory."""
    song_dir = os.path.expanduser("~\\Music")
    songs = os.listdir(song_dir)

    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]

    if songs:
        song = random.choice(songs)
        os.startfile(os.path.join(song_dir, song))
        speak(f"Playing {song}.")
        print(f"Playing {song}.")
    else:
        speak("No song found.")
        print("No song found.")

def set_name() -> None:
    """Sets a new name for the assistant."""
    speak("What would you like to name me?")
    name = takecommand()
    if name:
        with open("assistant_name.txt", "w") as file:
            file.write(name)
        speak(f"Alright, I will be called {name} from now on.")
    else:
        speak("Sorry, I couldn't catch that.")

def load_name() -> str:
    """Loads the assistant's name from a file, or uses a default name."""
    try:
        with open("assistant_name.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Jarvis"  # Default name


def search_wikipedia(query):
    """Searches Wikipedia and returns a summary."""
    try:
        speak("Searching Wikipedia...")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
        print(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please be more specific.")
    except Exception:
        speak("I couldn't find anything on Wikipedia.")


def get_openai_client() -> Optional[OpenAI]:
    """Create an OpenAI client from the OPENAI_API_KEY environment variable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        speak("Please set the OPENAI_API_KEY environment variable to use OpenAI features.")
        print("Missing OPENAI_API_KEY environment variable.")
        return None
    return OpenAI(api_key=api_key)


def ask_openai(prompt: str) -> None:
    """Send a prompt to OpenAI and speak back the response."""
    client = get_openai_client()
    if not client:
        return

    speak("Reaching out to OpenAI for you.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful desktop voice assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        message = response.choices[0].message.content.strip()
        print(f"OpenAI response: {message}")
        speak_in_chunks(message)
    except Exception as error:
        speak("I couldn't get a response from OpenAI right now.")
        print(f"OpenAI error: {error}")


if __name__ == "__main__":
    wishme()

    while True:
        query = takecommand()
        if not query:
            continue

        if "time" in query:
            time()
            
        elif "date" in query:
            date()

        elif "wikipedia" in query:
            query = query.replace("wikipedia", "").strip()
            search_wikipedia(query)

        elif "play music" in query:
            song_name = query.replace("play music", "").strip()
            play_music(song_name)

        elif "open youtube" in query:
            wb.open("youtube.com")
            
        elif "open google" in query:
            wb.open("google.com")

        elif "change your name" in query:
            set_name()

        elif "ask openai" in query or "ask ai" in query or "ask gpt" in query or "ask chatgpt" in query:
            prompt = query
            for keyword in ["ask openai", "ask ai", "ask gpt", "ask chatgpt"]:
                prompt = prompt.replace(keyword, "")
            prompt = prompt.strip()

            if not prompt:
                speak("What would you like me to ask OpenAI?")
                prompt = takecommand()

            if prompt:
                ask_openai(prompt)
            else:
                speak("Sorry, I couldn't capture your OpenAI request.")

        elif "screenshot" in query:
            screenshot()
            speak("I've taken screenshot, please check it")

        elif "tell me a joke" in query:
            joke = pyjokes.get_joke()
            speak(joke)
            print(joke)

        elif "shutdown" in query:
            speak("Shutting down the system, goodbye!")
            os.system("shutdown /s /f /t 1")
            break
            
        elif "restart" in query:
            speak("Restarting the system, please wait!")
            os.system("shutdown /r /f /t 1")
            break
            
        elif "offline" in query or "exit" in query:
            speak("Going offline. Have a good day!")
            break
