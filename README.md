# 🤖 JARVIS — AI Voice Assistant

A hands-free voice-activated AI assistant with a beautiful animated UI. Just say "Hey Jarvis" and speak your commands!

## Features

✨ **Voice Activated** — Fully voice-controlled, no typing required  
🎵 **Spotify Integration** — Play tracks, playlists, and artists  
🎥 **YouTube** — Search and watch videos  
📺 **Animated UI** — Smooth animated ball that moves while talking  
🌦️ **Weather** — Get current weather for any location  
🎮 **Minecraft** — Launch your favorite games  
🔍 **Web Search** — Search Google hands-free  
⏰ **Time & Date** — Ask for the current time or date  
🎙️ **Beautiful TTS** — High-quality voice synthesis  

## System Requirements

- **Python 3.10+**
- **Microphone** — For voice input
- **Speakers** — For audio output
- **Spotify Premium** (optional, but required for Spotify features)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/heroness9/jarvisai.git
cd jarvisai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows Users**: If you encounter issues with `PyAudio`:
```bash
pip install pipwin
pipwin install pyaudio
```

**Note for macOS Users**: Install PortAudio first:
```bash
brew install portaudio
pip install pyaudio
```

### 3. Configure Environment Variables

Copy the example configuration:
```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

#### Spotify Setup
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app and get your `Client ID` and `Client Secret`
3. Set Redirect URI to `http://localhost:8888/callback`
4. Add these to your `.env` file

#### YouTube Setup (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable YouTube Data API v3
3. Create an API key
4. Add to `.env` file (falls back to search without it)

#### Weather Setup
1. Go to [WeatherAPI.com](https://www.weatherapi.com/)
2. Create a free account and get your API key
3. Add to `.env` file

#### Minecraft Setup (Optional)
- Find your Minecraft executable path and add it to `.env`
- Windows: Usually in `Program Files`
- macOS: `/Applications/Minecraft.app/Contents/MacOS/Minecraft`
- Linux: Varies by distribution

## Usage

### Start Jarvis with GUI

```bash
python jarvis_gui.py
```

### Start Jarvis (CLI mode)

```bash
python jarvis.py
```

### Voice Commands

Say "Hey Jarvis" or "OK Jarvis" to activate, then try:

**Music Control**
- "Play [song name]" — Play a track on Spotify
- "Play artist [artist name]" — Play all music from an artist
- "Play my playlist [playlist name]" — Play a saved playlist
- "Pause" — Pause music
- "Resume" — Resume playback
- "Skip" — Skip to next track

**Video & Web**
- "Watch [video name]" — Search and open on YouTube
- "Open Spotify" — Open Spotify in browser
- "Search [query]" — Google search
- "Open [website]" — Open any website

**Information**
- "What time is it?" — Get current time
- "What's the date?" — Get current date
- "Weather" — Get weather for your location
- "Weather in [city]" — Get weather for specific city

**Games**
- "Launch Minecraft" — Start Minecraft

**General**
- "Help" — List all available commands
- "Stop" or "Exit" — Shut down Jarvis

## Testing

Before using Jarvis, test your microphone and speaker:

```bash
python test_voice.py
```

If you hear Jarvis say "Hello, I am Jarvis. Voice is working correctly." — you're all set!

## Troubleshooting

### Microphone Not Working
- Check system microphone permissions (especially on macOS/Linux)
- Test with: `python test_voice.py`
- Try: `python -c "import pyaudio; print(pyaudio.PyAudio().get_device_count())"`

### Spotify Features Not Working
- Verify your Spotify account is **Premium**
- Check your `.env` file has valid credentials
- Ensure Spotify app is open on at least one device

### Speech Recognition Not Accurate
- Speak clearly
- Reduce background noise
- Check microphone levels in system settings

### TTS Not Working
- Ensure speakers are not muted
- Try: `python test_voice.py`
- Check audio device in system settings

### Minecraft Won't Launch
- Verify the path in `.env` is correct
- Test the path manually to confirm it works

## Architecture

```
jarvis.py           - Core voice assistant logic
jarvis_gui.py       - Beautiful animated Tkinter UI
requirements.txt    - Python dependencies
test_voice.py       - Voice system tester
.env.example        - Configuration template
```

## Environment Variables

See `.env.example` for all available options:
- `SPOTIFY_CLIENT_ID` — Spotify API credentials
- `SPOTIFY_CLIENT_SECRET` — Spotify API secret
- `YOUTUBE_API_KEY` — YouTube Data API key
- `WEATHERAPI_KEY` — Weather API key
- `MINECRAFT_PATH` — Path to Minecraft executable

## Performance

- **Startup**: ~3-5 seconds
- **Voice Recognition**: ~1-2 seconds per phrase
- **API Calls**: <1 second for most operations
- **Memory**: ~50-100 MB at runtime

## License

MIT License — Feel free to modify and redistribute!

## Contributing

Found a bug or have a feature request? Feel free to open an issue or pull request!

---

Made with ❤️ for hands-free computing
