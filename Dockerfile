FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY jarvis.py .
COPY test_voice.py .
COPY .env .env 2>/dev/null || true

# Create non-root user
RUN useradd -m -u 1000 jarvis && chown -R jarvis:jarvis /app
USER jarvis

# Run the CLI version (GUI won't work in container)
CMD ["python", "jarvis.py"]
