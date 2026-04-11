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
        shell_bg = ui_patterns.blend_color(ui_patterns.PANEL_2, ui_patterns.BG, 0.36)
        self.header_frame = tk.Frame(parent, bg=shell_bg)
        self.header_frame.pack(fill="x", padx=0, pady=(0, SPACE_SM))
        tk.Frame(
            self.header_frame,
            bg=ui_patterns.blend_color(shell_bg, "#FFFFFF", 0.08),
            height=1,
        ).pack(fill="x")
        tk.Frame(
            self.header_frame,
            bg=ui_patterns.blend_color(shell_bg, ui_patterns.ACCENT_COOL, 0.22),
            height=1,
        ).pack(fill="x")

        # --- THE INLAY (Inset Effect) ---
        inlay_bg = ui_patterns.blend_color(ui_patterns.PANEL, ui_patterns.BG, 0.16)
        self.inner = tk.Frame(
            self.header_frame,
            bg=inlay_bg,
            height=104,
            highlightthickness=1,
            highlightbackground=ui_patterns.blend_color(ui_patterns.BORDER, "#FFFFFF", 0.10),
        )
        self.inner.pack(fill="both", expand=True, padx=0, pady=0)
        tk.Frame(self.inner, bg=ui_patterns.blend_color(inlay_bg, "#FFFFFF", 0.08), height=1).pack(fill="x", side="top")
        tk.Frame(self.inner, bg=ui_patterns.blend_color(inlay_bg, ui_patterns.ACCENT_COOL, 0.12), height=1).pack(fill="x", side="top")
        tk.Frame(self.header_frame, bg=ui_patterns.blend_color(inlay_bg, ui_patterns.ACCENT, 0.20), height=1).pack(fill="x")
        tk.Frame(self.header_frame, bg=ui_patterns.blend_color(inlay_bg, ui_patterns.BG, 0.52), height=5).pack(fill="x")
        
        # Logo & Brand Container
        brand_container = tk.Frame(self.inner, bg=inlay_bg)
        brand_container.pack(side="left", padx=SPACE_XL, pady=SPACE_MD)
        tk.Frame(brand_container, bg=ui_patterns.ACCENT, width=3, height=54).pack(side="left", padx=(0, SPACE_MD))
        tk.Frame(brand_container, bg=ui_patterns.ACCENT_COOL, width=1, height=54).pack(side="left", padx=(0, SPACE_MD))
        
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
            text=f"FORGE CONTROL ROOM  •  v{cfg.VERSION}",
            bg=inlay_bg,
            fg="#A3AFBF",
            font=FONT_ITALIC,
        ).pack(anchor="w")

        title_row = tk.Frame(brand_copy, bg=inlay_bg)
        title_row.pack(anchor="w")
        tk.Label(title_row, text="FUNKY MOOSE", bg=inlay_bg, fg=ui_patterns.ACCENT, font=FONT_XXXL).pack(side="left")
        tk.Label(title_row, text="RELEASE", bg=inlay_bg, fg=ui_patterns.ACCENT_COOL_GLOW, font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))
        tk.Label(title_row, text="FORGE", bg=inlay_bg, fg="#E2E8F0", font=FONT_XXXL).pack(side="left", padx=(SPACE_SM, 0))
        tk.Label(
            brand_copy,
            text="Werke, Cover, Loudness und Release in einem durchgehenden Produktionsfluss.",
            bg=inlay_bg,
            fg="#9AA6B5",
            font=FONT_MD_BOLD,
        ).pack(anchor="w", pady=(2, 0))
        telemetry_row = tk.Frame(brand_copy, bg=inlay_bg)
        telemetry_row.pack(anchor="w", pady=(SPACE_XS, 0))
        telemetry_specs = [
            ("GRID LIVE", ui_patterns.ACCENT_COOL),
            ("SYNC LOCKED", ui_patterns.ACCENT),
            ("AUDIO BUS", ui_patterns.ACCENT_COOL_GLOW),
        ]
        for index, (label, color) in enumerate(telemetry_specs):
            tk.Label(
                telemetry_row,
                text=label,
                bg=ui_patterns.blend_color(inlay_bg, color, 0.10),
                fg=ui_patterns.blend_color(color, "#FFFFFF", 0.18),
                font=FONT_BOLD,
                padx=10,
                pady=3,
                highlightthickness=1,
                highlightbackground=ui_patterns.blend_color(color, "#FFFFFF", 0.12),
            ).pack(side="left", padx=(0, SPACE_XS if index < len(telemetry_specs) - 1 else 0))

        # Right-side controls
        right_frame = tk.Frame(self.inner, bg=inlay_bg)
        right_frame.pack(side="right", padx=SPACE_XL, pady=SPACE_MD)

        tk.Label(
            right_frame,
            text=cfg.APP_NAME,
            bg=inlay_bg,
            fg=ui_patterns.ACCENT_COOL_GLOW,
            font=FONT_ITALIC,
        ).pack(anchor="e", pady=(0, SPACE_XS))

        button_row = tk.Frame(right_frame, bg=inlay_bg)
        button_row.pack(anchor="e")
        self.app.btn(button_row, "PROJEKT LADEN", self.app.load_project_dialog, quiet=True, width=148).pack(side="right")
        self.app.btn(button_row, "PROJEKT SPEICHERN", self.app.save_project, primary=True, width=166).pack(side="right", padx=(0, SPACE_SM))

        status_shell = tk.Frame(
            right_frame,
            bg=ui_patterns.blend_color(inlay_bg, ui_patterns.METAL_LOW, 0.34),
            highlightthickness=1,
            highlightbackground=ui_patterns.blend_color(ui_patterns.BORDER, "#FFFFFF", 0.10),
            padx=12,
            pady=8,
        )
        status_shell.pack(anchor="e", pady=(SPACE_XS, 0))
        tk.Frame(status_shell, bg=ui_patterns.blend_color(status_shell["bg"], ui_patterns.ACCENT_COOL, 0.26), height=1).pack(fill="x", pady=(0, 6))

        status_row = tk.Frame(status_shell, bg=status_shell["bg"])
        status_row.pack(anchor="e")
        status_copy = tk.Frame(status_row, bg=status_shell["bg"])
        status_copy.pack(side="right", padx=(SPACE_MD, 0))
        self.task_state_label = tk.Label(
            status_copy,
            text="System bereit",
            bg=status_shell["bg"],
            fg="#E2E8F0",
            font=FONT_MD_BOLD,
            anchor="e",
        )
        self.task_state_label.pack(anchor="e")
        self.task_detail_label = tk.Label(
            status_copy,
            text="Keine Hintergrundjobs aktiv",
            bg=status_shell["bg"],
            fg="#94A3B8",
            font=FONT_ITALIC,
            anchor="e",
        )
        self.task_detail_label.pack(anchor="e")

        # Activity Indicator
        self.task_indicator = PulseLabel(
            status_row,
            text="SYSTEM BEREIT",
            fg=ui_patterns.ACCENT_COOL_GLOW,
            base_color=ui_patterns.blend_color(status_shell["bg"], ui_patterns.BG, 0.12),
            pulse_color=ui_patterns.ACCENT_COOL,
            font=FONT_BOLD,
            padx=12,
            pady=6,
        )
        self.task_indicator.pack(side="right")
        self.task_indicator.stop()
