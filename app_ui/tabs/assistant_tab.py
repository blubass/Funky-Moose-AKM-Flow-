import tkinter as tk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmText, AkmScrollablePanel,
    ACCENT, PANEL, PANEL_2, SUBTLE, SPACE_MD, SPACE_SM, SPACE_XS, 
    CARD_PAD_X, CARD_PAD_Y, FONT_LG, FONT_MD, FONT_XL, LOG_BG, LOG_FG, FONT_LOG, fit_wraplength
)
from app_logic import assistant_tools

class AssistantTab(AkmPanel):
    ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._status_action_mode = None
        self._quick_action_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_entry_trace()
        self._update_assistant_radar()

    def build_ui(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        page = scroll_root.scrollable_frame

        AkmHeader(page, text="AKM Schnellstart").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text="Neue Werke anlegen, Status setzen und Excel-Import direkt aus dem schnellen Eingabebereich starten.",
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(page, min_height=118)
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

        self._create_button = self.app.btn(status_right, "Werk anlegen", lambda: self.app.add(self.app.assistant_entry.get().strip()), primary=True, width=136)
        self._create_button.pack(anchor="e", pady=(0, SPACE_XS))
        status_actions = tk.Frame(status_right, bg=PANEL_2)
        status_actions.pack(anchor="e")
        self._status_action_bar = status_actions
        self._status_action_buttons = (
            self.app.btn(status_actions, "Excel importieren", self.app.import_excel, quiet=True, width=132),
            self.app.btn(status_actions, "Lautheit", self.app.open_loudness_tab, quiet=True, width=92),
        )

        intake_card = AkmCard(page)
        intake_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(intake_card.inner, text="Titel eingeben", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        self._intake_intro_label = AkmSubLabel(
            intake_card.inner,
            text="Hier startet der schnelle Workflow für neue Werke oder direkte Statuswechsel.",
            bg=PANEL_2,
            justify="left",
        )
        self._intake_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.app.assistant_entry_var = tk.StringVar()
        self.app.assistant_entry = AkmEntry(intake_card.inner, textvariable=self.app.assistant_entry_var, width=50, font=FONT_MD)
        self.app.assistant_entry.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM), ipady=5)
        self.app.assistant_entry.bind("<Return>", lambda _event: self.app.add(self.app.assistant_entry.get().strip()))

        btn_row = AkmPanel(intake_card.inner, bg=PANEL_2)
        btn_row.pack(padx=CARD_PAD_X, pady=(0, SPACE_XS), anchor="w")
        self._quick_action_bar = btn_row
        self._quick_action_buttons = [
            self.app.btn(btn_row, "Werk anlegen", lambda: self.app.add(self.app.assistant_entry.get().strip()), primary=True)
        ]
        for label, status in assistant_tools.ASSISTANT_STATUS_ACTIONS:
            self._quick_action_buttons.append(self.app.btn(btn_row, label, lambda v=status: self.app.set_status(v)))

        imp_row = AkmPanel(intake_card.inner, bg=PANEL_2)
        imp_row.pack(padx=CARD_PAD_X, pady=(0, CARD_PAD_Y), anchor="w")
        self._import_action_bar = imp_row
        self._import_action_buttons = (
            self.app.btn(imp_row, "Excel importieren", self.app.import_excel, quiet=True),
            self.app.btn(imp_row, "Lautheit", self.app.open_loudness_tab),
        )

        log_card = AkmCard(page)
        log_card.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(log_card.inner, text="AKM Log", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        self._log_intro_label = AkmSubLabel(
            log_card.inner,
            text="Importe, Speicheraktionen und Hintergrundläufe landen hier als Chronik.",
            bg=PANEL_2,
            justify="left",
        )
        self._log_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        
        self.app.log = AkmText(log_card.inner, height=10, bg=LOG_BG, fg=LOG_FG, insertbackground=LOG_FG)
        self.app.log.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_button_bar(self._status_action_bar, self._status_action_buttons, width, "_status_action_mode")
        self._apply_button_bar(self._quick_action_bar, self._quick_action_buttons, width, "_quick_action_mode")
        self._apply_button_bar(self._import_action_bar, self._import_action_buttons, width, "_import_action_mode")
        self._update_wraplengths(width)

    def _apply_button_bar(self, container, buttons, width, state_attr):
        if not hasattr(self, state_attr):
            setattr(self, state_attr, None)
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if getattr(self, state_attr) == target_mode:
            return
        setattr(self, state_attr, target_mode)
        for button in buttons:
            button.pack_forget()
        if target_mode == "stack":
            container.pack(anchor="w", fill="x")
            for index, button in enumerate(buttons):
                button.pack(fill="x", pady=(0, SPACE_XS if index < len(buttons) - 1 else 0))
            return
        container.pack(anchor="w")
        for index, button in enumerate(buttons):
            pad_left = 0 if index == 0 else SPACE_XS
            button.pack(side="left", padx=(pad_left, 0))

    def _update_wraplengths(self, width):
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=300, maximum=820)
        fit_wraplength(self.app.assistant_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self._intake_intro_label, width, padding=120, minimum=280, maximum=620)
        fit_wraplength(self._log_intro_label, width, padding=120, minimum=280, maximum=760)

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
