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
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_dnd()

    def build_ui(self):
        AkmHeader(self, text="AKM Batch").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(
            self,
            text="Arbeite fokussiert durch offene Werke: Titel kopieren, Dauer mitnehmen und danach direkt als gemeldet markieren.",
            wraplength=760, justify="left"
        ).pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        # --- FOCUS CARD ---
        focus_card = AkmCard(self)
        focus_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(focus_card, text="Aktuelles Werk", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 0)
        )

        self.app.flow_title = AkmHeader(focus_card, text="Lade Werk...", fg=ACCENT, bg=PANEL_2)
        self.app.flow_title.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))

        meta_row = tk.Frame(focus_card, bg=PANEL_2)
        meta_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_MD))
        self.app.flow_meta = AkmSubLabel(meta_row, text="", bg=PANEL_2)
        self.app.flow_meta.pack(side="left")

        btn_row = AkmPanel(focus_card, bg=PANEL_2)
        btn_row.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        self.app.copy_button = self.app.btn(btn_row, "Titel kopieren", self.app.flow_copy, primary=True)
        self.app.copy_button.pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(btn_row, "Als gemeldet", self.app.flow_submit, primary=True).pack(side="left", padx=SPACE_SM)
        self.app.btn(btn_row, "Weiter →", self.app.flow_next, primary=True).pack(side="left", padx=SPACE_SM)
        self.app.btn(btn_row, "Neu laden", self.app.reload_flow_data, quiet=True).pack(side="left", padx=SPACE_SM)

        # --- PROGRESS CARD ---
        progress_card = AkmCard(self)
        progress_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(progress_card, text="Fortschritt", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )

        self.app.progress_label = AkmLabel(progress_card, text="0 / 0", fg=TEXT, bg=PANEL_2, font=FONT_BOLD)
        self.app.progress_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))

        self.app.progress = ttk.Progressbar(progress_card, length=420)
        self.app.progress.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        # --- QUICK-ADD CARD ---
        add_card = AkmCard(self)
        add_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(add_card, text="Werk schnell anlegen", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )

        add_row = AkmPanel(add_card, bg=PANEL_2)
        add_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        self.app.entry = AkmEntry(add_row, width=40)
        self.app.entry.pack(side="left", fill="x", expand=True, padx=(0, SPACE_SM))
        self.app.entry.bind("<Return>", lambda e: self.app.add())
        self.app.btn(add_row, "+ Werk anlegen", self.app.add, primary=True).pack(side="left")

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
