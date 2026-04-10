import tkinter as tk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmText, AkmScrollablePanel,
    ACCENT, PANEL, PANEL_2, SUBTLE, SPACE_MD, SPACE_SM, SPACE_XS, 
    CARD_PAD_X, CARD_PAD_Y, FONT_LG, FONT_MD, FONT_XL, LOG_BG, LOG_FG, FONT_LOG, fit_wraplength,
    apply_button_bar_layout,
)
from app_logic import assistant_tools, i18n

class AssistantTab(AkmPanel):
    ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._status_action_mode = None
        self._quick_action_mode = None
        self._import_action_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_entry_trace()
        self._update_assistant_radar()

    def build_ui(self):
        scroll_root, page = self._build_scroll_content()
        self._build_header(page)
        self._build_status_card(page)
        self._build_intake_card(page)
        self._build_log_card(page)
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _build_scroll_content(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        return scroll_root, scroll_root.scrollable_frame

    def _build_header(self, page):
        AkmHeader(page, text=i18n._t("ash_header_title")).pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text=i18n._t("ash_header_subtitle"),
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

    def _build_status_card(self, page):
        status_card = AkmCard(page, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)
        self._build_status_summary(status_left)
        self._build_status_actions(status_right)

    def _build_status_summary(self, parent):
        AkmLabel(parent, text=i18n._t("ash_radar_title"), fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.assistant_status_label = AkmLabel(
            parent,
            text=i18n._t("ash_radar_ready"),
            bg=PANEL_2,
            anchor="w",
            font=FONT_LG,
        )
        self.assistant_status_label.pack(fill="x", pady=(2, 2))
        self.assistant_hint_label = AkmSubLabel(
            parent,
            text=i18n._t("ash_radar_hint"),
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.assistant_hint_label.pack(fill="x")
        self.assistant_context_label = AkmSubLabel(
            parent,
            text=i18n._t("ash_radar_context_empty"),
            bg=PANEL_2,
            anchor="w",
        )
        self.assistant_context_label.pack(fill="x", pady=(2, 0))

    def _build_status_actions(self, parent):
        self._create_button = self.app.btn(parent, i18n._t("ash_btn_create"), lambda: self.app.add(self.get_entry_title()), primary=True, width=136)
        self._create_button.pack(anchor="e", pady=(0, SPACE_XS))
        status_actions = tk.Frame(parent, bg=PANEL_2)
        status_actions.pack(anchor="e")
        self._status_action_bar = status_actions
        self._status_action_buttons = (
            self.app.btn(status_actions, i18n._t("ash_btn_import"), self.app.import_excel, quiet=True, width=132),
            self.app.btn(status_actions, i18n._t("ash_btn_loudness"), self.app.open_loudness_tab, quiet=True, width=92),
        )

    def _build_intake_card(self, page):
        intake_card = AkmCard(page)
        intake_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(intake_card.inner, text=i18n._t("ash_intake_title"), fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        self._intake_intro_label = AkmSubLabel(
            intake_card.inner,
            text=i18n._t("ash_intake_hint"),
            bg=PANEL_2,
            justify="left",
        )
        self._intake_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        self.assistant_entry_var = tk.StringVar()
        self.assistant_entry = AkmEntry(intake_card.inner, textvariable=self.assistant_entry_var, width=50, font=FONT_MD)
        self.assistant_entry.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM), ipady=5)
        self.assistant_entry.bind("<Return>", lambda _event: self.app.add(self.get_entry_title()))
        self._build_quick_actions(intake_card)
        self._build_import_actions(intake_card)

    def _build_quick_actions(self, intake_card):
        btn_row = AkmPanel(intake_card.inner, bg=PANEL_2)
        btn_row.pack(padx=CARD_PAD_X, pady=(0, SPACE_XS), anchor="w")
        self._quick_action_bar = btn_row
        self._quick_action_buttons = [
            self.app.btn(btn_row, i18n._t("ash_btn_create"), lambda: self.app.add(self.get_entry_title()), primary=True)
        ]
        for label, status in assistant_tools.ASSISTANT_STATUS_ACTIONS:
            self._quick_action_buttons.append(self.app.btn(btn_row, label, lambda v=status: self.app.set_status(v)))

    def _build_import_actions(self, intake_card):
        imp_row = AkmPanel(intake_card.inner, bg=PANEL_2)
        imp_row.pack(padx=CARD_PAD_X, pady=(0, CARD_PAD_Y), anchor="w")
        self._import_action_bar = imp_row
        self._import_action_buttons = (
            self.app.btn(imp_row, "Excel importieren", self.app.import_excel, quiet=True),
            self.app.btn(imp_row, "Lautheit", self.app.open_loudness_tab),
        )

    def _build_log_card(self, page):
        log_card = AkmCard(page)
        log_card.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(log_card.inner, text=i18n._t("ash_log_title"), fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        self._log_intro_label = AkmSubLabel(
            log_card.inner,
            text=i18n._t("ash_log_subtitle"),
            bg=PANEL_2,
            justify="left",
        )
        self._log_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        self.log_widget = AkmText(log_card.inner, height=10, bg=LOG_BG, fg=LOG_FG, insertbackground=LOG_FG)
        self.log_widget.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.app.log = self.log_widget

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_button_bar(self._status_action_bar, self._status_action_buttons, width, "_status_action_mode")
        self._apply_button_bar(self._quick_action_bar, self._quick_action_buttons, width, "_quick_action_mode")
        self._apply_button_bar(self._import_action_bar, self._import_action_buttons, width, "_import_action_mode")
        self._update_wraplengths(width)

    def _apply_button_bar(self, container, buttons, width, state_attr):
        current_mode = getattr(self, state_attr, None)
        setattr(
            self,
            state_attr,
            apply_button_bar_layout(
                container,
                buttons,
                width,
                self.ACTION_STACK_BREAKPOINT,
                current_mode,
                row_spacing=SPACE_XS,
            ),
        )

    def _update_wraplengths(self, width):
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=300, maximum=820)
        fit_wraplength(self.assistant_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self._intake_intro_label, width, padding=120, minimum=280, maximum=620)
        fit_wraplength(self._log_intro_label, width, padding=120, minimum=280, maximum=760)

    def get_entry_title(self):
        return self.assistant_entry.get().strip()

    def _setup_entry_trace(self):
        self.assistant_entry_var.trace_add("write", lambda *_args: self._update_assistant_radar())

    def _update_assistant_radar(self):
        state = assistant_tools.build_assistant_radar_state(self.get_entry_title())
        self.assistant_status_label.config(text=state["status_text"])
        self.assistant_hint_label.config(text=state["hint_text"])
        self.assistant_context_label.config(text=state["meta_text"])
