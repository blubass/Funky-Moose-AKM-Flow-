"""
Modular Tab Orchestration for the Funky Moose Release Forge.
"""
import tkinter as tk
from tkinter import ttk
from app_ui import ui_patterns
from app_ui.ui_patterns import SPACE_LG

# Tab Content Modules
from app_ui.tabs.dashboard_tab import DashboardTab
from app_ui.tabs.assistant_tab import AssistantTab
from app_ui.tabs.batch_tab import BatchTab
from app_ui.tabs.overview_tab import OverviewTab
from app_ui.tabs.details_tab import DetailsTab
from app_ui.tabs.cover_tab import CoverTab
from app_ui.tabs.release_tab import ReleaseTab
from app_ui.tabs.loudness_tab import LoudnessTab

class AppTabs:
    """Orchestrates all functional modules within the central Tkinter Notebook.
    Uses lazy loading to initialize tab objects only when they are first accessed.
    """
    def __init__(self, parent, app):
        self.app = app
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        # Registry for tab frames (placeholders)
        self.map = {
            "dashboard": tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "assistant": tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "batch":     tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "overview":  tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "details":   tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "cover":     tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "release":   tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG),
            "loudness":  tk.Frame(self.notebook, bg=ui_patterns.BG, padx=SPACE_LG, pady=SPACE_LG)
        }

        # Lazy instantiation storage
        self._instances = {}
        self._classes = {
            "dashboard": DashboardTab,
            "assistant": AssistantTab,
            "batch":     BatchTab,
            "overview":  OverviewTab,
            "details":   DetailsTab,
            "cover":     CoverTab,
            "release":   ReleaseTab,
            "loudness":  LoudnessTab
        }

        # Initial notebook population (empty frames)
        for tid, frame in self.map.items():
            self.notebook.add(frame, text=tid.capitalize())

    def __getattr__(self, name):
        """Builds tab content on-demand when accessed (e.g., self.tab_system.dashboard)."""
        if name in self._classes:
            if name not in self._instances:
                # First Access: Create the heavy UI content
                cls = self._classes[name]
                frame = self.map[name]
                # Inject logic
                self._instances[name] = cls(frame, self.app)
            return self._instances[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def select(self, tab_id):
        """Switches visibility to the specified tab id."""
        if tab_id in self.map:
            self.notebook.select(self.map[tab_id])
            # Ensure it's built if we select it manually
            getattr(self, tab_id)
