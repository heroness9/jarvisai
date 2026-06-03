FROM python:3.11-slim

# System dependencies for audio, TTS, and speech recognition
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils \
    libasound2-dev \
    libsndfile1 \
    ffmpeg \
    espeak-ng \
    libespeak-ng1 \
    pulseaudio \
    pulseaudio-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jarvis.py .
COPY .env* ./

# PulseAudio socket (for audio passthrough from Windows host via PulseAudio)
ENV PULSE_SERVER=tcp:host.docker.internal:4713
ENV PYTHONUNBUFFERED=1

CMD ["python", "jarvis.py"]
