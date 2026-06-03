import os
import re
import sys
import time
import asyncio
import tempfile
import webbrowser
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

# Fix Windows Unicode encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

# ── Credentials ───────────────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI  = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
YOUTUBE_API_KEY       = os.getenv("YOUTUBE_API_KEY", "")
WEATHERAPI_KEY        = os.getenv("WEATHERAPI_KEY", "4eb9fb2c6e0a49ee8e154255261505")

# ── Config ────────────────────────────────────────────────────────────────────
MINECRAFT_PATH = r"C:\Users\alex.strydom\OneDrive - St Philip's College\Apps\Spearpvp\Spearpvp.exe"

# ── TTS (edge-tts) ────────────────────────────────────────────────────────────
try:
    import edge_tts
    import pygame
    pygame.mixer.init()
    TTS_AVAILABLE = True
except Exception as e:
    print(f"[TTS init error: {e}]")
    TTS_AVAILABLE = False

JARVIS_VOICE = "en-GB-RyanNeural"

async def _speak_async(text: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tmp_path = f.name
    communicate = edge_tts.Communicate(text, JARVIS_VOICE)
    await communicate.save(tmp_path)
    return tmp_path

def speak(text: str):
    print(f"🤖 Jarvis: {text}", flush=True)
    if not TTS_AVAILABLE:
        return
    try:
        tmp_path = asyncio.run(_speak_async(text))
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        pygame.mixer.music.unload()
        os.remove(tmp_path)
    except Exception as e:
        print(f"[TTS: {e}]")

# ── Speech recognition ────────────────────────────────────────────────────────
try:
    import speech_recognition as sr
    _recognizer = sr.Recognizer()
    _recognizer.energy_threshold = 300
    _recognizer.dynamic_energy_threshold = True
    SR_AVAILABLE = True
except ImportError as e:
    print(f"[STT import error: {e}]", file=sys.stderr)
    SR_AVAILABLE = False
except Exception as e:
    print(f"[STT initialization error: {e}]", file=sys.stderr)
    SR_AVAILABLE = False

WAKE_WORDS = [
    "jarvis", "hey jarvis", "ok jarvis", "okay jarvis",
    "davis", "hey davis", "dolivers", "hey dolivers",
]

def listen(timeout: int = 5, phrase_limit: int = 8) -> str | None:
    if not SR_AVAILABLE:
        speak("Speech recognition not available.")
        return None
    try:
        with sr.Microphone() as source:
            print("🎤 Listening...", flush=True)
            _recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = _recognizer.listen(source, timeout=timeout,
                                       phrase_time_limit=phrase_limit)
        text = _recognizer.recognize_google(audio)
        print(f"📝 You said: {text}", flush=True)
        return text.lower()
    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[STT error: {e}]")
        return None
    except Exception as e:
        print(f"[Listen error: {e}]")
        return None

def contains_wake_word(text: str) -> tuple[bool, str]:
    low = text.lower().strip()
    for ww in sorted(WAKE_WORDS, key=len, reverse=True):
        if ww in low:
            idx = low.find(ww)
            remainder = low[idx + len(ww):].strip().lstrip(",").strip()
            return True, remainder
    return False, ""

# ── Spotify (Premium) ─────────────────────────────────────────────────────────
_sp = None

def _get_spotify():
    global _sp
    if _sp:
        return _sp
    if not SPOTIFY_CLIENT_ID:
        return None
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyPKCE
        auth_manager = SpotifyPKCE(
            client_id=SPOTIFY_CLIENT_ID,
            redirect_uri="http://localhost:8888/callback",
            scope="user-modify-playback-state user-read-playback-state playlist-read-private",
            open_browser=True,
        )
        _sp = spotipy.Spotify(auth_manager=auth_manager)
        # Force token fetch now so auth happens at startup
        _sp.current_user()
        return _sp
    except Exception as e:
        print(f"[Spotify init: {e}]")
        return None

def _get_active_device(sp):
    try:
        devices = sp.devices()
        items = devices.get("devices", [])
        for d in items:
            if d["is_active"]:
                return d["id"]
        if items:
            return items[0]["id"]
    except Exception as e:
        print(f"[Spotify devices: {e}]")
    return None

def play_spotify_track(query: str):
    sp = _get_spotify()
    if not sp:
        speak("Spotify is not configured.")
        return
    try:
        results = sp.search(q=query, type="track", limit=1)
        tracks = results["tracks"]["items"]
        if not tracks:
            speak(f"I couldn't find {query} on Spotify.")
            return
        track = tracks[0]
        name = track["name"]
        artist = track["artists"][0]["name"]
        uri = track["uri"]
        device_id = _get_active_device(sp)
        sp.start_playback(device_id=device_id, uris=[uri])
        speak(f"Playing {name} by {artist}.")
    except Exception as e:
        speak("There was an issue playing that track.")
        print(f"[Spotify track: {e}]")

def play_spotify_playlist(query: str):
    sp = _get_spotify()
    if not sp:
        speak("Spotify is not configured.")
        return
    try:
        # Search user's own playlists first
        user_playlists = sp.current_user_playlists(limit=50)
        for pl in user_playlists["items"]:
            if query.lower() in pl["name"].lower():
                device_id = _get_active_device(sp)
                sp.start_playback(device_id=device_id, context_uri=pl["uri"])
                speak(f"Playing your playlist, {pl['name']}.")
                return
        # Fall back to searching public playlists
        results = sp.search(q=query, type="playlist", limit=1)
        playlists = results["playlists"]["items"]
        if not playlists:
            speak(f"I couldn't find a playlist called {query}.")
            return
        pl = playlists[0]
        device_id = _get_active_device(sp)
        sp.start_playback(device_id=device_id, context_uri=pl["uri"])
        speak(f"Playing playlist {pl['name']}.")
    except Exception as e:
        speak("There was an issue playing that playlist.")
        print(f"[Spotify playlist: {e}]")

def play_spotify_artist(query: str):
    sp = _get_spotify()
    if not sp:
        speak("Spotify is not configured.")
        return
    try:
        results = sp.search(q=query, type="artist", limit=1)
        artists = results["artists"]["items"]
        if not artists:
            speak(f"I couldn't find {query} on Spotify.")
            return
        artist = artists[0]
        device_id = _get_active_device(sp)
        sp.start_playback(device_id=device_id, context_uri=artist["uri"])
        speak(f"Playing {artist['name']} on Spotify.")
    except Exception as e:
        speak("There was an issue playing that artist.")
        print(f"[Spotify artist: {e}]")

def spotify_pause():
    sp = _get_spotify()
    if not sp:
        return
    try:
        sp.pause_playback()
        speak("Pausing Spotify.")
    except Exception as e:
        print(f"[Spotify pause: {e}]")

def spotify_resume():
    sp = _get_spotify()
    if not sp:
        return
    try:
        sp.start_playback()
        speak("Resuming.")
    except Exception as e:
        print(f"[Spotify resume: {e}]")

def spotify_skip():
    sp = _get_spotify()
    if not sp:
        return
    try:
        sp.next_track()
        speak("Skipping to the next track.")
    except Exception as e:
        print(f"[Spotify skip: {e}]")

# ── YouTube ───────────────────────────────────────────────────────────────────
def play_youtube(query: str):
    if not query:
        speak("What would you like to watch on YouTube?")
        return
    if YOUTUBE_API_KEY:
        try:
            params = {
                "q": query, "part": "snippet",
                "type": "video", "maxResults": 1,
                "key": YOUTUBE_API_KEY,
            }
            resp = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=params, timeout=10,
            )
            data = resp.json()
            items = data.get("items", [])
            if items:
                vid_id = items[0]["id"]["videoId"]
                title  = items[0]["snippet"]["title"]
                speak(f"Playing {title} on YouTube.")
                webbrowser.open(f"https://www.youtube.com/watch?v={vid_id}")
                return
        except Exception as e:
            print(f"[YouTube API: {e}]")
    speak(f"Searching YouTube for {query}.")
    webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")

# ── Time & Date ───────────────────────────────────────────────────────────────
def tell_time():
    now = datetime.now()
    t = now.strftime("%I:%M %p").lstrip("0")
    speak(f"The current time is {t}.")

def tell_date():
    now = datetime.now()
    d = now.strftime("%A, %B %d, %Y")
    speak(f"Today is {d}.")

# ── Weather ───────────────────────────────────────────────────────────────────
def _get_location() -> str:
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=5)
        data = resp.json()
        return data.get("city", "Adelaide")
    except Exception:
        return "Adelaide"

def tell_weather(city: str = ""):
    if not WEATHERAPI_KEY:
        speak("Weather API key is not configured. Please add WEATHERAPI_KEY to your dot env file.")
        return
    if not city:
        city = _get_location()
    try:
        resp = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": WEATHERAPI_KEY, "q": city, "aqi": "no"},
            timeout=10,
        )
        data = resp.json()
        if "error" in data:
            speak(f"I couldn't get the weather for {city}.")
            return
        loc  = data["location"]["name"]
        temp = data["current"]["temp_c"]
        feel = data["current"]["feelslike_c"]
        cond = data["current"]["condition"]["text"]
        speak(f"In {loc}, it is currently {temp} degrees Celsius, feels like {feel}. Conditions: {cond}.")
    except Exception as e:
        speak("I couldn't retrieve the weather right now.")
        print(f"[Weather: {e}]")

# ── Minecraft ─────────────────────────────────────────────────────────────────
def launch_minecraft():
    if not os.path.exists(MINECRAFT_PATH):
        speak("I couldn't find the Minecraft launcher. Please check the path in my settings.")
        print(f"[Minecraft] Path not found: {MINECRAFT_PATH}")
        return
    try:
        subprocess.Popen([MINECRAFT_PATH])
        speak("Launching Minecraft. Have fun.")
    except Exception as e:
        speak("There was an error launching Minecraft.")
        print(f"[Minecraft: {e}]")

# ── Spotify command parser ────────────────────────────────────────────────────
# Uses regex to cleanly extract the query without clobbering playlist names
# like "Ghost Girl" that contain common words.

_PLAYLIST_RE = re.compile(
    r"play\s+(?:my\s+)?(?:playlist|list)\s+(.+?)(?:\s+on\s+spotify)?$"
)
_ARTIST_RE = re.compile(
    r"play\s+(?:the\s+)?artist\s+(.+?)(?:\s+on\s+spotify)?$"
)
_SONG_RE = re.compile(
    r"play\s+(?:the\s+)?(?:song|track)\s+(.+?)(?:\s+on\s+spotify)?$"
)
_SPOTIFY_PLAY_RE = re.compile(
    r"(?:play|listen\s+to|put\s+on)\s+(.+?)\s+on\s+spotify$"
)
_GENERIC_PLAY_RE = re.compile(r"^play\s+(.+)$")


def _parse_spotify_command(cmd: str) -> bool:
    """
    Try to match cmd against known Spotify play patterns.
    Returns True if a Spotify action was taken, False otherwise.
    """
    # "play my playlist Ghost Girl"  /  "play playlist chill vibes"
    m = _PLAYLIST_RE.match(cmd)
    if m:
        play_spotify_playlist(m.group(1).strip())
        return True

    # "play artist The Weeknd"
    m = _ARTIST_RE.match(cmd)
    if m:
        play_spotify_artist(m.group(1).strip())
        return True

    # "play song Blinding Lights"  /  "play track ..."
    m = _SONG_RE.match(cmd)
    if m:
        play_spotify_track(m.group(1).strip())
        return True

    # "play X on spotify"  /  "listen to X on spotify"
    m = _SPOTIFY_PLAY_RE.match(cmd)
    if m:
        play_spotify_track(m.group(1).strip())
        return True

    return False


# ── Command handler ───────────────────────────────────────────────────────────
def process_command(command: str) -> bool:
    """Returns False to exit, True to keep running."""
    if not command:
        return True

    cmd = command.lower().strip()

    # ── Exit
    if any(w in cmd for w in ["stop", "exit", "quit", "goodbye", "shut down"]):
        speak("Goodbye.")
        return False

    # ── Time
    elif any(w in cmd for w in ["what time", "current time", "what's the time", "whats the time"]):
        tell_time()

    # ── Date
    elif any(w in cmd for w in ["what day", "what date", "today's date", "what is the date", "whats the date"]):
        tell_date()

    # ── Weather
    elif "weather" in cmd:
        city = ""
        for prep in ["in ", "for ", "at "]:
            if prep in cmd:
                city = cmd.split(prep, 1)[-1].strip()
                break
        tell_weather(city)

    # ── Minecraft
    elif any(w in cmd for w in ["open minecraft", "launch minecraft", "start minecraft", "play minecraft"]):
        launch_minecraft()

    # ── Spotify controls
    elif any(w in cmd for w in ["pause music", "pause spotify", "pause"]):
        spotify_pause()

    elif any(w in cmd for w in ["resume music", "resume spotify", "resume", "unpause", "continue music"]):
        spotify_resume()

    elif any(w in cmd for w in ["skip", "next song", "next track"]):
        spotify_skip()

    # ── Spotify play (playlist / artist / song / generic) ─────────────────────
    # Checked BEFORE YouTube so "play my playlist X" never falls through to YouTube.
    elif _parse_spotify_command(cmd):
        pass  # already handled inside _parse_spotify_command

    # ── YouTube
    elif "youtube" in cmd or "watch" in cmd:
        query = (cmd
                 .replace("watch", "").replace("on youtube", "")
                 .replace("youtube", "").replace("play", "")
                 .strip())
        play_youtube(query)

    # ── Open sites
    elif "open spotify" in cmd:
        webbrowser.open("https://open.spotify.com")
        speak("Opening Spotify.")

    elif "open youtube" in cmd:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube.")

    elif cmd.startswith("open "):
        site = cmd[5:].strip()
        webbrowser.open(f"https://{site}" if "." in site else f"https://www.google.com/search?q={site}")
        speak(f"Opening {site}.")

    # ── Search
    elif cmd.startswith("search ") or cmd.startswith("google "):
        query = cmd.split(" ", 1)[1].strip()
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        speak(f"Searching for {query}.")

    # ── Help
    elif "help" in cmd:
        speak(
            "Here is what I can do. "
            "Play a song, artist, or playlist on Spotify. "
            "Watch a video on YouTube. "
            "Tell you the time or date. "
            "Check the weather. "
            "Launch Minecraft. "
            "Or search the web."
        )

    else:
        speak("I am not sure about that. Say help for a list of commands.")

    return True

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 55)
    print("🤖  JARVIS — Voice Assistant")
    print("=" * 55)
    print(f"  Spotify  : {'✅ configured' if SPOTIFY_CLIENT_ID else '⚠️  not set'}")
    print(f"  YouTube  : {'✅ configured' if YOUTUBE_API_KEY else '⚠️  not set (search fallback)'}")
    print(f"  Weather  : {'✅ configured' if WEATHERAPI_KEY else '⚠️  not set'}")
    print(f"  TTS      : {'✅ enabled' if TTS_AVAILABLE else '❌ disabled'}")
    print(f"  STT      : {'✅ enabled' if SR_AVAILABLE else '❌ disabled'}")
    print(f"  Voice    : {JARVIS_VOICE}")
    print(f"  Minecraft: {MINECRAFT_PATH}")
    print("=" * 55)
    print("\nSay 'Hey Jarvis' to activate. Say 'stop' to quit.\n")

    speak("Hello. I am Jarvis. Say hey Jarvis to activate.")

    while True:
        text = listen(timeout=10, phrase_limit=8)
        if text is None:
            continue
        detected, command = contains_wake_word(text)
        if not detected:
            continue
        if not command:
            speak("Yes?")
            command = listen(timeout=6, phrase_limit=8) or ""
        if not process_command(command):
            break
        time.sleep(0.5)

if __name__ == "__main__":
    main()