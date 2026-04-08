import tkinter as tk
from app_ui import ui_patterns
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmSuccessIndicator, AkmScrollablePanel,
    ACCENT, PANEL_2, SPACE_MD, SPACE_SM, SPACE_XS,
    CARD_PAD_X, CARD_PAD_Y, FONT_BOLD, FONT_MD_BOLD, FONT_SM, FONT_LG, FONT_XXL, fit_wraplength
)

class DashboardTab(AkmPanel):
    ACTION_STACK_BREAKPOINT = 860
    CHIP_STACK_BREAKPOINT = 980

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._action_layout_mode = None
        self._chip_layout_mode = None
        self._stats_columns = None
        self._stat_cards = []
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        page = scroll_root.scrollable_frame

        AkmHeader(
            page,
            text="Dashboard",
        ).pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))

        self._header_intro_label = AkmSubLabel(
            page,
            text="Schneller Blick auf Status, Vollständigkeit und den aktuellen Arbeitsstand.",
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(page, min_height=118)
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

        self._refresh_button = self.app.btn(status_right, "Dashboard aktualisieren", self.app.refresh_dashboard, primary=True, width=186)
        self._refresh_button.pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(status_right, bg=PANEL_2)
        action_row.pack(anchor="e")
        self._status_action_bar = action_row
        self._status_action_buttons = (
            self.app.btn(action_row, "Letztes offenes Werk", self.app.jump_to_last_open, quiet=True, width=150),
            self.app.btn(action_row, "Loudness", self.app.open_loudness_tab, quiet=True, width=92),
            self.app.btn(action_row, "Speichern", self.app.save_project, quiet=True, width=96),
            self.app.btn(action_row, "Laden", self.app.load_project_dialog, quiet=True, width=84),
        )

        # Status Chips
        chip_row = AkmPanel(page)
        chip_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self._chip_row = chip_row

        self._chip_intro_label = AkmSubLabel(
            chip_row,
            text="Statuschips springen direkt in die gefilterte Übersicht.",
            justify="left",
        )
        self._chip_intro_label.pack(side="left", padx=(0, SPACE_SM))
        self._chip_wrap = tk.Frame(chip_row, bg=chip_row["bg"])
        self._chip_wrap.pack(side="left", fill="x", expand=True)
        
        for status in ["open", "in_progress", "ready", "submitted", "confirmed"]:
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
            self.app.dashboard_status_chips[status] = chip

        # Stats Grid
        stats_grid = AkmPanel(page)
        stats_grid.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self._stats_grid = stats_grid

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
            self._stat_cards.append(card)

        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

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
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if target_mode == self._action_layout_mode:
            return
        self._action_layout_mode = target_mode

        for button in self._status_action_buttons:
            button.pack_forget()
        if target_mode == "stack":
            self._status_action_bar.pack(anchor="e", fill="x")
            for index, button in enumerate(self._status_action_buttons):
                button.pack(anchor="e", fill="x", pady=(0, SPACE_XS if index < len(self._status_action_buttons) - 1 else 0))
            return
        self._status_action_bar.pack(anchor="e")
        for index, button in enumerate(self._status_action_buttons):
            button.pack(side="left", padx=(0, SPACE_XS if index < len(self._status_action_buttons) - 1 else 0))

    def _apply_chip_layout(self, width):
        if not hasattr(self, "_chip_wrap"):
            return
        target_mode = "stack" if width and width < self.CHIP_STACK_BREAKPOINT else "row"
        if target_mode == self._chip_layout_mode:
            return
        self._chip_layout_mode = target_mode

        self._chip_intro_label.pack_forget()
        self._chip_wrap.pack_forget()
        if target_mode == "stack":
            self._chip_intro_label.pack(anchor="w", pady=(0, SPACE_XS))
            self._chip_wrap.pack(anchor="w", fill="x")
            return
        self._chip_intro_label.pack(side="left", padx=(0, SPACE_SM))
        self._chip_wrap.pack(side="left", fill="x", expand=True)

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
        fit_wraplength(self.app.dashboard_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self._chip_intro_label, width, padding=140, minimum=260, maximum=420)
