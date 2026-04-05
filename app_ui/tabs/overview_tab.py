from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmCheckbutton,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, LOG_BG, LOG_FG,
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_XL, FONT_LG
)
import tkinter as tk

class OverviewTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        AkmHeader(self, text="Übersicht aller Werke").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Suche, filtere und sortiere den gesamten Katalog. Ein Doppelklick öffnet die Details.").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        filter_strip = AkmPanel(self)
        filter_strip.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        # Search
        search_wrap = tk.Frame(filter_strip, bg=PANEL)
        search_wrap.pack(side="left", padx=(0, SPACE_MD))
        AkmLabel(search_wrap, text="Suche:").pack(side="left", padx=(0, SPACE_XS))
        
        self.app.search_var = tk.StringVar()
        self.app.search_var.trace_add("write", lambda *args: self.app._schedule_refresh_list())
        
        search_entry = AkmEntry(search_wrap, textvariable=self.app.search_var, width=26)
        search_entry.pack(side="left", ipady=2)

        # Status Filter Chips
        filter_chips_wrap = AkmPanel(filter_strip)
        filter_chips_wrap.pack(side="left")
        
        self.app.status_filter_var = tk.StringVar(value="all")
        for value in ["all", "open", "in_progress", "ready", "submitted", "confirmed"]:
            chip = tk.Label(
                filter_chips_wrap, text="", font=FONT_BOLD,
                padx=10, pady=4, bd=1, relief="solid", cursor="hand2"
            )
            chip.pack(side="left", padx=(0, 4))
            chip.bind("<Button-1>", lambda _e, v=value: self.app._set_overview_status_filter(v))
            self.app.overview_filter_chips[value] = chip

        # Sort Row
        sort_row = AkmPanel(self)
        sort_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(sort_row, text="Sortierung:").pack(side="left", padx=(0, SPACE_XS))

        self.app.sort_key_var = tk.StringVar(value="title")
        sort_options = [("Titel", "title"), ("Status", "status"), ("Jahr", "year"), ("Änderung", "last_change")]
        sort_menu = tk.OptionMenu(sort_row, self.app.sort_key_var, *[v for _, v in sort_options], command=lambda _v: self.app.refresh_list())
        sort_menu.config(bg=PANEL_2, fg=TEXT, activebackground="#3a3a3a", activeforeground=TEXT, relief="flat", highlightthickness=0)
        sort_menu["menu"].config(bg=PANEL_2, fg=TEXT, activebackground=ACCENT, activeforeground="black")
        sort_menu.pack(side="left", padx=(0, SPACE_XS))

        self.app.sort_desc_var = tk.BooleanVar(value=False)
        AkmCheckbutton(sort_row, text="Absteigend", variable=self.app.sort_desc_var, command=self.app.refresh_list).pack(side="left")

        self.app.overview_summary_label = AkmSubLabel(self, text="0 Treffer", anchor="w")
        self.app.overview_summary_label.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_XS))

        # List Area
        list_frame = AkmPanel(self)
        list_frame.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))
        self.app.listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, relief="flat", exportselection=False,
            font=FONT_SM, selectbackground=ACCENT, selectforeground="black",
            highlightthickness=0, activestyle="none"
        )
        self.app.listbox.pack(side="left", fill="both", expand=True)
        self.app.listbox.bind("<Double-1>", self.app.on_listbox_activate)
        sb = tk.Scrollbar(list_frame, command=self.app.listbox.yview)
        sb.pack(side="right", fill="y")
        self.app.listbox.config(yscrollcommand=sb.set)
