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
    from tkinterdnd2 import TkinterDnD
except Exception:
    TkinterDnD = None


# Core Logic & Infrastructure
from app_logic import (
    akm_core, assistant_tools, app_state, task_runner,
    loudness_tools, i18n
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

from app_ui.header import MainHeader
from app_ui.tab_system import AppTabs

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_controllers.project_controller import ProjectController
    from app_controllers.overview_controller import OverviewController
    from app_controllers.loudness_controller import LoudnessController
    from app_controllers.release_controller import ReleaseController
    from app_controllers.batch_controller import BatchController
    from app_controllers.details_controller import DetailsController

class AKMApp(TkinterDnD.Tk if TkinterDnD is not None else tk.Tk):
    """
    Central orchestrator for the Funky Moose Release Forge.
    Manages state via AppState, background tasks via TaskRunner, and coordinates the modular tab-based UI.
    """
    OVERVIEW_FILTER_DEFAULTS = {
        "search": "",
        "filter": "all",
        "sort": "title",
        "desc": False,
    }

    def __init__(self):
        super().__init__()

        # Explicit Controller Type Annotations
        self.overview_ctrl: 'OverviewController'
        self.project_ctrl: 'ProjectController'
        self.loudness_ctrl: 'LoudnessController'
        self.release_ctrl: 'ReleaseController'
        self.batch_ctrl: 'BatchController'
        self.details_ctrl: 'DetailsController'

        self._perform_global_setup()
        self._set_window_config()
        self._init_services()
        self._init_runtime_state()
        self._init_controllers()
        self._build_application_shell()
        self._configure_runtime_bindings()
        self._bootstrap_application()

    # --- INITIALIZATION ---
    def _perform_global_setup(self):
        """Prepare writable paths and UI-backed logging before services come online."""
        cfg.ensure_dirs()
        logger_config.setup_logging(self)

    def _set_window_config(self):
        """Standard window initialization and styling."""
        self.title(cfg.APP_NAME)
        self.geometry("1100x860")
        self.minsize(860, 620)
        self.configure(bg=ui_patterns.BG)

    def _init_runtime_state(self):
        """Prepare shared runtime state used by UI, refresh logic and controller handoff."""
        self._init_ui_vars()
        self._init_refresh_trackers()

    def _init_services(self):
        """Instantiate core singleton services that are independent from the visual shell."""
        self.state = app_state.AppState()
        self.tasks = task_runner.TaskRunner(self)
        self.audio = AudioPlayerEngine(app_log_func=self.append_log)

    def _init_controllers(self):
        """Attach specialized controllers after state/services are ready."""
        controller_specs = (
            ("overview_ctrl", OverviewController),
            ("project_ctrl", ProjectController),
            ("loudness_ctrl", LoudnessController),
            ("release_ctrl", ReleaseController),
            ("batch_ctrl", BatchController),
            ("details_ctrl", DetailsController),
        )
        for attr_name, controller_cls in controller_specs:
            setattr(self, attr_name, controller_cls(self))
        self._bind_controller_delegates()

    def _configure_runtime_bindings(self):
        """Register top-level lifecycle, tab and global input bindings."""
        self._bind_window_events()
        self._bind_tab_events()
        self._bind_global_mousewheel()
        self._bind_global_shortcuts()

    def _build_application_shell(self):
        """Create the visual shell and shared app chrome."""
        ui_patterns.apply_ttk_styles()
        self.build_ui()

    def _bootstrap_application(self):
        """Run the post-build boot sequence once services, controllers and UI all exist."""
        self._log_boot_banner()
        self._schedule_initial_tab_bootstrap()
        self._announce_workspace_ready()
        self._prime_initial_views()
        self._apply_startup_focus()
        logging.info(f"GUI MASTER START: {cfg.APP_NAME} v{cfg.VERSION}")

    def _init_refresh_trackers(self):
        """Track refresh-sensitive state separately."""
        self._last_overview_refresh = self._build_overview_refresh_snapshot()
        self._refresh_timer = None
        self._prev_selected_path = None
        
        # Subscribe to data changes
        self.state.subscribe("cache_invalidated", self._on_data_invalidated)
        self.state.subscribe("data_changed", self._on_data_changed)

    def _bind_window_events(self):
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _bind_tab_events(self):
        self.tab_system.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed, add="+")

    def _bind_global_mousewheel(self):
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(sequence, self._on_root_mousewheel)

    def _bind_global_shortcuts(self):
        shortcut_map = {
            "<Command-a>": self.select_all,
            "<Command-q>": self._on_quit_shortcut,
            "<Control-q>": self._on_quit_shortcut,
        }
        for sequence, callback in shortcut_map.items():
            self.bind_all(sequence, callback)

    def _announce_workspace_ready(self):
        dnd_status = self._get_drag_and_drop_status_text(include_reason=True)
        self.append_log(f"Drag & Drop System: {dnd_status}")
        if hasattr(self, "header") and hasattr(self.header, "task_detail_label"):
            workspace_ready = i18n._t("workspace_ready")
            self.header.task_detail_label.config(text=f"{workspace_ready} | Drag & Drop: {dnd_status}")

    def _prime_initial_views(self):
        """Load controller-backed startup data once the shell is visible."""
        self.overview_ctrl.refresh_list()
        self.batch_ctrl.reload_flow_data(preferred_index=0)

    def _apply_startup_focus(self):
        """Force the initial app window to the front on startup, especially on macOS bundles."""
        self.update_idletasks()
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))
        self.focus_force()

    def _log_boot_banner(self):
        """Emit a small startup banner once the visible shell exists."""
        self.append_log("-" * 30)
        self.append_log(f"{cfg.APP_NAME} v{cfg.VERSION} INITIALIZED")
        self.append_log("System: Core architecture decoupled.")
        self.append_log("-" * 30)

    def _schedule_initial_tab_bootstrap(self):
        """Kick lazy tab loading and the first tab refresh into the event loop."""
        self.after(100, lambda: self.on_tab_changed(None))
        self.after(240, self._preload_tabs)

    def _get_drag_and_drop_status_text(self, include_reason=False):
        if TkinterDnD is not None:
            return "Aktiv"
        if include_reason:
            return "Deaktiviert (Paket fehlt)"
        return "Deaktiviert"

    def _bind_controller_delegates(self):
        """Expose shared controller actions explicitly for better transparency."""
        
        # Project Controller delegates
        self.save_project = self.project_ctrl.save_project
        self.load_project_dialog = self.project_ctrl.load_project_dialog
        self.import_excel = self.project_ctrl.import_excel
        self.import_excel_path = self.project_ctrl.import_excel_path
        
        # Overview Controller delegates
        self.refresh_list = self.overview_ctrl.refresh_list
        self.refresh_dashboard = self.overview_ctrl.refresh_dashboard
        self.load_selected_into_details = self.overview_ctrl.load_selected_into_details
        self.set_status = self.overview_ctrl.set_status
        self.on_listbox_activate = self.overview_ctrl.on_listbox_activate
        self.jump_to_last_open = self.overview_ctrl.jump_to_last_open

    def _init_ui_vars(self):
        """Prepare tracker variables and registries used across multiple tabs."""
        # Detail & Metadata Registry
        self.cover_state_cache = {}
        self.release_state_cache = {}
        self.detail_original_title = None
        self.current_detail_status = "in_progress"
        
        # Batch & Flow
        self.copy_button = None

    # --- UI BUILDING ---
    def build_ui(self):
        """Assembles the main application layout including header and tabs."""
        self.content_root = tk.Frame(self, bg=ui_patterns.BG)
        self.content_root.pack(fill="both", expand=True)

        self.header = MainHeader(self.content_root, self)
        self.tab_system = AppTabs(self.content_root, self)
        self.task_indicator = self.header.task_indicator

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
        tab_system = self.__dict__.get("tab_system")
        return getattr(tab_system, "_instances", {}).get(tab_id) if tab_system is not None else None

    def get_detail_form_vars(self):
        details_tab = self.get_built_tab("details")
        if details_tab is not None and hasattr(details_tab, "get_form_vars"):
            return details_tab.get_form_vars()
        return {}

    def get_release_form_vars(self):
        release_tab = self.get_built_tab("release")
        if release_tab is not None and hasattr(release_tab, "get_form_vars"):
            return release_tab.get_form_vars()
        return {}

    def get_overview_filter_state(self):
        overview_tab = self.get_built_tab("overview")
        if overview_tab is not None and hasattr(overview_tab, "get_filter_state"):
            return overview_tab.get_filter_state()
        return dict(self.OVERVIEW_FILTER_DEFAULTS)

    def _build_overview_refresh_snapshot(self, filter_state=None, mtime=None):
        """Normalize overview filter state into a tracker-friendly snapshot."""
        defaults = getattr(self, "OVERVIEW_FILTER_DEFAULTS", AKMApp.OVERVIEW_FILTER_DEFAULTS)
        if filter_state is not None:
            state = filter_state
        elif "tab_system" in self.__dict__:
            get_filter_state = getattr(self, "get_overview_filter_state", None)
            if callable(get_filter_state):
                state = get_filter_state()
            else:
                state = {
                    "search": (self.search_var.get() if getattr(self, "search_var", None) else ""),
                    "filter": (self.status_filter_var.get() if getattr(self, "status_filter_var", None) else defaults["filter"]),
                    "sort": (self.sort_key_var.get() if getattr(self, "sort_key_var", None) else defaults["sort"]),
                    "desc": bool(self.sort_desc_var.get()) if getattr(self, "sort_desc_var", None) else defaults["desc"],
                }
        else:
            state = dict(defaults)
        return {
            "search": (state.get("search") or "").lower(),
            "filter": state.get("filter") or defaults["filter"],
            "sort": state.get("sort") or defaults["sort"],
            "desc": bool(state.get("desc")),
            "mtime": mtime,
        }

    def _should_refresh_overview(self, snapshot):
        """Compare the active overview state against the last refresh snapshot."""
        return any(
            self._last_overview_refresh[key] != snapshot[key]
            for key in ("search", "filter", "sort", "desc")
        )

    def _remember_overview_refresh(self, snapshot):
        self._last_overview_refresh.update(snapshot)

    def open_loudness_tab(self):
        """Convenience method to access the primary optimization workflow."""
        self.select_tab_by_id("loudness")
        loudness_tab = self.loudness_tab
        view_state = assistant_tools.build_loudness_tab_open_state(loudness_tools is not None)
        if loudness_tab is not None and hasattr(loudness_tab, "set_open_state"):
            loudness_tab.set_open_state(view_state["status_text"], view_state["hint_text"])
        else:
            if hasattr(self, "loudness_status_label"):
                self.loudness_status_label.config(text=view_state["status_text"])
            if hasattr(self, "loudness_hint_label"):
                self.loudness_hint_label.config(text=view_state["hint_text"])
        self.append_log(view_state["log_message"])

    def on_tab_changed(self, event):
        """Central event handler for tab transitions (highly optimized)."""
        selected_path = self.tab_system.notebook.select()
        if not selected_path:
            return

        if self._prev_selected_path == selected_path:
            return
        self._prev_selected_path = selected_path

        active_tab_id = None
        for tid, widget in self.tab_system.map.items():
            if str(widget) == selected_path:
                active_tab_id = tid
                break

        if not active_tab_id:
            return

        getattr(self.tab_system, active_tab_id)
        self._handle_tab_refresh(active_tab_id)

    def _on_data_invalidated(self, _data=None):
        self.refresh_all_tabs()

    def _on_data_changed(self, _data=None):
        self.refresh_all_tabs()

    def _handle_tab_refresh(self, active_tab_id):
        """Runs only the refresh logic needed for the currently active tab."""
        if active_tab_id == "dashboard":
            self.overview_ctrl.refresh_dashboard()
            return

        if active_tab_id == "overview":
            snapshot = self._build_overview_refresh_snapshot()
            if self._should_refresh_overview(snapshot):
                self.overview_ctrl.refresh_list()
                self._remember_overview_refresh(snapshot)
            return

        if active_tab_id == "batch":
            self.batch_ctrl.update_flow()
            return

        if active_tab_id == "details":
            self.details_ctrl.refresh_titles()
            return

        if active_tab_id == "release":
            self.release_ctrl.refresh_view()

    def refresh_all_tabs(self):
        """Standardized orchestrator to update all modular components."""
        overview_snapshot = self._build_overview_refresh_snapshot()

        self.overview_ctrl.refresh_list()
        self.overview_ctrl.refresh_dashboard()
        self.details_ctrl.refresh_view()
        self.batch_ctrl.reload_flow_data()
        self.release_ctrl.refresh_view()
        cover_tab = getattr(getattr(self, "tab_system", None), "_instances", {}).get("cover")
        if cover_tab is not None and hasattr(cover_tab, "refresh_view"):
            cover_tab.refresh_view()
        self._last_overview_refresh.update(overview_snapshot)

    def on_closing(self):
        """Asks for confirmation before exiting."""
        res = messagebox.askyesnocancel(
            i18n._t("msg_beenden"), 
            i18n._t("msg_beenden_confirm"),
            icon='warning',
            default='yes'
        )
        if res is True:
            if self.save_project():
                self.destroy()
        elif res is False:
            self.destroy()

    def _on_quit_shortcut(self, _event=None):
        self.on_closing()
        return "break"

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
                self.task_indicator.config(text=i18n._t("task_active"), fg=ui_patterns.ACCENT)
                self.task_indicator.start()
                if hasattr(self, "header") and hasattr(self.header, "task_state_label"):
                    self.header.task_state_label.config(text=i18n._t("task_busy_text"))
                if hasattr(self, "header") and hasattr(self.header, "task_detail_label"):
                    self.header.task_detail_label.config(text="Import, Analyse oder Export arbeitet gerade.")
            else: 
                self.task_indicator.config(text=i18n._t("task_ready"), fg="#94A3B8")
                self.task_indicator.stop()
                if hasattr(self, "header") and hasattr(self.header, "task_state_label"):
                    self.header.task_state_label.config(text=i18n._t("task_idle_text"))
                if hasattr(self, "header") and hasattr(self.header, "task_detail_label"):
                    dnd_text = self._get_drag_and_drop_status_text()
                    self.header.task_detail_label.config(text=f"Keine Hintergrundjobs aktiv | Drag & Drop: {dnd_text}")

    def status_text(self, status): 
        """Translated status text helper."""
        return i18n.get_status_chip_text(status)

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
