import tkinter as tk
from tkinter import ttk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm, AkmEntry, AkmCheckbutton,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, LOG_BG, LOG_FG,
    SPACE_MD, SPACE_SM, SPACE_XS, SPACE_LG, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_XL, FONT_LG
)

class LoudnessTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        AkmHeader(self, text="Lautheit / Match-Export").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Analysiere LUFS und True Peak, exportiere Match-Dateien und rueckverlinke Ergebnisse direkt in die Werke.", wraplength=760, justify="left").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        action_card = AkmCard(self)
        action_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))

        AkmLabel(action_card, text="Ablauf", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        self.app.loudness_hint_label = AkmSubLabel(action_card, text="1. Dateien laden  2. Analyse starten  3. Match-Export bauen", bg=PANEL_2, anchor="w", justify="left")
        self.app.loudness_hint_label.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        controls = AkmPanel(action_card, bg=PANEL_2)
        controls.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_XS))
        self.app.loudness_choose_btn = self.app.btn(controls, "Dateien wählen", self.app.loudness_choose_files, primary=True)
        self.app.loudness_choose_btn.pack(side="left", padx=(0, SPACE_XS))
        self.app.loudness_analyze_btn = self.app.btn(controls, "Analyse starten", self.app.loudness_analyze_files, primary=True)
        self.app.loudness_analyze_btn.pack(side="left", padx=SPACE_XS)
        self.app.loudness_export_btn = self.app.btn(controls, "Match-Export", self.app.loudness_export_files, primary=True)
        self.app.loudness_export_btn.pack(side="left", padx=SPACE_XS)

        import_row = AkmPanel(action_card, bg=PANEL_2)
        import_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.app.btn(import_row, "Aus Auswahl übernehmen", self.app.loudness_import_selected_work).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(import_row, "Alle gefilterten Werke", self.app.loudness_import_filtered_works, quiet=True).pack(side="left", padx=SPACE_XS)

        # SETTINGS FORM
        settings_card = AkmCard(self)
        settings_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        
        settings_form = AkmForm(settings_card, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        settings_form.pack(fill="x")
        settings_form.add_header("Analyse & Export")
        
        self.app.loudness_target_var = tk.StringVar(value="-14.0")
        settings_form.add_entry("Ziel LUFS", self.app.loudness_target_var, width=10)
        
        self.app.loudness_peak_var = tk.StringVar(value="-1.0")
        settings_form.add_entry("True Peak Ceiling (dBTP)", self.app.loudness_peak_var, width=10)
        
        self.app.loudness_use_limiter_var = tk.BooleanVar(value=True)
        settings_form.add_checkbox("Limiter nur bei Peak-Warnung", self.app.loudness_use_limiter_var)
        
        self.app.loudness_auto_link_var = tk.BooleanVar(value=True)
        settings_form.add_checkbox("Nach Export automatisch rückverlinken", self.app.loudness_auto_link_var)

        # TREEVIEW
        tree_frame = AkmPanel(self)
        tree_frame.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_SM))

        cols = ("filename", "duration", "lufs", "peak", "sample", "gain", "predicted_tp", "status", "limit", "export_info")
        self.app.loudness_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        headers = {"filename": "Datei", "duration": "Dauer", "lufs": "LUFS", "peak": "TP", "sample": "SP", "gain": "Gain", "predicted_tp": "Z-TP", "status": "Match", "limit": "Lim", "export_info": "Export"}
        for col, head in headers.items():
            self.app.loudness_tree.heading(col, text=head)
            self.app.loudness_tree.column(col, width=80, anchor="center")
        self.app.loudness_tree.column("filename", width=180, anchor="w")
        
        from app_ui.ui_patterns import FLAVOR_WARN, FLAVOR_INFO, FLAVOR_SUCCESS, FLAVOR_ERROR, blend_color
        self.app.loudness_tree.tag_configure("peak_warn", background=blend_color("#f7f7f7", FLAVOR_WARN, 0.42), foreground="#111111")
        self.app.loudness_tree.tag_configure("match_ok", background=blend_color("#f7f7f7", FLAVOR_INFO, 0.28), foreground="#111111")
        self.app.loudness_tree.tag_configure("exported", background=blend_color("#f7f7f7", FLAVOR_SUCCESS, 0.28), foreground="#111111")
        self.app.loudness_tree.tag_configure("error", background=blend_color("#f7f7f7", FLAVOR_ERROR, 0.30), foreground="#111111")
        
        self.app.loudness_tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(tree_frame, command=self.app.loudness_tree.yview)
        sb.pack(side="right", fill="y")
        self.app.loudness_tree.config(yscrollcommand=sb.set)

        log_card = AkmCard(self)
        log_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self.app.loudness_status_label = AkmLabel(log_card, text="Bereit", bg=PANEL_2, anchor="w")
        self.app.loudness_status_label.pack(fill="x", padx=CARD_PAD_X, pady=SPACE_SM)
        self.app.loudness_log = tk.Text(log_card, height=4, bg=LOG_BG, fg=LOG_FG, relief="flat", font=("Courier", 9))
        self.app.loudness_log.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
