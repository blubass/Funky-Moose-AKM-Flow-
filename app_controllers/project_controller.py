
import os
import traceback
from tkinter import filedialog, messagebox
from .base_controller import BaseController
from app_logic import akm_core
from app_ui import ui_patterns

class ProjectController(BaseController):
    """Manages project persistence, exports, and data imports."""
    
    def save_project(self):
        """Saves current state and cover settings using the custom Moose Save Dialog."""
        try:
            os.makedirs(akm_core.PROJECTS_DIR, exist_ok=True)
            dialog = ui_patterns.AkmSaveDialog(self.app, "Projekt Speichern", akm_core.PROJECTS_DIR, extension=".akm")
            self.app.wait_window(dialog)
            
            path = dialog.result
            if not path:
                self.log("Speichervorgang abgebrochen.")
                return
            
            self.log(f"Speichere Projekt nach: {path}...")
            data = self.state.get_all_records()
            cover_state = self.app.cover_tab.get_state() if hasattr(self.app, "cover_tab") else {}
            
            akm_core.save_project(path, data, cover_state)
            
            self.log(f"Projekt erfolgreich gespeichert: {os.path.basename(path)}")
            self.toast("PROJEKT GESPEICHERT", color=ui_patterns.FLAVOR_SUCCESS)
            
        except Exception as e:
            err_msg = f"FEHLER beim Speichern: {str(e)}"
            self.log(err_msg)
            print(traceback.format_exc())
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{e}")

    def load_project_dialog(self):
        """Loads a project file using the custom Moose Load Dialog."""
        os.makedirs(akm_core.PROJECTS_DIR, exist_ok=True)
        dialog = ui_patterns.AkmLoadDialog(self.app, "Projekt Laden", akm_core.PROJECTS_DIR, extension=".akm")
        self.app.wait_window(dialog)
        
        path = dialog.result
        if not path: return
        
        bundle = akm_core.load_project(path)
        if not bundle:
            messagebox.showerror("Fehler", "Projekt konnte nicht geladen werden.")
            return
            
        data = bundle.get("data", [])
        akm_core.save_data(data)
        self.state.invalidate_cache()
        self.app.overview_ctrl.refresh_list()
        
        if "cover" in bundle and hasattr(self.app, "cover_tab"):
            self.app.cover_tab.set_state(bundle["cover"])
            
        self.log(f"Projekt geladen: {os.path.basename(path)}")
        self.toast("PROJEKT GELADEN", color=ui_patterns.FLAVOR_SUCCESS)

    def import_excel(self):
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if p: self.import_excel_path(p)

    def import_excel_path(self, path):
        if path: self.tasks.run(lambda: akm_core.import_excel(path), self._on_import_done, busy_text="Importiere...")

    def _on_import_done(self, r): 
        msg = f"Importiert: {r[0]} neu, {r[1]} alt"
        self.log(msg)
        self.toast(msg)
        self.state.invalidate_cache()
        self.app.overview_ctrl.refresh_list()

    def add_entry(self, title):
        if not title: return
        self.tasks.run(lambda: akm_core.add_entry(title), 
                       lambda r: self.app.overview_ctrl._on_g_done(r, f"'{title}' angelegt"), 
                       busy_text=f"Lege '{title}' an...")
