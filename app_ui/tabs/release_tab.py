from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm, AkmEntry,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_GAP, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_XL, FONT_LG
)
from app_logic import akm_core

class ReleaseTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        AkmHeader(self, text="Release / Export").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Baue aus Werken, gematchten Dateien und Cover-Varianten ein sauberes Release-Paket.").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        top = AkmPanel(self)
        top.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))

        left_card = AkmCard(top)
        right_card = AkmCard(top)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))

        # LEFT FORM
        left_form = AkmForm(left_card, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        left_form.pack(fill="both", expand=True)
        left_form.add_header("Release-Basis")
        AkmSubLabel(left_form, text="Metadaten, Cover und Exportpfad fuer das eigentliche Auslieferungspaket.", bg=PANEL_2, wraplength=320, justify="left").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, SPACE_SM))
        left_form._current_row += 1

        fields = [
            ("title", "Release-Titel"), ("artist", "Artist"), ("type", "Typ"),
            ("release_date", "Release-Datum"), ("genre", "Genre"), ("subgenre", "Subgenre"),
            ("label", "Label"), ("copyright_line", "Copyright"),
            ("cover_path", "Cover-Pfad"), ("export_dir", "Export-Ordner"),
        ]
        defaults = {"artist": akm_core.get_release_default_artist(), "type": "Album"}

        for key, label in fields:
            var = tk.StringVar(value=defaults.get(key, ""))
            self.app.release_vars[key] = var
            
            if key == "cover_path":
                def _create_cover_field(parent):
                    wrap = tk.Frame(parent, bg=PANEL_2)
                    AkmEntry(wrap, textvariable=var, font=FONT_SM).pack(side="left", fill="x", expand=True)
                    self.app.btn(wrap, "Wählen", self.app.choose_release_cover, primary=True).pack(side="left", padx=(SPACE_XS, 0))
                    self.app.btn(wrap, "Finder", self.app.open_release_cover_in_finder, quiet=True).pack(side="left", padx=(SPACE_XS, 0))
                    return wrap
                left_form.add_row(label, _create_cover_field)
            elif key == "export_dir":
                def _create_export_field(parent):
                    wrap = tk.Frame(parent, bg=PANEL_2)
                    AkmEntry(wrap, textvariable=var, font=FONT_SM).pack(side="left", fill="x", expand=True)
                    self.app.btn(wrap, "Wählen", self.app.choose_release_export_dir, primary=True).pack(side="left", padx=(SPACE_XS, 0))
                    return wrap
                left_form.add_row(label, _create_export_field)
            else:
                left_form.add_entry(label, var, font=FONT_SM)

        # RIGHT CARD: TRACK LIST
        AkmLabel(right_card, text="Inhalt (Tracks)", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        AkmSubLabel(right_card, text="Waehle Werke in der Übersicht oder ziehe Audio-Dateien direkt hierher.", bg=PANEL_2, wraplength=320, justify="left").pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        list_frame = AkmPanel(right_card, bg=PANEL_2)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.app.release_track_listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, relief="flat", exportselection=False,
            font=FONT_SM, selectbackground=ACCENT, selectforeground="black",
            highlightthickness=0, activestyle="none"
        )
        self.app.release_track_listbox.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(list_frame, command=self.app.release_track_listbox.yview)
        sb.pack(side="right", fill="y")
        self.app.release_track_listbox.config(yscrollcommand=sb.set)

        self.app.release_action_hint_label = AkmSubLabel(right_card, text="", bg=PANEL_2, anchor="w")
        self.app.release_action_hint_label.pack(fill="x", padx=CARD_PAD_X, pady=(4, SPACE_SM))

        tk_actions = AkmPanel(right_card, bg=PANEL_2)
        tk_actions.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.app.btn(tk_actions, "↑", self.app.release_move_track_up, quiet=True).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(tk_actions, "↓", self.app.release_move_track_down, quiet=True).pack(side="left", padx=SPACE_XS)
        self.app.btn(tk_actions, "Löschen", self.app.release_remove_track, quiet=True).pack(side="left", padx=SPACE_XS)

        # BOTTOM ACTIONS
        actions = AkmPanel(self)
        actions.pack(fill="x", side="bottom", padx=SPACE_MD, pady=SPACE_SM)
        self.app.btn(actions, "Distro-Export starten", self.app.build_distro_export, primary=True).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(actions, "Cover-Previews", self.app.open_release_cover_dialog, quiet=True).pack(side="left", padx=SPACE_XS)

        self.app.release_status_label = AkmSubLabel(self, text="0 Tracks im Release", bg=PANEL, anchor="w")
        self.app.release_status_label.pack(side="left", padx=SPACE_MD)
