
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from .base_controller import BaseController
from app_logic import release_tools
from app_ui import ui_patterns
from app_ui import release_view_tools
from app_workflows import release_workflows

class ReleaseController(BaseController):
    """Manages release creation, track ordering, and distribution export."""
    def __init__(self, app):
        super().__init__(app)
        self._last_view_signature = None

    def _get_release_view(self):
        if hasattr(self.app, "get_built_tab"):
            return self.app.get_built_tab("release")
        return getattr(getattr(self.app, "tab_system", None), "_instances", {}).get("release")

    def _has_release_track_list(self):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "has_track_list"):
            return bool(release_view.has_track_list())
        return hasattr(self.app, "release_track_listbox")

    def _render_legacy_release_view(self, signature):
        if hasattr(self.app, 'release_track_listbox'):
            self.app.release_track_listbox.delete(0, tk.END)
            for i, t in enumerate(self.state.release_tracks):
                label = release_view_tools.build_release_track_row_label(i + 1, t)
                self.app.release_track_listbox.insert(tk.END, label)
        if hasattr(self.app, "release_action_hint_label"):
            counts = release_view_tools.build_release_source_counts(self.state.release_tracks)
            self.app.release_action_hint_label.config(
                text=release_view_tools.build_release_action_hint(counts)
            )
        if hasattr(self.app, "release_status_label") and self.app.release_status_label:
            _track_signature, cover_path, export_dir, _has_listbox = signature
            self.app.release_status_label.config(
                text=release_view_tools.build_release_status_text(
                    len(self.state.release_tracks),
                    bool(cover_path),
                    bool(export_dir),
                    self._has_release_track_list(),
                )
            )

    def _get_selected_track_indices(self):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "get_selected_track_indices"):
            return tuple(release_view.get_selected_track_indices())
        if hasattr(self.app, "release_track_listbox"):
            return tuple(self.app.release_track_listbox.curselection())
        return ()

    def _select_track_index(self, index):
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "select_track_index"):
            release_view.select_track_index(index)
        elif hasattr(self.app, "release_track_listbox"):
            self.app.release_track_listbox.selection_set(index)

    def _build_view_signature(self):
        cover_path = ""
        export_dir = ""
        if hasattr(self.app, "release_vars"):
            cover_var = self.app.release_vars.get("cover_path")
            export_var = self.app.release_vars.get("export_dir")
            cover_path = cover_var.get().strip() if cover_var else ""
            export_dir = export_var.get().strip() if export_var else ""
        track_signature = tuple(
            (track.get("audio_path") or "", track.get("title") or "", track.get("source") or "")
            for track in self.state.release_tracks
        )
        return (track_signature, cover_path, export_dir, self._has_release_track_list())
    
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
                self.state.release_tracks = result["tracks"]
                self.refresh_view()
                self.log(f"Release DnD: {len(result['added'])} Tracks hinzugefügt.")
                if result["duplicates"]:
                    self.log(
                        f"Release DnD: {len(result['duplicates'])} Dubletten übersprungen."
                    )
                self.toast(f"{len(result['added'])} TRACKS HINZUGEFÜGT")
        except Exception as e:
            self.log(f"Release DnD Parse Fehler: {e}")

    def refresh_view(self, force=False):
        signature = self._build_view_signature()
        if not force and signature == self._last_view_signature:
            return
        release_view = self._get_release_view()
        if release_view and hasattr(release_view, "render_release_state"):
            counts = release_view_tools.build_release_source_counts(self.state.release_tracks)
            track_labels = [
                release_view_tools.build_release_track_row_label(i + 1, track)
                for i, track in enumerate(self.state.release_tracks)
            ]
            _track_signature, cover_path, export_dir, _has_listbox = signature
            release_view.render_release_state(
                track_labels=track_labels,
                action_hint=release_view_tools.build_release_action_hint(counts),
                status_text=release_view_tools.build_release_status_text(
                    len(self.state.release_tracks),
                    bool(cover_path),
                    bool(export_dir),
                    self._has_release_track_list(),
                ),
            )
        else:
            self._render_legacy_release_view(signature)
        self._last_view_signature = signature

    def choose_cover(self): 
        p = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png")])
        if p:
            self.app.release_vars["cover_path"].set(p)
            self.refresh_view(force=True)

    def choose_export_dir(self): 
        p = filedialog.askdirectory()
        if p:
            self.app.release_vars["export_dir"].set(p)
            self.refresh_view(force=True)

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
        selection = self._get_selected_track_indices()
        if not selection:
            return
            
        index = selection[0]
        if index > 0:
            self.state.release_tracks[index], self.state.release_tracks[index-1] = self.state.release_tracks[index-1], self.state.release_tracks[index]
            self.refresh_view()
            self._select_track_index(index-1)

    def move_track_down(self):
        selection = self._get_selected_track_indices()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.state.release_tracks) - 1:
            self.state.release_tracks[index], self.state.release_tracks[index+1] = self.state.release_tracks[index+1], self.state.release_tracks[index]
            self.refresh_view()
            self._select_track_index(index+1)

    def remove_track(self): 
        selection = sorted(self._get_selected_track_indices(), reverse=True)
        if selection:
            for idx in selection:
                if 0 <= idx < len(self.state.release_tracks):
                    self.state.release_tracks.pop(idx)
            self.refresh_view()
            self.toast(f"{len(selection)} TRACKS ENTFERNT")
