from .base_controller import BaseController
from app_controllers import detail_controller_tools
from app_logic import akm_core, overview_tools, loudness_tools

class OverviewController(BaseController):
    """Manages catalogue overview, filtering, and cross-tab triggers."""

    def _get_dashboard_view(self):
        return self.get_built_tab("dashboard")

    def _get_overview_view(self):
        return self.get_built_tab("overview")

    def _get_details_view(self):
        details_view = self.get_built_tab("details")
        if details_view is not None:
            return details_view
        try:
            return getattr(self.app, "details_tab")
        except AttributeError:
            return None

    def _get_overview_filter_state(self):
        overview_view = self._get_overview_view()
        if overview_view and hasattr(overview_view, "get_filter_state"):
            return overview_view.get_filter_state()
        if hasattr(self.app, "get_overview_filter_state"):
            return self.app.get_overview_filter_state()
        return {"search": "", "filter": "all", "sort": "title", "desc": False}

    def _set_overview_status_filter(self, status_key):
        overview_view = self._get_overview_view()
        if overview_view and hasattr(overview_view, "set_status_filter"):
            overview_view.set_status_filter(status_key)

    def _get_selected_overview_indices(self):
        overview_view = self._get_overview_view()
        if overview_view and hasattr(overview_view, "get_selected_indices"):
            return tuple(overview_view.get_selected_indices())
        return ()
    
    def refresh_list(self):
        """Orchestrates filtering, sorting, and UI population of the catalogue overview (Listbox optimized)."""
        recs = self.state.get_all_records(copy_data=False) or []

        filter_state = self._get_overview_filter_state()
        search = (filter_state.get("search") or "").lower()
        filt = filter_state.get("filter") or "all"
        key = filter_state.get("sort") or "title"
        desc = bool(filter_state.get("desc"))
        mtime = self.state._get_data_mtime()
        
        overview_view = self._get_overview_view()

        # Performance Guard: Skip if nothing has changed since last rendered visit
        curr_params = f"{search}|{filt}|{key}|{desc}|{mtime}"
        if (
            overview_view
            and hasattr(overview_view, "render_overview_records")
            and hasattr(overview_view, "render_overview_meta")
            and hasattr(self, "_last_refresh_params")
            and self._last_refresh_params == curr_params
        ):
            return

        self.state.filtered_records = overview_tools.filter_and_sort_entries(recs, search, filt, key, desc)

        s_map = akm_core.get_status_map(akm_core.get_lang())
        labels = [
            overview_tools.format_overview_list_label(
                it,
                s_map.get(it.get("status", "in_progress"), it.get("status", "in_progress")),
            )
            for it in self.state.filtered_records
        ]
        row_statuses = [it.get("status", "in_progress") for it in self.state.filtered_records]

        status_label = self.app.status_text(filt) if filt not in {"all", "open"} else None
        summary_text = overview_tools.build_overview_summary(
            len(self.state.filtered_records),
            status_filter=filt,
            query=search,
            sort_key=key,
            sort_desc=desc,
            status_label=status_label,
            open_label=self.app.status_text("open"),
        )
        status_text = overview_tools.build_overview_status_text(
            len(self.state.filtered_records),
            len(recs),
        )
        hint_text = overview_tools.build_overview_hint_text(
            len(self.state.filtered_records),
            len(recs),
            status_filter=filt,
            query=search,
        )
        if overview_view and hasattr(overview_view, "render_overview_records") and hasattr(overview_view, "render_overview_meta"):
            self._last_refresh_params = curr_params
            overview_view.render_overview_records(labels, row_statuses)
            overview_view.render_overview_meta(
                summary_text=summary_text,
                status_text=status_text,
                hint_text=hint_text,
                empty_text=hint_text,
                show_empty=not bool(self.state.filtered_records),
            )
        
        self._refresh_overview_filter_chips(recs)

    def refresh_dashboard(self):
        st = overview_tools.build_dashboard_stats(self.state.get_all_records(copy_data=False))
        dashboard_view = self._get_dashboard_view()
        counts = overview_tools.build_dashboard_chip_counts(st)
        status_text = overview_tools.build_dashboard_status_text(st)
        hint_text = overview_tools.build_dashboard_focus_text(st)
        meta_text = overview_tools.build_dashboard_meta_text(st)
        if dashboard_view and hasattr(dashboard_view, "render_dashboard_state"):
            dashboard_view.render_dashboard_state(
                st,
                status_text,
                hint_text,
                meta_text,
                counts,
                self.app.status_text,
            )
            return

    def _refresh_overview_filter_chips(self, records):
        current = self._get_overview_filter_state().get("filter") or "all"
        counts = overview_tools.build_overview_filter_counts(records)
        overview_view = self._get_overview_view()
        if overview_view and hasattr(overview_view, "update_filter_chip"):
            for st_key in ["all", "open", "in_progress", "ready", "submitted", "confirmed"]:
                overview_view.update_filter_chip(
                    st_key,
                    f"{self.app.status_text(st_key)}  {counts.get(st_key, 0)}",
                    st_key == current,
                )

    def _on_g_done(self, result, message):
        """Unified success/error callback for generic CRUD tasks."""
        if result[0]: 
            self.log(message)
            self.toast(message)
            self.state.invalidate_cache()
            self._last_refresh_params = None # Force refresh
            self.refresh_list()
        else: 
            self.log(f"FEHLER: {result[1]}")

    def load_selected_into_details(self):
        it = self._get_selected_overview_item()
        if it:
            details_view = self._get_details_view()
            detail_vars = self.app.get_detail_form_vars() if hasattr(self.app, "get_detail_form_vars") else getattr(self.app, "detail_vars", {})
            detail_controller_tools.populate_detail_view(detail_vars, it)
            detail_state = detail_controller_tools.build_detail_text_state(it)
            self.app.detail_original_title = detail_state["title"]
            if details_view and hasattr(details_view, "set_notes_text"):
                details_view.set_notes_text(detail_state["notes_text"])
            if details_view and hasattr(details_view, "set_tags_text"):
                details_view.set_tags_text(detail_state["tags_text"])
            if details_view and hasattr(details_view, "set_instrumental"):
                details_view.set_instrumental(detail_state["instrumental"])

            self.app.details_ctrl.set_status_chip(detail_state["status"])
            self.app.select_tab_by_id("details")

            # NEW: Extraction if duration is missing but audio path exists
            audio_p = it.get("audio_path")
            if audio_p and not it.get("duration"):
                def _ext():
                    try:
                        return loudness_tools.probe_duration(audio_p)
                    except Exception:
                        return 0
                def _upd(dur):
                    if dur:
                        mins, secs = int(dur // 60), int(dur % 60)
                        detail_vars["duration"].set(f"{mins}:{secs:02d}")
                        self.log(f"Dauer automatisch nacherfasst: {mins}:{secs:02d}")
                self.tasks.run(_ext, _upd, busy_text="Aktualisiere Dauer...")

    def set_status(self, s):
        items = self._get_selected_overview_items()
        if not items: return
        
        def _work():
            for it in items:
                akm_core.update_entry(it['title'], {"status": s})
            return len(items)
            
        self.tasks.run(_work, 
                       lambda count: self._on_g_done((True, None), f"Status {s} für {count} Werke gesetzt"), 
                       busy_text="Setze Status...")
        
    def on_listbox_activate(self, e): 
        it = self._get_selected_overview_item()
        if it:
            self.load_selected_into_details()

    def jump_to_last_open(self): 
        l = akm_core.get_last_open()
        if l:
            self.app.batch_ctrl.open_track_in_batch(l)

    def set_status_filter(self, s): 
        self._set_overview_status_filter(s)
        self.refresh_list()

    def open_with_filter(self, s): 
        _ = getattr(self.app, "overview_tab", None)
        self._set_overview_status_filter(s)
        self.app.select_tab_by_id("overview")
        self.refresh_list()

    def _get_selected_overview_item(self):
        try:
            sel = self._get_selected_overview_indices()
            if not sel: return None
            return self.state.filtered_records[sel[0]]
        except (AttributeError, IndexError, TypeError):
            return None

    def get_selected_item(self):
        """Public accessor for the currently selected overview item."""
        return self._get_selected_overview_item()

    def _get_selected_overview_items(self):
        try:
            return [self.state.filtered_records[idx] for idx in self._get_selected_overview_indices()]
        except (AttributeError, IndexError, TypeError):
            return []
