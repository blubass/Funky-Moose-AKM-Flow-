"""
Funky Moose Release Forge - Main Application Orchestrator
Modular, State-Driven, and Industrial-Themed Backend Manager for Music Release Workflows.
"""

import copy
import os
import sys
import time
import tkinter as tk
import logging
import traceback
from tkinter import filedialog, messagebox, ttk
from app_logic.config import cfg
from app_logic import logger_config

# Optional: DnD Support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None


# Core Logic & Infrastructure
from app_logic import (
    akm_core, assistant_tools, cover_tools, detail_tools, 
    flow_tools, overview_tools, release_tools, app_state, task_runner,
    loudness_tools
)
from app_ui import ui_patterns, path_ui_tools, release_view_tools
from app_ui.ui_patterns import * 
from app_workflows import loudness_workflows, release_workflows

# Audio Engine & Player
from app_logic.audio_player_engine import AudioPlayerEngine
from app_ui.audio_player_ui import AkmAudioPlayer

# Design Tokens & Themed Widgets
from app_ui.ui_patterns import (
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    FONT_SM, FONT_MD, FONT_BOLD, FONT_MD_BOLD, FONT_LG, FONT_XXXL,
    PulseLabel, AkmPanel, AkmLabel, AkmSubLabel, AkmToast
)

# Controllers
from app_controllers.project_controller import ProjectController
from app_controllers.overview_controller import OverviewController
from app_controllers.loudness_controller import LoudnessController
from app_controllers.release_controller import ReleaseController
from app_controllers.batch_controller import BatchController
from app_controllers.details_controller import DetailsController

# Architectural Layout Components
from app_ui.header import MainHeader
from app_ui.tab_system import AppTabs

class AKMApp(TkinterDnD.Tk if TkinterDnD is not None else tk.Tk):
    """
    Central orchestrator for the Funky Moose Release Forge.
    Manages state via AppState, background tasks via TaskRunner, and coordinates the modular tab-based UI.
    """
    def __init__(self):
        super().__init__()
        # 0. Global Setup (Paths & Logs)
        cfg.ensure_dirs()
        logger_config.setup_logging(self)
        
        self._set_window_config()
        self._init_state_and_services()
        self._init_ui_vars()
        
        # Setup & Boot
        ui_patterns.apply_ttk_styles()
        self.build_ui()
        
        # Final Bindings & Initial Data Load
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.tab_system.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed, add="+")
        
        # Performance Trackers (Reduces redundant tab refreshes)
        self._last_overview_refresh = {"search": None, "filter": None, "sort": None, "desc": None, "mtime": None}
        self._last_dashboard_refresh = {"mtime": None}
        self._last_batch_refresh = {"mtime": None}
        self._refresh_timer = None
        
        # --- GLOBAL MOUSEWHEEL FIX ---
        self.bind_all("<MouseWheel>", self._on_root_mousewheel)
        self.bind_all("<Button-4>", self._on_root_mousewheel)
        self.bind_all("<Button-5>", self._on_root_mousewheel)
        
        # --- COMMAND BINDINGS ---
        self.bind_all("<Command-a>", self.select_all)
        
        dnd_status = "Aktiv" if TkinterDnD is not None else "Deaktiviert (Paket fehlt)"
        self.append_log(f"Drag & Drop System: {dnd_status}")
        
        self.refresh_list()
        self.reload_flow_data(preferred_index=0)
        
        # --- MAC FOCUS FIX (Forcing bundle visibility) ---
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))
        self.focus_force()
        logging.info(f"GUI MASTER START: {cfg.APP_NAME} v{cfg.VERSION}")

    # --- INITIALIZATION ---
    def _set_window_config(self):
        """Standard window initialization and styling."""
        self.title(cfg.APP_NAME)
        self.geometry("1100x860")
        self.minsize(860, 620)
        self.configure(bg=ui_patterns.BG)

    def _init_state_and_services(self):
        """Instantiate core singleton services and logic controllers."""
        self.state = app_state.AppState()
        self.tasks = task_runner.TaskRunner(self)
        self.audio = AudioPlayerEngine(app_log_func=self.append_log)
        
        # Instantiate Specialized Controllers
        self.overview_ctrl = OverviewController(self)
        self.project_ctrl = ProjectController(self)
        self.loudness_ctrl = LoudnessController(self)
        self.release_ctrl = ReleaseController(self)
        self.batch_ctrl = BatchController(self)
        self.details_ctrl = DetailsController(self)

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
        
        # Loudness Perspective
        self.loudness_output_dir_var = tk.StringVar()
        self.loudness_target_var = tk.StringVar(value="-14.0")
        self.loudness_peak_var = tk.StringVar(value="-1.0")

    # --- UI BUILDING ---
    def build_ui(self):
        """Assembles the main application layout including header and tabs."""
        self.content_root = tk.Frame(self, bg=ui_patterns.BG)
        self.content_root.pack(fill="both", expand=True)
        
        # 1. Header (Branding & Global Controls)
        self.header = MainHeader(self.content_root, self)
        
        # 2. Tab System (Functional Modules)
        self.tab_system = AppTabs(self.content_root, self)
        
        # Dynamic Property Access for Functional Modules (Lazy)
        # These are generated on-demand by the Tab System
        self.task_indicator = self.header.task_indicator

        # Initial Boot Info Logger (Branding Trace)
        self.append_log("-" * 30)
        self.append_log("OBSIDIAN MASTER v1.0.1 INITIALIZED")
        self.append_log("System: Core architecture decoupled.")
        self.append_log("-" * 30)

        # Force initial tab loading
        self.after(100, lambda: self.on_tab_changed(None))

    @property
    def dashboard_tab(self): return self.tab_system.dashboard
    @property
    def assistant_tab(self): return self.tab_system.assistant
    @property
    def batch_tab(self): return self.tab_system.batch
    @property
    def overview_tab(self): return self.tab_system.overview
    @property
    def details_tab(self): return self.tab_system.details
    @property
    def cover_tab(self): return self.tab_system.cover
    @property
    def release_tab(self): return self.tab_system.release
    @property
    def loudness_tab(self): return self.tab_system.loudness

    @property
    def tabs(self): return self.tab_system.notebook
    @property
    def tab_map(self): return self.tab_system.map

    # --- TAB NAVIGATION & CONTROL ---
    def select_tab_by_id(self, tab_id):
        """Switches to the specified tab and triggers its refresh logic if necessary."""
        if tab_id in self.tab_system.map:
            self.tab_system.notebook.select(self.tab_system.map[tab_id])

    def open_loudness_tab(self):
        """Convenience method to access the primary optimization workflow."""
        self.select_tab_by_id("loudness")

    def on_tab_changed(self, event):
        """Central event handler for tab transitions (highly optimized)."""
        selected_path = self.tab_system.notebook.select()
        if not selected_path: return
        
        # 1. Deduplication (Prevents redundant calls on some OS/Tkinter versions)
        if hasattr(self, "_prev_selected_path") and self._prev_selected_path == selected_path:
            return
        self._prev_selected_path = selected_path

        # 2. Identify the active tab
        active_tab_id = None
        for tid, widget in self.tab_system.map.items():
            if str(widget) == selected_path:
                active_tab_id = tid
                break
        
        if not active_tab_id: return
        
        # 3. Ensure built (via lazy system)
        getattr(self.tab_system, active_tab_id)
        
        mtime = self.state._get_data_mtime()
        
        # 4. Perspective-Specific Logic (Only if data changed or filters mismatched)
        if active_tab_id == "dashboard":
            if self._last_dashboard_refresh["mtime"] != mtime:
                self.refresh_dashboard()
                self._last_dashboard_refresh["mtime"] = mtime
                
        elif active_tab_id == "overview":
            search = (self.search_var.get() or "").lower() if self.search_var else ""
            filt = (self.status_filter_var.get() or "all") if self.status_filter_var else "all"
            # We skip sort/desc for the immediate "back-and-forth" check to stay fast
            if self._last_overview_refresh["mtime"] != mtime or self._last_overview_refresh["filter"] != filt:
                self.refresh_list()
                self._last_overview_refresh.update({"search": search, "filter": filt, "mtime": mtime})
                
        elif active_tab_id == "batch":
            if self._last_batch_refresh["mtime"] != mtime:
                self.update_flow()
                self._last_batch_refresh["mtime"] = mtime

        elif active_tab_id == "release":
            self.release_ctrl.refresh_view()

    def refresh_all_tabs(self):
        """Standardized orchestrator to update all modular components and reset trackers."""
        self.overview_ctrl.refresh_list()
        self.overview_ctrl.refresh_dashboard()
        self.batch_ctrl.reload_flow_data()
        self.release_ctrl.refresh_view()
        # Reset trackers to ensure next tab switch catches up if needed
        self._last_overview_refresh["mtime"] = None
        self._last_dashboard_refresh["mtime"] = None
        self._last_batch_refresh["mtime"] = None

    def on_closing(self):
        """Asks for confirmation before exiting."""
        from tkinter import messagebox
        res = messagebox.askyesnocancel(
            "Beenden", 
            "Möchten Sie vor dem Beenden speichern? \nNur das Speichern als Projekt (.akm) erhält alle aktuellen Einstellungen.",
            icon='warning',
            default='yes'
        )
        if res is True:
            self.save_project()
            self.destroy()
        elif res is False:
            self.destroy()
        else:
            pass

    def _schedule_refresh_list(self):
        """Debounced list refresh for search input."""
        if self._refresh_timer:
            self.after_cancel(self._refresh_timer)
        self._refresh_timer = self.after(300, self.refresh_list)

    # --- SHARED DELEGATES (Called by Tabs) ---
    # --- DELEGATES: PROJECT & PERSISTENCE ---
    def save_project(self): 
        self.project_ctrl.save_project()
        
    def load_project_dialog(self): 
        self.project_ctrl.load_project_dialog()
        
    def import_excel(self): 
        self.project_ctrl.import_excel()
        
    def import_excel_path(self, path): 
        self.project_ctrl.import_excel_path(path)
        
    def add(self): 
        title = ""
        if hasattr(self, 'entry'):
            title = self.entry.get().strip()
        self.project_ctrl.add_entry(title)

    # --- DELEGATES: OVERVIEW & DASHBOARD ---
    def refresh_list(self): 
        self.overview_ctrl.refresh_list()
        
    def refresh_dashboard(self): 
        self.overview_ctrl.refresh_dashboard()

    def load_selected_into_details(self): 
        self.overview_ctrl.load_selected_into_details()
        
    def set_status(self, s): 
        self.overview_ctrl.set_status(s)
        
    def on_listbox_activate(self, e): 
        self.overview_ctrl.on_listbox_activate(e)
        
    def jump_to_last_open(self): 
        self.overview_ctrl.jump_to_last_open()
        
    def _set_overview_status_filter(self, s): 
        self.overview_ctrl.set_status_filter(s)

    def _open_overview_with_filter(self, s): 
        self.overview_ctrl.open_with_filter(s)

    # --- DELEGATES: DETAILS & METADATA ---
    def save_details(self): 
        self.details_ctrl.save_details()
        
    def toggle_release(self): 
        self.details_ctrl.toggle_release()

    def clear_details_form(self): 
        self.details_ctrl.clear_details_form()

    def set_detail_status(self, s): 
        self.details_ctrl._set_detail_status_chip(s)

    def choose_audio_path_for_details(self): 
        self.details_ctrl.choose_audio_path()

    def open_audio_path_in_finder(self): 
        self.details_ctrl.open_audio_path_in_finder()

    # --- DELEGATES: BATCH & FLOW ---
    def reload_flow_data(self, preferred_index=None): 
        self.batch_ctrl.reload_flow_data(preferred_index)
        
    def update_flow(self): 
        self.batch_ctrl.update_flow()

    def process_batch(self): 
        self.batch_ctrl.process_selected_flow()

    def flow_copy(self): 
        self.batch_ctrl.flow_copy()

    def flow_submit(self): 
        self.batch_ctrl.flow_submit()

    def flow_next(self): 
        self.batch_ctrl.flow_next()

    def open_track_in_batch(self, it): 
        self.batch_ctrl.open_track_in_batch(it)

    # --- DELEGATES: LOUDNESS ---
    def process_all_loudness(self): 
        self.loudness_ctrl.process_all()

    def loudness_choose_files(self): 
        self.loudness_ctrl.choose_files()
        
    def loudness_handle_drop(self, event): 
        self.loudness_ctrl.handle_drop(event)
        
    def loudness_choose_outdir(self): 
        self.loudness_ctrl.choose_outdir()
        
    def process_selected_loudness(self, item_index): 
        self.loudness_ctrl.process_selected(item_index)

    def loudness_delete_files(self): 
        self.loudness_ctrl.delete_files()
        
    def loudness_analyze_files(self): 
        self.loudness_ctrl.analyze_files()
        
    def loudness_export_files(self): 
        self.loudness_ctrl.export_files()
        
    def loudness_choose_output_dir(self): 
        self.loudness_ctrl.choose_output_dir()
        
    def loudness_import_selected_work(self): 
        self.loudness_ctrl.import_selected_work()
        
    def loudness_import_filtered_works(self): 
        self.loudness_ctrl.import_filtered_works()
        
    def on_loudness_tree_activate(self, event): 
        self.loudness_ctrl.on_tree_activate(event)

    # --- DELEGATES: RELEASE ---
    def open_release_cover_dialog(self): 
        self.release_ctrl.open_cover_dialog()

    def release_handle_drop(self, event): 
        self.release_ctrl.handle_drop(event)
        
    def refresh_release_view(self): 
        self.release_ctrl.refresh_view()
        
    def choose_release_cover(self): 
        self.release_ctrl.choose_cover()
        
    def choose_release_export_dir(self): 
        self.release_ctrl.choose_export_dir()
        
    def open_release_cover_in_finder(self): 
        self.release_ctrl.open_cover_in_finder()
        
    def build_distro_export(self): 
        self.release_ctrl.build_export()
        
    def release_move_track_up(self): 
        self.release_ctrl.move_track_up()
        
    def release_move_track_down(self): 
        self.release_ctrl.move_track_down()
        
    def release_remove_track(self): 
        self.release_ctrl.remove_track()

    # --- UTILITIES ---
    def btn(self, parent, text, cmd, primary=False, quiet=False, width=None, accent_color=None): 
        """Wrapper for the centralized design-system button creator."""
        return ui_patterns.create_btn(parent, text, cmd, primary=primary, quiet=quiet, width=width, accent_color=accent_color)

    def append_log(self, message): 
        """Safely appends activity to the global log via the central logging engine."""
        # This is now a wrapper around logging to keep compatibility
        logging.info(message)

    def resource_path(self, relative_path):
        return cfg.get_resource_path(relative_path)

    def update_task_indicator(self, busy):
        """Starts or stops the activity pulse on the Task Indicator label."""
        if hasattr(self, 'task_indicator'):
            if busy: 
                self.task_indicator.start()
            else: 
                self.task_indicator.stop()

    def status_text(self, status): 
        """Translated status text helper."""
        return ui_patterns.get_status_chip_text(status, akm_core.get_lang())

    # --- AUDIO HELPERS ---
    def open_audio_player_for_selected(self):
        """Opens the premium mini-player for the selected work's audio file."""
        it = self.overview_ctrl._get_selected_overview_item()
        if it and it.get("audio_path") and os.path.exists(it["audio_path"]):
            AkmAudioPlayer(self, self.audio, it["audio_path"], it.get("title", "Preview"))
        else:
            ui_patterns.AkmToast(self, "KEINE AUDIODATEI GEFUNDEN", color=ui_patterns.FLAVOR_ERROR)

    def open_audio_player_for_path(self, path, title="Preview"):
        """Opens the player for a specific raw path (used by Loudness tab)."""
        if path and os.path.exists(path):
            AkmAudioPlayer(self, self.audio, path, title)
        else:
            ui_patterns.AkmToast(self, "DATEI NICHT GEFUNDEN", color=ui_patterns.FLAVOR_ERROR)

    def _on_root_mousewheel(self, event):
        """Intelligent global scroll handler for Listboxes, Treeviews, and Text widgets on any OS."""
        x, y = event.x_root, event.y_root
        target = self.winfo_containing(x, y)
        if not target: return
        
        # Don't double-scroll if target is already handled by AkmScrollablePanel's canvas or children
        # But for standard Tkinter widgets, we'll force it.
        
        if isinstance(target, (tk.Listbox, tk.Text, ttk.Treeview)):
            # Handle scroll
            if event.num == 4: # Linux
                target.yview_scroll(-1, "units")
            elif event.num == 5: # Linux
                target.yview_scroll(1, "units")
            else: # macOS / Windows
                delta = event.delta
                if abs(delta) >= 120:
                    target.yview_scroll(int(-1*(delta/120)), "units")
                else: # macOS fine scrolling often gives 1 or -1
                    target.yview_scroll(int(-1*delta), "units")

    def select_all(self, event=None):
        """Universal 'Select All' handler for Listboxes and Treeviews (Cmd+A)."""
        focused = self.focus_get()
        if isinstance(focused, tk.Listbox):
            focused.select_set(0, tk.END)
            focused.event_generate("<<ListboxSelect>>")
        elif isinstance(focused, ttk.Treeview):
            focused.selection_set(focused.get_children())
        return "break"

if __name__ == "__main__":
    app = AKMApp()
    app.mainloop()
