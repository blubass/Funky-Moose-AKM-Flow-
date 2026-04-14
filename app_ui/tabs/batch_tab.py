import tkinter as tk
from tkinter import ttk
from app_logic import flow_tools
import app_ui.ui_patterns as ui_patterns
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmSuccessIndicator, AkmScrollablePanel,
    ACCENT, PANEL, PANEL_2, TEXT,
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_XL, FONT_LG, FONT_XXL, fit_wraplength, apply_button_bar_layout,
    build_badge_strip, build_radar_summary
)
from app_logic import i18n


class BatchTab(AkmPanel):
    ACTION_STACK_BREAKPOINT = 780

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.copy_stage = flow_tools.DEFAULT_COPY_STAGE
        self._batch_actions_enabled = False
        self._batch_action_buttons = []
        self._status_action_mode = None
        self._focus_strip_mode = None
        self._focus_action_mode = None
        self._quick_add_mode = None
        self.pack(fill="both", expand=True, padx=SPACE_SM, pady=SPACE_SM)
        self.build_ui()
        self._setup_dnd()
        self.set_batch_buttons_enabled(False)

    def build_ui(self):
        scroll_root, page = self._build_scroll_content()
        self._build_header(page)
        self._build_status_card(page)
        self._build_focus_card(page)
        self._build_progress_card(page)
        self._build_quick_add_card(page)
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

    def _build_scroll_content(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_resize, add="+")
        return scroll_root, scroll_root.scrollable_frame

    def _build_header(self, page):
        AkmHeader(page, text=i18n._t("batch_header_title")).pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text=i18n._t("batch_header_subtitle"),
            wraplength=760,
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))
        build_badge_strip(
            page,
            ("Queue", "Clipboard", "Submit", "Next"),
            active_indices={0, 1},
            padx=SPACE_MD,
            pady=(0, SPACE_SM),
        )

    def _build_status_card(self, page):
        status_card = AkmCard(page, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)
        self._build_status_summary(status_left)
        self._build_status_actions(status_right)

    def _build_status_summary(self, parent):
        summary = build_radar_summary(
            parent,
            title=i18n._t("batch_radar_title"),
            mode_text="BATCH CONTROL  •  One title in focus, one clean move after another",
            status_text=i18n._t("batch_radar_empty"),
            hint_text=i18n._t("batch_radar_hint"),
            context_text=i18n._t("batch_radar_context", in_progress=0, ready=0, queue=0),
            bg=PANEL_2,
            status_font=FONT_BOLD,
        )
        self.batch_status_label = summary["status_label"]
        self.batch_hint_label = summary["hint_label"]
        self.batch_meta_label = summary["context_label"]

    def _build_status_actions(self, parent):
        self._reload_status_button = self.app.btn(parent, i18n._t("dash_btn_refresh"), self.app.batch_ctrl.reload_flow_data, primary=True, width=118)
        self._reload_status_button.pack(anchor="e", pady=(0, SPACE_XS))
        status_actions = tk.Frame(parent, bg=PANEL_2)
        status_actions.pack(anchor="e")
        self._status_action_bar = status_actions
        self._status_action_buttons = (
            self.app.btn(status_actions, i18n._t("ash_btn_import"), self.app.import_excel, quiet=True, width=132),
            self.app.btn(status_actions, i18n._t("ash_btn_create"), lambda: self.app.add(self.get_quick_add_title()), quiet=True, width=126),
        )

    def _build_focus_card(self, page):
        focus_card = AkmCard(page)
        focus_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(focus_card.inner, text=i18n._t("batch_label_current"), fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 0)
        )
        self._focus_strip = tk.Frame(focus_card.inner, bg=PANEL_2)
        self._focus_strip.pack(fill="x", padx=CARD_PAD_X, pady=(SPACE_XS, SPACE_XS))
        self._focus_title_button = self.app.btn(self._focus_strip, i18n._t("det_label_title"), self.app.batch_ctrl.flow_copy_title, quiet=True, width=88)
        self._focus_duration_button = self.app.btn(self._focus_strip, i18n._t("det_label_duration"), self.app.batch_ctrl.flow_copy_duration, quiet=True, width=88)
        self._focus_submit_button = self.app.btn(self._focus_strip, i18n._t("batch_btn_submit"), self.app.batch_ctrl.flow_submit, quiet=True, width=96)
        self._focus_advance_button = self.app.btn(self._focus_strip, i18n._t("batch_btn_advance"), self.app.batch_ctrl.flow_next, quiet=True, width=104)
        self._focus_strip_buttons = (
            self._focus_title_button,
            self._focus_duration_button,
            self._focus_submit_button,
            self._focus_advance_button,
        )
        self._batch_action_buttons.extend(self._focus_strip_buttons)
        self._update_focus_strip_buttons()
        self.flow_title = AkmHeader(focus_card.inner, text=i18n._t("batch_status_loading"), fg=ACCENT, bg=PANEL_2)
        self.flow_title.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))
        meta_row = tk.Frame(focus_card.inner, bg=PANEL_2)
        meta_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_MD))
        self.flow_meta = AkmSubLabel(meta_row, text="", bg=PANEL_2)
        self.flow_meta.pack(side="left")
        self._build_focus_actions(focus_card)

    def _build_focus_actions(self, focus_card):
        btn_row = AkmPanel(focus_card.inner, bg=PANEL_2)
        btn_row.pack(anchor="w", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._focus_action_bar = btn_row
        self.copy_button = self.app.btn(btn_row, i18n._t("batch_btn_copy_title"), self.app.batch_ctrl.flow_copy, primary=True)
        self._batch_action_buttons.append(self.copy_button)
        submit_button = self.app.btn(btn_row, i18n._t("batch_btn_submit"), self.app.batch_ctrl.flow_submit, primary=True)
        self._batch_action_buttons.append(submit_button)
        next_button = self.app.btn(btn_row, i18n._t("batch_btn_advance"), self.app.batch_ctrl.flow_next, primary=True)
        self._batch_action_buttons.append(next_button)
        reload_button = self.app.btn(btn_row, i18n._t("dash_btn_refresh"), self.app.batch_ctrl.reload_flow_data, quiet=True)
        self._focus_action_buttons = (
            self.copy_button,
            submit_button,
            next_button,
            reload_button,
        )

    def _build_progress_card(self, page):
        progress_card = AkmCard(page)
        progress_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(progress_card.inner, text=i18n._t("batch_label_progress"), fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )
        AkmSubLabel(
            progress_card.inner,
            text=i18n._t("batch_progress_hint"),
            bg=PANEL_2,
            justify="left",
        ).pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))
        self.progress_label = AkmLabel(progress_card.inner, text="0 / 0", fg=TEXT, bg=PANEL_2, font=FONT_BOLD)
        self.progress_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_XS))
        self.progress = ttk.Progressbar(progress_card.inner, length=420)
        self.progress.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

    def _build_quick_add_card(self, page):
        add_card = AkmCard(page)
        add_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(add_card.inner, text=i18n._t("batch_label_quick_add"), fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )
        self._quick_add_intro_label = AkmSubLabel(
            add_card.inner,
            text=i18n._t("batch_quick_add_hint"),
            bg=PANEL_2,
            justify="left",
        )
        self._quick_add_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        add_row = AkmPanel(add_card.inner, bg=PANEL_2)
        add_row.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._quick_add_bar = add_row
        self.batch_entry = AkmEntry(add_row, width=40)
        self.batch_entry.bind("<Return>", lambda _event: self.app.add(self.get_quick_add_title()))
        self._quick_add_button = self.app.btn(add_row, i18n._t("ash_btn_create"), lambda: self.app.add(self.get_quick_add_title()), primary=True)

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_button_bar(self._status_action_bar, self._status_action_buttons, width, "_status_action_mode")
        self._apply_button_bar(self._focus_strip, self._focus_strip_buttons, width, "_focus_strip_mode")
        self._apply_button_bar(self._focus_action_bar, self._focus_action_buttons, width, "_focus_action_mode")
        self._apply_quick_add_layout(width)
        self._update_wraplengths(width)

    def _apply_button_bar(self, container, buttons, width, state_attr):
        current_mode = getattr(self, state_attr, None)
        setattr(
            self,
            state_attr,
            apply_button_bar_layout(
                container,
                buttons,
                width,
                self.ACTION_STACK_BREAKPOINT,
                current_mode,
                row_spacing=SPACE_SM,
            ),
        )

    def _apply_quick_add_layout(self, width):
        self._quick_add_mode = ui_patterns.apply_widget_layout(
            width,
            self.ACTION_STACK_BREAKPOINT,
            self._quick_add_mode,
            {
                "stack": (
                    (self.batch_entry, {"fill": "x", "expand": True, "pady": (0, SPACE_XS), "ipady": 2}),
                    (self._quick_add_button, {"fill": "x"}),
                ),
                "row": (
                    (self.batch_entry, {"side": "left", "fill": "x", "expand": True, "padx": (0, SPACE_SM)}),
                    (self._quick_add_button, {"side": "left"}),
                ),
            },
        )

    def _update_wraplengths(self, width):
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=300, maximum=840)
        fit_wraplength(self.batch_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self.batch_meta_label, width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self._quick_add_intro_label, width, padding=120, minimum=280, maximum=620)

    def get_quick_add_title(self):
        return self.batch_entry.get().strip()

    def get_copy_stage(self):
        return self.copy_stage

    def set_copy_stage(self, stage):
        self.copy_stage = stage or flow_tools.DEFAULT_COPY_STAGE
        self._update_focus_strip_buttons()

    def _update_focus_strip_buttons(self):
        title_text = f"{i18n._t('det_label_title')} •" if self.copy_stage == "title" else i18n._t('det_label_title')
        duration_text = f"{i18n._t('det_label_duration')} •" if self.copy_stage == "duration" else i18n._t('det_label_duration')
        self._focus_title_button.config(text=title_text)
        self._focus_duration_button.config(text=duration_text)
        # Keep the direct duration action available whenever the batch flow is active.
        # The controller already handles missing duration data and can probe audio or log why it is unavailable.
        duration_state = "normal" if self._batch_actions_enabled else "disabled"
        self._focus_duration_button.config(state=duration_state)

    def render_flow_state(self, *, title_text, meta_text, progress_value, progress_text, copy_button_label, status_text, hint_text, meta_summary, enabled, has_duration=False):
        self.flow_title.config(text=title_text)
        self.flow_meta.config(text=meta_text)
        self.progress["value"] = progress_value
        self.progress_label.config(text=progress_text)
        self.copy_button.config(text=copy_button_label)
        self.batch_status_label.config(text=status_text)
        self.batch_hint_label.config(text=hint_text)
        self.batch_meta_label.config(text=meta_summary)
        self.set_batch_buttons_enabled(enabled)

    def render_empty_state(self):
        self.flow_title.config(text=i18n._t("batch_status_all_done"))
        self.flow_meta.config(text=i18n._t("batch_status_ready_all"))
        self.progress["value"] = 100
        self.progress_label.config(text="0 / 0")

    def set_copy_button_label(self, text):
        self.copy_button.config(text=text)

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
            files = self.app.tasks.parse_dnd_files(data)
            excel_files = [f for f in files if f.lower().endswith((".xlsx", ".xls"))]
            if excel_files:
                self.app.import_excel_path(excel_files[0])
            else:
                self.app.append_log(f"Batch DnD: {len(files)} Dateien ignoriert (nur .xlsx unterstützt).")
        except Exception as e:
            self.app.append_log(f"Batch DnD Fehler: {e}")

    def set_batch_buttons_enabled(self, enabled):
        self._batch_actions_enabled = bool(enabled)
        state = "normal" if enabled else "disabled"
        for button in self._batch_action_buttons:
            try:
                button.config(state=state)
            except Exception:
                pass
        self._update_focus_strip_buttons()

    def _set_batch_buttons_enabled(self, enabled):
        self.set_batch_buttons_enabled(enabled)
