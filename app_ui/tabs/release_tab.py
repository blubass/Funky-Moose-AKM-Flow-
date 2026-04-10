import tkinter as tk
import app_ui.ui_patterns as ui_patterns
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm, AkmEntry, AkmScrollablePanel,
    fit_wraplength,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_GAP, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD_BOLD, FONT_XL, FONT_LG
)
from app_logic import akm_core


RELEASE_FORM_FIELDS = (
    ("title", "Release-Titel"),
    ("artist", "Artist"),
    ("type", "Typ"),
    ("release_date", "Datum (JJJJ-MM-TT)"),
    ("genre", "Genre"),
    ("subgenre", "Subgenre"),
    ("label", "Label"),
    ("copyright_line", "Copyright"),
    ("cover_path", "Cover-Bild (JPG/PNG)"),
    ("export_dir", "Export-Ordner"),
)


class ReleaseTab(AkmPanel):
    STACK_BREAKPOINT = 1180
    ACTION_STACK_BREAKPOINT = 520
    STATUS_ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.release_vars = {}
        self._release_layout_mode = None
        self._release_action_mode = None
        self._status_action_mode = None
        self._release_memory_after_id = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_dnd()

    def build_ui(self):
        self._build_header_section()
        self._build_status_card()
        scroll_root, top = self._build_scroll_content()
        self._build_release_cards(top, scroll_root)
        self.after_idle(self._update_track_selection_hint)

    def _build_header_section(self):
        AkmHeader(self, text="Release / Export").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            self,
            text="Baue aus Werken, gematchten Dateien und Cover-Varianten ein sauberes Release-Paket und gib die Titel direkt weiter in AKM Batch / Schnellstart.",
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

    def _build_status_card(self):
        status_card = AkmCard(self, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Release Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.release_status_label = AkmLabel(
            status_left,
            text="0 Tracks im Release | Cover: Nein | Export-Ordner: Nein | Drag&Drop aktiv",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
            justify="left",
        )
        self.release_status_label.pack(fill="x", pady=(2, 2))
        self.release_preflight_label = AkmSubLabel(
            status_left,
            text="Preflight: Tracks fehlen • Release-Titel fehlt • Cover fehlt • Export-Ordner fehlt",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.release_preflight_label.pack(fill="x")
        self.release_action_hint_label = AkmSubLabel(
            status_left,
            text="Werk 0  •  Datei→Werk 0  •  Datei 0",
            bg=PANEL_2,
            anchor="w",
            justify="left",
        )
        self.release_action_hint_label.pack(fill="x")
        self.release_flow_hint_label = AkmSubLabel(
            status_left,
            text="Ziehe Audiodateien hinein oder setze zuerst den Release-Titel, damit der Flow direkt weiterlaufen kann.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.release_flow_hint_label.pack(fill="x", pady=(2, 0))

        self._status_primary_button = self.app.btn(
            status_right,
            "Distro-Export starten",
            self.app.release_ctrl.build_export,
            primary=True,
            width=190,
        )
        self._status_primary_button.pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(status_right, bg=PANEL_2)
        action_row.pack(anchor="e")
        self._status_action_bar = action_row
        self._status_action_buttons = (
            self.app.btn(action_row, "In AKM laden", lambda: self.app.release_ctrl.import_release_to_batch(open_batch=True), quiet=True, width=122),
            self.app.btn(action_row, "Cover-Preview", self.app.release_ctrl.open_cover_dialog, quiet=True, width=122),
            self.app.btn(action_row, "Finder", self.app.release_ctrl.open_cover_in_finder, quiet=True, width=84),
        )

    def _build_scroll_content(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        top = scroll_root.scrollable_frame
        top.configure(padx=SPACE_MD, pady=0)
        return scroll_root, top

    def _build_release_cards(self, top, scroll_root):
        left_card = AkmCard(top)
        right_card = AkmCard(top)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))
        self._release_cards = (left_card, right_card)
        scroll_root.canvas.bind("<Configure>", self._on_responsive_resize, add="+")
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

        self._build_release_meta_card(left_card)
        self._build_release_track_card(right_card)

    def _build_release_meta_card(self, left_card):
        self._left_intro_label = AkmSubLabel(
            left_card.inner,
            text="Metadaten, Cover und Zielordner werden hier einmal sauber gesetzt.",
            bg=PANEL_2,
            justify="left",
            wraplength=360,
        )
        self._left_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_SM))

        left_form = AkmForm(left_card.inner, padx=CARD_PAD_X, pady=0)
        left_form.pack(fill="both", expand=True)
        left_form.add_header("Release-Basis")
        self._build_release_form_rows(left_form)

    def _build_release_form_rows(self, left_form):
        defaults = akm_core.get_release_memory()

        for key, label in RELEASE_FORM_FIELDS:
            var = self._create_release_var(key, defaults.get(key, ""))
            if key == "cover_path":
                left_form.add_row(
                    label,
                    lambda parent, current_var=var: self._create_cover_field(parent, current_var),
                )
            elif key == "export_dir":
                left_form.add_row(
                    label,
                    lambda parent, current_var=var: self._create_export_field(parent, current_var),
                )
            else:
                left_form.add_entry(label, var, font=FONT_SM)

    def _create_cover_field(self, parent, variable):
        wrap = tk.Frame(parent, bg=PANEL_2)
        AkmEntry(wrap, textvariable=variable, font=FONT_SM).pack(side="left", fill="x", expand=True)
        self.app.btn(wrap, "Wählen", self.app.release_ctrl.choose_cover, primary=True, width=92).pack(side="left", padx=(SPACE_XS, 0))
        self.app.btn(wrap, "Preview", self.app.release_ctrl.open_cover_dialog, quiet=True, width=92).pack(side="left", padx=(SPACE_XS, 0))
        return wrap

    def _create_export_field(self, parent, variable):
        wrap = tk.Frame(parent, bg=PANEL_2)
        AkmEntry(wrap, textvariable=variable, font=FONT_SM).pack(side="left", fill="x", expand=True)
        self.app.btn(wrap, "Wählen", self.app.release_ctrl.choose_export_dir, primary=True, width=92).pack(side="left", padx=(SPACE_XS, 0))
        return wrap

    def _build_release_track_card(self, right_card):
        AkmLabel(right_card.inner, text="Release-Zusammenstellung", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_MD))
        self._right_intro_label = AkmSubLabel(
            right_card.inner,
            text="Ziehe fertige Audiodateien direkt in die Liste. Exakte Titel werden automatisch auf Werke gemappt.",
            bg=PANEL_2,
            justify="left",
            wraplength=380,
        )
        self._right_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self._build_drop_zone(right_card)
        self._build_track_list(right_card)
        self._build_track_actions(right_card)
        right_card.bind("<Configure>", self._on_action_bar_resize, add="+")
        self.after_idle(lambda: self._apply_release_action_layout(right_card.winfo_width()))

    def _build_drop_zone(self, right_card):
        drop_zone = tk.Frame(right_card.inner, bg=FIELD_BG, highlightbackground="#2E323A", highlightthickness=1)
        drop_zone.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        AkmLabel(
            drop_zone,
            text="DROP ZONE",
            fg=ACCENT,
            bg=FIELD_BG,
            font=FONT_BOLD,
        ).pack(anchor="w", padx=12, pady=(10, 0))
        self._drop_zone_hint_label = AkmSubLabel(
            drop_zone,
            text="WAV, AIFF, MP3, FLAC oder M4A hier ablegen. Dubletten werden automatisch uebersprungen.",
            bg=FIELD_BG,
            justify="left",
            wraplength=360,
        )
        self._drop_zone_hint_label.pack(anchor="w", padx=12, pady=(2, 10))

    def _build_track_list(self, right_card):
        list_frame = AkmPanel(right_card.inner, bg=PANEL_2)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.release_track_listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, relief="flat", exportselection=False,
            font=FONT_SM, selectbackground=ACCENT, selectforeground="black",
            highlightthickness=0, activestyle="none", selectmode="extended"
        )
        self.release_track_listbox.pack(side="left", fill="both", expand=True)
        self.release_track_listbox.bind("<<ListboxSelect>>", lambda _event: self._update_track_selection_hint())
        scrollbar = tk.Scrollbar(list_frame, command=self.release_track_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.release_track_listbox.config(yscrollcommand=scrollbar.set)

    def _build_track_actions(self, right_card):
        tk_actions = AkmPanel(right_card.inner, bg=PANEL_2)
        tk_actions.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._release_action_bar = tk_actions
        self._release_action_buttons = (
            self.app.btn(tk_actions, "Nach oben", self.app.release_ctrl.move_track_up, quiet=True, width=108),
            self.app.btn(tk_actions, "Nach unten", self.app.release_ctrl.move_track_down, quiet=True, width=108),
            self.app.btn(tk_actions, "Entfernen", self.app.release_ctrl.remove_track, quiet=True, width=108),
        )
        self.release_selection_hint_label = AkmSubLabel(
            right_card.inner,
            text="Noch keine Tracks im Release. Ziehe Dateien hinein oder übernimm gematchte Werke.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=420,
        )
        self.release_selection_hint_label.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

    def _create_release_var(self, key, default_value=""):
        cache = getattr(self.app, "release_state_cache", {}) or {}
        initial_value = cache.get(key, default_value)
        var = tk.StringVar(value=initial_value)
        self.release_vars[key] = var

        if hasattr(self.app, "release_state_cache"):
            self.app.release_state_cache[key] = initial_value
            var.trace_add(
                "write",
                lambda *_args, cache_key=key, cache_var=var: self.app.release_state_cache.__setitem__(
                    cache_key,
                    cache_var.get(),
                ),
            )
        if key in akm_core.RELEASE_MEMORY_DEFAULTS:
            var.trace_add("write", lambda *_args: self._queue_release_memory_save())
        var.trace_add("write", lambda *_args: self._queue_release_refresh())
        return var

    def _queue_release_refresh(self):
        if hasattr(self.app, "release_ctrl"):
            self.after_idle(self.app.release_ctrl.refresh_view)

    def _queue_release_memory_save(self):
        if self._release_memory_after_id:
            self.after_cancel(self._release_memory_after_id)
        self._release_memory_after_id = self.after(300, self._save_release_memory)

    def _save_release_memory(self):
        self._release_memory_after_id = None
        akm_core.remember_release_memory(self.get_form_state())

    def _on_responsive_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_button_bar(self, container, buttons, width, breakpoint, state_attr, row_spacing=SPACE_XS, anchor="w"):
        current_mode = getattr(self, state_attr, None)
        mode = ui_patterns.apply_button_bar_layout(
            container,
            buttons,
            width,
            breakpoint,
            current_mode,
            row_spacing=row_spacing,
            anchor=anchor,
        )
        setattr(self, state_attr, mode)
        return mode

    def _apply_responsive_layout(self, width):
        if not hasattr(self, "_release_cards"):
            return
        left_card, right_card = self._release_cards
        self._release_layout_mode = ui_patterns.apply_widget_layout(
            width,
            self.STACK_BREAKPOINT,
            self._release_layout_mode,
            {
                "stack": (
                    (left_card, {"fill": "x", "expand": False, "pady": (0, CARD_GAP)}),
                    (right_card, {"fill": "x", "expand": False}),
                ),
                "split": (
                    (left_card, {"side": "left", "fill": "both", "expand": True, "padx": (0, CARD_GAP // 2)}),
                    (right_card, {"side": "left", "fill": "both", "expand": True, "padx": (CARD_GAP // 2, 0)}),
                ),
            },
            narrow_mode="stack",
            wide_mode="split",
        )

        self._apply_status_actions_layout(width)
        self._update_wraplengths(width)

    def _update_wraplengths(self, width):
        column_width = width if self._release_layout_mode == "stack" else max(340, (width - CARD_GAP) // 2)
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=280, maximum=820)
        fit_wraplength(self.release_status_label, width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self.release_preflight_label, width, padding=280, minimum=260, maximum=640)
        fit_wraplength(self.release_action_hint_label, width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self.release_flow_hint_label, width, padding=280, minimum=260, maximum=640)
        fit_wraplength(self._left_intro_label, column_width, padding=80, minimum=260, maximum=460)
        fit_wraplength(self._right_intro_label, column_width, padding=80, minimum=260, maximum=480)
        fit_wraplength(self._drop_zone_hint_label, column_width, padding=120, minimum=240, maximum=420)
        fit_wraplength(self.release_selection_hint_label, column_width, padding=80, minimum=260, maximum=460)

    def has_track_list(self):
        return True

    def render_release_state(self, track_labels, action_hint, preflight_text, flow_hint, status_text):
        self.release_track_listbox.delete(0, tk.END)
        if track_labels:
            self.release_track_listbox.insert(tk.END, *track_labels)
        self.release_action_hint_label.config(text=action_hint)
        self.release_preflight_label.config(text=preflight_text)
        self.release_flow_hint_label.config(text=flow_hint)
        self.release_status_label.config(text=status_text)
        self._update_track_selection_hint()

    def _update_track_selection_hint(self):
        track_count = self.release_track_listbox.size()
        selection = self.release_track_listbox.curselection()
        from app_ui import release_view_tools

        self.release_selection_hint_label.config(
            text=release_view_tools.build_release_selection_hint(track_count, selection)
        )

    def get_form_vars(self):
        return self.release_vars

    def get_form_state(self):
        return {key: var.get() for key, var in self.release_vars.items()}

    def set_form_state(self, values):
        for key, value in (values or {}).items():
            if key in self.release_vars:
                self.release_vars[key].set(value)

    def get_form_value(self, key):
        var = self.release_vars.get(key)
        return var.get().strip() if var else ""

    def set_form_value(self, key, value):
        if key in self.release_vars:
            self.release_vars[key].set(value)

    def get_selected_track_indices(self):
        return tuple(self.release_track_listbox.curselection())

    def select_track_index(self, index):
        self.release_track_listbox.selection_set(index)

    def _on_action_bar_resize(self, event):
        self._apply_release_action_layout(event.width)

    def _apply_release_action_layout(self, width):
        if not hasattr(self, "_release_action_buttons"):
            return
        self._apply_button_bar(
            self._release_action_bar,
            self._release_action_buttons,
            width,
            self.ACTION_STACK_BREAKPOINT,
            "_release_action_mode",
            row_spacing=SPACE_XS,
        )

    def _apply_status_actions_layout(self, width):
        if not hasattr(self, "_status_action_buttons"):
            return
        target_mode = ui_patterns.resolve_layout_mode(
            width,
            self.STATUS_ACTION_STACK_BREAKPOINT,
        )
        if target_mode == self._status_action_mode:
            return

        self._status_primary_button.pack_forget()
        self._status_action_bar.pack_forget()

        if target_mode == "stack":
            self._status_primary_button.pack(anchor="e", fill="x", pady=(0, SPACE_XS))
        else:
            self._status_primary_button.pack(anchor="e", pady=(0, SPACE_XS))

        self._apply_button_bar(
            self._status_action_bar,
            self._status_action_buttons,
            width,
            self.STATUS_ACTION_STACK_BREAKPOINT,
            "_status_action_mode",
            row_spacing=SPACE_XS,
            anchor="e",
        )

    def _setup_dnd(self):
        try:
            from tkinterdnd2 import DND_FILES
            self.release_track_listbox.drop_target_register(DND_FILES)
            self.release_track_listbox.dnd_bind('<<Drop>>', self.app.release_ctrl.handle_drop)
            self.app.append_log("Release DnD bereit.")
        except Exception:
            pass
