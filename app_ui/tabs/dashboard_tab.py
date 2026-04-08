import tkinter as tk
from app_ui import ui_patterns
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmSuccessIndicator,
    ACCENT, PANEL_2, SPACE_MD, SPACE_SM, SPACE_XS,
    CARD_PAD_X, CARD_PAD_Y, FONT_BOLD, FONT_MD_BOLD, FONT_SM, FONT_LG, FONT_XXL
)

class DashboardTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        AkmHeader(
            self,
            text="Dashboard",
        ).pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))

        AkmSubLabel(
            self,
            text="Schneller Blick auf Status, Vollständigkeit und den aktuellen Arbeitsstand.",
        ).pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(self, height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Operations Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.app.dashboard_status_label = AkmLabel(
            status_left,
            text="Noch keine Werke im Katalog",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
        )
        self.app.dashboard_status_label.pack(fill="x", pady=(2, 2))
        self.app.dashboard_hint_label = AkmSubLabel(
            status_left,
            text="Importiere ein Werk oder lege direkt einen neuen Titel an, um loszulegen.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.app.dashboard_hint_label.pack(fill="x")
        self.app.dashboard_meta_label = AkmSubLabel(
            status_left,
            text="Mit Produktion: 0   •   Mit Notizen: 0   •   Instrumental: 0",
            bg=PANEL_2,
            anchor="w",
        )
        self.app.dashboard_meta_label.pack(fill="x", pady=(2, 0))

        self.app.btn(status_right, "Dashboard aktualisieren", self.app.refresh_dashboard, primary=True, width=186).pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(status_right, bg=PANEL_2)
        action_row.pack(anchor="e")
        self.app.btn(action_row, "Letztes offenes Werk", self.app.jump_to_last_open, quiet=True, width=150).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(action_row, "Loudness", self.app.open_loudness_tab, quiet=True, width=92).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(action_row, "Speichern", self.app.save_project, quiet=True, width=96).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(action_row, "Laden", self.app.load_project_dialog, quiet=True, width=84).pack(side="left")

        # Status Chips
        chip_row = AkmPanel(self)
        chip_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmSubLabel(
            chip_row,
            text="Statuschips springen direkt in die gefilterte Übersicht.",
        ).pack(side="left", padx=(0, SPACE_SM))
        
        for status in ["open", "in_progress", "ready", "submitted", "confirmed"]:
            chip = tk.Label(
                chip_row,
                text="",
                font=FONT_BOLD,
                padx=12,
                pady=5,
                bd=1,
                relief="solid",
                cursor="hand2",
            )
            chip.pack(side="left", padx=(0, SPACE_XS))
            chip.bind(
                "<Button-1>",
                lambda _event, value=status: self.app._open_overview_with_filter(value),
            )
            self.app.dashboard_status_chips[status] = chip

        # Stats Grid
        stats_grid = AkmPanel(self)
        stats_grid.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        stats = [
            ("total", "Gesamt"),
            ("open", "Offen"),
            ("ready", "Bereit"),
            ("submitted", "Gemeldet"),
            ("confirmed", "Bestätigt"),
            ("instrumental", "Instrumental"),
            ("with_production", "Mit Produktion"),
            ("with_notes", "Mit Notizen"),
        ]

        for i, (key, label) in enumerate(stats):
            card = AkmCard(stats_grid)
            card.grid(row=i // 4, column=i % 4, sticky="nsew", padx=5, pady=5)
            stats_grid.columnconfigure(i % 4, weight=1)
            
            # Label
            header = tk.Frame(card.inner, bg=ui_patterns.PANEL_2)
            header.pack(fill="x", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 0))
            AkmSubLabel(header, text=label, bg=ui_patterns.PANEL_2).pack(side="left")
            
            if key in ["submitted", "confirmed"]:
                AkmSuccessIndicator(header, bg=ui_patterns.PANEL_2).pack(side="right")
            
            # Value
            val = tk.Label(card.inner, text="0", fg=ui_patterns.ACCENT, bg=ui_patterns.PANEL_2, font=FONT_XXL)
            val.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
            self.app.dashboard_labels[key] = val
