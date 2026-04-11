import tkinter as tk
from tkinter import ttk
import app_ui.ui_patterns as ui_patterns
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmCheckbutton, AkmScrollablePanel, AkmBadge,
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
        self.filter_chips = {}
        self.search_var = tk.StringVar()
        self.status_filter_var = tk.StringVar(value="all")
        self.sort_key_var = tk.StringVar(value="title")
        self.sort_desc_var = tk.BooleanVar(value=False)
        self._filter_layout_mode = None
        self._status_action_mode = None
        self._bottom_action_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        scroll_root, page = self._build_scroll_content()
        self._build_header_section(page)
        self._build_status_card(page)
        self._build_controls_card(page)
        self._build_list_card(page)
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _build_scroll_content(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        return scroll_root, scroll_root.scrollable_frame

    def _build_header_section(self, page):
        AkmHeader(page, text="Übersicht aller Werke").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text="Suche, filtere und sortiere den gesamten Katalog. Doppelklick öffnet die Details, Audio-Preview bleibt als eigener Move erhalten.",
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))
        signal_row = AkmPanel(page)
        signal_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        for index, text in enumerate(("Search", "Filter", "Details", "Loudness")):
            badge = AkmBadge(signal_row, text)
            badge.pack(side="left", padx=(0 if index == 0 else SPACE_XS, 0))
            badge.set_active(index < 2)

    def _build_status_card(self, page):
        status_card = AkmCard(page, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Catalog Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        AkmSubLabel(
            status_left,
            text="CATALOG DESK  •  Browse the whole workspace without losing the current thread",
            bg=PANEL_2,
            anchor="w",
        ).pack(fill="x", pady=(1, 1))
        self.overview_status_label = AkmLabel(
            status_left,
            text="Noch keine Werke im Katalog",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
        )
        self.overview_status_label.pack(fill="x", pady=(2, 2))
        self.overview_hint_label = AkmSubLabel(
            status_left,
            text="Lege neue Werke an oder importiere eine Excel-Datei, damit sich die Übersicht füllt.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.overview_hint_label.pack(fill="x")

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

    def _build_controls_card(self, page):
        controls_card = AkmCard(page)
        controls_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(controls_card.inner, text="Filter & Sortierung", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        AkmSubLabel(
            controls_card.inner,
            text="Finde schnell die richtigen Werke und halte die Liste im passenden Arbeitsmodus.",
            bg=PANEL_2,
            justify="left",
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        self._build_filter_strip(controls_card)
        self._build_sort_row(controls_card)
        self.overview_summary_label = AkmSubLabel(controls_card.inner, text="0 Treffer", anchor="w", bg=PANEL_2)
        self.overview_summary_label.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

    def _build_filter_strip(self, controls_card):
        filter_strip = AkmPanel(controls_card.inner, bg=PANEL_2)
        filter_strip.pack(fill="x", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_SM))
        self._filter_strip = filter_strip

        search_wrap = tk.Frame(filter_strip, bg=PANEL_2)
        search_wrap.pack(side="left", padx=(0, SPACE_MD))
        self._search_wrap = search_wrap
        AkmLabel(search_wrap, text="Suche:", bg=PANEL_2).pack(side="left", padx=(0, SPACE_XS))

        self.search_var.trace_add("write", lambda *_args: self.app._schedule_refresh_list())
        search_entry = AkmEntry(search_wrap, textvariable=self.search_var, width=26)
        search_entry.pack(side="left", ipady=2)

        filter_chips_wrap = AkmPanel(filter_strip, bg=PANEL_2)
        filter_chips_wrap.pack(side="left")
        self._filter_chips_wrap = filter_chips_wrap

        for value in ["all", "open", "in_progress", "ready", "submitted", "confirmed"]:
            chip = tk.Label(
                filter_chips_wrap, text="", font=FONT_BOLD,
                padx=10, pady=4, bd=1, relief="solid", cursor="hand2"
            )
            chip.pack(side="left", padx=(0, 4))
            chip.bind("<Button-1>", lambda _event, status=value: self.app._set_overview_status_filter(status))
            self.filter_chips[value] = chip

    def _build_sort_row(self, controls_card):
        sort_row = AkmPanel(controls_card.inner, bg=PANEL_2)
        sort_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_XS))
        AkmLabel(sort_row, text="Sortierung:", bg=PANEL_2).pack(side="left", padx=(0, SPACE_XS))

        sort_options = [("Titel", "title"), ("Status", "status"), ("Jahr", "year"), ("Änderung", "last_change")]
        sort_menu = tk.OptionMenu(sort_row, self.sort_key_var, *[value for _label, value in sort_options], command=lambda _value: self.app.refresh_list())
        sort_menu.config(bg=PANEL_2, fg=TEXT, activebackground="#3a3a3a", activeforeground=TEXT, relief="flat", highlightthickness=0)
        sort_menu["menu"].config(bg=PANEL_2, fg=TEXT, activebackground=ACCENT, activeforeground="black")
        sort_menu.pack(side="left", padx=(0, SPACE_XS))

        AkmCheckbutton(sort_row, text="Absteigend", variable=self.sort_desc_var, command=self.app.refresh_list, bg=PANEL_2).pack(side="left")

    def _build_list_card(self, page):
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
        list_strip = tk.Frame(list_card.inner, bg=PANEL_2)
        list_strip.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        for index, text in enumerate(("Multi-select", "Double-click", "Preview", "Detail jump")):
            badge = AkmBadge(list_strip, text)
            badge.pack(side="left", padx=(0 if index == 0 else SPACE_XS, 0))
            badge.set_active(index in {0, 3})

        self._build_list_frame(list_card)
        self._build_empty_state(list_card)
        self._build_bottom_actions(list_card)

    def _build_list_frame(self, list_card):
        list_frame = AkmPanel(list_card.inner, bg=PANEL_2)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, SPACE_XS))

        self.listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, relief="flat", exportselection=False,
            font=FONT_SM, selectbackground=ACCENT, selectforeground="black",
            highlightthickness=0, activestyle="none", selectmode="extended"
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<Double-1>", self.app.on_listbox_activate)
        self.listbox.bind("<Return>", lambda _event: self.app.load_selected_into_details())

        scrollbar = tk.Scrollbar(
            list_frame,
            command=self.listbox.yview,
            bg=PANEL_2,
            activebackground=ui_patterns.blend_color(PANEL_2, ACCENT, 0.18),
            troughcolor=ui_patterns.BG,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

    def _build_empty_state(self, list_card):
        self.overview_empty_label = AkmSubLabel(
            list_card.inner,
            text="Noch keine sichtbaren Werke.",
            bg=PANEL_2,
            justify="left",
            wraplength=760,
        )

    def _build_bottom_actions(self, list_card):
        bottom_actions = AkmPanel(list_card.inner, bg=PANEL_2)
        self.overview_bottom_actions = bottom_actions
        bottom_actions.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._bottom_action_bar = bottom_actions
        self._bottom_action_buttons = (
            self.app.btn(bottom_actions, "Details öffnen", self.app.load_selected_into_details, primary=True, width=138),
            self.app.btn(bottom_actions, "Audio Preview", self.app.open_audio_player_for_selected, quiet=True, width=126),
            self.app.btn(bottom_actions, "Lautheit aus Auswahl", self.app.loudness_ctrl.import_selected_work, quiet=True, width=164),
        )

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_button_bar(self, container, buttons, width, state_attr, row_spacing=SPACE_XS, anchor="w"):
        current_mode = getattr(self, state_attr, None)
        mode = ui_patterns.apply_button_bar_layout(
            container,
            buttons,
            width,
            self.ACTION_STACK_BREAKPOINT,
            current_mode,
            row_spacing=row_spacing,
            anchor=anchor,
        )
        setattr(self, state_attr, mode)
        return mode

    def _apply_responsive_layout(self, width):
        self._apply_filter_layout(width)
        self._apply_status_actions_layout(width)
        self._apply_bottom_actions_layout(width)
        self._update_wraplengths(width)

    def _apply_filter_layout(self, width):
        if not hasattr(self, "_filter_strip"):
            return
        self._filter_layout_mode = ui_patterns.apply_widget_layout(
            width,
            self.FILTER_STACK_BREAKPOINT,
            self._filter_layout_mode,
            {
                "stack": (
                    (self._search_wrap, {"anchor": "w", "pady": (0, SPACE_XS)}),
                    (self._filter_chips_wrap, {"anchor": "w"}),
                ),
                "row": (
                    (self._search_wrap, {"side": "left", "padx": (0, SPACE_MD)}),
                    (self._filter_chips_wrap, {"side": "left"}),
                ),
            },
        )

    def _apply_status_actions_layout(self, width):
        if not hasattr(self, "_status_action_buttons"):
            return
        self._status_action_mode = ui_patterns.apply_button_bar_layout(
            self._status_action_bar,
            self._status_action_buttons,
            width,
            self.ACTION_STACK_BREAKPOINT,
            self._status_action_mode,
            row_spacing=SPACE_XS,
            anchor="e",
        )

    def _apply_bottom_actions_layout(self, width):
        if not hasattr(self, "_bottom_action_buttons"):
            return
        self._bottom_action_mode = ui_patterns.apply_button_bar_layout(
            self._bottom_action_bar,
            self._bottom_action_buttons,
            width,
            self.ACTION_STACK_BREAKPOINT,
            self._bottom_action_mode,
            row_spacing=SPACE_XS,
        )

    def _update_wraplengths(self, width):
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=320, maximum=880)
        fit_wraplength(self.overview_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self._list_intro_label, width, padding=120, minimum=320, maximum=820)
        fit_wraplength(self.overview_empty_label, width, padding=120, minimum=320, maximum=820)

    def render_overview_records(self, labels, row_statuses):
        self.listbox.delete(0, tk.END)
        if labels:
            self.listbox.insert(tk.END, *labels)
        for idx, row_status in enumerate(row_statuses):
            if row_status in ui_patterns.STATUS_PALETTES:
                bg_col = ui_patterns.get_row_color(row_status, 0.16)
                self.listbox.itemconfig(idx, bg=bg_col, fg=ui_patterns.FIELD_FG)

    def render_overview_meta(self, *, summary_text, status_text, hint_text, empty_text, show_empty):
        self.overview_summary_label.config(text=summary_text)
        self.overview_status_label.config(text=status_text)
        self.overview_hint_label.config(text=hint_text)
        self.overview_empty_label.config(text=empty_text)
        if show_empty:
            self.overview_empty_label.pack(fill="x", padx=12, pady=12, before=self.overview_bottom_actions)
        else:
            self.overview_empty_label.pack_forget()

    def update_filter_chip(self, status_key, text, selected=False):
        widget = self.filter_chips.get(status_key)
        if widget:
            ui_patterns.style_chip_label(widget, status_key, text, selected)

    def get_filter_state(self):
        return {
            "search": (self.search_var.get() or ""),
            "filter": (self.status_filter_var.get() or "all"),
            "sort": (self.sort_key_var.get() or "title"),
            "desc": bool(self.sort_desc_var.get()),
        }

    def set_status_filter(self, status_key):
        self.status_filter_var.set(status_key or "all")

    def get_selected_indices(self):
        return tuple(self.listbox.curselection())
