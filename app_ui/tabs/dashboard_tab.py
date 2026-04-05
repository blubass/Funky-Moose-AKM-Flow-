import tkinter as tk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, 
    ACCENT, PANEL, PANEL_2, SUBTLE, SPACE_MD, SPACE_SM, SPACE_XS, 
    CARD_PAD_X, CARD_PAD_Y, FONT_BOLD, FONT_SM, FONT_XXL
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

        # Status Chips
        chip_row = AkmPanel(self)
        chip_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        
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

        for index, (key, label) in enumerate(stats):
            card = AkmCard(stats_grid, padx=CARD_PAD_X - 4, pady=CARD_PAD_Y - 6)
            row, col = index // 4, index % 4
            card.grid(row=row, column=col, padx=SPACE_XS, pady=SPACE_XS, sticky="nsew")
            stats_grid.grid_columnconfigure(col, weight=1)

            AkmSubLabel(card, text=label, bg=PANEL_2).pack(anchor="w", padx=SPACE_SM, pady=(SPACE_SM, 0))
            v_l = AkmLabel(card, text="0", fg=ACCENT, bg=PANEL_2, font=FONT_XXL)
            v_l.pack(anchor="w", padx=SPACE_SM, pady=(2, SPACE_SM))
            self.app.dashboard_labels[key] = v_l

        # Actions
        actions = AkmPanel(self)
        actions.pack(anchor="w", padx=SPACE_MD, pady=SPACE_SM)
        
        self.app.btn(actions, "Aktualisieren", self.app.refresh_dashboard, quiet=True).pack(
            side="left", padx=(0, SPACE_XS)
        )
        self.app.btn(
            actions,
            "Letztes offenes Werk",
            self.app.jump_to_last_open,
        ).pack(
            side="left", padx=SPACE_XS
        )
        self.app.btn(
            actions,
            "Lautheit öffnen",
            self.app.open_loudness_tab,
            primary=True,
        ).pack(side="left", padx=SPACE_XS)
