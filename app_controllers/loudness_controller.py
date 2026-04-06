
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from .base_controller import BaseController
from app_logic import loudness_tools
from app_ui import ui_patterns, path_ui_tools
from app_workflows import loudness_workflows

class LoudnessController(BaseController):
    """Manages audio analysis, loudness normalization, and matching workflows."""
    
    def choose_files(self):
        p = filedialog.askopenfilenames(filetypes=path_ui_tools.AUDIO_FILETYPES)
        if p: 
            self.state.loudness_files = list(p)
            self.state.loudness_results = [] # Reset to show new files
            self._pop_l_tree()
            self.log(f"{len(p)} neue Audio-Dateien geladen.")

    def handle_drop(self, event):
        """Unified drop handler for loudness files."""
        data = event.data
        if not data: return
        try:
            raw_files = self.app.tk.splitlist(data)
            valid_files = []
            for f in raw_files:
                f = f.strip('"\'')
                if os.path.exists(f) and os.path.isfile(f):
                    ext = os.path.splitext(f.lower())[1]
                    if ext in ['.wav', '.aiff', '.aif', '.mp3', '.flac', '.m4a']:
                        if f not in self.state.loudness_files:
                            valid_files.append(f)
            if valid_files:
                self.state.loudness_files.extend(valid_files)
                self._pop_l_tree()
                self.log(f"Loudness DnD: {len(valid_files)} Audio-Dateien hinzugefügt.")
                self.toast(f"{len(valid_files)} DATEIEN HINZUGEFÜGT")
        except Exception as e:
            self.log(f"Loudness DnD Parse Fehler: {e}")

    def delete_files(self):
        if not hasattr(self.app, 'loudness_tree'): return
        selected = self.app.loudness_tree.selection()
        if not selected:
            self.toast("KEINE AUSWAHL", color=ui_patterns.FLAVOR_ERROR)
            return
        count = 0
        for path in selected:
            if path in self.state.loudness_files:
                self.state.loudness_files.remove(path)
                count += 1
            self.state.loudness_results = [r for r in self.state.loudness_results if r.get("path") != path]
        self._pop_l_tree()
        self.log(f"{count} Dateien aus der Liste entfernt.")
        self.toast(f"{count} ENTFERNT")

    def analyze_files(self):
        if not self.state.loudness_files:
            self.toast("KEINE DATEIEN GELADEN", color=ui_patterns.FLAVOR_ERROR)
            return
        try:
            t_str = self.app.loudness_target_var.get().replace(",", ".")
            p_str = self.app.loudness_peak_var.get().replace(",", ".")
            t = float(t_str or -14.0)
            pk = float(p_str or -1.0)
        except ValueError:
            messagebox.showerror("Eingabefehler", "LUFS oder Peak-Wert ist kein gültiges Zahlenformat.")
            return

        def _work():
            results = []
            for p in self.state.loudness_files:
                try:
                    analysis = loudness_tools.analyze_full_track(p)
                    enriched = loudness_workflows.enrich_analysis_item(analysis, t, pk, loudness_tools)
                    results.append(enriched)
                except Exception as e:
                    self.log(f"Fehler bei {os.path.basename(p)}: {e}")
                    results.append({"filename": os.path.basename(p), "path": p, "ok": False, "error": str(e), "match_status": "Fehler"})
            return results

        self.tasks.run(_work, self._on_l_done, busy_text="Analysiere Lautheit...")

    def _on_l_done(self, r): 
        self.state.loudness_results = r
        self._pop_l_tree()
        self.log(f"Analyse abgeschlossen: {len(r)} Dateien.")

    def _pop_l_tree(self):
        if not hasattr(self.app, 'loudness_tree'): return
        self.app.loudness_tree.delete(*self.app.loudness_tree.get_children())
        results_map = {it.get("path"): it for it in self.state.loudness_results} if self.state.loudness_results else {}
        if self.state.loudness_files:
            for f in self.state.loudness_files:
                it = results_map.get(f) or {
                    "filename": os.path.basename(f), "path": f,
                    "duration_display": "---", "integrated_lufs": None,
                    "true_peak_dbtp": None, "sample_peak_dbfs": None,
                    "gain_to_target_db": None, "predicted_true_peak_after_gain": None,
                    "match_status": "Neu geladen", "export_info": "Bereit für Analyse"
                }
                row = loudness_workflows.build_tree_row(it)
                self.app.loudness_tree.insert("", tk.END, iid=f, values=row["values"], tags=row["tags"])

    def on_tree_activate(self, event):
        selected = self.app.loudness_tree.selection()
        if selected:
            path = selected[0]
            if os.path.exists(path):
                self.app.open_audio_player_for_path(path, os.path.basename(path))
            else:
                self.toast("DATEI NICHT GEFUNDEN", color=ui_patterns.FLAVOR_ERROR)

    def import_selected_work(self):
        it = self.app.overview_ctrl._get_selected_overview_item()
        if it and it.get("audio_path"):
            self.state.loudness_files = [it["audio_path"]]
            self._pop_l_tree()
            self.app.select_tab_by_id("loudness")

    def import_filtered_works(self):
        self.state.loudness_files = [it["audio_path"] for it in self.state.filtered_records if it.get("audio_path")]
        self._pop_l_tree()
        self.app.select_tab_by_id("loudness")

    def choose_output_dir(self):
        p = filedialog.askdirectory()
        if p: self.app.loudness_output_dir_var.set(p)

    def export_files(self):
        out = self.app.loudness_output_dir_var.get()
        if not out:
            out = filedialog.askdirectory(title="Wähle Zielordner für Match-Export")
            if out: self.app.loudness_output_dir_var.set(out)
            else: return

        pk = float(self.app.loudness_peak_var.get() or -1.0)
        lim = self.app.loudness_use_limiter_var.get() if hasattr(self.app, 'loudness_use_limiter_var') else True
        if not self.state.loudness_results:
            self.toast("ANALYSE FEHLT", color=ui_patterns.FLAVOR_ERROR)
            return

        def _work():
            return [loudness_workflows.export_result_item(it, out, pk, lim, loudness_tools) for it in self.state.loudness_results]

        self.tasks.run(_work, self._on_export_done, busy_text="Exportiere Audio...")

    def _on_export_done(self, r):
        self.log(f"Export abgeschlossen: {len(r)} Dateien verarbeitet.")
        self._pop_l_tree()
        self.toast("EXPORT FERTIG", color=ui_patterns.FLAVOR_SUCCESS)
