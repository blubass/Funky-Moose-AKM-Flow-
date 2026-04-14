
import os
from tkinter import filedialog, messagebox
from .base_controller import BaseController
from app_logic import loudness_tools, i18n
from app_ui import ui_patterns, path_ui_tools
from app_workflows import loudness_workflows

class LoudnessController(BaseController):
    """Manages audio analysis, loudness normalization, and matching workflows."""

    def _get_loudness_view(self):
        return self.get_built_tab("loudness")

    def _ensure_loudness_view(self):
        try:
            loudness_tab = getattr(self.app, "loudness_tab", None)
        except Exception:
            loudness_tab = None
        return loudness_tab or self._get_loudness_view()

    def _has_loudness_tree(self):
        loudness_view = self._get_loudness_view()
        return bool(loudness_view and hasattr(loudness_view, "has_tree") and loudness_view.has_tree())

    def _get_selected_paths(self):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "get_selected_paths"):
            return tuple(loudness_view.get_selected_paths())
        return ()

    def _clear_tree(self):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "clear_tree"):
            loudness_view.clear_tree()

    def _insert_tree_row(self, path, values, tags=()):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "insert_tree_row"):
            loudness_view.insert_tree_row(path, values, tags=tags)

    def _get_target_text(self):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "get_target_text"):
            return loudness_view.get_target_text()
        return "-14.0"

    def _get_peak_text(self):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "get_peak_text"):
            return loudness_view.get_peak_text()
        return "-1.0"

    def _get_output_dir(self):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "get_output_dir"):
            return loudness_view.get_output_dir()
        return ""

    def _set_output_dir(self, path):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "set_output_dir"):
            loudness_view.set_output_dir(path)

    def _get_use_limiter(self):
        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "get_use_limiter"):
            return loudness_view.get_use_limiter()
        return True
    
    def choose_files(self):
        p = filedialog.askopenfilenames(filetypes=path_ui_tools.AUDIO_FILETYPES)
        if p: 
            self.state.loudness_files = list(p)
            self.state.loudness_results = [] # Reset to show new files
            self._pop_l_tree()
            self._apply_workflow_state(
                loudness_workflows.build_loaded_files_state(self.state.loudness_files)
            )

    def handle_drop(self, event):
        """Unified drop handler for loudness files."""
        data = event.data
        if not data: return
        try:
            raw_files = self.tasks.parse_dnd_files(data)
            valid_files = []
            for f in raw_files:
                if os.path.exists(f) and os.path.isfile(f):
                    ext = os.path.splitext(f.lower())[1]
                    if ext in ['.wav', '.aiff', '.aif', '.mp3', '.flac', '.m4a']:
                        if f not in self.state.loudness_files:
                            valid_files.append(f)
            if valid_files:
                self.state.loudness_files.extend(valid_files)
                self._pop_l_tree()
                self._apply_workflow_state(
                    loudness_workflows.build_loaded_files_state(self.state.loudness_files)
                )
                self.log(i18n._t("log_work_loaded", title=f"{len(valid_files)} Audio files"))
                self.toast(i18n._t("rel_preflight_ready", count=len(valid_files)).upper())
        except Exception as e:
            self.log(i18n._t("log_error", error=str(e)))

    def delete_files(self):
        if not self._has_loudness_tree():
            return
        selected = self._get_selected_paths()
        if not selected:
            self.toast(i18n._t("rel_radar_empty").upper(), color=ui_patterns.FLAVOR_ERROR)
            return
        count = 0
        for path in selected:
            if path in self.state.loudness_files:
                self.state.loudness_files.remove(path)
                count += 1
            self.state.loudness_results = [r for r in self.state.loudness_results if r.get("path") != path]
        self._pop_l_tree()
        self.log(i18n._t("log_work_deleted", title=f"{count} files"))
        self.toast(i18n._t("ui_btn_remove", default="ENTFERNT").upper())

    def analyze_files(self):
        if not self.state.loudness_files:
            self.toast(i18n._t("rel_radar_empty").upper(), color=ui_patterns.FLAVOR_ERROR)
            return
        try:
            t_str = self._get_target_text().replace(",", ".")
            p_str = self._get_peak_text().replace(",", ".")
            t = float(t_str or -14.0)
            pk = float(p_str or -1.0)
        except ValueError:
            messagebox.showerror("Eingabefehler", i18n._t("log_error", error="Invalid number format"))
            return

        def _work():
            results = []
            for p in self.state.loudness_files:
                try:
                    analysis = loudness_tools.analyze_full_track(p)
                    enriched = loudness_workflows.enrich_analysis_item(analysis, t, pk, loudness_tools)
                    results.append(enriched)
                except Exception as e:
                    self.log(i18n._t("log_error", error=f"{os.path.basename(p)}: {e}"))
                    results.append({"filename": os.path.basename(p), "path": p, "ok": False, "error": str(e), "match_status": i18n._t("cov_status_error")})
            return results

        self.tasks.run(_work, self._on_l_done, busy_text="Analysiere Lautheit...")

    def _on_l_done(self, r): 
        self.state.loudness_results = r
        self._pop_l_tree()
        self.log(i18n._t("loud_status_done", lufs=f"{len(r)} files")) # repurposing

    def _pop_l_tree(self):
        if not self._has_loudness_tree():
            return
        self._clear_tree()
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
                self._insert_tree_row(f, row["values"], tags=row["tags"])

    def on_tree_activate(self, event):
        selected = self._get_selected_paths()
        if selected:
            path = selected[0]
            if os.path.exists(path):
                self.app.open_audio_player_for_path(path, os.path.basename(path))
            else:
                self.toast(i18n._t("err_file_not_found").upper(), color=ui_patterns.FLAVOR_ERROR)

    def import_selected_work(self):
        it = self.app.overview_ctrl._get_selected_overview_item()
        if it and it.get("audio_path"):
            self._ensure_loudness_view()
            self.state.loudness_files = [it["audio_path"]]
            self.state.loudness_results = []
            self._pop_l_tree()
            self._apply_workflow_state(
                loudness_workflows.build_selected_work_import_state(
                    it.get("title") or os.path.basename(it["audio_path"]),
                    it["audio_path"],
                )
            )
            self.app.select_tab_by_id("loudness")

    def import_filtered_works(self):
        items = loudness_workflows.collect_importable_overview_audio(
            self.state.filtered_records
        )
        self._ensure_loudness_view()
        self.state.loudness_files = [item["path"] for item in items]
        self.state.loudness_results = []
        self._pop_l_tree()
        if items:
            self._apply_workflow_state(
                loudness_workflows.build_filtered_works_import_state(items)
            )
        self.app.select_tab_by_id("loudness")

    def choose_output_dir(self):
        p = filedialog.askdirectory()
        if p:
            self._set_output_dir(p)

    def export_files(self):
        out = self._get_output_dir()
        if not out:
            out = filedialog.askdirectory(title="Wähle Zielordner für Match-Export")
            if out:
                self._set_output_dir(out)
            else:
                return

        pk = float(self._get_peak_text() or -1.0)
        lim = self._get_use_limiter()
        if not self.state.loudness_results:
            self.toast(i18n._t("rel_radar_empty").upper(), color=ui_patterns.FLAVOR_ERROR)
            return

        def _work():
            return [loudness_workflows.export_result_item(it, out, pk, lim, loudness_tools) for it in self.state.loudness_results]

        self.tasks.run(_work, self._on_export_done, busy_text="Exportiere Audio...")

    def _on_export_done(self, r):
        self.log(i18n._t("rel_status_ready") + f" ({len(r)})")
        self._pop_l_tree()
        self.toast(i18n._t("log_export_success").upper(), color=ui_patterns.FLAVOR_SUCCESS)

    def _apply_workflow_state(self, workflow_state):
        if not workflow_state:
            return

        status_text = workflow_state.get("status_text")
        hint_text = workflow_state.get("hint_text")
        log_lines = workflow_state.get("log_lines", [])

        loudness_view = self._get_loudness_view()
        if loudness_view and hasattr(loudness_view, "apply_workflow_state"):
            loudness_view.apply_workflow_state(status_text, hint_text, log_lines)

        for line in log_lines:
            self.log(line)
