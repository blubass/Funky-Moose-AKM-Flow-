import os
import threading
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

class AudioPlayerEngine:
    """
    A non-blocking audio engine using pygame.mixer.
    Supports playback, volume, seeking and status callbacks.
    """
    def __init__(self, app_log_func=None):
        self.log = app_log_func
        self._initialized = False
        self._current_path = None
        self._duration = 0
        self._is_playing = False
        self._pause_offset = 0
        self._time_at_play = 0
        self._start_pos_at_play = 0
        self._lock = threading.Lock()
        
        if HAS_PYGAME:
            try:
                # Use standard 44.1kHz, 16bit, stereo for maximum compatibility
                pygame.mixer.init(frequency=44100, size=-16, channels=2)
                self._initialized = True
            except Exception as e:
                if self.log: self.log(f"Audio Engine Init Fehler: {e}")
        else:
            if self.log: self.log("Pygame nicht installiert. Audio-Player deaktiviert.")

    def load(self, path):
        if not self._initialized or not os.path.exists(path):
            return False
            
        with self._lock:
            try:
                pygame.mixer.music.load(path)
                # We need to get duration. Pygame doesn't give it easily for all formats
                # But we can use mutagen or just a hack.
                # Since we already have loudness_tools, maybe we can use probe_duration there?
                self._current_path = path
                self._is_playing = False
                self._pause_offset = 0
                return True
            except Exception as e:
                if self.log: self.log(f"Laden Fehler: {e}")
                return False

    def play(self, start_pos=0):
        if not self._initialized: return
        with self._lock:
            try:
                # Store the absolute time when we started THIS segment
                self._time_at_play = time.time()
                self._start_pos_at_play = start_pos
                
                pygame.mixer.music.play(start=start_pos)
                self._is_playing = True
            except Exception as e:
                if self.log: self.log(f"Wiedergabe Fehler: {e}")

    def pause(self):
        if not self._initialized: return
        with self._lock:
            if self._is_playing:
                pygame.mixer.music.pause()
                self._is_playing = False
                # Save where we were for unpausing
                self._pause_offset = self.get_pos()
            else:
                pygame.mixer.music.unpause()
                self._is_playing = True
                # Resume: our new time is NOW, but starting from the old offset
                self._time_at_play = time.time()
                self._start_pos_at_play = self._pause_offset

    def stop(self):
        if not self._initialized: return
        with self._lock:
            pygame.mixer.music.stop()
            self._is_playing = False
            self._start_pos_at_play = 0
            self._pause_offset = 0

    def set_volume(self, val):
        """Val should be 0.0 to 1.0"""
        if not self._initialized: return
        pygame.mixer.music.set_volume(max(0.0, min(1.0, val)))

    def get_pos(self):
        """Returns current position in seconds."""
        if not self._initialized: return 0
        if not self._is_playing: return self._pause_offset
        # Accurate time tracking in seconds
        return self._start_pos_at_play + (time.time() - self._time_at_play)

    def set_pos(self, secs):
        """Seeks to position in seconds."""
        if not self._initialized: return
        self.play(start_pos=secs)

    def is_playing(self):
        return self._is_playing
