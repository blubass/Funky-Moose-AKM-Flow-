"""
High-fidelity Header Branding Component for the Funky Moose Release Forge.
"""
import tkinter as tk
import os
from PIL import Image, ImageTk
from app_ui import ui_patterns
from app_ui.ui_patterns import (
    SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
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
        self.inner = tk.Frame(self.header_frame, bg=inlay_bg, height=80)
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
        
        # Dashboard Label (Version Tag)
        tk.Label(brand_container, text="OBSIDIAN MASTER v1.0.0", bg=inlay_bg, fg=ui_patterns.ACCENT, font=FONT_ITALIC).pack(side="top", anchor="w")
        
        # Title Branding
        tk.Label(brand_container, text="FUNKY MOOSE", bg=inlay_bg, fg=ui_patterns.ACCENT, font=FONT_XXXL).pack(side="left")
        tk.Label(brand_container, text="RELEASE", bg=inlay_bg, fg="#94A3B8", font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))
        tk.Label(brand_container, text="FORGE", bg=inlay_bg, fg="#D1D5DB", font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))

        # Right-side controls
        right_frame = tk.Frame(self.inner, bg=inlay_bg)
        right_frame.pack(side="right", padx=SPACE_XL)
        
        # Project Controls
        self.btn(right_frame, "PROJEKT SPEICHERN", self.app.save_project).pack(side="right", padx=SPACE_MD)
        self.btn(right_frame, "PROJEKT LADEN", self.app.load_project_dialog).pack(side="right")

        # Activity Indicator
        self.task_indicator = PulseLabel(right_frame, text="TASK AKTIV", fg=ui_patterns.ACCENT, 
                                          font=FONT_BOLD, padx=12, pady=6)
        self.task_indicator.pack(side="right")
        self.task_indicator.stop()

    def btn(self, parent, text, cmd):
        # We reuse app's btn wrapper but since we want the header separated, we could use ui_patterns directly
        return ui_patterns.create_btn(parent, text, cmd)
