import tkinter as tk
from tkinter import ttk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmSuccessIndicator, AkmScrollablePanel,
    ACCENT, PANEL, PANEL_2, TEXT,
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_XL, FONT_LG, FONT_XXL, fit_wraplength
)


class BatchTab(AkmPanel):
    ACTION_STACK_BREAKPOINT = 780

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._batch_action_buttons = []
        self._status_action_mode = None
        self._focus_action_mode = None
        self._quick_add_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_dnd()
        self.app._set_batch_buttons_enabled = self._set_batch_buttons_enabled
        self._set_batch_buttons_enabled(False)

    def build_ui(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        page = scroll_root.scrollable_frame

        AkmHeader(page, text="AKM Batch").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text="Arbeite fokussiert durch offene Werke: Titel kopieren, Dauer mitnehmen und danach direkt als gemeldet markieren.",
            wraplength=760, justify="left"
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(page, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Flow Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.app.batch_status_label = AkmLabel(
            status_left,
            text="Keine offenen Batch-Werke",
            fg=TEXT,
            bg=PANEL_2,
            font=FONT_BOLD,
            anchor="w",
        )
        self.app.batch_status_label.pack(fill="x", pady=(2, 2))
        self.app.batch_hint_label = AkmSubLabel(
            status_left,
            text="Importiere Excel oder lege neue Werke an, dann füllt sich die Queue automatisch.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.app.batch_hint_label.pack(fill="x")
        self.app.batch_meta_label = AkmSubLabel(
            status_left,
            text="In Arbeit: 0   •   Bereit: 0   •   Queue: 0",
            bg=PANEL_2,
            anchor="w",
        )
        self.app.batch_meta_label.pack(fill="x", pady=(2, 0))

        self._reload_status_button = self.app.btn(status_right, "Neu laden", self.app.reload_flow_data, primary=True, width=118)
        self._reload_status_button.pack(anchor="e", pady=(0, SPACE_XS))
        status_actions = tk.Frame(status_right, bg=PANEL_2)
        status_actions.pack(anchor="e")
        self._status_action_bar = status_actions
        self._status_action_buttons = (
            self.app.btn(status_actions, "Excel importieren", self.app.import_excel, quiet=True, width=132),
            self.app.btn(status_actions, "Werk anlegen", lambda: self.app.add(self.app.batch_entry.get().strip()), quiet=True, width=126),
        )

        # --- FOCUS CARD ---
        focus_card = AkmCard(page)
        focus_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(focus_card.inner, text="Aktuelles Werk", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 0)
        )

        self.app.flow_title = AkmHeader(focus_card.inner, text="Lade Werk...", fg=ACCENT, bg=PANEL_2)
        self.app.flow_title.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))

        meta_row = tk.Frame(focus_card.inner, bg=PANEL_2)
        meta_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_MD))
        self.app.flow_meta = AkmSubLabel(meta_row, text="", bg=PANEL_2)
        self.app.flow_meta.pack(side="left")

        btn_row = AkmPanel(focus_card.inner, bg=PANEL_2)
        btn_row.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._focus_action_bar = btn_row

        self.app.copy_button = self.app.btn(btn_row, "Titel kopieren", self.app.flow_copy, primary=True)
        self._batch_action_buttons.append(self.app.copy_button)
        submit_button = self.app.btn(btn_row, "Als gemeldet", self.app.flow_submit, primary=True)
        self._batch_action_buttons.append(submit_button)
        next_button = self.app.btn(btn_row, "Weiter →", self.app.flow_next, primary=True)
        self._batch_action_buttons.append(next_button)
        reload_button = self.app.btn(btn_row, "Neu laden", self.app.reload_flow_data, quiet=True)
        self._focus_action_buttons = (
            self.app.copy_button,
            submit_button,
            next_button,
            reload_button,
        )

        # --- PROGRESS CARD ---
        progress_card = AkmCard(page)
        progress_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(progress_card.inner, text="Fortschritt", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )

        self.app.progress_label = AkmLabel(progress_card.inner, text="0 / 0", fg=TEXT, bg=PANEL_2, font=FONT_BOLD)
        self.app.progress_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))

        self.app.progress = ttk.Progressbar(progress_card.inner, length=420)
        self.app.progress.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        # --- QUICK-ADD CARD ---
        add_card = AkmCard(page)
        add_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(add_card.inner, text="Werk schnell anlegen", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )
        self._quick_add_intro_label = AkmSubLabel(
            add_card.inner,
            text="Ideal, wenn beim Batch-Durchlauf spontan noch ein Titel ergänzt werden muss.",
            bg=PANEL_2,
            justify="left",
        )
        self._quick_add_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        add_row = AkmPanel(add_card.inner, bg=PANEL_2)
        add_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._quick_add_bar = add_row

        self.app.batch_entry = AkmEntry(add_row, width=40)
        self.app.batch_entry.bind("<Return>", lambda _event: self.app.add(self.app.batch_entry.get().strip()))
        self._quick_add_button = self.app.btn(add_row, "+ Werk anlegen", lambda: self.app.add(self.app.batch_entry.get().strip()), primary=True)
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_button_bar(self._status_action_bar, self._status_action_buttons, width, "_status_action_mode")
        self._apply_button_bar(self._focus_action_bar, self._focus_action_buttons, width, "_focus_action_mode")
        self._apply_quick_add_layout(width)
        self._update_wraplengths(width)

    def _apply_button_bar(self, container, buttons, width, state_attr):
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if getattr(self, state_attr) == target_mode:
            return
        setattr(self, state_attr, target_mode)
        for button in buttons:
            button.pack_forget()
        if target_mode == "stack":
            container.pack(anchor="w", fill="x")
            for index, button in enumerate(buttons):
                button.pack(fill="x", pady=(0, SPACE_XS if index < len(buttons) - 1 else 0))
            return
        container.pack(anchor="w")
        for index, button in enumerate(buttons):
            pad_left = 0 if index == 0 else SPACE_SM
            button.pack(side="left", padx=(pad_left, 0))

    def _apply_quick_add_layout(self, width):
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if target_mode == self._quick_add_mode:
            return
        self._quick_add_mode = target_mode
        self.app.batch_entry.pack_forget()
        self._quick_add_button.pack_forget()
        if target_mode == "stack":
            self.app.batch_entry.pack(fill="x", expand=True, pady=(0, SPACE_XS), ipady=2)
            self._quick_add_button.pack(fill="x")
            return
        self.app.batch_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACE_SM))
        self._quick_add_button.pack(side="left")

    def _update_wraplengths(self, width):
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=300, maximum=840)
        fit_wraplength(self.app.batch_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self._quick_add_intro_label, width, padding=120, minimum=280, maximum=620)

    def _setup_dnd(self):
        try:
            from tkinterdnd2 import DND_FILES
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_dnd_drop)
        except Exception:
            pass

    def _on_dnd_drop(self, event):
        data = event.data
        if not data:
            return
        try:
            files = self.tk.splitlist(data)
            excel_files = [f.strip("\"'") for f in files if f.lower().endswith((".xlsx", ".xls"))]
            if excel_files:
                self.app.import_excel_path(excel_files[0])
            else:
                self.app.append_log(f"Batch DnD: {len(files)} Dateien ignoriert (nur .xlsx unterstützt).")
        except Exception as e:
            self.app.append_log(f"Batch DnD Fehler: {e}")

    def _set_batch_buttons_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for button in self._batch_action_buttons:
            try:
                button.config(state=state)
            except Exception:
                pass
