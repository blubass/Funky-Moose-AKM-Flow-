"""
Funky Moose Release Forge - Main Application Orchestrator
Modular, State-Driven, and Industrial-Themed Backend Manager for Music Release Workflows.
"""

import copy
import os
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox, ttk

# Optional: DnD Support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None

# Core Logic & Infrastructure
from app_logic import (
    akm_core, assistant_tools, cover_tools, detail_tools, 
    flow_tools, overview_tools, release_tools, app_state, task_runner
)
from app_ui import ui_patterns, path_ui_tools, release_view_tools
from app_workflows import loudness_workflows, release_workflows

# UI Components (Tabs)
from app_ui.tabs.dashboard_tab import DashboardTab
from app_ui.tabs.assistant_tab import AssistantTab
from app_ui.tabs.batch_tab import BatchTab
from app_ui.tabs.overview_tab import OverviewTab
from app_ui.tabs.details_tab import DetailsTab
from app_ui.tabs.cover_tab import CoverTab
from app_ui.tabs.release_tab import ReleaseTab
from app_ui.tabs.loudness_tab import LoudnessTab

# Design Tokens & Themed Widgets
from app_ui.ui_patterns import (
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    FONT_SM, FONT_MD, FONT_BOLD, FONT_MD_BOLD, FONT_LG, FONT_XXXL,
    PulseLabel, AkmPanel, AkmLabel, AkmSubLabel
)

class AKMApp(TkinterDnD.Tk if TkinterDnD is not None else tk.Tk):
    """
    Central orchestrator for the Funky Moose Release Forge.
    Manages state via AppState, background tasks via TaskRunner, and coordinates the modular tab-based UI.
    """
    def __init__(self):
        super().__init__()
        self._set_window_config()
        self._init_state_and_services()
        self._init_ui_vars()
        
        # Setup & Boot
        ui_patterns.apply_ttk_styles()
        self.build_ui()
        
        # Final Bindings & Initial Data Load
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        dnd_status = "Aktiv" if TkinterDnD is not None else "Deaktiviert (Paket fehlt)"
        self.append_log(f"Drag & Drop System: {dnd_status}")
        
        self.refresh_list()
        self.reload_flow_data(preferred_index=0)

    # --- INITIALIZATION ---
    def _set_window_config(self):
        """Standard window initialization and styling."""
        self.title("Funky Moose Release Forge")
        self.geometry("1000x820")
        self.minsize(860, 620)
        self.configure(bg=ui_patterns.BG)

    def _init_state_and_services(self):
        """Instantiate core singleton services."""
        self.state = app_state.AppState()
        self.tasks = task_runner.TaskRunner(self)

    def _init_ui_vars(self):
        """Prepare tracker variables and registries used across multiple tabs."""
        # Overview Registry
        self.overview_filter_chips = {}
        self.dashboard_labels = {}
        self.dashboard_status_chips = {}
        
        # Detail & Metadata Registry
        self.detail_vars = {}
        self.release_vars = {}
        self.detail_original_title = None
        self.current_detail_status = "in_progress"
        
        # Batch & Flow
        self.copy_stage = flow_tools.DEFAULT_COPY_STAGE
        self.copy_button = None
        
        # Search & Filtering
        self.search_var = None
        self.status_filter_var = None
        self.sort_key_var = None
        self.sort_desc_var = None

    # --- UI BUILDING ---
    def build_ui(self):
        """Assembles the main application layout including header and tabs."""
        self.content_root = tk.Frame(self, bg=ui_patterns.BG)
        self.content_root.pack(fill="both", expand=True)
        
        self._build_header(self.content_root)
        self._build_tab_system(self.content_root)

    def _build_header(self, parent):
        """Builds the top branding header with title and activity indicator."""
        header_frame = tk.Frame(parent, bg=ui_patterns.BG)
        header_frame.pack(fill="x", padx=SPACE_LG, pady=(SPACE_LG, SPACE_LG))
        
        tk.Label(header_frame, text="Funky Moose Release Forge", 
                 fg=ui_patterns.ACCENT, bg=ui_patterns.BG, font=FONT_XXXL).pack(side="left")
        
        # Theme Toggle (Manual Control)
        theme_btn = tk.Button(header_frame, text="🌓", bg=ui_patterns.BG, fg=ui_patterns.TEXT, borderwidth=0, 
                             highlightthickness=0, activebackground=ui_patterns.PANEL_2, cursor="hand2",
                             command=self.toggle_theme)
        theme_btn.pack(side="right", padx=SPACE_LG, pady=SPACE_XS)
        
        # Modern Pulsing Activity Monitor
        self.task_indicator = PulseLabel(header_frame, text="TASK ACTIVE", fg=ui_patterns.ACCENT, 
                                         font=FONT_BOLD, padx=10, pady=4)
        self.task_indicator.pack(side="right", pady=SPACE_XS)
        self.task_indicator.stop()

    def _build_tab_system(self, parent):
        """Initializes and adds all functional modules to the central Notebook."""
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True)

        # Tab Register (for easier access)
        self.tab_map = {
            "dashboard": tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "assistant": tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "batch":     tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "overview":  tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "details":   tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "cover":     tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "release":   tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "loudness":  tk.Frame(self.tabs, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG)
        }

        # Add to Notebook
        for tid, frame in self.tab_map.items():
            self.tabs.add(frame, text=tid.capitalize())

        # Instantiate Tab Content
        DashboardTab(self.tab_map["dashboard"], self)
        AssistantTab(self.tab_map["assistant"], self)
        BatchTab(self.tab_map["batch"], self)
        OverviewTab(self.tab_map["overview"], self)
        DetailsTab(self.tab_map["details"], self)
        CoverTab(self.tab_map["cover"], self)
        ReleaseTab(self.tab_map["release"], self)
        LoudnessTab(self.tab_map["loudness"], self)

    # --- TAB NAVIGATION & CONTROL ---
    def select_tab_by_id(self, tab_id):
        """Switches to the specified tab and triggers its refresh logic if necessary."""
        if tab_id in self.tab_map:
            self.tabs.select(self.tab_map[tab_id])

    def open_loudness_tab(self):
        """Convenience method to access the primary optimization workflow."""
        self.select_tab_by_id("loudness")

    def on_tab_changed(self, event):
        """Central event handler for tab transitions (e.g., to trigger data refreshes)."""
        selected = self.tabs.select()
        if selected == str(self.tab_map["dashboard"]): self.refresh_dashboard()
        elif selected == str(self.tab_map["overview"]): self.refresh_list()

    # --- DATA OPERATIONS & CORE WORKFLOWS ---
    def refresh_list(self):
        """Orchestrates filtering, sorting, and UI population of the catalogue overview."""
        recs = self.state.get_all_records()
        if not recs: return
        
        search = (self.search_var.get() or "").lower() if self.search_var else ""
        filt = self.status_filter_var.get() if self.status_filter_var else "all"
        key = self.sort_key_var.get() if self.sort_key_var else "title"
        desc = self.sort_desc_var.get() if self.sort_desc_var else False
        
        self.state.filtered_records = overview_tools.filter_and_sort_entries(recs, search, filt, key, desc)
        
        if hasattr(self, 'listbox'):
            self.listbox.delete(0, tk.END)
            s_map = akm_core.get_status_map(akm_core.get_lang())
            for it in self.state.filtered_records:
                self.listbox.insert(tk.END, overview_tools.format_overview_list_label(it, s_map.get(it['status'], it['status'])))
                self.listbox.itemconfig(tk.END, bg=ui_patterns.get_row_color(it.get("status", "in_progress"), 0.16), fg=ui_patterns.FIELD_FG)
        
        if hasattr(self, 'overview_summary_label') and self.overview_summary_label:
            self.overview_summary_label.config(text=f"{len(self.state.filtered_records)} Werke gefunden")
        
        self._refresh_overview_filter_chips(recs)
        self.refresh_dashboard()

    def _on_g_done(self, result, message):
        """Unified success/error callback for generic CRUD tasks."""
        if result[0]: 
            self.append_log(message)
            AkmToast(self, message)
            self.state.invalidate_cache()
            self.refresh_list()
        else: 
            self.append_log(f"FEHLER: {result[1]}")

    # --- BATCH & FLOW LOGIC ---
    def reload_flow_data(self, preferred_index=None):
        """Re-synchronizes the Batch/Batch Queue with current state."""
        self.state.batch_queue = flow_tools.filter_batch_entries(self.state.get_all_records(True))
        if preferred_index is not None: self.state.batch_index = preferred_index
        self.update_flow()

    def update_flow(self):
        """Updates the visual state of the Batch Tab."""
        if self.state.batch_queue:
            item = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
            if hasattr(self, 'flow_title'): self.flow_title.config(text=item['title'])
            if hasattr(self, 'flow_meta'): self.flow_meta.config(text=flow_tools.build_flow_meta_text(item))
            if hasattr(self, 'progress'): 
                self.progress["value"] = ((self.state.batch_index + 1) / len(self.state.batch_queue)) * 100

    # --- UTILITIES ---
    def btn(self, p, t, c, primary=False, quiet=False): 
        """Wrapper for the centralized design-system button creator."""
        return ui_patterns.create_btn(p, t, c, primary=primary, quiet=quiet)

    def append_log(self, message): 
        """Safely appends activity to the global log (if present)."""
        if hasattr(self, 'log'): 
            self.log.insert(tk.END, str(message) + "\n")
            self.log.see(tk.END)

    def update_task_indicator(self, busy):
        """Starts or stops the activity pulse on the Task Indicator label."""
        if hasattr(self, 'task_indicator'):
            if busy: self.task_indicator.start()
            else: self.task_indicator.stop()

    def status_text(self, status): 
        """Translated status text helper."""
        return ui_patterns.get_status_chip_text(status, akm_core.get_lang())

    # --- WRAPPERS FOR EXTERNAL TOOLS (Called by Tabs) ---
    def import_excel(self):
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
        if p: self.tasks.run(lambda: akm_core.import_excel(p), self._on_import_done, "Importiere...")

    def _on_import_done(self, r): 
        msg = f"Importiert: {r[0]} neu, {r[1]} alt"
        self.append_log(msg); AkmToast(self, msg); self.state.invalidate_cache(); self.refresh_list()

    def load_selected_into_details(self):
        it = self._get_selected_overview_item()
        if it:
            self.detail_original_title = it.get("title")
            for k, v in self.detail_vars.items(): v.set(str(it.get(k, "")))
            if hasattr(self, 'detail_notes'): self.detail_notes.delete("1.0", tk.END); self.detail_notes.insert("1.0", it.get("notes", ""))
            self._set_detail_status_chip(it.get("status", "in_progress")); self.select_tab_by_id("details")

    def save_details(self):
        orig = self.detail_original_title
        if orig:
            upd = {k: v.get().strip() for k, v in self.detail_vars.items()}
            upd["notes"] = self.detail_notes.get("1.0", tk.END).strip(); upd["status"] = self.current_detail_status
            self.tasks.run(lambda: akm_core.update_entry(orig, upd), lambda r: self._on_g_done(r, "Gespeichert"), "Speichere...")

    def refresh_dashboard(self):
        st = overview_tools.build_dashboard_stats(self.state.get_all_records())
        for k, l in self.dashboard_labels.items(): l.config(text=str(st.get(k, 0)))
        counts = overview_tools.build_dashboard_chip_counts(st)
        for st_key, widget in self.dashboard_status_chips.items(): 
            ui_patterns.style_chip_label(widget, st_key, f"{self.status_text(st_key)}  {counts.get(st_key, 0)}")

    def _refresh_overview_filter_chips(self, records):
        current = (self.status_filter_var.get() or "all") if self.status_filter_var else "all"
        counts = overview_tools.build_overview_filter_counts(records)
        for st_key, widget in self.overview_filter_chips.items(): 
            ui_patterns.style_chip_label(widget, st_key, f"{self.status_text(st_key)}  {counts.get(st_key, 0)}", st_key == current)

    def flow_copy(self):
        it = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
        res = flow_tools.resolve_copy_action(it, self.copy_stage)
        self.clipboard_clear(); self.clipboard_append(res["value"]); self.copy_stage = res["next_stage"]
        if self.copy_button: self.copy_button.config(text=f"{res['copied_label']} kopiert")

    def flow_submit(self):
        it = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
        self.tasks.run(lambda: akm_core.update_entry(it['title'], {"status": "submitted"}), lambda r: self.reload_flow_data(), "Melde...")

    def flow_next(self): self.state.batch_index += 1; self.update_flow()

    def refresh_release_view(self):
        if hasattr(self, 'release_track_listbox'):
            self.release_track_listbox.delete(0, tk.END)
            for i, t in enumerate(self.state.release_tracks): self.release_track_listbox.insert(tk.END, f"{i+1}. {t['title']}")
            if self.release_status_label: self.release_status_label.config(text=f"{len(self.state.release_tracks)} Tracks")

    def loudness_choose_files(self):
        p = filedialog.askopenfilenames(filetypes=path_ui_tools.AUDIO_FILETYPES)
        if p: self.state.loudness_files = list(p); self._pop_l_tree()

    def loudness_analyze_files(self):
        t = float(self.loudness_target_var.get() or -14); pk = float(self.loudness_peak_var.get() or -1)
        def _work(): return [loudness_workflows.enrich_analysis_item(loudness_tools.analyze_full_track(p), t, pk, loudness_tools) for p in self.state.loudness_files]
        self.tasks.run(_work, self._on_l_done, "Analysiere...")

    def _on_l_done(self, r): self.state.loudness_results = r; self._pop_l_tree()

    def _pop_l_tree(self):
        if not hasattr(self, 'loudness_tree'): return
        self.loudness_tree.delete(*self.loudness_tree.get_children())
        for it in self.state.loudness_results: self.loudness_tree.insert("", tk.END, values=loudness_workflows.build_tree_row(it)["values"], tags=loudness_workflows.build_tree_row(it)["tags"])

    def _get_selected_overview_item(self):
        try: return self.state.filtered_records[self.listbox.curselection()[0]]
        except: return None
    
    def _schedule_refresh_list(self): self.after(150, self.refresh_list)
    
    def _set_detail_status_chip(self, s):
        self.current_detail_status = s or "in_progress"
        if hasattr(self, 'detail_status_var') and self.detail_status_var: self.detail_status_var.set(self.status_text(s))
        if hasattr(self, 'detail_status_chip') and self.detail_status_chip: ui_patterns.style_chip_label(self.detail_status_chip, s, self.status_text(s))

    # --- WRAPPERS FOR TAB ACTIONS ---
    def toggle_theme(self):
        """Manually switches between light and dark industrial themes."""
        new_is_dark = not ui_patterns.IS_DARK
        ui_patterns.update_global_constants(new_is_dark)
        
        # 1. Update the overall root UI colors
        self.configure(bg=ui_patterns.BG)
        self.content_root.configure(bg=ui_patterns.BG)
        
        # 2. Update all widgets recursively
        ui_patterns.refresh_ui_hierarchy(self)
        
        # 3. Force rebuild of global styles
        ui_patterns.apply_ttk_styles()

    def add(self):
        (t := self.entry.get().strip()) and self.tasks.run(lambda: akm_core.add_entry(t), lambda r: self._on_g_done(r, f"'{t}' angelegt"), f"Lege '{t}' an...")
    def set_status(self, s):
        (it := self._get_selected_overview_item()) and self.tasks.run(lambda: akm_core.update_entry(it['title'], {"status": s}), lambda r: self._on_g_done(r, f"Status {s} gesetzt"), "Setze Status...")
    def clear_details_form(self):
        self.detail_original_title = None
        for v in self.detail_vars.values(): v.set("")
        self._set_detail_status_chip("in_progress")

    def open_track_in_batch(self, it):
        self.reload_flow_data()
        for i, f in enumerate(self.state.batch_queue):
            if f['title'] == it['title']: self.state.batch_index = i; self.select_tab_by_id("batch"); self.update_flow(); return
    def on_listbox_activate(self, e): (it := self._get_selected_overview_item()) and self.open_track_in_batch(it)
    def jump_to_last_open(self): (l := akm_core.get_last_open()) and self.open_track_in_batch(l)
    def _set_overview_status_filter(self, s): self.status_filter_var.set(s); self.refresh_list()
    def _open_overview_with_filter(self, s): self.status_filter_var.set(s); self.select_tab_by_id("overview"); self.refresh_list()
    def choose_audio_path_for_details(self): (p := filedialog.askopenfilename(filetypes=path_ui_tools.AUDIO_FILETYPES)) and self.detail_vars["audio_path"].set(p)
    def open_audio_path_in_finder(self): (p := self.detail_vars["audio_path"].get()) and os.path.exists(p) and ui_patterns.open_in_finder(p)
    def choose_release_cover(self): (p := filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png")])) and self.release_vars["cover_path"].set(p)
    def choose_release_export_dir(self): (p := filedialog.askdirectory()) and self.release_vars["export_dir"].set(p)
    def open_release_cover_in_finder(self): (p := self.release_vars["cover_path"].get()) and os.path.exists(p) and ui_patterns.open_in_finder(p)
    def open_release_cover_dialog(self): messagebox.showinfo("Cover", "Vorschau...")
    def build_distro_export(self):
        m = {k: v.get().strip() for k, v in self.release_vars.items()}
        if m.get("title") and self.state.release_tracks: self.tasks.run(lambda: release_workflows.start_distro_export(m, self.state.release_tracks), lambda r: self.append_log(r[1]), "Exportiere...")

    def release_move_track_up(self):
        if (s := self.release_track_listbox.curselection()) and (i := s[0]) > 0:
            self.state.release_tracks[i], self.state.release_tracks[i-1] = self.state.release_tracks[i-1], self.state.release_tracks[i]
            self.refresh_release_view(); self.release_track_listbox.selection_set(i-1)
    def release_move_track_down(self):
        if (s := self.release_track_listbox.curselection()) and (i := s[0]) < len(self.state.release_tracks)-1:
            self.state.release_tracks[i], self.state.release_tracks[i+1] = self.state.release_tracks[i+1], self.state.release_tracks[i]
            self.refresh_release_view(); self.release_track_listbox.selection_set(i+1)
    def release_remove_track(self): (s := self.release_track_listbox.curselection()) and self.state.release_tracks.pop(s[0]) or self.refresh_release_view()

    def set_detail_status(self, s): self._set_detail_status_chip(s)
    def loudness_import_selected_work(self):
        if (it := self._get_selected_overview_item()) and it.get("audio_path"):
            self.state.loudness_files = [it["audio_path"]]; self._pop_l_tree(); self.select_tab_by_id("loudness")
    def loudness_import_filtered_works(self):
        self.state.loudness_files = [it["audio_path"] for it in self.state.filtered_records if it.get("audio_path")]
        self._pop_l_tree(); self.select_tab_by_id("loudness")
    def loudness_export_files(self):
        out = self.loudness_output_dir_var.get(); pk = float(self.loudness_peak_var.get() or -1)
        if out: self.tasks.run(lambda: [loudness_workflows.export_result_item(it, out, pk, True, loudness_tools) for it in self.state.loudness_results], lambda r: self.append_log("Export fertig"), "Exportiere...")

if __name__ == "__main__":
    app = AKMApp()
    app.mainloop()
