import tkinter as tk
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm,
    AkmEntry, AkmText, AkmCheckbutton,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_GAP, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_XL, FONT_LG
)
from app_logic import detail_tools

class DetailsTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()

    def build_ui(self):
        AkmHeader(self, text="Werkdetails").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Metadaten, Notizen und Status an einem Ort pflegen.").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        content = scroll_root.scrollable_frame
        content.configure(padx=SPACE_MD, pady=0)

        left_card = AkmCard(content)
        right_card = AkmCard(content)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))

        # LEFT FORM
        left_form = AkmForm(left_card, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        left_form.pack(fill="both", expand=True)
        left_form.add_header("Basis")

        for key, label in detail_tools.DETAIL_FIELD_LABELS:
            var = tk.StringVar()
            self.app.detail_vars[key] = var
            
            if key == "audio_path":
                def _create_audio_field(parent):
                    wrap = tk.Frame(parent, bg=PANEL_2)
                    entry = AkmEntry(wrap, textvariable=var)
                    entry.pack(side="left", fill="x", expand=True)
                    self.app.btn(wrap, "Wählen", self.app.choose_audio_path_for_details, primary=True).pack(side="left", padx=(SPACE_XS, 0))
                    self.app.btn(wrap, "Finder", self.app.open_audio_path_in_finder, quiet=True).pack(side="left", padx=(SPACE_XS, 0))
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
            self.app.btn(btn_row, "In Arbeit", lambda: self.app.set_detail_status("in_progress"), quiet=True).pack(side="left", padx=(0, SPACE_XS))
            self.app.btn(btn_row, "Bereit", lambda: self.app.set_detail_status("ready")).pack(side="left", padx=SPACE_XS)
            self.app.btn(btn_row, "Bestätigt", lambda: self.app.set_detail_status("confirmed")).pack(side="left", padx=SPACE_XS)
            return wrap
        
        left_form.add_row("Status", _create_status_row)

        # RIGHT FORM
        right_form = AkmForm(right_card, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        right_form.pack(fill="both", expand=True)
        right_form.add_header("Tags & Notizen")
        
        self.app.detail_tags = right_form.add_text("Tags (Kommata)", height=4)
        self.app.detail_notes = right_form.add_text("Notizen", height=12)

        # GLOBAL ACTIONS
        actions = AkmPanel(self)
        actions.pack(anchor="w", padx=SPACE_MD, pady=SPACE_SM)
        self.app.btn(actions, "Speichern", self.app.save_details, primary=True).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(actions, "Zurücksetzen", self.app.clear_details_form, quiet=True).pack(side="left", padx=SPACE_XS)
