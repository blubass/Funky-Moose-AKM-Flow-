import tkinter as tk
from tkinter import ttk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, 
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_XL, FONT_LG, FONT_XXL
)

class BatchTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        AkmHeader(self, text="AKM Batch").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Arbeite fokussiert durch offene Werke: Titel kopieren, Dauer mitnehmen und danach direkt als gemeldet markieren.", wraplength=760, justify="left").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        focus_card = AkmCard(self)
        focus_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(focus_card, text="Aktuelles Werk", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))

        self.app.flow_title = AkmLabel(focus_card, text="—", fg=ACCENT, bg=PANEL_2, font=FONT_XXL)
        self.app.flow_title.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))

        self.app.flow_meta = AkmLabel(focus_card, text="", fg=SUBTLE, bg=PANEL_2, font=FONT_MD, wraplength=620, justify="left")
        self.app.flow_meta.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_MD))

        btn_row = AkmPanel(focus_card, bg=PANEL_2)
        btn_row.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        self.app.copy_button = self.app.btn(btn_row, "Titel kopieren", self.app.flow_copy, primary=True)
        self.app.btn(btn_row, "Als gemeldet", self.app.flow_submit).pack(side="left", padx=SPACE_SM)
        self.app.btn(btn_row, "Weiter", self.app.flow_next, quiet=True).pack(side="left", padx=SPACE_SM)
        self.app.btn(btn_row, "Neu laden", self.app.reload_flow_data, quiet=True).pack(side="left", padx=SPACE_SM)

        self.app.copy_button.pack(side="left", padx=(0, SPACE_XS))

        progress_card = AkmCard(self)
        progress_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(progress_card, text="Fortschritt", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))

        self.app.progress_label = AkmLabel(progress_card, text="0 / 0", fg=TEXT, bg=PANEL_2, font=FONT_BOLD)
        self.app.progress_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))

        self.app.progress = ttk.Progressbar(progress_card, length=420)
        self.app.progress.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
