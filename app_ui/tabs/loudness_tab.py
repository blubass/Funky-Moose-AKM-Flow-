import tkinter as tk
from tkinter import ttk
import os
from app_ui.ui_patterns import *
import app_ui.ui_patterns as ui_patterns
import app_logic.loudness_tools as loudness_tools
from app_ui import loudness_view_tools
import app_workflows.loudness_workflows as loudness_workflows
from app_logic import i18n

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None

class LoudnessTab(AkmPanel):
    MID_STACK_BREAKPOINT = 1040
    ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.output_dir_var = tk.StringVar()
        self.target_var = tk.StringVar(value="-14.0")
        self.peak_var = tk.StringVar(value="-1.0")
        self.use_limiter_var = tk.BooleanVar(value=True)
        self.auto_link_var = tk.BooleanVar(value=True)
        self._mid_layout_mode = None
        self._action_mode = None
        self._aux_action_mode = None
        self._split_layout_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.wv_ref = None 
        self.build_ui()
        self._setup_dnd()

    def build_ui(self):
        scroll_root, page = self._build_scroll_content()
        self._build_header(page)
        self._build_waveform_card(page)
        self._build_mid_row(page)
        self._build_split_row(page)
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _build_scroll_content(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        return scroll_root, scroll_root.scrollable_frame

    def _build_header(self, page):
        AkmHeader(page, text=i18n._t("loud_header_title")).pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text=i18n._t("loud_header_subtitle"),
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))
        signal_row = AkmPanel(page)
        signal_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        for index, text in enumerate(("Analyze", "Match", "Limiter", "Export")):
            badge = AkmBadge(signal_row, text)
            badge.pack(side="left", padx=(0 if index == 0 else SPACE_XS, 0))
            badge.set_active(index < 2)

    def _build_waveform_card(self, page):
        self.preview_card = AkmCard(page, height=240)
        self.preview_card.pack(fill="x", padx=SPACE_MD, pady=(SPACE_MD, SPACE_SM))

        inlay = tk.Frame(self.preview_card.inner, bg="#050507", padx=2, pady=2)
        inlay.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=CARD_PAD_Y)

        self.waveform_container = tk.Frame(inlay, bg="#0A0A0E")
        self.waveform_container.pack(fill="both", expand=True)
        tk.Frame(inlay, bg="#1E1E22", height=1).place(relx=0, rely=0, relwidth=1)

        self.waveform_label = tk.Label(
            self.waveform_container,
            bg="#0A0A0E",
            fg=ui_patterns.ACCENT,
            font=("Inter", 14, "bold"),
            text=i18n._t("loud_label_waveform").upper(),
        )
        self.waveform_label.pack(fill="both", expand=True)

    def _build_mid_row(self, page):
        mid_row = tk.Frame(page, bg=BG)
        mid_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        self._mid_row = mid_row

        self._build_workflow_card(mid_row)
        self._build_status_log_card(mid_row)

    def _build_workflow_card(self, mid_row):
        action_card = AkmCard(mid_row, min_height=140)
        action_card.pack(side="left", fill="both", expand=True, padx=(0, SPACE_XS))
        self._workflow_card = action_card
        AkmLabel(action_card.inner, text="Workflow", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(10, 0))
        self._workflow_intro_label = AkmSubLabel(
            action_card.inner,
            text=i18n._t("ash_radar_hint"), # repurposing
            bg=PANEL_2,
            wraplength=380,
            justify="left",
        )
        self._workflow_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(2, 6))

        controls = AkmPanel(action_card.inner, bg=PANEL_2)
        controls.pack(fill="x", padx=CARD_PAD_X, pady=(2, 4))
        self._workflow_action_bar = controls
        self.loudness_choose_btn = self.app.btn(controls, i18n._t("loud_btn_files"), self.app.loudness_ctrl.choose_files, primary=True, width=96)
        self.loudness_analyze_btn = self.app.btn(controls, i18n._t("loud_btn_analyze"), self.app.loudness_ctrl.analyze_files, primary=True, width=96)
        self.loudness_export_btn = self.app.btn(controls, i18n._t("rel_btn_export"), self.app.loudness_ctrl.export_files, primary=True, width=96)
        self._workflow_action_buttons = (
            self.loudness_choose_btn,
            self.loudness_analyze_btn,
            self.loudness_export_btn,
        )

        aux_controls = AkmPanel(action_card.inner, bg=PANEL_2)
        aux_controls.pack(fill="x", padx=CARD_PAD_X, pady=(0, 6))
        self._workflow_aux_bar = aux_controls
        self._workflow_aux_buttons = (
            self.app.btn(aux_controls, i18n._t("loud_btn_import"), self.app.loudness_ctrl.import_selected_work, quiet=True, width=96),
            self.app.btn(aux_controls, i18n._t("loud_btn_import_filter"), self.app.loudness_ctrl.import_filtered_works, quiet=True, width=96),
            self.app.btn(aux_controls, i18n._t("det_btn_clear"), self.app.loudness_ctrl.delete_files, quiet=True, width=96),
        )

    def _build_status_log_card(self, mid_row):
        log_card = AkmCard(mid_row, min_height=140)
        log_card.pack(side="left", fill="both", expand=True, padx=(SPACE_XS, 0))
        self._status_log_card = log_card
        AkmLabel(log_card.inner, text=i18n._t("ash_log_title"), fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(10, 0))
        AkmSubLabel(
            log_card.inner,
            text="MASTER DESK  •  Current result state, hints and protocol output",
            bg=PANEL_2,
            justify="left",
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(2, 2))
        self.loudness_status_label = AkmLabel(log_card.inner, text=i18n._t("task_ready"), bg=PANEL_2, anchor="w", font=FONT_BOLD)
        self.loudness_status_label.pack(fill="x", padx=CARD_PAD_X, pady=(2, 0))
        self.loudness_hint_label = AkmSubLabel(
            log_card.inner,
            text=i18n._t("loud_radar_hint"),
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=420,
        )
        self.loudness_hint_label.pack(fill="x", padx=CARD_PAD_X, pady=(2, 2))
        self.loudness_log = tk.Text(log_card.inner, height=3, bg=LOG_BG, fg=LOG_FG, relief="flat", font=("Courier", 9))
        self.loudness_log.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(2, 10))

    def _build_split_row(self, page):
        split_frame = tk.Frame(page, bg=BG)
        split_frame.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_MD))
        self._split_frame = split_frame

        left_p = tk.Frame(split_frame, bg=BG)
        left_p.pack(side="left", fill="both", expand=True, padx=(0, SPACE_SM))
        self._settings_panel = left_p
        self._build_settings_card(left_p)

        right_p = tk.Frame(split_frame, bg=BG)
        right_p.pack(side="left", fill="both", expand=True)
        self._tree_panel = right_p
        self._build_tree_card(right_p)

    def _build_settings_card(self, left_panel):
        settings_card = AkmCard(left_panel)
        settings_card.pack(fill="both", expand=True)
        settings_form = AkmForm(settings_card.inner, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        settings_form.pack(fill="both")
        settings_form.add_header(i18n._t("loud_label_target"))
        settings_form.add_entry(i18n._t("loud_label_lufs"), self.target_var, width=8)
        settings_form.add_entry(i18n._t("loud_label_peak"), self.peak_var, width=8)
        settings_form.add_row(
            i18n._t("loud_label_outdir"),
            lambda parent: self._create_output_dir_field(parent),
        )
        settings_form.add_checkbox(i18n._t("loud_label_limiter"), self.use_limiter_var)
        settings_form.add_checkbox(i18n._t("loud_label_autolink"), self.auto_link_var)
        self._settings_hint_label = AkmSubLabel(
            settings_card.inner,
            text="Limiter greift nur bei Peak-Warnungen. Auto-Link ist fuer spaetere Rueckverweise gedacht.",
            bg=PANEL_2,
            justify="left",
            wraplength=260,
        )
        self._settings_hint_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

    def _build_tree_card(self, right_panel):
        tree_card = AkmCard(right_panel)
        tree_card.pack(fill="both", expand=True)
        AkmLabel(tree_card.inner, text=i18n._t("loud_label_results"), fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        self._tree_intro_label = AkmSubLabel(
            tree_card.inner,
            text="Doppelklick oeffnet den Player, Auswahl aktualisiert die Wellenform.",
            bg=PANEL_2,
            justify="left",
        )
        self._tree_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        tree_wrap = tk.Frame(tree_card.inner, bg=PANEL_2)
        tree_wrap.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._build_loudness_tree(tree_wrap)

    def _build_loudness_tree(self, tree_wrap):
        cols = ("filename", "duration", "lufs", "peak", "sample", "gain", "predicted_tp", "status", "limit", "export_info")
        self.loudness_tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", height=8, selectmode="extended")
        headers = {
            "filename": i18n._t("col_file"),
            "duration": i18n._t("col_duration"),
            "lufs": i18n._t("col_lufs"),
            "peak": i18n._t("col_tp"),
            "sample": i18n._t("col_peak"),
            "gain": i18n._t("col_gain"),
            "predicted_tp": i18n._t("col_tp_gain"),
            "status": i18n._t("col_match"),
            "limit": i18n._t("col_limiter"),
            "export_info": i18n._t("col_export"),
        }
        for col in cols:
            head = headers.get(col, col.upper()[:4])
            self.loudness_tree.heading(col, text=head)
            self.loudness_tree.column(col, width=78, anchor="center")
        self.loudness_tree.column("filename", width=200, anchor="w")
        self.loudness_tree.column("status", width=110, anchor="center")
        self.loudness_tree.column("export_info", width=120, anchor="center")
        self.loudness_tree.column("predicted_tp", width=110, anchor="center")
        self.loudness_tree.tag_configure("exported", background=ui_patterns.get_row_color("confirmed", ratio=0.22))
        self.loudness_tree.tag_configure("error", background=ui_patterns.blend_color(FIELD_BG, ui_patterns.FLAVOR_ERROR, 0.18))
        self.loudness_tree.tag_configure("peak_warn", background=ui_patterns.blend_color(FIELD_BG, ui_patterns.FLAVOR_WARN, 0.2))
        self.loudness_tree.tag_configure("match_ok", background=ui_patterns.get_row_color("ready", ratio=0.18))
        self.loudness_tree.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(
            tree_wrap,
            command=self.loudness_tree.yview,
            bg=ui_patterns.PANEL_2,
            activebackground=ui_patterns.blend_color(ui_patterns.PANEL_2, ui_patterns.ACCENT, 0.18),
            troughcolor=ui_patterns.BG,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        sb.pack(side="right", fill="y")
        self.loudness_tree.config(yscrollcommand=sb.set)
        self.loudness_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.loudness_tree.bind("<Double-1>", self.app.loudness_ctrl.on_tree_activate)

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_mid_layout(width)
        self._apply_button_bar(self._workflow_action_bar, self._workflow_action_buttons, width, "_action_mode")
        self._apply_button_bar(self._workflow_aux_bar, self._workflow_aux_buttons, width, "_aux_action_mode")
        self._apply_split_layout(width)
        self._update_wraplengths(width)

    def _apply_mid_layout(self, width):
        self._mid_layout_mode = ui_patterns.apply_widget_layout(
            width,
            self.MID_STACK_BREAKPOINT,
            self._mid_layout_mode,
            {
                "stack": (
                    (self._workflow_card, {"fill": "x", "expand": False, "pady": (0, SPACE_SM)}),
                    (self._status_log_card, {"fill": "x", "expand": False}),
                ),
                "row": (
                    (self._workflow_card, {"side": "left", "fill": "both", "expand": True, "padx": (0, SPACE_XS)}),
                    (self._status_log_card, {"side": "left", "fill": "both", "expand": True, "padx": (SPACE_XS, 0)}),
                ),
            },
        )

    def _apply_button_bar(self, container, buttons, width, state_attr):
        current_mode = getattr(self, state_attr, None)
        setattr(
            self,
            state_attr,
            ui_patterns.apply_button_bar_layout(
                container,
                buttons,
                width,
                self.ACTION_STACK_BREAKPOINT,
                current_mode,
                row_spacing=4,
            ),
        )

    def _apply_split_layout(self, width):
        self._split_layout_mode = ui_patterns.apply_widget_layout(
            width,
            self.MID_STACK_BREAKPOINT,
            self._split_layout_mode,
            {
                "stack": (
                    (self._settings_panel, {"fill": "x", "expand": False, "pady": (0, SPACE_SM)}),
                    (self._tree_panel, {"fill": "both", "expand": True}),
                ),
                "row": (
                    (self._settings_panel, {"side": "left", "fill": "both", "expand": True, "padx": (0, SPACE_SM)}),
                    (self._tree_panel, {"side": "left", "fill": "both", "expand": True}),
                ),
            },
        )

    def _update_wraplengths(self, width):
        upper_width = width if self._mid_layout_mode == "stack" else max(340, (width - SPACE_XS) // 2)
        lower_width = width if self._split_layout_mode == "stack" else max(320, (width - SPACE_SM) // 2)
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=280, maximum=860)
        fit_wraplength(self._workflow_intro_label, upper_width, padding=90, minimum=260, maximum=420)
        fit_wraplength(self.loudness_hint_label, upper_width, padding=90, minimum=260, maximum=420)
        fit_wraplength(self._settings_hint_label, lower_width, padding=90, minimum=240, maximum=320)
        fit_wraplength(self._tree_intro_label, lower_width, padding=90, minimum=260, maximum=420)

    def _on_tree_select(self, event):
        selected = self.loudness_tree.selection()
        if not selected: return
        path = selected[0]
        if os.path.exists(path): self._show_waveform(path)

    def _show_waveform(self, path):
        self.waveform_label.config(text=i18n._t("loud_status_checking", file="...").upper(), image="")

        def _bg():
            try:
                from PIL import Image
                return loudness_view_tools.render_waveform_preview(
                    path,
                    os.path.expanduser("~"),
                    ACCENT,
                    loudness_tools.generate_waveform_image,
                    Image,
                )
            except Exception as e:
                return None, str(e)

        def _done(res):
            img_obj, err = res if isinstance(res, tuple) else (res, None)
            if err:
                self.waveform_label.config(text=f"FEHLER: {err}", image="")
            elif img_obj:
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img_obj)
                self.wv_ref = photo
                self.waveform_label.config(image=photo, text="")
                self.app.append_log("Master-Display synchron.")
            else:
                self.waveform_label.config(text=i18n._t("err_file_not_found").upper(), image="")

        self.app.tasks.run(_bg, _done, busy_text="Erzeuge Grafik...")

    def _create_output_dir_field(self, parent):
        frame = tk.Frame(parent, bg=PANEL_2)
        AkmEntry(frame, textvariable=self.output_dir_var, font=FONT_SM).pack(side="left", fill="x", expand=True, padx=(0, SPACE_SM))
        self.app.btn(frame, i18n._t("ui_btn_browse", default="Wählen"), self.app.loudness_ctrl.choose_output_dir, quiet=True, width=86).pack(side="right")
        return frame

    def has_tree(self):
        return True

    def get_target_text(self):
        return self.target_var.get()

    def get_peak_text(self):
        return self.peak_var.get()

    def get_output_dir(self):
        return (self.output_dir_var.get() or "").strip()

    def set_output_dir(self, path):
        self.output_dir_var.set(path or "")

    def get_use_limiter(self):
        return bool(self.use_limiter_var.get())

    def get_selected_paths(self):
        return tuple(self.loudness_tree.selection())

    def clear_tree(self):
        self.loudness_tree.delete(*self.loudness_tree.get_children())

    def insert_tree_row(self, path, values, tags=()):
        self.loudness_tree.insert("", tk.END, iid=path, values=values, tags=tags)

    def apply_workflow_state(self, status_text="", hint_text="", log_lines=None):
        self.loudness_status_label.config(text=status_text or "")
        self.loudness_hint_label.config(text=hint_text or "")
        self.loudness_log.delete("1.0", tk.END)
        if log_lines:
            self.loudness_log.insert("1.0", "\n".join(log_lines))

    def set_open_state(self, status_text="", hint_text=""):
        self.loudness_status_label.config(text=status_text or "")
        self.loudness_hint_label.config(text=hint_text or "")

    def _setup_dnd(self):
        if DND_FILES:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_dnd_drop)

    def _on_dnd_drop(self, event):
        self.app.loudness_ctrl.handle_drop(event)
