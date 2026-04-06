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
    """Orchestrates all functional modules within the central Tkinter Notebook."""
    def __init__(self, parent, app):
        self.app = app
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        # Registry for frames
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

        for tid, frame in self.map.items():
            self.notebook.add(frame, text=tid.capitalize())

        # Logic Injection
        self.dashboard = DashboardTab(self.map["dashboard"], self.app)
        self.assistant = AssistantTab(self.map["assistant"], self.app)
        self.batch     = BatchTab(self.map["batch"], self.app)
        self.overview  = OverviewTab(self.map["overview"], self.app)
        self.details   = DetailsTab(self.map["details"], self.app)
        self.cover     = CoverTab(self.map["cover"], self.app)
        self.release   = ReleaseTab(self.map["release"], self.app)
        self.loudness  = LoudnessTab(self.map["loudness"], self.app)

    def select(self, tab_id):
        """Switches visibility to the specified tab id."""
        if tab_id in self.map:
            self.notebook.select(self.map[tab_id])
