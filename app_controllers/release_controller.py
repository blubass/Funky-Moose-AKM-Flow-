
import os
from tkinter import filedialog
from .base_controller import BaseController
from app_logic import akm_core, assistant_tools, release_tools, i18n
from app_ui import ui_patterns
from app_ui import release_view_tools
from app_workflows import release_workflows

class ReleaseController(BaseController):
    """Manages release creation, track ordering, and distribution export."""
    def __init__(self, app):
        super().__init__(app)
        self._last_view_signature = None

    def _get_release_view(self):
        return self.get_built_tab("release")

    def _get_release_form_value(self, key):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "get_form_value"):
            return release_view.get_form_value(key)
        cache = getattr(self.app, "release_state_cache", {}) or {}
        return (cache.get(key) or "").strip()

    def _set_release_form_value(self, key, value):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "set_form_value"):
            release_view.set_form_value(key, value)
        if hasattr(self.app, "release_state_cache"):
            self.app.release_state_cache[key] = value

    def _get_release_form_state(self):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "get_form_state"):
            form_state = release_view.get_form_state()
            if hasattr(self.app, "release_state_cache"):
                self.app.release_state_cache = dict(form_state)
            return form_state
        return dict(getattr(self.app, "release_state_cache", {}) or {})

    def _has_release_track_list(self):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "has_track_list"):
            return bool(release_view.has_track_list())
        return False

    def _build_release_track_labels(self):
        return [
            release_view_tools.build_release_track_row_label(i + 1, track)
            for i, track in enumerate(self.state.release_tracks)
        ]

    def _build_release_action_hint(self):
        counts = release_view_tools.build_release_source_counts(self.state.release_tracks)
        return release_view_tools.build_release_action_hint(counts)

    def _build_release_status_text(self, signature):
        _track_signature, _release_title, cover_path, export_dir, _has_listbox = signature
        return release_view_tools.build_release_status_text(
            len(self.state.release_tracks),
            bool(cover_path),
            bool(export_dir),
            self._has_release_track_list(),
        )

    def _build_release_preflight_text(self, signature):
        _track_signature, release_title, cover_path, export_dir, _has_listbox = signature
        return release_view_tools.build_release_preflight_text(
            len(self.state.release_tracks),
            release_title,
            bool(cover_path),
            bool(export_dir),
            release_view_tools.build_release_source_counts(self.state.release_tracks),
        )

    def _build_release_flow_hint(self, signature):
        _track_signature, release_title, cover_path, export_dir, _has_listbox = signature
        return release_view_tools.build_release_flow_hint(
            len(self.state.release_tracks),
            release_title,
            bool(cover_path),
            bool(export_dir),
            release_view_tools.build_release_source_counts(self.state.release_tracks),
        )

    def _get_selected_track_indices(self):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "get_selected_track_indices"):
            return tuple(release_view.get_selected_track_indices())
        return ()

    def _select_track_index(self, index):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "select_track_index"):
            release_view.select_track_index(index)

    def _build_view_signature(self):
        release_title = self._get_release_form_value("title")
        cover_path = self._get_release_form_value("cover_path")
        export_dir = self._get_release_form_value("export_dir")
        track_signature = tuple(
            (track.get("audio_path") or "", track.get("title") or "", track.get("source") or "")
            for track in self.state.release_tracks
        )
        return (track_signature, release_title, cover_path, export_dir, self._has_release_track_list())

    def _refresh_after_release_import(self, open_batch=False):
        self.state.invalidate_cache()
        overview_ctrl = getattr(self.app, "overview_ctrl", None)
        if overview_ctrl is not None and hasattr(overview_ctrl, "refresh_list"):
            overview_ctrl.refresh_list()
        batch_ctrl = getattr(self.app, "batch_ctrl", None)
        if batch_ctrl is not None and hasattr(batch_ctrl, "reload_flow_data"):
            batch_ctrl.reload_flow_data(preferred_index=0)
        if open_batch:
            self.app.select_tab_by_id("batch")

    def _on_release_import_done(self, imported_items, open_batch=False):
        messages = assistant_tools.build_import_log_messages(imported_items)
        summary = messages[0].replace("Excel-Import", "Release -> AKM")
        self.log(summary)
        for message in messages[1:]:
            self.log(message)
        self.toast(summary, color=ui_patterns.FLAVOR_SUCCESS)
        self._refresh_after_release_import(open_batch=open_batch)

    def _on_export_done(self, result):
        ok, message = result
        self.log(message)
        if not ok:
            self.toast(i18n._t("log_export_error", error="").upper(), color=ui_patterns.FLAVOR_ERROR)
            return
        self.toast(i18n._t("log_export_success").upper(), color=ui_patterns.FLAVOR_SUCCESS)
        self.import_release_to_batch(open_batch=True)

    def import_release_to_batch(self, open_batch=False):
        import_tracks = release_workflows.build_release_import_tracks(self.state.release_tracks)
        if not import_tracks:
            self.toast(i18n._t("rel_radar_empty").upper(), color=ui_patterns.FLAVOR_ERROR)
            return
        self.tasks.run(
            lambda: akm_core.import_tracks(import_tracks),
            lambda items: self._on_release_import_done(items, open_batch=open_batch),
            busy_text="Lade Release in AKM...",
        )
    
    def handle_drop(self, event):
        data = event.data
        if not data: return
        try:
            raw_files = self.tasks.parse_dnd_files(data)
            clean_paths = release_workflows.clean_release_drop_paths(raw_files)
            records = self.state.get_all_records(copy_data=False)
            candidate_tracks = []
            for path in clean_paths:
                if not release_tools.is_supported_audio_path(path):
                    continue
                exact_work = release_tools.find_work_by_exact_audio_path(records, path)
                title_work = None
                if exact_work is None:
                    title_work = release_tools.find_work_by_title_like_audio_path(records, path)
                candidate_tracks.append(
                    release_workflows.build_release_track_from_match(
                        path,
                        exact_work=exact_work,
                        title_work=title_work,
                    )
                )

            result = release_workflows.append_unique_release_tracks(
                self.state.release_tracks,
                candidate_tracks,
            )
            if result["added"]:
                added_count = len(result["added"])
                self.state.release_tracks = result["tracks"]
                self.refresh_view()
                self.log(i18n._t("log_release_drop_added", count=added_count))
                self.toast(i18n._t("log_tracks_added", count=added_count).upper())
        except Exception as e:
            self.log(f"Release DnD Parse Fehler: {e}")

    def refresh_view(self, force=False):
        release_view = self._get_release_view()
        if release_view is None or not hasattr(release_view, "render_release_state"):
            return

        signature = self._build_view_signature()
        if not force and signature == self._last_view_signature:
            return
        release_view.render_release_state(
            track_labels=self._build_release_track_labels(),
            action_hint=self._build_release_action_hint(),
            preflight_text=self._build_release_preflight_text(signature),
            flow_hint=self._build_release_flow_hint(signature),
            status_text=self._build_release_status_text(signature),
        )
        self._last_view_signature = signature

    def choose_cover(self): 
        p = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png")])
        if p:
            self._set_release_form_value("cover_path", p)
            self.refresh_view(force=True)

    def choose_export_dir(self): 
        p = filedialog.askdirectory()
        if p:
            self._set_release_form_value("export_dir", p)
            self.refresh_view(force=True)

    def open_cover_in_finder(self): 
        p = self._get_release_form_value("cover_path")
        if p and os.path.exists(p): ui_patterns.open_in_finder(p)

    def open_cover_dialog(self): 
        p = self._get_release_form_value("cover_path")
        if p and os.path.exists(p):
            from app_ui.ui_patterns import AkmImagePreviewDialog
            AkmImagePreviewDialog(self.app, p, i18n._t("cov_btn_zoom"))
        else:
            self.toast(i18n._t("rel_preflight_cover_missing").upper(), color=ui_patterns.FLAVOR_ERROR)

    def build_export(self):
        m = {k: (v or "").strip() for k, v in self._get_release_form_state().items()}
        if m.get("title") and self.state.release_tracks: 
            self.tasks.run(
                lambda: release_workflows.start_distro_export(m, self.state.release_tracks),
                self._on_export_done,
                busy_text="Exportiere...",
            )

    def move_track_up(self):
        selection = self._get_selected_track_indices()
        if not selection:
            return

        updated_tracks, target_index = release_workflows.move_release_track(
            self.state.release_tracks,
            selection[0],
            -1,
        )
        if target_index is not None:
            self.state.release_tracks = updated_tracks
            self.refresh_view()
            self._select_track_index(target_index)

    def move_track_down(self):
        selection = self._get_selected_track_indices()
        if not selection:
            return

        updated_tracks, target_index = release_workflows.move_release_track(
            self.state.release_tracks,
            selection[0],
            1,
        )
        if target_index is not None:
            self.state.release_tracks = updated_tracks
            self.refresh_view()
            self._select_track_index(target_index)

    def remove_track(self): 
        selection = sorted(self._get_selected_track_indices(), reverse=True)
        if selection:
            updated_tracks = list(self.state.release_tracks)
            for idx in selection:
                updated_tracks, _removed = release_workflows.remove_release_track_at(
                    updated_tracks,
                    idx,
                )
            self.state.release_tracks = updated_tracks
            self.refresh_view()
            self.toast(i18n._t("ui_btn_remove", default="ENTFERNT").upper())
