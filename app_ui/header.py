"""
High-fidelity Header Branding Component for the Funky Moose Release Forge.
"""
import tkinter as tk
import os
from PIL import Image, ImageTk
from app_logic.config import cfg
from app_ui import ui_patterns
from app_ui.ui_patterns import (
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    FONT_BOLD, FONT_MD_BOLD, FONT_XXXL, FONT_ITALIC,
    PulseLabel
)

class MainHeader:
    """Assembles the high-fidelity 2026 branding header area."""
    def __init__(self, parent, app):
        self.app = app
        self.header_frame = tk.Frame(parent, bg=ui_patterns.BG)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        
        # --- THE INLAY (Inset Effect) ---
        inlay_bg = "#070708" 
        self.inner = tk.Frame(self.header_frame, bg=inlay_bg, height=92)
        self.inner.pack(fill="both", expand=True, padx=0, pady=(0, 1))
        tk.Frame(self.header_frame, bg="#1E1E22", height=1).pack(fill="x") # Subtle light-catch edge
        
        # Logo & Brand Container
        brand_container = tk.Frame(self.inner, bg=inlay_bg)
        brand_container.pack(side="left", padx=SPACE_XL, pady=SPACE_MD)
        
        # Logo Loading (Premium 2026 Design)
        self.logo_img_obj = None
        logo_path = self.app.resource_path("assets/logo.png")
        try:
            if os.path.exists(logo_path):
                with Image.open(logo_path) as img:
                    img = img.resize((48, 48), Image.Resampling.LANCZOS)
                    self.logo_img_obj = ImageTk.PhotoImage(img)
                    tk.Label(brand_container, image=self.logo_img_obj, bg=inlay_bg).pack(side="left", padx=(0, SPACE_MD))
            else:
                self.app.append_log("System: Branding Logo im Bundle nicht gefunden.")
        except Exception as e:
            self.app.append_log(f"System: Logo-Initialisierung fehlgeschlagen ({str(e)})")
        
        brand_copy = tk.Frame(brand_container, bg=inlay_bg)
        brand_copy.pack(side="left", fill="y")

        tk.Label(
            brand_copy,
            text=f"OBSIDIAN MASTER v{cfg.VERSION}",
            bg=inlay_bg,
            fg=ui_patterns.ACCENT,
            font=FONT_ITALIC,
        ).pack(anchor="w")

        title_row = tk.Frame(brand_copy, bg=inlay_bg)
        title_row.pack(anchor="w")
        tk.Label(title_row, text="FUNKY MOOSE", bg=inlay_bg, fg=ui_patterns.ACCENT, font=FONT_XXXL).pack(side="left")
        tk.Label(title_row, text="RELEASE", bg=inlay_bg, fg="#94A3B8", font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))
        tk.Label(title_row, text="FORGE", bg=inlay_bg, fg="#D1D5DB", font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))
        tk.Label(
            brand_copy,
            text="Werke, Cover, Loudness und Release in einem durchgehenden Produktionsfluss.",
            bg=inlay_bg,
            fg="#9AA3AF",
            font=FONT_MD_BOLD,
        ).pack(anchor="w", pady=(2, 0))

        # Right-side controls
        right_frame = tk.Frame(self.inner, bg=inlay_bg)
        right_frame.pack(side="right", padx=SPACE_XL, pady=SPACE_MD)

        button_row = tk.Frame(right_frame, bg=inlay_bg)
        button_row.pack(anchor="e")
        self.app.btn(button_row, "PROJEKT LADEN", self.app.load_project_dialog, quiet=True, width=148).pack(side="right")
        self.app.btn(button_row, "PROJEKT SPEICHERN", self.app.save_project, primary=True, width=166).pack(side="right", padx=(0, SPACE_SM))

        status_row = tk.Frame(right_frame, bg=inlay_bg)
        status_row.pack(anchor="e", pady=(SPACE_XS, 0))
        status_copy = tk.Frame(status_row, bg=inlay_bg)
        status_copy.pack(side="right", padx=(SPACE_MD, 0))
        self.task_state_label = tk.Label(
            status_copy,
            text="System bereit",
            bg=inlay_bg,
            fg="#D1D5DB",
            font=FONT_MD_BOLD,
            anchor="e",
        )
        self.task_state_label.pack(anchor="e")
        self.task_detail_label = tk.Label(
            status_copy,
            text="Keine Hintergrundjobs aktiv",
            bg=inlay_bg,
            fg="#94A3B8",
            font=FONT_ITALIC,
            anchor="e",
        )
        self.task_detail_label.pack(anchor="e")

        # Activity Indicator
        self.task_indicator = PulseLabel(
            status_row,
            text="SYSTEM BEREIT",
            fg="#94A3B8",
            base_color="#101115",
            pulse_color=ui_patterns.ACCENT,
            font=FONT_BOLD,
            padx=12,
            pady=6,
        )
        self.task_indicator.pack(side="right")
        self.task_indicator.stop()
