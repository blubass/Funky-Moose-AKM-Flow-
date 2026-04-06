
import tkinter as tk
from .base_controller import BaseController
from app_logic import akm_core, overview_tools
from app_ui import ui_patterns

class OverviewController(BaseController):
    """Manages catalogue overview, filtering, and cross-tab triggers."""
    
    def refresh_list(self):
        """Orchestrates filtering, sorting, and UI population of the catalogue overview."""
        recs = self.state.get_all_records()
        if not recs: return
        
        search = (self.app.search_var.get() or "").lower() if self.app.search_var else ""
        filt = self.app.status_filter_var.get() if self.app.status_filter_var else "all"
        key = self.app.sort_key_var.get() if self.app.sort_key_var else "title"
        desc = self.app.sort_desc_var.get() if self.app.sort_desc_var else False
        
        self.state.filtered_records = overview_tools.filter_and_sort_entries(recs, search, filt, key, desc)
        
        if hasattr(self.app, 'listbox'):
            self.app.listbox.delete(0, tk.END)
            s_map = akm_core.get_status_map(akm_core.get_lang())
            for it in self.state.filtered_records:
                self.app.listbox.insert(tk.END, overview_tools.format_overview_list_label(it, s_map.get(it['status'], it['status'])))
                self.app.listbox.itemconfig(tk.END, bg=ui_patterns.get_row_color(it.get("status", "in_progress"), 0.16), fg=ui_patterns.FIELD_FG)
        
        if hasattr(self.app, 'overview_summary_label') and self.app.overview_summary_label:
            self.app.overview_summary_label.config(text=f"{len(self.state.filtered_records)} Werke gefunden")
        
        self._refresh_overview_filter_chips(recs)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        st = overview_tools.build_dashboard_stats(self.state.get_all_records())
        for k, l in self.app.dashboard_labels.items(): 
            l.config(text=str(st.get(k, 0)))
        
        counts = overview_tools.build_dashboard_chip_counts(st)
        for st_key, widget in self.app.dashboard_status_chips.items(): 
            ui_patterns.style_chip_label(widget, st_key, f"{self.app.status_text(st_key)}  {counts.get(st_key, 0)}")

    def _refresh_overview_filter_chips(self, records):
        current = (self.app.status_filter_var.get() or "all") if self.app.status_filter_var else "all"
        counts = overview_tools.build_overview_filter_counts(records)
        for st_key, widget in self.app.overview_filter_chips.items(): 
            ui_patterns.style_chip_label(widget, st_key, f"{self.app.status_text(st_key)}  {counts.get(st_key, 0)}", st_key == current)

    def _on_g_done(self, result, message):
        """Unified success/error callback for generic CRUD tasks."""
        if result[0]: 
            self.log(message)
            self.toast(message)
            self.state.invalidate_cache()
            self.refresh_list()
        else: 
            self.log(f"FEHLER: {result[1]}")

    def load_selected_into_details(self):
        it = self._get_selected_overview_item()
        if it:
            self.app.detail_original_title = it.get("title")
            for k, v in self.app.detail_vars.items(): 
                v.set(str(it.get(k, "")))
            if hasattr(self.app, 'detail_notes'): 
                self.app.detail_notes.delete("1.0", tk.END)
                self.app.detail_notes.insert("1.0", it.get("notes", ""))
            
            self.app.details_ctrl._set_detail_status_chip(it.get("status", "in_progress"))
            self.app.select_tab_by_id("details")

    def set_status(self, s):
        it = self._get_selected_overview_item()
        if it:
            self.tasks.run(lambda: akm_core.update_entry(it['title'], {"status": s}), 
                           lambda r: self._on_g_done(r, f"Status {s} gesetzt"), 
                           busy_text="Setze Status...")

    def on_listbox_activate(self, e): 
        it = self._get_selected_overview_item()
        if it:
            self.app.open_audio_player_for_selected()

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
        try: return self.state.filtered_records[self.app.listbox.curselection()[0]]
        except: return None
