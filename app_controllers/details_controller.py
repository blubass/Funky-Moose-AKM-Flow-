
import os
import tkinter as tk
from tkinter import filedialog
from .base_controller import BaseController
from app_logic import akm_core, loudness_tools
from app_ui import ui_patterns, path_ui_tools

class DetailsController(BaseController):
    """Manages granular work metadata editing and resource linking."""
    
    def save_details(self):
        orig = self.app.detail_original_title
        if orig:
            upd = {k: v.get().strip() for k, v in self.app.detail_vars.items()}
            upd["notes"] = self.app.detail_notes.get("1.0", tk.END).strip()
            upd["status"] = self.app.current_detail_status
            self.tasks.run(lambda: akm_core.update_entry(orig, upd), 
                           lambda r: self.app.overview_ctrl._on_g_done(r, "Gespeichert"), 
                           busy_text="Speichere...")

    def clear_details_form(self):
        self.app.detail_original_title = None
        for v in self.app.detail_vars.values(): v.set("")
        self._set_detail_status_chip("in_progress")

    def choose_audio_path(self):
        p = filedialog.askopenfilename(filetypes=path_ui_tools.AUDIO_FILETYPES)
        if p:
            self.app.detail_vars["audio_path"].set(p)
            filename = os.path.basename(p)
            title_guess = os.path.splitext(filename)[0].replace("_", " ").title()
            self.app.detail_vars["title"].set(title_guess)
            
            def _extract():
                try: return loudness_tools.get_audio_duration(p)
                except: return 0
            
            def _done(dur):
                if dur:
                    mins, secs = int(dur // 60), int(dur % 60)
                    self.app.detail_vars["duration"].set(f"{mins}:{secs:02d}")
                    self.log(f"Metadaten extrahiert: {title_guess} ({mins}:{secs:02d})")
                else:
                    self.log(f"Dauer konnte nicht extrahiert werden für {filename}")
            
            self.tasks.run(_extract, _done, busy_text="Lese Metadaten...")

    def open_audio_path_in_finder(self): 
        p = self.app.detail_vars["audio_path"].get()
        if p and os.path.exists(p): ui_patterns.open_in_finder(p)

    def _set_detail_status_chip(self, s):
        self.app.current_detail_status = s or "in_progress"
        if hasattr(self.app, 'detail_status_var') and self.app.detail_status_var: 
            self.app.detail_status_var.set(self.app.status_text(s))
        if hasattr(self.app, 'detail_status_chip') and self.app.detail_status_chip: 
            ui_patterns.style_chip_label(self.app.detail_status_chip, s, self.app.status_text(s))
