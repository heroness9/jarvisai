import asyncio
import edge_tts
import pygame
import tempfile
import time
import os

async def test():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tmp = f.name
    await edge_tts.Communicate("Hello, I am Jarvis. Voice is working correctly.", "en-GB-RyanNeural").save(tmp)
    return tmp

print("Initialising pygame...")
pygame.mixer.init()
print("Generating speech...")
path = asyncio.run(test())
print("Playing audio...")
pygame.mixer.music.load(path)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    time.sleep(0.1)
pygame.mixer.music.unload()
os.remove(path)
print("Done! If you heard Jarvis speak, voice is working.")
