import tkinter as tk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmText,
    ACCENT, PANEL, PANEL_2, SUBTLE, SPACE_MD, SPACE_SM, SPACE_XS, 
    CARD_PAD_X, CARD_PAD_Y, FONT_LG, FONT_MD, FONT_XL, LOG_BG, LOG_FG, FONT_LOG
)
from app_logic import assistant_tools

class AssistantTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        AkmHeader(self, text="AKM Schnellstart").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Neue Werke anlegen, Status setzen und Excel-Import direkt aus dem schnellen Eingabebereich starten.", wraplength=720, justify="left").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        intake_card = AkmCard(self)
        intake_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(intake_card, text="Titel eingeben", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        AkmSubLabel(intake_card, text="Hier startet der schnelle Workflow fuer neue Werke oder direkte Statuswechsel.", bg=PANEL_2).pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.app.entry = AkmEntry(intake_card, width=50, font=FONT_MD)
        self.app.entry.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM), ipady=5)

        btn_row = AkmPanel(intake_card, bg=PANEL_2)
        btn_row.pack(padx=CARD_PAD_X, pady=(0, SPACE_XS), anchor="w")
        self.app.btn(btn_row, "Werk anlegen", self.app.add, primary=True).pack(side="left", padx=(0, SPACE_XS))
        for label, status in assistant_tools.ASSISTANT_STATUS_ACTIONS:
            self.app.btn(btn_row, label, lambda v=status: self.app.set_status(v)).pack(side="left", padx=SPACE_XS)

        imp_row = AkmPanel(intake_card, bg=PANEL_2)
        imp_row.pack(padx=CARD_PAD_X, pady=(0, CARD_PAD_Y), anchor="w")
        self.app.btn(imp_row, "Excel importieren", self.app.import_excel, quiet=True).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(imp_row, "Lautheit", self.app.open_loudness_tab).pack(side="left", padx=SPACE_SM)

        log_card = AkmCard(self)
        log_card.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(log_card, text="AKM Log", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        
        self.app.log = AkmText(log_card, height=10, bg=LOG_BG, fg=LOG_FG, insertbackground=LOG_FG)
        self.app.log.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
