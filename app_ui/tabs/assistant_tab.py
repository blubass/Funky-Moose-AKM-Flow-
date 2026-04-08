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
        self._setup_entry_trace()
        self._update_assistant_radar()

    def build_ui(self):
        AkmHeader(self, text="AKM Schnellstart").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Neue Werke anlegen, Status setzen und Excel-Import direkt aus dem schnellen Eingabebereich starten.", wraplength=720, justify="left").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(self, height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Quick Launch Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.app.assistant_status_label = AkmLabel(
            status_left,
            text="Schnellstart bereit",
            bg=PANEL_2,
            anchor="w",
            font=FONT_LG,
        )
        self.app.assistant_status_label.pack(fill="x", pady=(2, 2))
        self.app.assistant_hint_label = AkmSubLabel(
            status_left,
            text="Gib einen Titel ein, importiere Excel oder nutze die Status-Aktionen mit deiner Auswahl aus der Übersicht.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.app.assistant_hint_label.pack(fill="x")
        self.app.assistant_context_label = AkmSubLabel(
            status_left,
            text="Keine Eingabe aktiv | Excel-Import und Statuswechsel stehen bereit",
            bg=PANEL_2,
            anchor="w",
        )
        self.app.assistant_context_label.pack(fill="x", pady=(2, 0))

        self.app.btn(status_right, "Werk anlegen", lambda: self.app.add(self.app.assistant_entry.get().strip()), primary=True, width=136).pack(anchor="e", pady=(0, SPACE_XS))
        status_actions = tk.Frame(status_right, bg=PANEL_2)
        status_actions.pack(anchor="e")
        self.app.btn(status_actions, "Excel importieren", self.app.import_excel, quiet=True, width=132).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(status_actions, "Lautheit", self.app.open_loudness_tab, quiet=True, width=92).pack(side="left")

        intake_card = AkmCard(self)
        intake_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(intake_card.inner, text="Titel eingeben", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        AkmSubLabel(intake_card.inner, text="Hier startet der schnelle Workflow für neue Werke oder direkte Statuswechsel.", bg=PANEL_2).pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.app.assistant_entry_var = tk.StringVar()
        self.app.assistant_entry = AkmEntry(intake_card.inner, textvariable=self.app.assistant_entry_var, width=50, font=FONT_MD)
        self.app.assistant_entry.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM), ipady=5)
        self.app.assistant_entry.bind("<Return>", lambda _event: self.app.add(self.app.assistant_entry.get().strip()))

        btn_row = AkmPanel(intake_card.inner, bg=PANEL_2)
        btn_row.pack(padx=CARD_PAD_X, pady=(0, SPACE_XS), anchor="w")
        self.app.btn(btn_row, "Werk anlegen", lambda: self.app.add(self.app.assistant_entry.get().strip()), primary=True).pack(side="left", padx=(0, SPACE_XS))
        for label, status in assistant_tools.ASSISTANT_STATUS_ACTIONS:
            self.app.btn(btn_row, label, lambda v=status: self.app.set_status(v)).pack(side="left", padx=SPACE_XS)

        imp_row = AkmPanel(intake_card.inner, bg=PANEL_2)
        imp_row.pack(padx=CARD_PAD_X, pady=(0, CARD_PAD_Y), anchor="w")
        self.app.btn(imp_row, "Excel importieren", self.app.import_excel, quiet=True).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(imp_row, "Lautheit", self.app.open_loudness_tab).pack(side="left", padx=SPACE_SM)

        log_card = AkmCard(self)
        log_card.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(log_card.inner, text="AKM Log", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        AkmSubLabel(
            log_card.inner,
            text="Importe, Speicheraktionen und Hintergrundläufe landen hier als Chronik.",
            bg=PANEL_2,
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        
        self.app.log = AkmText(log_card.inner, height=10, bg=LOG_BG, fg=LOG_FG, insertbackground=LOG_FG)
        self.app.log.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

    def _setup_entry_trace(self):
        if hasattr(self.app, "assistant_entry_var"):
            self.app.assistant_entry_var.trace_add("write", lambda *_args: self._update_assistant_radar())

    def _update_assistant_radar(self):
        if not hasattr(self.app, "assistant_entry"):
            return
        state = assistant_tools.build_assistant_radar_state(self.app.assistant_entry.get())
        self.app.assistant_status_label.config(text=state["status_text"])
        self.app.assistant_hint_label.config(text=state["hint_text"])
        self.app.assistant_context_label.config(text=state["meta_text"])
