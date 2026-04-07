import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
from app_ui.ui_patterns import *
import app_ui.ui_patterns as ui_patterns
import app_logic.loudness_tools as loudness_tools
import app_logic.overview_tools as overview_tools
import app_logic.flow_tools as flow_tools
import app_workflows.loudness_workflows as loudness_workflows

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None

class LoudnessTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.wv_ref = None 
        self.build_ui()
        self._setup_dnd()

    def build_ui(self):
        # --- 1. WAVEFORM PROMINENCE (TOP) ---
        self.preview_card = AkmCard(self, height=240)
        self.preview_card.pack(fill="x", padx=SPACE_MD, pady=(SPACE_MD, SPACE_SM))
        
        inlay = tk.Frame(self.preview_card.inner, bg="#050507", padx=2, pady=2)
        inlay.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        
        self.waveform_container = tk.Frame(inlay, bg="#0A0A0E")
        self.waveform_container.pack(fill="both", expand=True)
        tk.Frame(inlay, bg="#1E1E22", height=1).place(relx=0, rely=0, relwidth=1)
        
        self.waveform_label = tk.Label(self.waveform_container, bg="#0A0A0E", fg=ui_patterns.ACCENT, 
                                      font=("Inter", 14, "bold"), text="WELLENFORM MASTER DISPLAY") 
        self.waveform_label.pack(fill="both", expand=True)

        # --- 2. MIDDLE ROW (Workflow | Status) ---
        mid_row = tk.Frame(self, bg=BG)
        mid_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        
        # Workflow (Narrower)
        action_card = AkmCard(mid_row, height=140)
        action_card.pack(side="left", fill="both", expand=True, padx=(0, SPACE_XS))
        AkmLabel(action_card.inner, text="Workflow", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(10, 0))
        
        controls = AkmPanel(action_card.inner, bg=PANEL_2)
        controls.pack(fill="x", padx=CARD_PAD_X, pady=(5, 5))
        self.app.loudness_choose_btn = self.app.btn(controls, "Wählen", self.app.loudness_choose_files, primary=True, width=80)
        self.app.loudness_choose_btn.pack(side="left", padx=(0, 2))
        self.app.btn(controls, "Löschen", self.app.loudness_delete_files, quiet=True, width=80).pack(side="left", padx=2)
        self.app.loudness_analyze_btn = self.app.btn(controls, "Analyse", self.app.loudness_analyze_files, primary=True, width=80)
        self.app.loudness_analyze_btn.pack(side="left", padx=2)
        self.app.loudness_export_btn = self.app.btn(controls, "Export", self.app.loudness_export_files, primary=True, width=80)
        self.app.loudness_export_btn.pack(side="left", padx=2)

        # Status / Log (Side-by-side with Workflow)
        log_card = AkmCard(mid_row, height=140)
        log_card.pack(side="left", fill="both", expand=True, padx=(SPACE_XS, 0))
        self.app.loudness_status_label = AkmLabel(log_card.inner, text="Bereit", bg=PANEL_2, anchor="w", font=FONT_BOLD)
        self.app.loudness_status_label.pack(fill="x", padx=CARD_PAD_X, pady=(10, 0))
        self.app.loudness_log = tk.Text(log_card.inner, height=3, bg=LOG_BG, fg=LOG_FG, relief="flat", font=("Courier", 9))
        self.app.loudness_log.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(2, 10))

        # --- 3. BOTTOM ROW (Settings | List) ---
        split_frame = tk.Frame(self, bg=BG)
        split_frame.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_MD))
        
        # Left: Settings
        left_p = tk.Frame(split_frame, bg=BG)
        left_p.pack(side="left", fill="both", expand=True, padx=(0, SPACE_SM))
        
        settings_card = AkmCard(left_p)
        settings_card.pack(fill="both", expand=True)
        settings_form = AkmForm(settings_card.inner, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        settings_form.pack(fill="both")
        settings_form.add_header("Parameter")
        settings_form.add_entry("LUFS", self.app.loudness_target_var, width=8)
        settings_form.add_entry("TP", self.app.loudness_peak_var, width=8)
        self.app.loudness_use_limiter_var = tk.BooleanVar(value=True)
        settings_form.add_checkbox("Limiter", self.app.loudness_use_limiter_var)
        self.app.loudness_auto_link_var = tk.BooleanVar(value=True)
        settings_form.add_checkbox("Auto-Link", self.app.loudness_auto_link_var)

        # Right: Treeview
        right_p = tk.Frame(split_frame, bg=BG)
        right_p.pack(side="left", fill="both", expand=True)
        tree_card = AkmCard(right_p)
        tree_card.pack(fill="both", expand=True)
        
        cols = ("filename", "duration", "lufs", "peak", "sample", "gain", "predicted_tp", "status", "limit", "export_info")
        self.app.loudness_tree = ttk.Treeview(tree_card.inner, columns=cols, show="headings", height=8, selectmode="extended")
        headers = {"filename": "Datei", "duration": "Dauer", "lufs": "LUFS", "peak": "TP", "status": "Match"}
        for col in cols:
            head = headers.get(col, col.upper()[:4])
            self.app.loudness_tree.heading(col, text=head)
            self.app.loudness_tree.column(col, width=50, anchor="center")
        self.app.loudness_tree.column("filename", width=120, anchor="w")
        self.app.loudness_tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(tree_card.inner, command=self.app.loudness_tree.yview)
        sb.pack(side="right", fill="y")
        self.app.loudness_tree.config(yscrollcommand=sb.set)
        self.app.loudness_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.app.loudness_tree.bind("<Double-1>", self.app.on_loudness_tree_activate)

    def _on_tree_select(self, event):
        selected = self.app.loudness_tree.selection()
        if not selected: return
        path = selected[0]
        if os.path.exists(path): self._show_waveform(path)

    def _show_waveform(self, path):
        self.waveform_label.config(text="ANALYSIERE WELLENFORM...", image="")
        temp_dir = os.path.join(os.path.expanduser("~"), ".akm_temp")
        os.makedirs(temp_dir, exist_ok=True)
        out_path = os.path.join(temp_dir, "preview.png")

        def _bg():
            try:
                ok = loudness_tools.generate_waveform_image(path, out_path, hex_color=ACCENT)
                if not ok or not os.path.exists(out_path): return None, "Bild-Fehler"
                from PIL import Image
                with Image.open(out_path) as img:
                    w, h = 800, 220
                    return img.resize((w, h), Image.Resampling.LANCZOS).copy(), None
            except Exception as e: return None, str(e)

        def _done(res):
            img_obj, err = res if isinstance(res, tuple) else (res, None)
            if err:
                self.waveform_label.config(text=f"FEHLER: {err}", image="")
            elif img_obj:
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img_obj)
                self.app.wv_ref = photo 
                self.waveform_label.config(image=photo, text="")
                self.app.append_log("Master-Display synchron.")
            else:
                self.waveform_label.config(text="KEINE VORSCHAU", image="")

        self.app.tasks.run(_bg, _done, busy_text="Erzeuge Grafik...")

    def _create_dir_row(self, parent, var):
        frame = tk.Frame(parent, bg=PANEL_2)
        frame.pack(fill="x", expand=True)
        AkmEntry(frame, textvariable=var).pack(side="left", fill="x", expand=True, padx=(0, SPACE_SM))
        tk.Button(frame, text="Wählen", command=self.app.loudness_choose_output_dir).pack(side="right")
        return frame

    def _setup_dnd(self):
        if DND_FILES:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_dnd_drop)

    def _on_dnd_drop(self, event):
        new_files = self.app.tasks.parse_dnd_files(event.data)
        if new_files:
            # Initialize if None
            if not self.app.state.loudness_files: self.app.state.loudness_files = []
            
            # Add only if not already present
            added = 0
            for f in new_files:
                if f not in self.app.state.loudness_files:
                    self.app.state.loudness_files.append(f)
                    added += 1
            
            self.app._pop_l_tree()
            self.app.append_log(f"{added} neue Dateien via Drag & Drop hinzugefügt (Total: {len(self.app.state.loudness_files)}).")
