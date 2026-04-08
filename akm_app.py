"""
Funky Moose Release Forge - Main Application Orchestrator
Modular, State-Driven, and Industrial-Themed Backend Manager for Music Release Workflows.
"""

import os
import tkinter as tk
import logging
from tkinter import messagebox, ttk
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
    akm_core, assistant_tools, flow_tools, app_state, task_runner,
    loudness_tools
)
from app_ui import ui_patterns

# Audio Engine & Player
from app_logic.audio_player_engine import AudioPlayerEngine
from app_ui.audio_player_ui import AkmAudioPlayer

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
        if hasattr(self, "header") and hasattr(self.header, "task_detail_label"):
            self.header.task_detail_label.config(text=f"Workspace bereit | Drag & Drop: {dnd_status}")
        
        self.overview_ctrl.refresh_list()
        self.batch_ctrl.reload_flow_data(preferred_index=0)
        
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
        self._bind_controller_delegates()

    def _bind_controller_delegates(self):
        """Expose only the shared controller actions that multiple app surfaces need."""
        delegate_map = {
            self.project_ctrl: (
                "save_project",
                "load_project_dialog",
                "import_excel",
                "import_excel_path",
            ),
            self.overview_ctrl: (
                "refresh_list",
                "refresh_dashboard",
                "load_selected_into_details",
                "set_status",
                "on_listbox_activate",
                "jump_to_last_open",
            ),
        }
        for controller, bindings in delegate_map.items():
            for binding in bindings:
                if isinstance(binding, tuple):
                    app_name, controller_name = binding
                else:
                    app_name = controller_name = binding
                setattr(self, app_name, getattr(controller, controller_name))

    def _init_ui_vars(self):
        """Prepare tracker variables and registries used across multiple tabs."""
        # Overview Registry
        self.overview_filter_chips = {}
        self.dashboard_labels = {}
        self.dashboard_status_chips = {}
        
        # Detail & Metadata Registry
        self.detail_vars = {}
        self.cover_state_cache = {}
        self.release_vars = {}
        self.release_state_cache = {}
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
        self.append_log(f"{cfg.APP_NAME} v{cfg.VERSION} INITIALIZED")
        self.append_log("System: Core architecture decoupled.")
        self.append_log("-" * 30)

        # Force initial tab loading
        self.after(100, lambda: self.on_tab_changed(None))
        self.after(240, self._preload_tabs)

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

    def _preload_tabs(self):
        self.tab_system.preload(
            ("assistant", "overview", "details", "batch", "cover", "release", "loudness"),
            delay_ms=140,
        )

    # --- TAB NAVIGATION & CONTROL ---
    def select_tab_by_id(self, tab_id):
        """Switches to the specified tab and triggers its refresh logic if necessary."""
        if tab_id in self.tab_system.map:
            self.tab_system.notebook.select(self.tab_system.map[tab_id])

    def get_built_tab(self, tab_id):
        """Returns an already instantiated tab without triggering lazy construction."""
        return getattr(self.tab_system, "_instances", {}).get(tab_id)

    def open_loudness_tab(self):
        """Convenience method to access the primary optimization workflow."""
        self.select_tab_by_id("loudness")
        view_state = assistant_tools.build_loudness_tab_open_state(loudness_tools is not None)
        if hasattr(self, "loudness_status_label"):
            self.loudness_status_label.config(text=view_state["status_text"])
        if hasattr(self, "loudness_hint_label"):
            self.loudness_hint_label.config(text=view_state["hint_text"])
        self.append_log(view_state["log_message"])

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
        
        # 4. Perspective-Specific Logic
        self._handle_tab_refresh(active_tab_id, mtime)

    def _handle_tab_refresh(self, active_tab_id, mtime):
        """Runs only the refresh logic needed for the currently active tab."""
        if active_tab_id == "dashboard":
            if self._last_dashboard_refresh["mtime"] != mtime:
                self.overview_ctrl.refresh_dashboard()
                self._last_dashboard_refresh["mtime"] = mtime
            return

        if active_tab_id == "overview":
            search = (self.search_var.get() or "").lower() if self.search_var else ""
            filt = (self.status_filter_var.get() or "all") if self.status_filter_var else "all"
            sort_key = self.sort_key_var.get() if self.sort_key_var else "title"
            sort_desc = bool(self.sort_desc_var.get()) if self.sort_desc_var else False

            if (
                self._last_overview_refresh["mtime"] != mtime
                or self._last_overview_refresh["search"] != search
                or self._last_overview_refresh["filter"] != filt
                or self._last_overview_refresh["sort"] != sort_key
                or self._last_overview_refresh["desc"] != sort_desc
            ):
                self.overview_ctrl.refresh_list()
                self._last_overview_refresh.update({
                    "search": search,
                    "filter": filt,
                    "sort": sort_key,
                    "desc": sort_desc,
                    "mtime": mtime,
                })
            return

        if active_tab_id == "batch":
            if self._last_batch_refresh["mtime"] != mtime:
                self.batch_ctrl.update_flow()
                self._last_batch_refresh["mtime"] = mtime
            return

        if active_tab_id == "details":
            self.details_ctrl.refresh_titles()
            return

        if active_tab_id == "release":
            self.release_ctrl.refresh_view()

    def refresh_all_tabs(self):
        """Standardized orchestrator to update all modular components and reset trackers."""
        current_search = (self.search_var.get() or "").lower() if self.search_var else ""
        current_filter = (self.status_filter_var.get() or "all") if self.status_filter_var else "all"
        current_sort = self.sort_key_var.get() if self.sort_key_var else "title"
        current_desc = bool(self.sort_desc_var.get()) if self.sort_desc_var else False
        current_mtime = self.state._get_data_mtime()

        self.overview_ctrl.refresh_list()
        self.overview_ctrl.refresh_dashboard()
        self.details_ctrl.refresh_view()
        self.batch_ctrl.reload_flow_data()
        self.release_ctrl.refresh_view()
        cover_tab = getattr(getattr(self, "tab_system", None), "_instances", {}).get("cover")
        if cover_tab is not None and hasattr(cover_tab, "refresh_view"):
            cover_tab.refresh_view()
        self._last_overview_refresh.update({
            "search": current_search,
            "filter": current_filter,
            "sort": current_sort,
            "desc": current_desc,
            "mtime": current_mtime,
        })
        self._last_dashboard_refresh["mtime"] = current_mtime
        self._last_batch_refresh["mtime"] = current_mtime

    def on_closing(self):
        """Asks for confirmation before exiting."""
        res = messagebox.askyesnocancel(
            "Beenden", 
            "Möchten Sie vor dem Beenden speichern? \nNur das Speichern als Projekt (.akm) erhält alle aktuellen Einstellungen.",
            icon='warning',
            default='yes'
        )
        if res is True:
            if self.save_project():
                self.destroy()
        elif res is False:
            self.destroy()

    def _schedule_refresh_list(self):
        """Debounced list refresh for search input."""
        if self._refresh_timer:
            self.after_cancel(self._refresh_timer)
        self._refresh_timer = self.after(300, self.refresh_list)

    def add(self, title=""): 
        self.project_ctrl.add_entry((title or "").strip())

    def _set_overview_status_filter(self, s): 
        self.overview_ctrl.set_status_filter(s)

    def _open_overview_with_filter(self, s): 
        self.overview_ctrl.open_with_filter(s)

    # --- UTILITIES ---
    def btn(self, parent, text, cmd, primary=False, quiet=False, width=None, accent_color=None): 
        """Wrapper for the centralized design-system button creator."""
        return ui_patterns.create_btn(parent, text, cmd, primary=primary, quiet=quiet, width=width, accent_color=accent_color)

    def append_log(self, message): 
        """Central app logging entrypoint mirrored to the UI by the logger handler."""
        logging.info(str(message))

    def resource_path(self, relative_path):
        return cfg.get_resource_path(relative_path)

    def update_task_indicator(self, busy):
        """Starts or stops the activity pulse on the Task Indicator label."""
        if hasattr(self, 'task_indicator'):
            if busy:
                self.task_indicator.config(text="TASK AKTIV", fg=ui_patterns.ACCENT)
                self.task_indicator.start()
                if hasattr(self, "header") and hasattr(self.header, "task_state_label"):
                    self.header.task_state_label.config(text="Hintergrundjob läuft")
                if hasattr(self, "header") and hasattr(self.header, "task_detail_label"):
                    self.header.task_detail_label.config(text="Import, Analyse oder Export arbeitet gerade.")
            else: 
                self.task_indicator.config(text="SYSTEM BEREIT", fg="#94A3B8")
                self.task_indicator.stop()
                if hasattr(self, "header") and hasattr(self.header, "task_state_label"):
                    self.header.task_state_label.config(text="System bereit")
                if hasattr(self, "header") and hasattr(self.header, "task_detail_label"):
                    dnd_text = "Aktiv" if TkinterDnD is not None else "Deaktiviert"
                    self.header.task_detail_label.config(text=f"Keine Hintergrundjobs aktiv | Drag & Drop: {dnd_text}")

    def status_text(self, status): 
        """Translated status text helper."""
        return ui_patterns.get_status_chip_text(status, akm_core.get_lang())

    # --- AUDIO HELPERS ---
    def open_audio_player_for_selected(self):
        """Opens the premium mini-player for the selected work's audio file."""
        it = self.overview_ctrl.get_selected_item()
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
        """Global scroll handler that prefers native widgets, then the nearest scrollable page."""
        x, y = event.x_root, event.y_root
        target = self.winfo_containing(x, y)
        if not target:
            return

        def _scroll_target(widget):
            if event.num == 4:
                widget.yview_scroll(-1, "units")
                return
            if event.num == 5:
                widget.yview_scroll(1, "units")
                return
            delta = event.delta
            if abs(delta) >= 120:
                widget.yview_scroll(int(-1 * (delta / 120)), "units")
            else:
                widget.yview_scroll(int(-1 * delta), "units")

        if isinstance(target, (tk.Listbox, tk.Text, ttk.Treeview)):
            _scroll_target(target)
            return

        widget = target
        while widget is not None:
            if isinstance(widget, ui_patterns.AkmScrollablePanel):
                _scroll_target(widget.canvas)
                return
            parent_name = widget.winfo_parent()
            if not parent_name:
                break
            widget = widget.nametowidget(parent_name)

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
