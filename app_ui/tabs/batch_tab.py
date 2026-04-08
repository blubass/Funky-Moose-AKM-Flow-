import tkinter as tk
from tkinter import ttk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmSuccessIndicator,
    ACCENT, PANEL, PANEL_2, TEXT,
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_XL, FONT_LG, FONT_XXL
)


class BatchTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._batch_action_buttons = []
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_dnd()
        self.app._set_batch_buttons_enabled = self._set_batch_buttons_enabled
        self._set_batch_buttons_enabled(False)

    def build_ui(self):
        AkmHeader(self, text="AKM Batch").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(
            self,
            text="Arbeite fokussiert durch offene Werke: Titel kopieren, Dauer mitnehmen und danach direkt als gemeldet markieren.",
            wraplength=760, justify="left"
        ).pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(self, height=118)
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

        self.app.btn(status_right, "Neu laden", self.app.reload_flow_data, primary=True, width=118).pack(anchor="e", pady=(0, SPACE_XS))
        status_actions = tk.Frame(status_right, bg=PANEL_2)
        status_actions.pack(anchor="e")
        self.app.btn(status_actions, "Excel importieren", self.app.import_excel, quiet=True, width=132).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(status_actions, "Werk anlegen", lambda: self.app.add(self.app.batch_entry.get().strip()), quiet=True, width=126).pack(side="left")

        # --- FOCUS CARD ---
        focus_card = AkmCard(self)
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

        self.app.copy_button = self.app.btn(btn_row, "Titel kopieren", self.app.flow_copy, primary=True)
        self.app.copy_button.pack(side="left", padx=(0, SPACE_XS))
        self._batch_action_buttons.append(self.app.copy_button)
        submit_button = self.app.btn(btn_row, "Als gemeldet", self.app.flow_submit, primary=True)
        submit_button.pack(side="left", padx=SPACE_SM)
        self._batch_action_buttons.append(submit_button)
        next_button = self.app.btn(btn_row, "Weiter →", self.app.flow_next, primary=True)
        next_button.pack(side="left", padx=SPACE_SM)
        self._batch_action_buttons.append(next_button)
        reload_button = self.app.btn(btn_row, "Neu laden", self.app.reload_flow_data, quiet=True)
        reload_button.pack(side="left", padx=SPACE_SM)

        # --- PROGRESS CARD ---
        progress_card = AkmCard(self)
        progress_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(progress_card.inner, text="Fortschritt", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )

        self.app.progress_label = AkmLabel(progress_card.inner, text="0 / 0", fg=TEXT, bg=PANEL_2, font=FONT_BOLD)
        self.app.progress_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))

        self.app.progress = ttk.Progressbar(progress_card.inner, length=420)
        self.app.progress.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        # --- QUICK-ADD CARD ---
        add_card = AkmCard(self)
        add_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(add_card.inner, text="Werk schnell anlegen", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )
        AkmSubLabel(
            add_card.inner,
            text="Ideal, wenn beim Batch-Durchlauf spontan noch ein Titel ergänzt werden muss.",
            bg=PANEL_2,
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        add_row = AkmPanel(add_card.inner, bg=PANEL_2)
        add_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        self.app.batch_entry = AkmEntry(add_row, width=40)
        self.app.batch_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACE_SM))
        self.app.batch_entry.bind("<Return>", lambda _event: self.app.add(self.app.batch_entry.get().strip()))
        self.app.btn(add_row, "+ Werk anlegen", lambda: self.app.add(self.app.batch_entry.get().strip()), primary=True).pack(side="left")

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
