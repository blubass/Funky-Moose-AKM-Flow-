import os
import tkinter as tk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm,
    AkmEntry, AkmText, AkmCheckbutton, AkmScrollablePanel,
    fit_wraplength,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_GAP, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_MD_BOLD, FONT_XL, FONT_LG
)
from app_logic import detail_tools

class DetailsTab(AkmPanel):
    STACK_BREAKPOINT = 1180
    ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._detail_layout_mode = None
        self._status_action_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_dnd()
        self._setup_state_traces()
        self._update_detail_radar()

    def refresh_view(self):
        """Refresh summary UI that depends on the current form state."""
        self._update_detail_radar()

    def _setup_dnd(self):
        try:
            from tkinterdnd2 import DND_FILES
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_dnd_drop)
        except: pass

    def _on_dnd_drop(self, event):
        data = event.data
        if not data: return
        try:
            files = self.app.tasks.parse_dnd_files(data)
            if files:
                f = files[0]
                # Trigger the controller's logic with the dropped path
                self.app.details_ctrl.handle_audio_drop(f)
        except Exception: pass

    def build_ui(self):
        AkmHeader(self, text="Werkdetails").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            self,
            text="Metadaten, Notizen und Status an einem Ort pflegen.",
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(self, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Werk Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.app.details_status_label = AkmLabel(
            status_left,
            text="Noch kein Werk geladen",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
            justify="left",
        )
        self.app.details_status_label.pack(fill="x", pady=(2, 2))
        self.app.details_hint_label = AkmSubLabel(
            status_left,
            text="Wähle ein bestehendes Werk, lege einen Titel an oder ziehe eine Audiodatei direkt auf den Tab.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.app.details_hint_label.pack(fill="x")
        self.app.details_context_label = AkmSubLabel(
            status_left,
            text="Audio: keines   •   Status: —   •   Instrumental: Nein",
            bg=PANEL_2,
            anchor="w",
            justify="left",
        )
        self.app.details_context_label.pack(fill="x", pady=(2, 0))

        self.app.btn(status_right, "Speichern", self.app.details_ctrl.save_details, primary=True, width=126).pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(status_right, bg=PANEL_2)
        action_row.pack(anchor="e")
        self._status_action_bar = action_row
        self._status_action_buttons = (
            self.app.btn(action_row, "Audio wählen", self.app.details_ctrl.choose_audio_path, quiet=True, width=118),
            self.app.btn(action_row, "Finder", self.app.details_ctrl.open_audio_path_in_finder, quiet=True, width=84),
            self.app.btn(action_row, "Zurück", self.app.details_ctrl.clear_details_form, quiet=True, width=84),
        )

        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        content = scroll_root.scrollable_frame
        content.configure(padx=SPACE_MD, pady=0)

        left_card = AkmCard(content)
        right_card = AkmCard(content)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))
        self._detail_cards = (left_card, right_card)
        scroll_root.canvas.bind("<Configure>", self._on_responsive_resize, add="+")
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

        # LEFT FORM
        self._left_intro_label = AkmSubLabel(
            left_card.inner,
            text="Titel, Audio, Credits und Status bleiben hier in einer sauberen Arbeitsansicht gebündelt.",
            bg=PANEL_2,
            justify="left",
            wraplength=360,
        )
        self._left_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_SM))
        left_form = AkmForm(left_card.inner, padx=CARD_PAD_X, pady=0)
        left_form.pack(fill="both", expand=True)
        left_form.add_header("Werksteuerung")

        for key, label in detail_tools.DETAIL_FIELD_LABELS:
            var = tk.StringVar()
            self.app.detail_vars[key] = var
            
            if key == "title":
                # Special Case: Title is a Combobox for quick selection/search
                self.app.detail_title_combo = left_form.add_combobox(label, var, [])
                self.app.detail_title_combo.bind("<<ComboboxSelected>>", lambda e: self.app.details_ctrl.load_selected_title())
            elif key == "audio_path":
                def _create_audio_field(parent):
                    wrap = tk.Frame(parent, bg=PANEL_2)
                    entry = AkmEntry(wrap, textvariable=var)
                    entry.pack(side="left", fill="x", expand=True)
                    self.app.btn(wrap, "Wählen", self.app.details_ctrl.choose_audio_path, primary=True).pack(side="left", padx=(SPACE_XS, 0))
                    self.app.btn(wrap, "Finder", self.app.details_ctrl.open_audio_path_in_finder, quiet=True).pack(side="left", padx=(SPACE_XS, 0))
                    return wrap
                left_form.add_row(label, _create_audio_field)
            else:
                left_form.add_entry(label, var)

        self.app.detail_instrumental_var = tk.BooleanVar(value=False)
        left_form.add_checkbox("Instrumental", self.app.detail_instrumental_var)

        # Status Chip Row (Custom row in form)
        def _create_status_row(parent):
            wrap = tk.Frame(parent, bg=PANEL_2)
            self.app.detail_status_var = tk.StringVar(value="—")
            self.app.detail_status_chip = tk.Label(
                wrap, textvariable=self.app.detail_status_var,
                fg=TEXT, bg=PANEL, font=FONT_BOLD,
                padx=12, pady=5, bd=1, relief="solid"
            )
            self.app.detail_status_chip.pack(anchor="w", pady=(0, SPACE_SM))
            
            btn_row = tk.Frame(wrap, bg=PANEL_2)
            btn_row.pack(anchor="w")
            self.app.btn(btn_row, "In Arbeit", lambda: self.app.details_ctrl.set_status_chip("in_progress"), quiet=True).pack(side="left", padx=(0, SPACE_XS))
            self.app.btn(btn_row, "Bereit", lambda: self.app.details_ctrl.set_status_chip("ready")).pack(side="left", padx=SPACE_XS)
            self.app.btn(btn_row, "Bestätigt", lambda: self.app.details_ctrl.set_status_chip("confirmed")).pack(side="left", padx=SPACE_XS)
            return wrap
        
        left_form.add_row("Status", _create_status_row)

        # RIGHT FORM
        AkmLabel(right_card.inner, text="Tags & Notizen", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        self._right_intro_label = AkmSubLabel(
            right_card.inner,
            text="Sammle Ideen, Produktionshinweise und Suchbegriffe so, dass spätere Übergaben leicht bleiben.",
            bg=PANEL_2,
            justify="left",
            wraplength=360,
        )
        self._right_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        right_form = AkmForm(right_card.inner, padx=CARD_PAD_X, pady=0)
        right_form.pack(fill="both", expand=True)
        self.app.detail_tags = right_form.add_text("Tags (Kommata)", height=4)
        self.app.detail_notes = right_form.add_text("Notizen", height=12)

        # GLOBAL ACTIONS
        actions = AkmPanel(self)
        actions.pack(anchor="w", padx=SPACE_MD, pady=SPACE_SM)
        self.app.btn(actions, "Speichern", self.app.details_ctrl.save_details, primary=True, width=118).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(actions, "Zurücksetzen", self.app.details_ctrl.clear_details_form, quiet=True, width=118).pack(side="left", padx=SPACE_XS)

    def _on_responsive_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        if not hasattr(self, "_detail_cards"):
            return
        target_mode = "stack" if width and width < self.STACK_BREAKPOINT else "split"
        if target_mode != self._detail_layout_mode:
            self._detail_layout_mode = target_mode

            left_card, right_card = self._detail_cards
            for card in self._detail_cards:
                card.pack_forget()

            if target_mode == "stack":
                left_card.pack(fill="x", expand=False, pady=(0, CARD_GAP))
                right_card.pack(fill="x", expand=False)
            else:
                left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
                right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))

        self._apply_status_actions_layout(width)
        self._update_wraplengths(width)

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

    def _update_wraplengths(self, width):
        column_width = width if self._detail_layout_mode == "stack" else max(340, (width - CARD_GAP) // 2)
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=280, maximum=780)
        fit_wraplength(self.app.details_status_label, width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self.app.details_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self.app.details_context_label, width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self._left_intro_label, column_width, padding=80, minimum=260, maximum=460)
        fit_wraplength(self._right_intro_label, column_width, padding=80, minimum=260, maximum=460)

    def _setup_state_traces(self):
        tracked = []
        for key in ("title", "audio_path", "composer", "duration", "year"):
            if key in self.app.detail_vars:
                tracked.append(self.app.detail_vars[key])
        if hasattr(self.app, "detail_instrumental_var"):
            tracked.append(self.app.detail_instrumental_var)
        if hasattr(self.app, "detail_status_var"):
            tracked.append(self.app.detail_status_var)

        for var in tracked:
            var.trace_add("write", lambda *args: self._update_detail_radar())

    def _detail_value(self, key):
        var = self.app.detail_vars.get(key)
        if not var:
            return ""
        return (var.get() or "").strip()

    def _update_detail_radar(self):
        title = self._detail_value("title")
        audio_path = self._detail_value("audio_path")
        composer = self._detail_value("composer")
        duration = self._detail_value("duration")
        year = self._detail_value("year")
        instrumental = bool(self.app.detail_instrumental_var.get()) if hasattr(self.app, "detail_instrumental_var") else False
        status_text = self.app.detail_status_var.get().strip() if hasattr(self.app, "detail_status_var") and self.app.detail_status_var.get() else "—"

        if not hasattr(self.app, "details_status_label"):
            return

        if title:
            headline = f"{title} | Status: {status_text}"
        else:
            headline = f"Noch kein Werk geladen | Status: {status_text}"
        self.app.details_status_label.config(text=headline)

        context_parts = []
        if composer:
            context_parts.append(f"Komponist: {composer}")
        if duration:
            context_parts.append(f"Dauer: {duration}")
        if year:
            context_parts.append(f"Jahr: {year}")
        context_parts.append(f"Instrumental: {'Ja' if instrumental else 'Nein'}")

        if audio_path:
            audio_name = os.path.basename(audio_path)
            if os.path.exists(audio_path):
                context_parts.insert(0, f"Audio: {audio_name}")
            else:
                context_parts.insert(0, f"Audio fehlt: {audio_name}")
        else:
            context_parts.insert(0, "Audio: keines")

        self.app.details_context_label.config(text="   •   ".join(context_parts))

        if not title and not audio_path:
            hint = "Wähle ein bestehendes Werk oder ziehe eine Audiodatei hier hinein, damit Titel und Dauer schneller zusammenfinden."
        elif audio_path and not os.path.exists(audio_path):
            hint = "Der gesetzte Audio-Pfad existiert nicht mehr. Prüfe die Datei oder verknüpfe das Werk neu."
        elif title and not audio_path:
            hint = "Die Metadaten stehen schon. Wenn du Audio verknüpfst, kann die App Dauer und Pfad direkt mitziehen."
        elif audio_path and not title:
            hint = "Audio ist da – gib dem Werk jetzt noch Titel, Credits und Status, dann ist der Datensatz rund."
        else:
            hint = "Werk und Audio sind verbunden. Jetzt noch Notizen, Tags oder Status nachziehen und sauber speichern."

        self.app.details_hint_label.config(text=hint)
