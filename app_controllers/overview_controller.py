
import tkinter as tk
from .base_controller import BaseController
from app_logic import akm_core, overview_tools, loudness_tools
from app_ui import ui_patterns

class OverviewController(BaseController):
    """Manages catalogue overview, filtering, and cross-tab triggers."""

    def _get_overview_view(self):
        if hasattr(self.app, "get_built_tab"):
            return self.app.get_built_tab("overview")
        return getattr(getattr(self.app, "tab_system", None), "_instances", {}).get("overview")

    def _render_legacy_overview_records(self, labels, row_statuses):
        if not hasattr(self.app, "listbox"):
            return
        self.app.listbox.delete(0, tk.END)
        if labels:
            self.app.listbox.insert(tk.END, *labels)
        for idx, row_status in enumerate(row_statuses):
            if row_status in ui_patterns.STATUS_PALETTES:
                bg_col = ui_patterns.get_row_color(row_status, 0.16)
                self.app.listbox.itemconfig(idx, bg=bg_col, fg=ui_patterns.FIELD_FG)

    def _render_legacy_overview_meta(self, summary_text, status_text, hint_text, empty_text, show_empty):
        if hasattr(self.app, "overview_summary_label") and self.app.overview_summary_label:
            self.app.overview_summary_label.config(text=summary_text)
        if hasattr(self.app, "overview_status_label") and self.app.overview_status_label:
            self.app.overview_status_label.config(text=status_text)
        if hasattr(self.app, "overview_hint_label") and self.app.overview_hint_label:
            self.app.overview_hint_label.config(text=hint_text)
        if hasattr(self.app, "overview_empty_label") and self.app.overview_empty_label:
            self.app.overview_empty_label.config(text=empty_text)
            if show_empty:
                pack_kwargs = {"fill": "x", "padx": 12, "pady": 12}
                if hasattr(self.app, "overview_bottom_actions"):
                    pack_kwargs["before"] = self.app.overview_bottom_actions
                self.app.overview_empty_label.pack(**pack_kwargs)
            else:
                self.app.overview_empty_label.pack_forget()

    def _get_selected_overview_indices(self):
        overview_view = self._get_overview_view()
        if overview_view and hasattr(overview_view, "get_selected_indices"):
            return tuple(overview_view.get_selected_indices())
        if hasattr(self.app, "listbox"):
            return tuple(self.app.listbox.curselection())
        return ()
    
    def refresh_list(self):
        """Orchestrates filtering, sorting, and UI population of the catalogue overview (Listbox optimized)."""
        recs = self.state.get_all_records(copy_data=False) or []
        
        search = (self.app.search_var.get() or "").lower() if self.app.search_var else ""
        filt = (self.app.status_filter_var.get() or "all") if self.app.status_filter_var else "all"
        key = (self.app.sort_key_var.get() or "title") if self.app.sort_key_var else "title"
        desc = (self.app.sort_desc_var.get() or False) if self.app.sort_desc_var else False
        mtime = self.state._get_data_mtime()
        
        # Performance Guard: Skip if nothing has changed since last visit
        curr_params = f"{search}|{filt}|{key}|{desc}|{mtime}"
        if hasattr(self, "_last_refresh_params") and self._last_refresh_params == curr_params:
            return
        self._last_refresh_params = curr_params

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
        overview_view = self._get_overview_view()
        if overview_view and hasattr(overview_view, "render_overview_records"):
            overview_view.render_overview_records(labels, row_statuses)
        else:
            self._render_legacy_overview_records(labels, row_statuses)
        if overview_view and hasattr(overview_view, "render_overview_meta"):
            overview_view.render_overview_meta(
                summary_text=summary_text,
                status_text=status_text,
                hint_text=hint_text,
                empty_text=hint_text,
                show_empty=not bool(self.state.filtered_records),
            )
        else:
            self._render_legacy_overview_meta(
                summary_text,
                status_text,
                hint_text,
                hint_text,
                not bool(self.state.filtered_records),
            )
        
        self._refresh_overview_filter_chips(recs)

    def refresh_dashboard(self):
        st = overview_tools.build_dashboard_stats(self.state.get_all_records(copy_data=False))
        if not hasattr(self.app, 'dashboard_labels'): return
        
        for k, l in self.app.dashboard_labels.items(): 
            l.config(text=str(st.get(k, 0)))

        if hasattr(self.app, "dashboard_status_label") and self.app.dashboard_status_label:
            self.app.dashboard_status_label.config(text=overview_tools.build_dashboard_status_text(st))
        if hasattr(self.app, "dashboard_hint_label") and self.app.dashboard_hint_label:
            self.app.dashboard_hint_label.config(text=overview_tools.build_dashboard_focus_text(st))
        if hasattr(self.app, "dashboard_meta_label") and self.app.dashboard_meta_label:
            self.app.dashboard_meta_label.config(text=overview_tools.build_dashboard_meta_text(st))
        
        counts = overview_tools.build_dashboard_chip_counts(st)
        for st_key, widget in self.app.dashboard_status_chips.items(): 
            ui_patterns.style_chip_label(widget, st_key, f"{self.app.status_text(st_key)}  {counts.get(st_key, 0)}")

    def _refresh_overview_filter_chips(self, records):
        current = (self.app.status_filter_var.get() or "all") if self.app.status_filter_var else "all"
        counts = overview_tools.build_overview_filter_counts(records)
        overview_view = self._get_overview_view()
        if overview_view and hasattr(overview_view, "update_filter_chip"):
            for st_key in ["all", "open", "in_progress", "ready", "submitted", "confirmed"]:
                overview_view.update_filter_chip(
                    st_key,
                    f"{self.app.status_text(st_key)}  {counts.get(st_key, 0)}",
                    st_key == current,
                )
            return
        for st_key, widget in self.app.overview_filter_chips.items():
            ui_patterns.style_chip_label(widget, st_key, f"{self.app.status_text(st_key)}  {counts.get(st_key, 0)}", st_key == current)

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
            _ = self.app.details_tab
            details_view = self.app.get_built_tab("details") if hasattr(self.app, "get_built_tab") else None
            self.app.detail_original_title = it.get("title")
            detail_vars = self.app.get_detail_form_vars() if hasattr(self.app, "get_detail_form_vars") else getattr(self.app, "detail_vars", {})
            for k, v in detail_vars.items():
                v.set(str(it.get(k, "")))
            if details_view and hasattr(details_view, "set_notes_text"):
                details_view.set_notes_text(it.get("notes", ""))
            elif hasattr(self.app, 'detail_notes'): 
                self.app.detail_notes.delete("1.0", tk.END)
                self.app.detail_notes.insert("1.0", it.get("notes", ""))
            # Load Tags
            raw_tags = it.get("tags", [])
            tags_text = ", ".join(raw_tags) if isinstance(raw_tags, list) else str(raw_tags)
            if details_view and hasattr(details_view, "set_tags_text"):
                details_view.set_tags_text(tags_text)
            elif hasattr(self.app, 'detail_tags'):
                self.app.detail_tags.delete("1.0", tk.END)
                self.app.detail_tags.insert("1.0", tags_text)
            # Load Instrumental flag
            if details_view and hasattr(details_view, "set_instrumental"):
                details_view.set_instrumental(bool(it.get("instrumental", False)))
            elif hasattr(self.app, 'detail_instrumental_var'):
                self.app.detail_instrumental_var.set(bool(it.get("instrumental", False)))
            
            self.app.details_ctrl.set_status_chip(it.get("status", "in_progress"))
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
        self.app.status_filter_var.set(s)
        self.refresh_list()

    def open_with_filter(self, s): 
        self.app.status_filter_var.set(s)
        self.app.select_tab_by_id("overview")
        self.refresh_list()

    def _get_selected_overview_item(self):
        try:
            sel = self._get_selected_overview_indices()
            if not sel: return None
            return self.state.filtered_records[sel[0]]
        except (AttributeError, IndexError, TypeError, tk.TclError):
            return None

    def get_selected_item(self):
        """Public accessor for the currently selected overview item."""
        return self._get_selected_overview_item()

    def _get_selected_overview_items(self):
        try:
            return [self.state.filtered_records[idx] for idx in self._get_selected_overview_indices()]
        except (AttributeError, IndexError, TypeError, tk.TclError):
            return []
