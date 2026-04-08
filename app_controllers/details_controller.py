
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

    def _get_details_view(self):
        if hasattr(self.app, "get_built_tab"):
            return self.app.get_built_tab("details")
        return getattr(getattr(self.app, "tab_system", None), "_instances", {}).get("details")

    def refresh_view(self):
        """Refresh detail-tab chrome without overwriting unsaved form edits."""
        self.refresh_titles()
        details_view = self._get_details_view()
        if details_view is not None and hasattr(details_view, "refresh_view"):
            details_view.refresh_view()
    
    def save_details(self):
        orig = self.app.detail_original_title
        if orig:
            details_view = self._get_details_view()
            if details_view and hasattr(details_view, "get_tags_text"):
                tags_text = details_view.get_tags_text()
            else:
                tags_text = self.app.detail_tags.get("1.0", "end-1c").strip() if hasattr(self.app, 'detail_tags') else ""
            if details_view and hasattr(details_view, "get_notes_text"):
                notes_text = details_view.get_notes_text()
            else:
                notes_text = self.app.detail_notes.get("1.0", "end-1c").strip() if hasattr(self.app, 'detail_notes') else ""
            if details_view and hasattr(details_view, "get_instrumental"):
                instrumental = details_view.get_instrumental()
            else:
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
        details_view = self._get_details_view()
        if details_view and hasattr(details_view, "clear_tags"):
            details_view.clear_tags()
        elif hasattr(self.app, 'detail_tags'):
            self.app.detail_tags.delete("1.0", tk.END)
        if details_view and hasattr(details_view, "clear_notes"):
            details_view.clear_notes()
        elif hasattr(self.app, 'detail_notes'):
            self.app.detail_notes.delete("1.0", tk.END)
        if details_view and hasattr(details_view, "set_instrumental"):
            details_view.set_instrumental(False)
        elif hasattr(self.app, 'detail_instrumental_var'):
            self.app.detail_instrumental_var.set(False)
        self.set_status_chip("in_progress")

    def refresh_titles(self):
        """Updates the Title combobox with current records."""
        recs = self.state.get_all_records(False)
        signature = (self.state._get_data_mtime(), len(recs))
        details_view = self._get_details_view()
        if signature == self._title_signature and (
            (details_view and hasattr(details_view, "set_title_options")) or hasattr(self.app, 'detail_title_combo')
        ):
            return
        titles = sorted([r.get("title", "") for r in recs if r.get("title")])
        if details_view and hasattr(details_view, "set_title_options"):
            details_view.set_title_options(titles)
        elif hasattr(self.app, 'detail_title_combo'):
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
            details_view = self._get_details_view()
            if details_view and hasattr(details_view, "set_notes_text"):
                details_view.set_notes_text(match.get("notes", ""))
            elif hasattr(self.app, 'detail_notes'):
                self.app.detail_notes.delete("1.0", tk.END)
                self.app.detail_notes.insert("1.0", match.get("notes", ""))
            # Load Tags
            raw_tags = match.get("tags", [])
            tags_text = ", ".join(raw_tags) if isinstance(raw_tags, list) else str(raw_tags)
            if details_view and hasattr(details_view, "set_tags_text"):
                details_view.set_tags_text(tags_text)
            elif hasattr(self.app, 'detail_tags'):
                self.app.detail_tags.delete("1.0", tk.END)
                self.app.detail_tags.insert("1.0", tags_text)
            # Load Instrumental flag
            if details_view and hasattr(details_view, "set_instrumental"):
                details_view.set_instrumental(bool(match.get("instrumental", False)))
            elif hasattr(self.app, 'detail_instrumental_var'):
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
            try:
                return loudness_tools.probe_duration(p)
            except Exception:
                return 0
        
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
        status_label = self.app.status_text(s)
        details_view = self._get_details_view()
        if details_view and hasattr(details_view, "set_status_chip_display"):
            details_view.set_status_chip_display(s, status_label)
            return
        if hasattr(self.app, 'detail_status_var') and self.app.detail_status_var: 
            self.app.detail_status_var.set(status_label)
        if hasattr(self.app, 'detail_status_chip') and self.app.detail_status_chip: 
            ui_patterns.style_chip_label(self.app.detail_status_chip, s, status_label)
