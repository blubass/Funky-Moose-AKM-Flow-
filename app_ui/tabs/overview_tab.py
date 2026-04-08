import tkinter as tk
from tkinter import ttk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmCheckbutton, AkmScrollablePanel,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, LOG_BG, LOG_FG,
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_MD_BOLD, FONT_SM, FONT_XL, FONT_LG, fit_wraplength
)


class OverviewTab(AkmPanel):
    FILTER_STACK_BREAKPOINT = 980
    ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._filter_layout_mode = None
        self._status_action_mode = None
        self._bottom_action_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        page = scroll_root.scrollable_frame

        AkmHeader(page, text="Übersicht aller Werke").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text="Suche, filtere und sortiere den gesamten Katalog. Doppelklick öffnet die Details, Audio-Preview bleibt als eigener Move erhalten.",
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(page, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Catalog Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.app.overview_status_label = AkmLabel(
            status_left,
            text="Noch keine Werke im Katalog",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
        )
        self.app.overview_status_label.pack(fill="x", pady=(2, 2))
        self.app.overview_hint_label = AkmSubLabel(
            status_left,
            text="Lege neue Werke an oder importiere eine Excel-Datei, damit sich die Übersicht füllt.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.app.overview_hint_label.pack(fill="x")

        self._refresh_button = self.app.btn(status_right, "Aktualisieren", self.app.refresh_list, primary=True, width=126)
        self._refresh_button.pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(status_right, bg=PANEL_2)
        action_row.pack(anchor="e")
        self._status_action_bar = action_row
        self._status_action_buttons = (
            self.app.btn(action_row, "Details öffnen", self.app.load_selected_into_details, quiet=True, width=126),
            self.app.btn(action_row, "Audio Preview", self.app.open_audio_player_for_selected, quiet=True, width=126),
            self.app.btn(action_row, "Lautheit", self.app.loudness_ctrl.import_selected_work, quiet=True, width=96),
        )

        controls_card = AkmCard(page)
        controls_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        filter_strip = AkmPanel(controls_card.inner, bg=PANEL_2)
        filter_strip.pack(fill="x", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_SM))
        self._filter_strip = filter_strip

        search_wrap = tk.Frame(filter_strip, bg=PANEL_2)
        search_wrap.pack(side="left", padx=(0, SPACE_MD))
        self._search_wrap = search_wrap
        AkmLabel(search_wrap, text="Suche:", bg=PANEL_2).pack(side="left", padx=(0, SPACE_XS))

        self.app.search_var = tk.StringVar()
        self.app.search_var.trace_add("write", lambda *args: self.app._schedule_refresh_list())

        search_entry = AkmEntry(search_wrap, textvariable=self.app.search_var, width=26)
        search_entry.pack(side="left", ipady=2)

        filter_chips_wrap = AkmPanel(filter_strip, bg=PANEL_2)
        filter_chips_wrap.pack(side="left")
        self._filter_chips_wrap = filter_chips_wrap

        self.app.status_filter_var = tk.StringVar(value="all")
        for value in ["all", "open", "in_progress", "ready", "submitted", "confirmed"]:
            chip = tk.Label(
                filter_chips_wrap, text="", font=FONT_BOLD,
                padx=10, pady=4, bd=1, relief="solid", cursor="hand2"
            )
            chip.pack(side="left", padx=(0, 4))
            chip.bind("<Button-1>", lambda _e, v=value: self.app._set_overview_status_filter(v))
            self.app.overview_filter_chips[value] = chip

        sort_row = AkmPanel(controls_card.inner, bg=PANEL_2)
        sort_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_XS))
        AkmLabel(sort_row, text="Sortierung:", bg=PANEL_2).pack(side="left", padx=(0, SPACE_XS))

        self.app.sort_key_var = tk.StringVar(value="title")
        sort_options = [("Titel", "title"), ("Status", "status"), ("Jahr", "year"), ("Änderung", "last_change")]
        sort_menu = tk.OptionMenu(sort_row, self.app.sort_key_var, *[v for _, v in sort_options], command=lambda _v: self.app.refresh_list())
        sort_menu.config(bg=PANEL_2, fg=TEXT, activebackground="#3a3a3a", activeforeground=TEXT, relief="flat", highlightthickness=0)
        sort_menu["menu"].config(bg=PANEL_2, fg=TEXT, activebackground=ACCENT, activeforeground="black")
        sort_menu.pack(side="left", padx=(0, SPACE_XS))

        self.app.sort_desc_var = tk.BooleanVar(value=False)
        AkmCheckbutton(sort_row, text="Absteigend", variable=self.app.sort_desc_var, command=self.app.refresh_list, bg=PANEL_2).pack(side="left")

        self.app.overview_summary_label = AkmSubLabel(controls_card.inner, text="0 Treffer", anchor="w", bg=PANEL_2)
        self.app.overview_summary_label.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        list_card = AkmCard(page)
        list_card.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(list_card.inner, text="Katalogliste", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        self._list_intro_label = AkmSubLabel(
            list_card.inner,
            text="Mehrfachauswahl erlaubt Batch-Statuswechsel. Details und Loudness greifen immer auf die aktuelle Auswahl.",
            bg=PANEL_2,
            justify="left",
            wraplength=760,
        )
        self._list_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        list_frame = AkmPanel(list_card.inner, bg=PANEL_2)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, SPACE_XS))

        self.app.listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, relief="flat", exportselection=False,
            font=FONT_SM, selectbackground=ACCENT, selectforeground="black",
            highlightthickness=0, activestyle="none", selectmode="extended"
        )
        self.app.listbox.pack(side="left", fill="both", expand=True)
        self.app.listbox.bind("<Double-1>", self.app.on_listbox_activate)
        self.app.listbox.bind("<Return>", lambda _event: self.app.load_selected_into_details())

        sb = tk.Scrollbar(list_frame, command=self.app.listbox.yview)
        sb.pack(side="right", fill="y")
        self.app.listbox.config(yscrollcommand=sb.set)

        self.app.overview_empty_label = AkmSubLabel(
            list_card.inner,
            text="Noch keine sichtbaren Werke.",
            bg=PANEL_2,
            justify="left",
            wraplength=760,
        )

        bottom_actions = AkmPanel(list_card.inner, bg=PANEL_2)
        self.app.overview_bottom_actions = bottom_actions
        bottom_actions.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._bottom_action_bar = bottom_actions
        self._bottom_action_buttons = (
            self.app.btn(bottom_actions, "Details öffnen", self.app.load_selected_into_details, primary=True, width=138),
            self.app.btn(bottom_actions, "Audio Preview", self.app.open_audio_player_for_selected, quiet=True, width=126),
            self.app.btn(bottom_actions, "Lautheit aus Auswahl", self.app.loudness_ctrl.import_selected_work, quiet=True, width=164),
        )
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_filter_layout(width)
        self._apply_status_actions_layout(width)
        self._apply_bottom_actions_layout(width)
        self._update_wraplengths(width)

    def _apply_filter_layout(self, width):
        if not hasattr(self, "_filter_strip"):
            return
        target_mode = "stack" if width and width < self.FILTER_STACK_BREAKPOINT else "row"
        if target_mode == self._filter_layout_mode:
            return
        self._filter_layout_mode = target_mode

        self._search_wrap.pack_forget()
        self._filter_chips_wrap.pack_forget()
        if target_mode == "stack":
            self._search_wrap.pack(anchor="w", pady=(0, SPACE_XS))
            self._filter_chips_wrap.pack(anchor="w")
            return
        self._search_wrap.pack(side="left", padx=(0, SPACE_MD))
        self._filter_chips_wrap.pack(side="left")

    def _apply_status_actions_layout(self, width):
        if not hasattr(self, "_status_action_buttons"):
            return
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if target_mode == self._status_action_mode:
            return
        self._status_action_mode = target_mode

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

    def _apply_bottom_actions_layout(self, width):
        if not hasattr(self, "_bottom_action_buttons"):
            return
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if target_mode == self._bottom_action_mode:
            return
        self._bottom_action_mode = target_mode

        for button in self._bottom_action_buttons:
            button.pack_forget()
        if target_mode == "stack":
            for index, button in enumerate(self._bottom_action_buttons):
                button.pack(fill="x", pady=(0, SPACE_XS if index < len(self._bottom_action_buttons) - 1 else 0))
            return
        for index, button in enumerate(self._bottom_action_buttons):
            pad_left = 0 if index == 0 else SPACE_XS
            button.pack(side="left", padx=(pad_left, 0))

    def _update_wraplengths(self, width):
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=320, maximum=880)
        fit_wraplength(self.app.overview_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self._list_intro_label, width, padding=120, minimum=320, maximum=820)
        fit_wraplength(self.app.overview_empty_label, width, padding=120, minimum=320, maximum=820)
