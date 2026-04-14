
import os
import traceback
from tkinter import filedialog, messagebox
from .base_controller import BaseController
from app_logic import akm_core, assistant_tools, i18n
from app_ui import ui_patterns

class ProjectController(BaseController):
    """Manages project persistence, exports, and data imports."""

    def _ensure_projects_dir(self):
        os.makedirs(akm_core.PROJECTS_DIR, exist_ok=True)

    def _open_project_dialog(self, dialog_cls, title):
        self._ensure_projects_dir()
        dialog = dialog_cls(self.app, title, akm_core.PROJECTS_DIR, extension=".akm")
        self.app.wait_window(dialog)
        return dialog.result

    def _collect_tab_state(self, cache_attr, tab_id, getter_name):
        state = dict(getattr(self.app, cache_attr, {}) or {})
        tab = self.get_built_tab(tab_id)
        getter = getattr(tab, getter_name, None) if tab is not None else None
        if callable(getter):
            live_state = getter()
            if isinstance(live_state, dict):
                state = dict(live_state)
        if hasattr(self.app, cache_attr):
            setattr(self.app, cache_attr, dict(state))
        return state

    def _apply_tab_state(self, cache_attr, tab_id, state, setter_name):
        normalized_state = dict(state or {})
        if hasattr(self.app, cache_attr):
            setattr(self.app, cache_attr, dict(normalized_state))
        tab = self.get_built_tab(tab_id)
        setter = getattr(tab, setter_name, None) if tab is not None else None
        if callable(setter):
            setter(normalized_state)
        return normalized_state

    def _collect_cover_state(self):
        """Collect cover metadata without forcing the cover tab to build."""
        return self._collect_tab_state("cover_state_cache", "cover", "get_state")

    def _collect_release_vars(self):
        """Collect release metadata even if the release tab has not been built yet."""
        return self._collect_tab_state("release_state_cache", "release", "get_form_state")

    def _build_release_state(self):
        return {
            "vars": self._collect_release_vars(),
            "tracks": list(self.state.release_tracks),
        }

    def _apply_cover_state(self, cover_state):
        self._apply_tab_state("cover_state_cache", "cover", cover_state, "set_state")

    def _apply_release_state(self, release_state):
        payload = dict(release_state or {})
        self.state.release_tracks = list(payload.get("tracks", []) or [])
        self._apply_tab_state(
            "release_state_cache",
            "release",
            payload.get("vars", {}),
            "set_form_state",
        )
        self.app.release_ctrl.refresh_view(force=True)
    
    def save_project(self):
        """Saves current state and cover settings using the custom Moose Save Dialog."""
        try:
            path = self._open_project_dialog(ui_patterns.AkmSaveDialog, "Projekt Speichern")
            if not path:
                self.log(i18n._t("log_error", error="Save cancelled"))
                return False
            
            self.log(i18n._t("log_export_status", path=path))
            data = self.state.get_all_records()
            cover_state = self._collect_cover_state()
            release_state = self._build_release_state()
            
            akm_core.save_project(path, data, cover_state, release_state)
            
            self.log(i18n._t("log_export_success") + f": {os.path.basename(path)}")
            self.toast(i18n._t("ui_btn_save", default="PROJEKT GESPEICHERT").upper(), color=ui_patterns.FLAVOR_SUCCESS)
            return True
            
        except Exception as e:
            err_msg = i18n._t("log_export_error", error=str(e))
            self.log(err_msg)
            print(traceback.format_exc())
            messagebox.showerror("Fehler", f"Save failed:\n{e}")
            return False

    def load_project_dialog(self):
        """Loads a project file using the custom Moose Load Dialog."""
        path = self._open_project_dialog(ui_patterns.AkmLoadDialog, "Projekt Laden")
        if not path:
            return

        try:
            bundle = akm_core.load_project(path)
        except akm_core.DataFileError as exc:
            self.log(f"FEHLER beim Laden: {exc}")
            messagebox.showerror("Fehler", str(exc))
            return
        except Exception as exc:
            self.log(f"FEHLER beim Laden: {exc}")
            messagebox.showerror("Fehler", f"Projekt konnte nicht geladen werden:\n{exc}")
            return

        if not bundle:
            messagebox.showerror("Fehler", i18n._t("log_project_load_error", error="Bundle is empty"))
            return
            
        data = bundle.get("data", [])
        akm_core.save_data(data)
        self.state.invalidate_cache()
        self.app.overview_ctrl.refresh_list()
        
        if "cover" in bundle:
            self._apply_cover_state(bundle.get("cover"))
            
        if "release" in bundle:
            self._apply_release_state(bundle.get("release"))
            
        self.log(i18n._t("log_work_loaded", title=os.path.basename(path)))
        self.toast(i18n._t("log_project_loaded", title=os.path.basename(path)).upper(), color=ui_patterns.FLAVOR_SUCCESS)

    def import_excel(self):
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if p: self.import_excel_path(p)

    def import_excel_path(self, path):
        if path: self.tasks.run(lambda: akm_core.import_excel(path), self._on_import_done, busy_text="Importiere...")

    def _on_import_done(self, imported_items):
        messages = assistant_tools.build_import_log_messages(imported_items)
        for message in messages:
            self.log(message)
        self.toast(messages[0])
        self.state.invalidate_cache()
        self.app.overview_ctrl.refresh_list()
        batch_ctrl = getattr(self.app, "batch_ctrl", None)
        if batch_ctrl is not None and hasattr(batch_ctrl, "reload_flow_data"):
            batch_ctrl.reload_flow_data(preferred_index=0)

    def add_entry(self, title):
        if not title: return
        defaults = akm_core.get_detail_memory()
        self.tasks.run(
                       lambda: akm_core.add_entry(
                           title,
                           composer=defaults.get("composer", ""),
                           production=defaults.get("production", ""),
                           year=defaults.get("year", ""),
                       ),
                       lambda r: self.app.overview_ctrl._on_g_done(r, i18n._t("log_work_updated", title=title)), 
                       busy_text=i18n._t("task_busy_text"))
