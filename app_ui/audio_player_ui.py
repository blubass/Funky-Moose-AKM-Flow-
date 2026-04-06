import tkinter as tk
from tkinter import ttk
import os
import threading
from PIL import Image, ImageTk
from app_ui.ui_patterns import (
    BG, PANEL, PANEL_2, ACCENT, TEXT, SUBTLE, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, SPACE_LG, FONT_BOLD, FONT_SM, FONT_MD_BOLD, FONT_XL, FONT_LG,
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmToast, blend_color
)
from app_logic import loudness_tools

class AkmAudioPlayer(tk.Toplevel):
    """
    A standalone, premium-themed audio player popup.
    """
    def __init__(self, parent, engine, track_path, track_title="Audio Preview"):
        super().__init__(parent)
        self.parent = parent
        self.engine = engine
        self.path = track_path
        self.title_text = track_title
        
        self.title(f"Funky Moose Player - {os.path.basename(track_path)}")
        w, h = 640, 480
        self.resizable(False, False)
        self.configure(bg=BG)
        self.transient(parent)
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.grab_set()
        
        self._photo = None
        self._waveform_path = os.path.join(os.path.dirname(track_path), ".waveform_cache.png")
        self._duration = loudness_tools.probe_duration(track_path) or 1.0 # Fallback
        
        # Center Window + Proper Size Lockdown
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self.build_ui()
        self.start_engine()
        self.update_pos()

    def build_ui(self):
        # Header area
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=SPACE_MD, pady=SPACE_MD)
        
        AkmHeader(hdr, text=self.title_text.upper(), font=FONT_LG, fg=ACCENT).pack(anchor="w")
        AkmSubLabel(hdr, text=os.path.basename(self.path), font=FONT_SM).pack(anchor="w")
        
        # Waveform Container (FORCE HEIGHT)
        self.wave_card = AkmCard(self, bg_color="#08080A", height=180)
        self.wave_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self.wave_label = tk.Label(self.wave_card.inner, bg="#08080A")
        self.wave_label.pack(fill="both", expand=True)
        
        # Async waveform generation
        def _gen():
            if loudness_tools.generate_waveform_image(self.path, self._waveform_path, width=560, height=180, hex_color=ACCENT):
                self.after(50, self._load_waveform)
        
        # Quick check if exists, otherwise generate
        if os.path.exists(self._waveform_path): self._load_waveform()
        else: threading.Thread(target=_gen, daemon=True).start() if "threading" in globals() else None

        # Progress Section (FORCE HEIGHT)
        prog_card = AkmCard(self, bg_color=PANEL, height=80)
        prog_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        p_inner = prog_card.inner
        
        self.pos_var = tk.DoubleVar()
        self.pos_slider = tk.Scale(p_inner, from_=0, to=self._duration, orient="horizontal", 
                                   variable=self.pos_var, bg=PANEL, fg=TEXT, 
                                   highlightthickness=0, troughcolor="#000000", activebackground=ACCENT,
                                   showvalue=False)
        self.pos_slider.pack(fill="x", padx=SPACE_SM, pady=(SPACE_SM, 0))
        
        # Smooth Seeking: Drag detection
        self._drag_active = False
        self.pos_slider.bind("<Button-1>", lambda e: setattr(self, "_drag_active", True))
        self.pos_slider.bind("<ButtonRelease-1>", self._on_drag_end)
        
        # Update during drag (display only)
        self.pos_slider.config(command=self._on_seek)
        
        time_frame = tk.Frame(p_inner, bg=PANEL)
        time_frame.pack(fill="x", padx=SPACE_SM, pady=(0, SPACE_XS))
        self.curr_time_label = AkmLabel(time_frame, text="0:00", bg=PANEL, font=FONT_SM)
        self.curr_time_label.pack(side="left")
        AkmLabel(time_frame, text=loudness_tools.format_seconds(self._duration), bg=PANEL, font=FONT_SM).pack(side="right")

        # Controls Row (FORCE HEIGHT)
        ctrl_card = AkmCard(self, bg_color=PANEL, height=100)
        ctrl_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        c_inner = ctrl_card.inner
        
        # Play/Pause Pill
        from app_ui.ui_patterns import create_btn
        self.play_btn = create_btn(c_inner, "PLAY / PAUSE", self.toggle_pause, primary=True, width=140)
        self.play_btn.pack(side="left", padx=SPACE_SM, pady=20)
        
        # Seek Pills
        self.rw_btn = create_btn(c_inner, "RW", lambda: self.seek_offset(-10), quiet=True, width=60)
        self.rw_btn.pack(side="left", padx=2, pady=20)
        
        self.ff_btn = create_btn(c_inner, "FF", lambda: self.seek_offset(10), quiet=True, width=60)
        self.ff_btn.pack(side="left", padx=2, pady=20)

        # Volume Inlay
        vol_frame = tk.Frame(c_inner, bg=PANEL)
        vol_frame.pack(side="left", padx=SPACE_LG)
        AkmLabel(vol_frame, text="VOL", bg=PANEL, font=FONT_SM).pack(side="left", padx=5)
        self.vol_var = tk.DoubleVar(value=0.8)
        self.vol_slider = tk.Scale(vol_frame, from_=0, to=1.0, resolution=0.05, orient="horizontal",
                                   variable=self.vol_var, length=80, bg=PANEL, highlightthickness=0,
                                   showvalue=False, command=self._on_volume)
        self.vol_slider.pack(side="left")
        
        # Close
        create_btn(c_inner, "CLOSE", self.destroy, quiet=True, width=100).pack(side="right", padx=(SPACE_MD, SPACE_SM))

    def _load_waveform(self):
        try:
            with Image.open(self._waveform_path) as img:
                w, h = 560, 180
                img_resized = img.resize((w, h), Image.Resampling.LANCZOS)
                self._photo = ImageTk.PhotoImage(img_resized)
                self.wave_label.config(image=self._photo)
        except: pass

    def start_engine(self):
        try:
            if self.engine.load(self.path):
                self.engine.set_volume(self.vol_var.get())
                self.engine.play()
                # Initial poll
                self.update_pos()
        except Exception as e:
            print(f"ERROR starting engine: {e}")

    def toggle_pause(self):
        self.engine.pause()

    def seek_offset(self, delta):
        cur = self.engine.get_pos() or 0
        new_pos = cur + delta
        self.engine.set_pos(max(0, min(self._duration, new_pos)))

    def _on_drag_end(self, event):
        """Finalizes seek on mouse release to prevent audio crackling."""
        self._drag_active = False
        new_pos = self.pos_var.get()
        self.engine.set_pos(new_pos)
        self.app.append_log(f"Seek: {loudness_tools.format_seconds(new_pos)}")

    def _on_seek(self, val):
        """Optional: live display update during drag (no audio seek)."""
        if self._drag_active:
            self.curr_time_label.config(text=loudness_tools.format_seconds(float(val)))

    def _on_volume(self, val):
        self.engine.set_volume(float(val))

    def update_pos(self):
        if not self.winfo_exists(): return
        
        try:
            pos = self.engine.get_pos()
            if pos is not None:
                # ONLY update the slider if the user isn't dragging it!
                if not self._drag_active:
                    self.pos_var.set(pos)
                    self.curr_time_label.config(text=loudness_tools.format_seconds(pos))
                
                if pos >= self._duration - 0.1:
                    # End reached (don't stop immediately)
                    pass
        except: pass
            
        self.after(100, self.update_pos)

    def destroy(self):
        self.engine.stop()
        super().destroy()

import threading # Ensure we have it for the waveform gen
