
import sys
import threading
import time
import queue
from datetime import datetime

import customtkinter as ctk

from jarvis import (
    speak,
    listen,
    contains_wake_word,
    process_command,
    TTS_AVAILABLE,
    SR_AVAILABLE,
    SPOTIFY_CLIENT_ID,
    YOUTUBE_API_KEY,
)

#Theme-------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg":        "#0a0a0f",
    "panel":     "#10101a",
    "border":    "#1e1e32",
    "accent":    "#00c8ff",
    "accent2":   "#0077ff",
    "user_msg":  "#1a2a3a",
    "bot_msg":   "#0d1a2a",
    "text":      "#e8f4ff",
    "subtext":   "#6a7f9a",
    "danger":    "#ff4466",
    "success":   "#00e5a0",
    "warning":   "#ffaa00",
}
#------------------------------end of theme--------------------

class JarvisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("J.A.R.V.I.S")
        self.geometry("860x640")
        self.minsize(640, 480)
        self.configure(fg_color=COLORS["bg"])

        # Thread-safe queue for messages from background threads
        self._msg_queue: queue.Queue = queue.Queue()
        self._running = True
        self._voice_active = False

        self._build_ui()
        self._poll_queue()

        # Greet
        self._add_message("jarvis", "Ready to get into business sir?.")
        self._update_status()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0, height=58)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="  ◈  J.A.R.V.I.S",
            font=ctk.CTkFont(family="Courier New", size=20, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=18)

        # Status pills
        self._pill_tts = self._make_pill(header, "TTS", TTS_AVAILABLE)
        self._pill_stt = self._make_pill(header, "STT", SR_AVAILABLE)
        self._pill_spotify = self._make_pill(header, "Spotify", bool(SPOTIFY_CLIENT_ID))
        self._pill_yt = self._make_pill(header, "YouTube", bool(YOUTUBE_API_KEY))

        # Chat area
        self._chat = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg"], corner_radius=0,
        )
        self._chat.pack(fill="both", expand=True, padx=0, pady=0)

        # Input bar
        bar = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0, height=62)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._entry = ctk.CTkEntry(
            bar,
            placeholder_text="Type a command…",
            font=ctk.CTkFont(family="Courier New", size=14),
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            height=38,
            corner_radius=8,
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(14, 8), pady=12)
        self._entry.bind("<Return>", lambda e: self._on_send())

        self._btn_send = ctk.CTkButton(
            bar, text="Send", width=72, height=38,
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            fg_color=COLORS["accent2"], hover_color=COLORS["accent"],
            text_color="#ffffff", corner_radius=8,
            command=self._on_send,
        )
        self._btn_send.pack(side="left", pady=12)

        self._btn_mic = ctk.CTkButton(
            bar, text="🎤", width=46, height=38,
            font=ctk.CTkFont(size=18),
            fg_color=COLORS["border"], hover_color="#2a2a44",
            corner_radius=8,
            command=self._on_voice,
        )
        self._btn_mic.pack(side="left", padx=(6, 14), pady=12)

    def _make_pill(self, parent, label: str, ok: bool) -> ctk.CTkLabel:
        color = COLORS["success"] if ok else COLORS["danger"]
        dot = "●"
        pill = ctk.CTkLabel(
            parent,
            text=f"{dot} {label}",
            font=ctk.CTkFont(family="Courier New", size=11),
            text_color=color,
            fg_color=COLORS["border"],
            corner_radius=10,
            padx=8, pady=2,
        )
        pill.pack(side="right", padx=6)
        return pill

    # ── Message Rendering ─────────────────────────────────────────────────────

    def _add_message(self, sender: str, text: str):
        """Add a chat bubble. Must be called from main thread."""
        is_user = (sender == "user")
        now = datetime.now().strftime("%H:%M")

        outer = ctk.CTkFrame(self._chat, fg_color="transparent")
        outer.pack(fill="x", padx=16, pady=(4, 4))

        bubble_color = COLORS["user_msg"] if is_user else COLORS["bot_msg"]
        border_color = COLORS["accent2"] if is_user else COLORS["accent"]
        anchor = "e" if is_user else "w"

        bubble = ctk.CTkFrame(
            outer,
            fg_color=bubble_color,
            border_color=border_color,
            border_width=1,
            corner_radius=12,
        )
        bubble.pack(anchor=anchor, padx=4)

        # Label row
        name = "You" if is_user else "Jarvis"
        name_color = COLORS["accent2"] if is_user else COLORS["accent"]

        top = ctk.CTkFrame(bubble, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(6, 0))
        ctk.CTkLabel(top, text=name,
                     font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
                     text_color=name_color).pack(side="left")
        ctk.CTkLabel(top, text=now,
                     font=ctk.CTkFont(family="Courier New", size=10),
                     text_color=COLORS["subtext"]).pack(side="right")

        ctk.CTkLabel(
            bubble, text=text,
            font=ctk.CTkFont(family="Courier New", size=13),
            text_color=COLORS["text"],
            wraplength=480,
            justify="left",
        ).pack(padx=12, pady=(2, 10), anchor="w")

        # Auto-scroll
        self.after(50, lambda: self._chat._parent_canvas.yview_moveto(1.0))

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _on_send(self):
        text = self._entry.get().strip()
        if not text:
            return
        self._entry.delete(0, "end")
        self._add_message("user", text)
        threading.Thread(target=self._run_command, args=(text,), daemon=True).start()

    def _on_voice(self):
        if self._voice_active:
            return
        self._voice_active = True
        self._btn_mic.configure(fg_color=COLORS["accent"], text="⏹")
        threading.Thread(target=self._voice_loop_once, daemon=True).start()

    def _voice_loop_once(self):
        """Listen for one command (with optional wake-word detection)."""
        self._msg_queue.put(("status", "🎤 Listening for wake word…"))
        text = listen(timeout=10, phrase_limit=8)

        if text is None:
            self._msg_queue.put(("status", "idle"))
            self._msg_queue.put(("mic_reset", None))
            return

        detected, command = contains_wake_word(text)

        if not detected:
            # In GUI mode, also accept direct commands without wake word
            command = text

        self._msg_queue.put(("user_msg", text))

        if not command:
            self._msg_queue.put(("status", "🎤 Listening for command…"))
            command = listen(timeout=6, phrase_limit=8) or ""
            if command:
                self._msg_queue.put(("user_msg", command))

        self._msg_queue.put(("status", "⚙️ Processing…"))
        self._run_command(command)
        self._msg_queue.put(("mic_reset", None))

    def _run_command(self, command: str):
        """Run in background thread. Monkey-patches speak() to also show in GUI."""
        original_speak = __builtins__  # we'll patch via queue instead

        # Capture speak output by wrapping it
        import jarvis as _j
        _original = _j.speak

        def gui_speak(text):
            _original(text)
            self._msg_queue.put(("bot_msg", text))

        _j.speak = gui_speak
        try:
            keep_going = process_command(command)
            if not keep_going:
                self._msg_queue.put(("quit", None))
        finally:
            _j.speak = _original
            self._voice_active = False
            self._msg_queue.put(("status", "idle"))

    # ── Queue Polling ─────────────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                kind, data = self._msg_queue.get_nowait()
                if kind == "bot_msg":
                    self._add_message("jarvis", data)
                elif kind == "user_msg":
                    self._add_message("user", data)
                elif kind == "status":
                    self._set_status(data)
                elif kind == "mic_reset":
                    self._btn_mic.configure(fg_color=COLORS["border"], text="🎤")
                elif kind == "quit":
                    self.destroy()
                    return
        except queue.Empty:
            pass
        if self._running:
            self.after(80, self._poll_queue)

    def _set_status(self, msg: str):
        pass  # optionally update a status bar if you add one

    def _update_status(self):
        pass

    def on_closing(self):
        self._running = False
        self.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = JarvisApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
