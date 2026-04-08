
import os
import traceback
from tkinter import filedialog, messagebox
from .base_controller import BaseController
from app_logic import akm_core, assistant_tools
from app_ui import ui_patterns

class ProjectController(BaseController):
    """Manages project persistence, exports, and data imports."""

    def _get_built_tab(self, tab_id):
        tab_system = getattr(self.app, "tab_system", None)
        instances = getattr(tab_system, "_instances", None)
        if not instances:
            return None
        return instances.get(tab_id)

    def _collect_cover_state(self):
        """Collect cover metadata without forcing the cover tab to build."""
        cover_state = dict(getattr(self.app, "cover_state_cache", {}) or {})
        cover_tab = self._get_built_tab("cover")
        if cover_tab is not None:
            cover_state = cover_tab.get_state()
        if hasattr(self.app, "cover_state_cache"):
            self.app.cover_state_cache = dict(cover_state)
        return cover_state

    def _collect_release_vars(self):
        """Collect release metadata even if the release tab has not been built yet."""
        release_vars = dict(getattr(self.app, "release_state_cache", {}) or {})
        release_tab = self._get_built_tab("release")
        if release_tab is not None and hasattr(release_tab, "get_form_state"):
            release_vars.update(release_tab.get_form_state())
        if hasattr(self.app, "release_state_cache"):
            self.app.release_state_cache = dict(release_vars)
        return release_vars
    
    def save_project(self):
        """Saves current state and cover settings using the custom Moose Save Dialog."""
        try:
            os.makedirs(akm_core.PROJECTS_DIR, exist_ok=True)
            dialog = ui_patterns.AkmSaveDialog(self.app, "Projekt Speichern", akm_core.PROJECTS_DIR, extension=".akm")
            self.app.wait_window(dialog)
            
            path = dialog.result
            if not path:
                self.log("Speichervorgang abgebrochen.")
                return False
            
            self.log(f"Speichere Projekt nach: {path}...")
            data = self.state.get_all_records()
            cover_state = self._collect_cover_state()
            
            # Collect Release State
            release_vars = self._collect_release_vars()
            release_state = {
                "vars": release_vars,
                "tracks": self.state.release_tracks
            }
            
            akm_core.save_project(path, data, cover_state, release_state)
            
            self.log(f"Projekt erfolgreich gespeichert: {os.path.basename(path)}")
            self.toast("PROJEKT GESPEICHERT", color=ui_patterns.FLAVOR_SUCCESS)
            return True
            
        except Exception as e:
            err_msg = f"FEHLER beim Speichern: {str(e)}"
            self.log(err_msg)
            print(traceback.format_exc())
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{e}")
            return False

    def load_project_dialog(self):
        """Loads a project file using the custom Moose Load Dialog."""
        os.makedirs(akm_core.PROJECTS_DIR, exist_ok=True)
        dialog = ui_patterns.AkmLoadDialog(self.app, "Projekt Laden", akm_core.PROJECTS_DIR, extension=".akm")
        self.app.wait_window(dialog)
        
        path = dialog.result
        if not path: return

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
            messagebox.showerror("Fehler", "Projekt konnte nicht geladen werden.")
            return
            
        data = bundle.get("data", [])
        akm_core.save_data(data)
        self.state.invalidate_cache()
        self.app.overview_ctrl.refresh_list()
        
        if "cover" in bundle:
            cover_state = dict(bundle.get("cover") or {})
            if hasattr(self.app, "cover_state_cache"):
                self.app.cover_state_cache = dict(cover_state)
            cover_tab = self._get_built_tab("cover")
            if cover_tab is not None:
                cover_tab.set_state(cover_state)
            
        if "release" in bundle:
            r_data = bundle["release"]
            self.state.release_tracks = r_data.get("tracks", [])
            release_vars = dict(r_data.get("vars", {}))
            if hasattr(self.app, "release_state_cache"):
                self.app.release_state_cache = dict(release_vars)
            release_tab = self._get_built_tab("release")
            if release_tab is not None and hasattr(release_tab, "set_form_state"):
                release_tab.set_form_state(release_vars)
            self.app.release_ctrl.refresh_view(force=True)
            
        self.log(f"Projekt geladen: {os.path.basename(path)}")
        self.toast("PROJEKT GELADEN", color=ui_patterns.FLAVOR_SUCCESS)

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

    def add_entry(self, title):
        if not title: return
        self.tasks.run(lambda: akm_core.add_entry(title),
                       lambda r: self.app.overview_ctrl._on_g_done(r, f"'{title}' angelegt"), 
                       busy_text=f"Lege '{title}' an...")
