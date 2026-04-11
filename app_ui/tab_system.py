"""
Modular Tab Orchestration for the Funky Moose Release Forge.
"""
import tkinter as tk
import time
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
        shell = tk.Frame(parent, bg=ui_patterns.blend_color(ui_patterns.PANEL, ui_patterns.BG, 0.18))
        shell.pack(fill="both", expand=True)
        tk.Frame(shell, bg=ui_patterns.blend_color(ui_patterns.PANEL, "#FFFFFF", 0.08), height=1).pack(fill="x")
        tk.Frame(shell, bg=ui_patterns.blend_color(ui_patterns.PANEL, ui_patterns.ACCENT_COOL, 0.16), height=1).pack(fill="x")
        tk.Frame(shell, bg=ui_patterns.blend_color(ui_patterns.ACCENT, ui_patterns.PANEL, 0.72), height=1).pack(fill="x")

        stage = tk.Frame(
            shell,
            bg=ui_patterns.blend_color(ui_patterns.PANEL_2, ui_patterns.BG, 0.12),
            highlightthickness=1,
            highlightbackground=ui_patterns.blend_color(ui_patterns.BORDER, "#FFFFFF", 0.10),
            padx=3,
            pady=3,
        )
        stage.pack(fill="both", expand=True, pady=(0, 8))

        notebook_stage = tk.Frame(stage, bg=ui_patterns.PANEL)
        notebook_stage.pack(fill="both", expand=True)
        tk.Frame(notebook_stage, bg=ui_patterns.blend_color(ui_patterns.PANEL, "#FFFFFF", 0.05), height=1).pack(fill="x")
        tk.Frame(notebook_stage, bg=ui_patterns.blend_color(ui_patterns.PANEL, ui_patterns.ACCENT_COOL, 0.12), height=1).pack(fill="x")

        hud_bar = tk.Frame(
            notebook_stage,
            bg=ui_patterns.blend_color(ui_patterns.PANEL, ui_patterns.METAL_LOW, 0.18),
            padx=12,
            pady=8,
            highlightthickness=1,
            highlightbackground=ui_patterns.blend_color(ui_patterns.BORDER, "#FFFFFF", 0.06),
        )
        hud_bar.pack(fill="x", padx=8, pady=(8, 6))
        tk.Label(
            hud_bar,
            text="GRID ACTIVE",
            bg=hud_bar["bg"],
            fg=ui_patterns.ACCENT_COOL_GLOW,
            font=ui_patterns.FONT_BOLD,
        ).pack(side="left")
        tk.Label(
            hud_bar,
            text="FORGE BUS 01",
            bg=hud_bar["bg"],
            fg=ui_patterns.blend_color(ui_patterns.ACCENT, "#FFFFFF", 0.18),
            font=ui_patterns.FONT_BOLD,
        ).pack(side="right")

        self.notebook = ttk.Notebook(notebook_stage)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        tk.Frame(shell, bg=ui_patterns.blend_color(ui_patterns.PANEL, ui_patterns.BG, 0.60), height=6).pack(fill="x")

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
        self.build_metrics = {}
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

        TAB_LABELS = {
            "dashboard": "Dashboard",
            "assistant": "Schnellstart",
            "batch":     "Batch",
            "overview":  "Katalog",
            "details":   "Details",
            "cover":     "Cover",
            "release":   "Release",
            "loudness":  "Lautheit",
        }

        # Initial notebook population (empty frames)
        for tid, frame in self.map.items():
            self.notebook.add(frame, text=TAB_LABELS.get(tid, tid.capitalize()))

            
        # Internal Lazy-Build Trigger
        self.notebook.bind("<<NotebookTabChanged>>", self._on_internal_tab_change)
        self._preload_job = None
        self._preload_reported = False

    def _on_internal_tab_change(self, event=None):
        """Ensures the selected tab is built when the user clicks it or it's changed programmatically."""
        try:
            selected = self.notebook.select()
            if not selected: return
            
            for tid, widget in self.map.items():
                if str(widget) == selected:
                    # Triggers __getattr__ to build the tab
                    getattr(self, tid)
                    break
        except Exception:
            pass

    def __getattr__(self, name):
        """Builds tab content on-demand when accessed (e.g., self.tab_system.dashboard)."""
        if name in self._classes:
            if name not in self._instances:
                # First Access: Create the heavy UI content
                cls = self._classes[name]
                frame = self.map[name]
                # Inject logic
                start = time.perf_counter()
                self._instances[name] = cls(frame, self.app)
                self.build_metrics[name] = round((time.perf_counter() - start) * 1000, 1)
            return self._instances[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def select(self, tab_id):
        """Switches visibility to the specified tab id."""
        if tab_id in self.map:
            self.notebook.select(self.map[tab_id])
            # getattr(self, tab_id) is now handled by <<NotebookTabChanged>>

    def preload(self, tab_ids=None, delay_ms=120):
        """Warm tabs incrementally in idle time so the first click feels immediate."""
        if self._preload_job is not None:
            try:
                self.notebook.after_cancel(self._preload_job)
            except Exception:
                pass
            self._preload_job = None
        pending = []
        for tab_id in (tab_ids or self._classes.keys()):
            if tab_id in self._classes and tab_id not in self._instances:
                pending.append(tab_id)
        if not pending:
            return

        def _step(index=0):
            if index >= len(pending):
                self._preload_job = None
                if not self._preload_reported and self.build_metrics and hasattr(self.app, "append_log"):
                    metrics = ", ".join(
                        f"{tab} {duration:.0f}ms"
                        for tab, duration in sorted(self.build_metrics.items(), key=lambda item: item[1], reverse=True)
                    )
                    self.app.append_log(f"Tab warmup: {metrics}")
                    self._preload_reported = True
                return
            getattr(self, pending[index])
            self._preload_job = self.notebook.after(delay_ms, lambda: _step(index + 1))

        self._preload_job = self.notebook.after_idle(_step)
