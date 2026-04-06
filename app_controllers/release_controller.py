
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from .base_controller import BaseController
from app_ui import ui_patterns
from app_workflows import release_workflows

class ReleaseController(BaseController):
    """Manages release creation, track ordering, and distribution export."""
    
    def handle_drop(self, event):
        data = event.data
        if not data: return
        try:
            raw_files = self.app.tk.splitlist(data)
            added = 0
            for f in raw_files:
                f = f.strip('"\'')
                if os.path.exists(f) and os.path.isfile(f):
                    ext = os.path.splitext(f.lower())[1]
                    if ext in ['.wav', '.aiff', '.aif', '.mp3', '.flac', '.m4a']:
                        track = {
                            "title": os.path.splitext(os.path.basename(f))[0].replace("_", " ").title(),
                            "path": f
                        }
                        self.state.release_tracks.append(track)
                        added += 1
            if added:
                self.refresh_view()
                self.log(f"Release DnD: {added} Tracks hinzugefügt.")
                self.toast(f"{added} TRACKS HINZUGEFÜGT")
        except Exception as e:
            self.log(f"Release DnD Parse Fehler: {e}")

    def refresh_view(self):
        if hasattr(self.app, 'release_track_listbox'):
            self.app.release_track_listbox.delete(0, tk.END)
            for i, t in enumerate(self.state.release_tracks): 
                self.app.release_track_listbox.insert(tk.END, f"{i+1}. {t['title']}")
            if self.app.release_status_label: 
                self.app.release_status_label.config(text=f"{len(self.state.release_tracks)} Tracks")

    def choose_cover(self): 
        p = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png")])
        if p: self.app.release_vars["cover_path"].set(p)

    def choose_export_dir(self): 
        p = filedialog.askdirectory()
        if p: self.app.release_vars["export_dir"].set(p)

    def open_cover_in_finder(self): 
        p = self.app.release_vars["cover_path"].get()
        if p and os.path.exists(p): ui_patterns.open_in_finder(p)

    def open_cover_dialog(self): 
        p = self.app.release_vars["cover_path"].get()
        if p and os.path.exists(p):
            from app_ui.ui_patterns import AkmImagePreviewDialog
            AkmImagePreviewDialog(self.app, p, "Cover Vorschau")
        else:
            self.toast("KEIN COVER GEWÄHLT", color=ui_patterns.FLAVOR_ERROR)

    def build_export(self):
        m = {k: v.get().strip() for k, v in self.app.release_vars.items()}
        if m.get("title") and self.state.release_tracks: 
            self.tasks.run(lambda: release_workflows.start_distro_export(m, self.state.release_tracks), 
                           lambda r: self.log(r[1]), busy_text="Exportiere...")

    def move_track_up(self):
        selection = self.app.release_track_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index > 0:
            self.state.release_tracks[index], self.state.release_tracks[index-1] = self.state.release_tracks[index-1], self.state.release_tracks[index]
            self.refresh_view()
            self.app.release_track_listbox.selection_set(index-1)

    def move_track_down(self):
        selection = self.app.release_track_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.state.release_tracks) - 1:
            self.state.release_tracks[index], self.state.release_tracks[index+1] = self.state.release_tracks[index+1], self.state.release_tracks[index]
            self.refresh_view()
            self.app.release_track_listbox.selection_set(index+1)

    def remove_track(self): 
        selection = self.app.release_track_listbox.curselection()
        if selection:
            self.state.release_tracks.pop(selection[0])
            self.refresh_view()
