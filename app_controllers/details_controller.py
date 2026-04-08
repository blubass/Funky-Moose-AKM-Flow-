
import os
import tkinter as tk
from tkinter import filedialog
from .base_controller import BaseController
from app_logic import akm_core, loudness_tools
from app_ui import ui_patterns, path_ui_tools

class DetailsController(BaseController):
    """Manages granular work metadata editing and resource linking."""
    def __init__(self, app):
        super().__init__(app)
        self._title_signature = None

    def refresh_view(self):
        """Refresh detail-tab chrome without overwriting unsaved form edits."""
        self.refresh_titles()
        tab_system = getattr(self.app, "tab_system", None)
        details_tab = getattr(tab_system, "_instances", {}).get("details") if tab_system else None
        if details_tab is not None and hasattr(details_tab, "refresh_view"):
            details_tab.refresh_view()
    
    def save_details(self):
        orig = self.app.detail_original_title
        if orig:
            tags_text = self.app.detail_tags.get("1.0", "end-1c").strip() if hasattr(self.app, 'detail_tags') else ""
            notes_text = self.app.detail_notes.get("1.0", "end-1c").strip() if hasattr(self.app, 'detail_notes') else ""
            instrumental = self.app.detail_instrumental_var.get() if hasattr(self.app, 'detail_instrumental_var') else False
            detail_values = {k: v.get().strip() for k, v in self.app.detail_vars.items()}
            
            from app_logic import detail_tools
            upd = detail_tools.build_detail_updates(
                detail_values, tags_text, notes_text,
                self.app.current_detail_status, instrumental
            )
            self.tasks.run(lambda: akm_core.update_entry(orig, upd), 
                           lambda r: self.app.overview_ctrl._on_g_done(r, "Gespeichert"), 
                           busy_text="Speichere...")

    def clear_details_form(self):
        self.app.detail_original_title = None
        for v in self.app.detail_vars.values(): v.set("")
        if hasattr(self.app, 'detail_tags'):
            self.app.detail_tags.delete("1.0", tk.END)
        if hasattr(self.app, 'detail_notes'):
            self.app.detail_notes.delete("1.0", tk.END)
        if hasattr(self.app, 'detail_instrumental_var'):
            self.app.detail_instrumental_var.set(False)
        self.set_status_chip("in_progress")

    def refresh_titles(self):
        """Updates the Title combobox with current records."""
        recs = self.state.get_all_records(False)
        signature = (self.state._get_data_mtime(), len(recs))
        if signature == self._title_signature and hasattr(self.app, 'detail_title_combo'):
            return
        titles = sorted([r.get("title", "") for r in recs if r.get("title")])
        if hasattr(self.app, 'detail_title_combo'):
            self.app.detail_title_combo.config(values=titles)
        self._title_signature = signature

    def load_selected_title(self):
        """Loads data for a title chosen from the combobox."""
        title = self.app.detail_vars["title"].get().strip()
        recs = self.state.get_all_records(False)
        match = next((r for r in recs if r.get("title") == title), None)
        if match:
            self.app.detail_original_title = title
            for k, v in self.app.detail_vars.items():
                v.set(str(match.get(k, "")))
            if hasattr(self.app, 'detail_notes'):
                self.app.detail_notes.delete("1.0", tk.END)
                self.app.detail_notes.insert("1.0", match.get("notes", ""))
            # Load Tags
            if hasattr(self.app, 'detail_tags'):
                raw_tags = match.get("tags", [])
                tags_text = ", ".join(raw_tags) if isinstance(raw_tags, list) else str(raw_tags)
                self.app.detail_tags.delete("1.0", tk.END)
                self.app.detail_tags.insert("1.0", tags_text)
            # Load Instrumental flag
            if hasattr(self.app, 'detail_instrumental_var'):
                self.app.detail_instrumental_var.set(bool(match.get("instrumental", False)))
            self.set_status_chip(match.get("status", "in_progress"))
            self.log(f"Werk geladen: {title}")

    def choose_audio_path(self):
        """Selects audio file via dialog and extracts metadata."""
        p = filedialog.askopenfilename(filetypes=path_ui_tools.AUDIO_FILETYPES)
        if p:
            self._process_audio_path(p)

    def handle_audio_drop(self, p):
        """Processes an audio file dropped onto the DetailsTab."""
        if p:
            self._process_audio_path(p)

    def _process_audio_path(self, p):
        """Internal logic to extract title/duration and match with existing database entries."""
        self.app.detail_vars["audio_path"].set(p)
        filename = os.path.basename(p)
        title_guess = os.path.splitext(filename)[0].replace("_", " ").title()
        
        # Smart logic: If title is empty, use guess. If guess exists in DB, load it!
        current_title = self.app.detail_vars["title"].get().strip()
        if not current_title or current_title == title_guess:
            self.app.detail_vars["title"].set(title_guess)
            recs = self.state.get_all_records(False)
            match = next((r for r in recs if r.get("title") == title_guess), None)
            if match:
                self.load_selected_title()

        def _extract():
            try: return loudness_tools.probe_duration(p)
            except: return 0
        
        def _done(dur):
            if dur:
                mins, secs = int(dur // 60), int(dur % 60)
                self.app.detail_vars["duration"].set(f"{mins}:{secs:02d}")
                self.log(f"Audio-Info erfasst: {title_guess} ({mins}:{secs:02d})")
            else:
                self.log(f"Dauer konnte nicht gelesen werden: {filename}")
        
        self.tasks.run(_extract, _done, busy_text="Metadaten-Analyse...")

    def open_audio_path_in_finder(self): 
        p = self.app.detail_vars["audio_path"].get()
        if p and os.path.exists(p): ui_patterns.open_in_finder(p)

    def set_status_chip(self, s):
        self.app.current_detail_status = s or "in_progress"
        if hasattr(self.app, 'detail_status_var') and self.app.detail_status_var: 
            self.app.detail_status_var.set(self.app.status_text(s))
        if hasattr(self.app, 'detail_status_chip') and self.app.detail_status_chip: 
            ui_patterns.style_chip_label(self.app.detail_status_chip, s, self.app.status_text(s))
