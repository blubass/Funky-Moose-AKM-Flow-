import tkinter as tk
from app_ui import ui_patterns
from app_logic import i18n
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmSuccessIndicator, AkmScrollablePanel, AkmBadge,
    ACCENT, PANEL_2, SPACE_MD, SPACE_SM, SPACE_XS,
    CARD_PAD_X, CARD_PAD_Y, FONT_BOLD, FONT_MD_BOLD, FONT_SM, FONT_LG, FONT_XXL, fit_wraplength
)

class DashboardTab(AkmPanel):
    ACTION_STACK_BREAKPOINT = 860
    CHIP_STACK_BREAKPOINT = 980

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.dashboard_labels = {}
        self.dashboard_status_chips = {}
        self._action_layout_mode = None
        self._chip_layout_mode = None
        self._stats_columns = None
        self._stat_cards = []
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        scroll_root, page = self._build_scroll_content()
        self._build_header(page)
        self._build_status_card(page)
        self._build_chip_row(page)
        self._build_stats_grid(page)
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _build_scroll_content(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        return scroll_root, scroll_root.scrollable_frame

    def _build_header(self, page):
        AkmHeader(page, text=i18n._t("dash_header_title")).pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text=i18n._t("dash_header_subtitle"),
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))
        signal_row = AkmPanel(page)
        signal_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self._dashboard_signal_badges = []
        for index, text in enumerate(("Catalog Live", "Batch Flow", "Cover Forge", "Release Desk")):
            badge = AkmBadge(signal_row, text)
            badge.pack(side="left", padx=(0 if index == 0 else SPACE_XS, 0))
            badge.set_active(index < 2)
            self._dashboard_signal_badges.append(badge)

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
        AkmLabel(parent, text=i18n._t("dash_radar_title"), fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self._dashboard_mode_label = AkmSubLabel(
            parent,
            text="CONTROL ROOM  •  Live catalog pulse and release readiness",
            bg=PANEL_2,
            anchor="w",
        )
        self._dashboard_mode_label.pack(fill="x", pady=(1, 1))
        self.dashboard_status_label = AkmLabel(
            parent,
            text=i18n._t("dash_radar_empty"),
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
        )
        self.dashboard_status_label.pack(fill="x", pady=(2, 2))
        self.dashboard_hint_label = AkmSubLabel(
            parent,
            text=i18n._t("dash_radar_hint"),
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.dashboard_hint_label.pack(fill="x")
        self.dashboard_meta_label = AkmSubLabel(
            parent,
            text="", # Will be filled by render_dashboard_state
            bg=PANEL_2,
            anchor="w",
        )
        self.dashboard_meta_label.pack(fill="x", pady=(2, 0))

    def _build_status_actions(self, parent):
        self._refresh_button = self.app.btn(parent, i18n._t("dash_btn_refresh"), self.app.refresh_dashboard, primary=True, width=186)
        self._refresh_button.pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(parent, bg=PANEL_2)
        action_row.pack(anchor="e")
        self._status_action_bar = action_row
        self._status_action_buttons = (
            self.app.btn(action_row, "Letztes offenes Werk", self.app.jump_to_last_open, quiet=True, width=150),
            self.app.btn(action_row, "Loudness", self.app.open_loudness_tab, quiet=True, width=92),
            self.app.btn(action_row, "Speichern", self.app.save_project, quiet=True, width=96),
            self.app.btn(action_row, "Laden", self.app.load_project_dialog, quiet=True, width=84),
        )

    def _build_chip_row(self, page):
        chip_row = AkmPanel(page)
        chip_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self._chip_row = chip_row
        self._chip_intro_label = AkmSubLabel(
            chip_row,
            text=i18n._t("dash_chip_hint"),
            justify="left",
        )
        self._chip_intro_label.pack(side="left", padx=(0, SPACE_SM))
        self._chip_wrap = tk.Frame(chip_row, bg=chip_row["bg"])
        self._chip_wrap.pack(side="left", fill="x", expand=True)

        for status in ("open", "in_progress", "ready", "submitted", "confirmed"):
            self.dashboard_status_chips[status] = self._build_status_chip(status)

    def _build_status_chip(self, status):
        chip = tk.Label(
            self._chip_wrap,
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
        return chip

    def _build_stats_grid(self, page):
        stats_grid = AkmPanel(page)
        stats_grid.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self._stats_intro_label = AkmSubLabel(
            stats_grid,
            text="Die Metriken unten zeigen dir sofort, wo der Katalog Luft braucht und wo der Release-Flow schon sauber steht.",
            justify="left",
        )
        self._stats_intro_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=5, pady=(0, SPACE_SM))
        self._stats_grid = stats_grid
        for index, (key, label_key) in enumerate(
            (
                ("total", "dash_stat_total"),
                ("open", "dash_stat_open"),
                ("ready", "dash_stat_ready"),
                ("submitted", "dash_stat_submitted"),
                ("confirmed", "dash_stat_confirmed"),
                ("instrumental", "dash_stat_instrumental"),
                ("with_production", "dash_stat_with_production"),
                ("with_notes", "dash_stat_with_notes"),
            )
        ):
            self._build_stat_card(stats_grid, key, i18n._t(label_key), index)

    def _build_stat_card(self, parent, key, label, index):
        card = AkmCard(parent)
        card.grid(row=(index // 4) + 1, column=index % 4, sticky="nsew", padx=5, pady=5)
        header = tk.Frame(card.inner, bg=ui_patterns.PANEL_2)
        header.pack(fill="x", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 0))
        AkmSubLabel(header, text=label, bg=ui_patterns.PANEL_2).pack(side="left")
        if key in {"submitted", "confirmed"}:
            AkmSuccessIndicator(header, bg=ui_patterns.PANEL_2).pack(side="right")
        value_label = tk.Label(card.inner, text="0", fg=ui_patterns.ACCENT, bg=ui_patterns.PANEL_2, font=FONT_XXL)
        value_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))
        AkmSubLabel(
            card.inner,
            text="live status signal",
            bg=ui_patterns.PANEL_2,
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.dashboard_labels[key] = value_label
        self._stat_cards.append(card)

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_status_actions_layout(width)
        self._apply_chip_layout(width)
        self._apply_stats_layout(width)
        self._update_wraplengths(width)

    def _apply_status_actions_layout(self, width):
        if not hasattr(self, "_status_action_buttons"):
            return
        self._action_layout_mode = ui_patterns.apply_button_bar_layout(
            self._status_action_bar,
            self._status_action_buttons,
            width,
            self.ACTION_STACK_BREAKPOINT,
            self._action_layout_mode,
            row_spacing=SPACE_XS,
            anchor="e",
        )

    def _apply_chip_layout(self, width):
        if not hasattr(self, "_chip_wrap"):
            return
        self._chip_layout_mode = ui_patterns.apply_widget_layout(
            width,
            self.CHIP_STACK_BREAKPOINT,
            self._chip_layout_mode,
            {
                "stack": (
                    (self._chip_intro_label, {"anchor": "w", "pady": (0, SPACE_XS)}),
                    (self._chip_wrap, {"anchor": "w", "fill": "x"}),
                ),
                "row": (
                    (self._chip_intro_label, {"side": "left", "padx": (0, SPACE_SM)}),
                    (self._chip_wrap, {"side": "left", "fill": "x", "expand": True}),
                ),
            },
        )

    def _apply_stats_layout(self, width):
        if not hasattr(self, "_stat_cards") or not self._stat_cards:
            return
        columns = 1 if width < 760 else 2 if width < 1180 else 4
        if columns == self._stats_columns:
            return
        self._stats_columns = columns

        for col in range(4):
            self._stats_grid.columnconfigure(col, weight=0)
        for col in range(columns):
            self._stats_grid.columnconfigure(col, weight=1)
        for index, card in enumerate(self._stat_cards):
            card.grid_forget()
            card.grid(row=index // columns, column=index % columns, sticky="nsew", padx=5, pady=5)

    def _update_wraplengths(self, width):
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=320, maximum=860)
        fit_wraplength(self.dashboard_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self._chip_intro_label, width, padding=140, minimum=260, maximum=420)
        fit_wraplength(self._stats_intro_label, width, padding=120, minimum=280, maximum=820)

    def render_dashboard_state(self, stats, status_text, hint_text, meta_text, chip_counts, status_text_fn):
        for key, label in self.dashboard_labels.items():
            label.config(text=str(stats.get(key, 0)))
        self.dashboard_status_label.config(text=status_text)
        self.dashboard_hint_label.config(text=hint_text)
        self.dashboard_meta_label.config(text=meta_text)
        for status_key, widget in self.dashboard_status_chips.items():
            ui_patterns.style_chip_label(
                widget,
                status_key,
                f"{status_text_fn(status_key)}  {chip_counts.get(status_key, 0)}",
            )
