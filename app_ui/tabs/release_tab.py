import tkinter as tk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm, AkmEntry, AkmScrollablePanel,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_GAP, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD_BOLD, FONT_XL, FONT_LG
)
from app_logic import akm_core

class ReleaseTab(AkmPanel):
    STACK_BREAKPOINT = 1180

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._release_layout_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_dnd()

    def build_ui(self):
        AkmHeader(self, text="Release / Export").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Baue aus Werken, gematchten Dateien und Cover-Varianten ein sauberes Release-Paket.").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(self, height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Release Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.app.release_status_label = AkmLabel(
            status_left,
            text="0 Tracks im Release | Cover: Nein | Export-Ordner: Nein | Drag&Drop aktiv",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
        )
        self.app.release_status_label.pack(fill="x", pady=(2, 2))
        self.app.release_action_hint_label = AkmSubLabel(
            status_left,
            text="Werk 0  •  Datei→Werk 0  •  Datei 0",
            bg=PANEL_2,
            anchor="w",
        )
        self.app.release_action_hint_label.pack(fill="x")

        self.app.btn(status_right, "Distro-Export starten", self.app.build_distro_export, primary=True, width=190).pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(status_right, bg=PANEL_2)
        action_row.pack(anchor="e")
        self.app.btn(action_row, "Cover-Preview", self.app.open_release_cover_dialog, quiet=True, width=122).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(action_row, "Finder", self.app.open_release_cover_in_finder, quiet=True, width=84).pack(side="left")

        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        top = scroll_root.scrollable_frame
        top.configure(padx=SPACE_MD, pady=0)

        left_card = AkmCard(top)
        right_card = AkmCard(top)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))
        self._release_cards = (left_card, right_card)
        scroll_root.canvas.bind("<Configure>", self._on_responsive_resize, add="+")
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

        AkmSubLabel(
            left_card.inner,
            text="Metadaten, Cover und Zielordner werden hier einmal sauber gesetzt.",
            bg=PANEL_2,
            justify="left",
            wraplength=360,
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_SM))
        # LEFT FORM
        left_form = AkmForm(left_card.inner, padx=CARD_PAD_X, pady=0)
        left_form.pack(fill="both", expand=True)
        left_form.add_header("Release-Basis")
        
        fields = [
            ("title", "Release-Titel"), ("artist", "Artist"), ("type", "Typ"),
            ("release_date", "Datum (JJJJ-MM-TT)"), ("genre", "Genre"),
            ("subgenre", "Subgenre"), ("label", "Label"), ("copyright_line", "Copyright"),
            ("cover_path", "Cover-Bild (JPG/PNG)"), ("export_dir", "Export-Ordner"),
        ]
        defaults = {"artist": akm_core.get_release_default_artist(), "type": "Single"}

        for key, label in fields:
            var = tk.StringVar(value=defaults.get(key, ""))
            self.app.release_vars[key] = var
            
            if key == "cover_path":
                def _create_cover_field(parent, v=var):
                    wrap = tk.Frame(parent, bg=PANEL_2)
                    AkmEntry(wrap, textvariable=v, font=FONT_SM).pack(side="left", fill="x", expand=True)
                    self.app.btn(wrap, "Wählen", self.app.choose_release_cover, primary=True, width=92).pack(side="left", padx=(SPACE_XS, 0))
                    self.app.btn(wrap, "Preview", self.app.open_release_cover_dialog, quiet=True, width=92).pack(side="left", padx=(SPACE_XS, 0))
                    return wrap
                left_form.add_row(label, _create_cover_field)
            elif key == "export_dir":
                def _create_export_field(parent, v=var):
                    wrap = tk.Frame(parent, bg=PANEL_2)
                    AkmEntry(wrap, textvariable=var, font=FONT_SM).pack(side="left", fill="x", expand=True)
                    self.app.btn(wrap, "Wählen", self.app.choose_release_export_dir, primary=True, width=92).pack(side="left", padx=(SPACE_XS, 0))
                    return wrap
                left_form.add_row(label, _create_export_field)
            else:
                left_form.add_entry(label, var, font=FONT_SM)

        # RIGHT CARD: TRACK LIST & ASSEMBLY
        AkmLabel(right_card.inner, text="Release-Zusammenstellung", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_MD))
        AkmSubLabel(
            right_card.inner,
            text="Ziehe fertige Audiodateien direkt in die Liste. Exakte Titel werden automatisch auf Werke gemappt.",
            bg=PANEL_2,
            justify="left",
            wraplength=380,
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        drop_zone = tk.Frame(right_card.inner, bg=FIELD_BG, highlightbackground="#2E323A", highlightthickness=1)
        drop_zone.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        AkmLabel(
            drop_zone,
            text="DROP ZONE",
            fg=ACCENT,
            bg=FIELD_BG,
            font=FONT_BOLD,
        ).pack(anchor="w", padx=12, pady=(10, 0))
        AkmSubLabel(
            drop_zone,
            text="WAV, AIFF, MP3, FLAC oder M4A hier ablegen. Dubletten werden automatisch uebersprungen.",
            bg=FIELD_BG,
            justify="left",
            wraplength=360,
        ).pack(anchor="w", padx=12, pady=(2, 10))
        
        list_frame = AkmPanel(right_card.inner, bg=PANEL_2)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.app.release_track_listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, relief="flat", exportselection=False,
            font=FONT_SM, selectbackground=ACCENT, selectforeground="black",
            highlightthickness=0, activestyle="none", selectmode="extended"
        )
        self.app.release_track_listbox.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(list_frame, command=self.app.release_track_listbox.yview)
        sb.pack(side="right", fill="y")
        self.app.release_track_listbox.config(yscrollcommand=sb.set)

        tk_actions = AkmPanel(right_card.inner, bg=PANEL_2)
        tk_actions.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.app.btn(tk_actions, "Nach oben", self.app.release_move_track_up, quiet=True, width=108).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(tk_actions, "Nach unten", self.app.release_move_track_down, quiet=True, width=108).pack(side="left", padx=SPACE_XS)
        self.app.btn(tk_actions, "Entfernen", self.app.release_remove_track, quiet=True, width=108).pack(side="left", padx=SPACE_XS)

    def _on_responsive_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        if not hasattr(self, "_release_cards"):
            return
        target_mode = "stack" if width and width < self.STACK_BREAKPOINT else "split"
        if target_mode == self._release_layout_mode:
            return
        self._release_layout_mode = target_mode

        left_card, right_card = self._release_cards
        for card in self._release_cards:
            card.pack_forget()

        if target_mode == "stack":
            left_card.pack(fill="x", expand=False, pady=(0, CARD_GAP))
            right_card.pack(fill="x", expand=False)
            return

        left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))

    def _setup_dnd(self):
        try:
            from tkinterdnd2 import DND_FILES
            self.app.release_track_listbox.drop_target_register(DND_FILES)
            self.app.release_track_listbox.dnd_bind('<<Drop>>', self.app.release_handle_drop)
            self.app.append_log("Release DnD bereit.")
        except: pass
