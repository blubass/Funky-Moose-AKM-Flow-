"""
Funky Moose Release Forge - Main Application Orchestrator
Modular, State-Driven, and Industrial-Themed Backend Manager for Music Release Workflows.
"""

import copy
import os
import sys
import time
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox, ttk

# Optional: DnD Support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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

# UI Components (Tabs)
from app_ui.tabs.dashboard_tab import DashboardTab
from app_ui.tabs.assistant_tab import AssistantTab
from app_ui.tabs.batch_tab import BatchTab
from app_ui.tabs.overview_tab import OverviewTab
from app_ui.tabs.details_tab import DetailsTab
from app_ui.tabs.cover_tab import CoverTab
from app_ui.tabs.release_tab import ReleaseTab
from app_ui.tabs.loudness_tab import LoudnessTab

# Controllers
from app_controllers.project_controller import ProjectController
from app_controllers.overview_controller import OverviewController
from app_controllers.loudness_controller import LoudnessController
from app_controllers.release_controller import ReleaseController
from app_controllers.batch_controller import BatchController
from app_controllers.details_controller import DetailsController

# Design Tokens & Themed Widgets
from app_ui.ui_patterns import (
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    FONT_SM, FONT_MD, FONT_BOLD, FONT_MD_BOLD, FONT_LG, FONT_XXXL,
    PulseLabel, AkmPanel, AkmLabel, AkmSubLabel, AkmToast
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
        
        # --- GLOBAL MOUSEWHEEL FIX ---
        self.bind_all("<MouseWheel>", self._on_root_mousewheel)
        self.bind_all("<Button-4>", self._on_root_mousewheel)
        self.bind_all("<Button-5>", self._on_root_mousewheel)
        
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
        print("[2026] GUI MASTER START: Sichtbar auf Host.")

    # --- INITIALIZATION ---
    def _set_window_config(self):
        """Standard window initialization and styling."""
        self.title("Funky Moose Release Forge")
        self.geometry("1000x820")
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
        
        self._build_header(self.content_root)
        self._build_tab_system(self.content_root)

    def _build_header(self, parent):
        """Assembles the high-fidelity 2026 branding header area."""
        header_frame = tk.Frame(parent, bg=ui_patterns.BG)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        # --- THE INLAY (Inset Effect) ---
        inlay_bg = "#070708" 
        self.header_inner = tk.Frame(header_frame, bg=inlay_bg, height=80)
        self.header_inner.pack(fill="both", expand=True, padx=0, pady=(0, 1))
        tk.Frame(header_frame, bg="#1E1E22", height=1).pack(fill="x") # Subtle light-catch edge
        
        # Logo & Brand Container
        brand_container = tk.Frame(self.header_inner, bg=inlay_bg)
        brand_container.pack(side="left", padx=SPACE_XL, pady=SPACE_MD)
        
        # Logo Loading (Premium 2026 Design)
        self.logo_img = None
        logo_path = resource_path("assets/logo.png")
        try:
            from PIL import Image, ImageTk
            import os
            if os.path.exists(logo_path):
                with Image.open(logo_path) as img:
                    img = img.resize((48, 48), Image.Resampling.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(img)
                    tk.Label(brand_container, image=self.logo_img, bg=inlay_bg).pack(side="left", padx=(0, SPACE_MD))
            else:
                self.append_log("System: Branding Logo im Bundle nicht gefunden.")
        except Exception as e:
            self.append_log(f"System: Logo-Initialisierung fehlgeschlagen ({str(e)})")
        
        # Initial Boot Sequence
        self.append_log("-" * 30)
        self.append_log("OBSIDIAN MASTER v1.0.0 BOOTING")
        self.append_log("Status: Version 1.0.0 stabilisiert.")
        self.after(500, lambda: self.append_log("Status: Slate-Steel Palette geladen."))
        self.after(1000, lambda: self.append_log("Status: System bereit für Produktion."))
        self.append_log("-" * 30)
        
        # Dashboard Label (Version Tag)
        tk.Label(brand_container, text="OBSIDIAN MASTER v1.0.0", bg=inlay_bg, fg=ui_patterns.ACCENT, font=FONT_ITALIC).pack(side="top", anchor="w")
        
        # Dual-Color Title (Full Branding)
        tk.Label(brand_container, text="FUNKY MOOSE", bg=inlay_bg, fg=ui_patterns.ACCENT, font=FONT_XXXL).pack(side="left")
        tk.Label(brand_container, text="RELEASE", bg=inlay_bg, fg="#94A3B8", font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))
        tk.Label(brand_container, text="FORGE", bg=inlay_bg, fg="#D1D5DB", font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))

        # Right-side controls
        right_frame = tk.Frame(self.header_inner, bg=inlay_bg)
        right_frame.pack(side="right", padx=SPACE_XL)
        
        # Project Controls (Massive 3D Orange)
        self.btn(right_frame, "PROJEKT SPEICHERN", self.save_project).pack(side="right", padx=SPACE_MD)
        self.btn(right_frame, "PROJEKT LADEN", self.load_project_dialog).pack(side="right")

        # Activity Pulsing
        self.task_indicator = PulseLabel(right_frame, text="TASK AKTIV", fg=ui_patterns.ACCENT, 
                                          font=FONT_BOLD, padx=12, pady=6)
        self.task_indicator.pack(side="right")
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
        self.dashboard_tab = DashboardTab(self.tab_map["dashboard"], self)
        self.assistant_tab = AssistantTab(self.tab_map["assistant"], self)
        self.batch_tab = BatchTab(self.tab_map["batch"], self)
        self.overview_tab = OverviewTab(self.tab_map["overview"], self)
        self.details_tab = DetailsTab(self.tab_map["details"], self)
        self.cover_tab = CoverTab(self.tab_map["cover"], self)
        self.release_tab = ReleaseTab(self.tab_map["release"], self)
        self.loudness_tab = LoudnessTab(self.tab_map["loudness"], self)

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
        if selected == str(self.tab_map["dashboard"]):
            self.refresh_dashboard()
        elif selected == str(self.tab_map["overview"]):
            self.refresh_list()
        elif selected == str(self.tab_map["batch"]):
            self.update_flow()
    def refresh_all_tabs(self):
        """Standardized orchestrator to update all modular components after a state change."""
        self.overview_ctrl.refresh_list()
        self.overview_ctrl.refresh_dashboard()
        self.batch_ctrl.reload_flow_data()
        self.release_ctrl.refresh_view()

    # --- SHARED DELEGATES (Called by Tabs) ---
    def refresh_list(self): 
        self.overview_ctrl.refresh_list()
        
    def refresh_dashboard(self): 
        self.overview_ctrl.refresh_dashboard()
        
    def reload_flow_data(self, preferred_index=None): 
        self.batch_ctrl.reload_flow_data(preferred_index)
        
    def update_flow(self): 
        self.batch_ctrl.update_flow()
        
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

    # --- UTILITIES ---
    def btn(self, parent, text, cmd, primary=False, quiet=False, width=None, accent_color=None): 
        """Wrapper for the centralized design-system button creator."""
        return ui_patterns.create_btn(parent, text, cmd, primary=primary, quiet=quiet, width=width, accent_color=accent_color)

    def append_log(self, message): 
        """Safely appends activity to the global log and prints to console for redundancy."""
        msg_str = f"[{time.strftime('%H:%M:%S')}] {message}"
        print(msg_str)
        if hasattr(self, 'log'): 
            self.log.insert(tk.END, msg_str + "\n")
            self.log.see(tk.END)

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

    def process_all_loudness(self): 
        self.loudness_ctrl.process_all()
    
    def process_batch(self): 
        self.batch_ctrl.process_selected_flow()
    
    def open_release_cover_dialog(self): 
        self.release_ctrl.open_cover_dialog()

    def flow_copy(self): 
        self.batch_ctrl.flow_copy()

    def flow_submit(self): 
        self.batch_ctrl.flow_submit()

    def flow_next(self): 
        self.batch_ctrl.flow_next()

    def open_track_in_batch(self, it): 
        self.batch_ctrl.open_track_in_batch(it)

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
        
    def open_release_cover_dialog(self): 
        self.release_ctrl.open_cover_dialog()
        
    def build_distro_export(self): 
        self.release_ctrl.build_export()
        
    def release_move_track_up(self): 
        self.release_ctrl.move_track_up()
        
    def release_move_track_down(self): 
        self.release_ctrl.move_track_down()
        
    def release_remove_track(self): 
        self.release_ctrl.remove_track()

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

if __name__ == "__main__":
    app = AKMApp()
    app.mainloop()
