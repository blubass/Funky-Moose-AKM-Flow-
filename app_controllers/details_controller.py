
import os
from tkinter import filedialog
from .base_controller import BaseController
from app_logic import akm_core, loudness_tools, i18n
from app_controllers import detail_controller_tools
from app_ui import ui_patterns, path_ui_tools

class DetailsController(BaseController):
    """Manages granular work metadata editing and resource linking."""
    def __init__(self, app):
        super().__init__(app)
        self._title_signature = None

    def _get_details_view(self):
        return self.get_built_tab("details")

    def refresh_view(self):
        """Refresh detail-tab chrome without overwriting unsaved form edits."""
        self.refresh_titles()
        details_view = self._get_details_view()
        if details_view is not None and hasattr(details_view, "refresh_view"):
            details_view.refresh_view()

    def _get_detail_form_vars(self):
        details_view = self._get_details_view()
        if details_view is not None and hasattr(details_view, "get_form_vars"):
            return details_view.get_form_vars()
        if hasattr(self.app, "get_detail_form_vars"):
            return self.app.get_detail_form_vars()
        return getattr(self.app, "detail_vars", {})

    def _apply_detail_memory_defaults(self):
        detail_vars = self._get_detail_form_vars()
        defaults = akm_core.get_detail_memory()
        for key, value in defaults.items():
            if key in detail_vars:
                detail_vars[key].set(value)
    
    def save_details(self):
        orig = self.app.detail_original_title
        if orig:
            details_view = self._get_details_view()
            tags_text = details_view.get_tags_text() if details_view and hasattr(details_view, "get_tags_text") else ""
            notes_text = details_view.get_notes_text() if details_view and hasattr(details_view, "get_notes_text") else ""
            instrumental = details_view.get_instrumental() if details_view and hasattr(details_view, "get_instrumental") else False
            detail_values = {k: v.get().strip() for k, v in self._get_detail_form_vars().items()}
            
            from app_logic import detail_tools
            upd = detail_tools.build_detail_updates(
                detail_values, tags_text, notes_text,
                self.app.current_detail_status, instrumental
            )
            self.tasks.run(
                lambda: akm_core.update_entry(orig, upd),
                lambda r, updates=upd: self._on_save_details_done(r, updates),
                busy_text="Speichere...",
            )

    def _on_save_details_done(self, result, updates):
        if result[0]:
            akm_core.remember_detail_memory(updates)
        self.app.overview_ctrl._on_g_done(result, i18n._t("ui_btn_save", default="Gespeichert"))

    def clear_details_form(self):
        self.app.detail_original_title = None
        for v in self._get_detail_form_vars().values(): v.set("")
        self._apply_detail_memory_defaults()
        details_view = self._get_details_view()
        if details_view and hasattr(details_view, "clear_tags"):
            details_view.clear_tags()
        if details_view and hasattr(details_view, "clear_notes"):
            details_view.clear_notes()
        if details_view and hasattr(details_view, "set_instrumental"):
            details_view.set_instrumental(False)
        self.set_status_chip("in_progress")

    def refresh_titles(self):
        """Updates the Title combobox with current records."""
        details_view = self._get_details_view()
        if details_view is None or not hasattr(details_view, "set_title_options"):
            self._title_signature = None
            return

        recs = self.state.get_all_records(False)
        signature = (self.state._get_data_mtime(), len(recs))
        if signature == self._title_signature:
            return
        titles = sorted([r.get("title", "") for r in recs if r.get("title")])
        details_view.set_title_options(titles)
        self._title_signature = signature

    def load_selected_title(self):
        """Loads data for a title chosen from the combobox."""
        detail_vars = self._get_detail_form_vars()
        title = detail_vars["title"].get().strip()
        recs = self.state.get_all_records(False)
        match = next((r for r in recs if r.get("title") == title), None)
        if match:
            self._populate_details_from_item(match)
            self.log(i18n._t("log_work_loaded", title=title))

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
        detail_vars = self._get_detail_form_vars()
        detail_vars["audio_path"].set(p)
        filename = os.path.basename(p)
        title_guess = os.path.splitext(filename)[0].replace("_", " ").title()
        
        # Smart logic: If title is empty, use guess. If guess exists in DB, load it!
        current_title = detail_vars["title"].get().strip()
        if not current_title or current_title == title_guess:
            detail_vars["title"].set(title_guess)
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
                detail_vars["duration"].set(f"{mins}:{secs:02d}")
                self.log(i18n._t("log_work_updated", title=f"{title_guess} ({mins}:{secs:02d})"))
            else:
                self.log(i18n._t("log_error", error=f"Metadata error: {filename}"))
        
        self.tasks.run(_extract, _done, busy_text="Metadaten-Analyse...")

    def open_audio_path_in_finder(self): 
        detail_vars = self._get_detail_form_vars()
        p = detail_vars["audio_path"].get()
        if p and os.path.exists(p): ui_patterns.open_in_finder(p)

    def set_status_chip(self, s):
        self.app.current_detail_status = s or "in_progress"
        status_label = self.app.status_text(s)
        details_view = self._get_details_view()
        if details_view and hasattr(details_view, "set_status_chip_display"):
            details_view.set_status_chip_display(s, status_label)

    def _populate_details_from_item(self, item):
        detail_vars = self._get_detail_form_vars()
        detail_controller_tools.populate_detail_view(detail_vars, item)
        state = detail_controller_tools.build_detail_text_state(item)
        self.app.detail_original_title = state["title"]
        details_view = self._get_details_view()
        if details_view and hasattr(details_view, "set_notes_text"):
            details_view.set_notes_text(state["notes_text"])
        if details_view and hasattr(details_view, "set_tags_text"):
            details_view.set_tags_text(state["tags_text"])
        if details_view and hasattr(details_view, "set_instrumental"):
            details_view.set_instrumental(state["instrumental"])
        self.set_status_chip(state["status"])
