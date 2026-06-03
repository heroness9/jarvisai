import tkinter as tk
from tkinter import ttk
import threading
import math
import jarvis

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 JARVIS — Voice Assistant")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Configure dark theme
        self.root.configure(bg="#0a0e27")
        self.bg_color = "#0a0e27"
        self.accent_color = "#00d9ff"
        self.secondary_color = "#1a1f3a"
        
        # Set up styles
        self.setup_styles()
        
        # Animation state
        self.is_speaking = False
        self.animation_frame = 0
        self.animation_speed = 0.15
        
        # Create UI
        self.create_widgets()
        
        # Set speech callbacks
        jarvis.set_speech_callbacks(self.on_speak_start, self.on_speak_end)
        
        # Start the main loop in a separate thread
        self.running = True
        self.jarvis_thread = threading.Thread(target=self.run_jarvis, daemon=True)
        self.jarvis_thread.start()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground="#ffffff")
        style.configure('Title.TLabel', background=self.bg_color, foreground=self.accent_color, 
                       font=('Helvetica', 24, 'bold'))
        style.configure('Status.TLabel', background=self.bg_color, foreground="#888888",
                       font=('Helvetica', 12))
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 JARVIS", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Voice Activated AI Assistant", 
                                  style='Status.TLabel')
        subtitle_label.pack(pady=(0, 30))
        
        # Canvas for animated ball
        self.canvas = tk.Canvas(main_frame, width=300, height=300, 
                               bg=self.secondary_color, highlightthickness=0)
        self.canvas.pack(pady=20)
        
        # Draw static background circle
        self.draw_background_circle()
        
        # Status text
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=20)
        
        self.status_label = ttk.Label(status_frame, text="🎤 Listening for 'Hey Jarvis'...",
                                     style='Status.TLabel')
        self.status_label.pack()
        
        # Info panel
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = (
            "Say 'Hey Jarvis' or 'OK Jarvis' to activate\n"
            "• Play music on Spotify\n"
            "• Watch videos on YouTube\n"
            "• Check weather, time, date\n"
            "• Search the web\n\n"
            "Say 'Stop' or 'Exit' to quit"
        )
        
        info_label = tk.Label(info_frame, text=info_text, 
                             bg=self.secondary_color, fg="#888888",
                             font=('Helvetica', 10), justify=tk.LEFT,
                             padx=15, pady=15)
        info_label.pack(fill=tk.BOTH, expand=True)
        info_label.config(relief=tk.RAISED, bd=1)
        
        # Start animation loop
        self.animate_ball()
    
    def draw_background_circle(self):
        """Draw the background circle for the ball"""
        self.canvas.create_oval(50, 50, 250, 250, outline=self.accent_color, width=2)
        self.canvas.create_text(150, 280, text="JARVIS", fill=self.accent_color,
                               font=('Helvetica', 14, 'bold'))
    
    def draw_ball(self, x, y, size=40, color=None):
        """Draw the animated Jarvis ball"""
        if color is None:
            color = self.accent_color if not self.is_speaking else "#ff00ff"
        
        # Draw outer glow
        glow_size = size * 1.3
        self.canvas.create_oval(x - glow_size//2, y - glow_size//2,
                              x + glow_size//2, y + glow_size//2,
                              fill="", outline=color, width=1)
        
        # Draw main ball
        self.canvas.create_oval(x - size//2, y - size//2,
                              x + size//2, y + size//2,
                              fill=color, outline=color)
        
        # Draw inner shine
        shine_size = size // 3
        self.canvas.create_oval(x - shine_size//2 - 5, y - shine_size//2 - 5,
                              x + shine_size//2 - 5, y + shine_size//2 - 5,
                              fill="white", outline="")
    
    def animate_ball(self):
        """Animate the ball movement"""
        if not self.running:
            return
        
        self.canvas.delete("all")
        self.draw_background_circle()
        
        if self.is_speaking:
            # Pulsing and moving animation when speaking
            progress = (math.sin(self.animation_frame * self.animation_speed) + 1) / 2
            
            # Circular motion
            angle = self.animation_frame * self.animation_speed
            radius = 40 * progress
            x = 150 + math.cos(angle) * radius
            y = 150 + math.sin(angle) * radius * 0.7
            
            # Pulsing size
            size = 40 + int(15 * progress)
            
            # Draw pulsing effect
            for i in range(3):
                alpha_progress = (progress - i * 0.3) % 1.0
                if alpha_progress > 0:
                    pulse_size = size + int(20 * (1 - alpha_progress))
                    self.canvas.create_oval(x - pulse_size//2, y - pulse_size//2,
                                          x + pulse_size//2, y + pulse_size//2,
                                          outline="#ff00ff", width=1)
            
            self.draw_ball(int(x), int(y), size, "#ff00ff")
        else:
            # Gentle breathing animation when idle
            progress = (math.sin(self.animation_frame * self.animation_speed * 0.5) + 1) / 2
            size = 35 + int(10 * progress)
            self.draw_ball(150, 150, size, self.accent_color)
        
        self.animation_frame += 1
        self.root.after(50, self.animate_ball)
    
    def on_speak_start(self):
        """Called when Jarvis starts speaking"""
        self.is_speaking = True
        self.status_label.config(text="🤖 Speaking...")
        self.root.update_idletasks()
    
    def on_speak_end(self):
        """Called when Jarvis stops speaking"""
        self.is_speaking = False
        self.status_label.config(text="🎤 Listening...")
        self.root.update_idletasks()
    
    def run_jarvis(self):
        """Run the main Jarvis loop"""
        try:
            # Print startup info
            print("\n" + "=" * 55)
            print("🤖  JARVIS — Voice Assistant (GUI Mode)")
            print("=" * 55)
            print(f"  Spotify  : {'✅ configured' if jarvis.SPOTIFY_CLIENT_ID else '⚠️  not set'}")
            print(f"  YouTube  : {'✅ configured' if jarvis.YOUTUBE_API_KEY else '⚠️  not set (search fallback)'}")
            print(f"  Weather  : {'✅ configured' if jarvis.WEATHERAPI_KEY else '⚠️  not set'}")
            print(f"  TTS      : {'✅ enabled' if jarvis.TTS_AVAILABLE else '❌ disabled'}")
            print(f"  STT      : {'✅ enabled' if jarvis.SR_AVAILABLE else '❌ disabled'}")
            print(f"  Voice    : {jarvis.JARVIS_VOICE}")
            if jarvis.MINECRAFT_PATH:
                print(f"  Minecraft: ✅ configured")
            else:
                print(f"  Minecraft: ⚠️  not set")
            print("=" * 55 + "\n")
            
            jarvis.speak("Hello. I am Jarvis. Say hey Jarvis to activate.")
            
            while self.running:
                text = jarvis.listen(timeout=10, phrase_limit=8)
                if text is None:
                    continue
                
                detected, command = jarvis.contains_wake_word(text)
                if not detected:
                    continue
                
                if not command:
                    jarvis.speak("Yes?")
                    command = jarvis.listen(timeout=6, phrase_limit=8) or ""
                
                if not jarvis.process_command(command):
                    self.stop_jarvis()
                    break
        
        except Exception as e:
            print(f"[GUI Error: {e}]")
            self.stop_jarvis()
    
    def stop_jarvis(self):
        """Stop the Jarvis thread and close the app"""
        self.running = False
        self.root.quit()
    
    def on_closing(self):
        """Handle window close"""
        self.running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    gui = JarvisGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
