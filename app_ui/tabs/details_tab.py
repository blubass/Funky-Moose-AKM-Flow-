import os
import tkinter as tk
import logging
import app_ui.ui_patterns as ui_patterns
from app_ui import detail_view_tools
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm,
    AkmEntry, AkmText, AkmCheckbutton, AkmScrollablePanel,
    fit_wraplength, build_badge_strip, build_radar_summary,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_GAP, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_MD_BOLD, FONT_XL, FONT_LG
)
from app_logic import akm_core, detail_tools, i18n


class DetailsTab(AkmPanel):
    STACK_BREAKPOINT = 1180
    ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.detail_vars = {}
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
        except Exception as exc:
            logging.debug("Details DnD setup skipped: %s", exc)

    def _on_dnd_drop(self, event):
        data = event.data
        if not data: return
        try:
            files = self.app.tasks.parse_dnd_files(data)
            if files:
                f = files[0]
                # Trigger the controller's logic with the dropped path
                self.app.details_ctrl.handle_audio_drop(f)
        except Exception as exc:
            logging.exception("Details DnD drop handling failed: %s", exc)

    def build_ui(self):
        self._build_header_section()
        self._build_status_card()
        scroll_root, content = self._build_scroll_content()
        self._build_detail_cards(content, scroll_root)
        self._build_bottom_actions()

    def _build_header_section(self):
        AkmHeader(self, text=i18n._t("det_header_title")).pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            self,
            text=i18n._t("det_header_subtitle"),
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))
        build_badge_strip(
            self,
            ("Metadata", "Audio", "Status", "Notes"),
            active_indices={0, 1},
            padx=SPACE_MD,
            pady=(0, SPACE_SM),
        )

    def _build_status_card(self):
        status_card = AkmCard(self, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        summary = build_radar_summary(
            status_left,
            title=i18n._t("det_radar_title"),
            mode_text="DETAIL DESK  •  One record, all metadata, no context switching",
            status_text=i18n._t("det_radar_empty"),
            hint_text=i18n._t("det_radar_hint"),
            context_text=i18n._t("det_radar_context", audio="—", status="—", inst="—"),
            bg=PANEL_2,
        )
        self.details_status_label = summary["status_label"]
        self.details_hint_label = summary["hint_label"]
        self.details_context_label = summary["context_label"]

        self.app.btn(status_right, i18n._t("det_btn_save"), self.app.details_ctrl.save_details, primary=True, width=126).pack(anchor="e", pady=(0, SPACE_XS))
        action_row = tk.Frame(status_right, bg=PANEL_2)
        action_row.pack(anchor="e")
        self._status_action_bar = action_row
        self._status_action_buttons = (
            self.app.btn(action_row, i18n._t("det_btn_audio"), self.app.details_ctrl.choose_audio_path, quiet=True, width=118),
            self.app.btn(action_row, i18n._t("det_btn_finder"), self.app.details_ctrl.open_audio_path_in_finder, quiet=True, width=84),
            self.app.btn(action_row, i18n._t("det_btn_back"), self.app.details_ctrl.clear_details_form, quiet=True, width=84),
        )

    def _build_scroll_content(self):
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        content = scroll_root.scrollable_frame
        content.configure(padx=SPACE_MD, pady=0)
        return scroll_root, content

    def _build_detail_cards(self, content, scroll_root):
        left_card = AkmCard(content)
        right_card = AkmCard(content)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        right_card.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))
        self._detail_cards = (left_card, right_card)
        scroll_root.canvas.bind("<Configure>", self._on_responsive_resize, add="+")
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

        self._build_detail_form_card(left_card)
        self._build_notes_card(right_card)

    def _build_detail_form_card(self, left_card):
        detail_defaults = akm_core.get_detail_memory()
        self._left_intro_label = AkmSubLabel(
            left_card.inner,
            text=i18n._t("det_intro_left"),
            bg=PANEL_2,
            justify="left",
            wraplength=360,
        )
        self._left_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_SM))
        left_form = AkmForm(left_card.inner, padx=CARD_PAD_X, pady=0)
        left_form.pack(fill="both", expand=True)
        left_form.add_header(i18n._t("ash_radar_title")) # Fallback to Quick Launch or similar
        self._build_detail_form_rows(left_form, detail_defaults)

    def _build_detail_form_rows(self, left_form, detail_defaults):
        for key, label in detail_tools.DETAIL_FIELD_LABELS:
            var = tk.StringVar(value=detail_defaults.get(key, ""))
            self.detail_vars[key] = var

            if key == "title":
                self.detail_title_combo = left_form.add_combobox(label, var, [])
                self.detail_title_combo.bind("<<ComboboxSelected>>", lambda _event: self.app.details_ctrl.load_selected_title())
            elif key == "audio_path":
                left_form.add_row(
                    label,
                    lambda parent, current_var=var: self._create_audio_field(parent, current_var),
                )
            else:
                left_form.add_entry(label, var)

        self.detail_instrumental_var = tk.BooleanVar(value=False)
        left_form.add_checkbox(i18n._t("det_label_instrumental"), self.detail_instrumental_var)
        left_form.add_row(i18n._t("det_label_status"), self._create_status_row)

    def _create_audio_field(self, parent, variable):
        wrap = tk.Frame(parent, bg=PANEL_2)
        entry = AkmEntry(wrap, textvariable=variable)
        entry.pack(side="left", fill="x", expand=True)
        self.app.btn(wrap, i18n._t("det_btn_audio"), self.app.details_ctrl.choose_audio_path, primary=True).pack(side="left", padx=(SPACE_XS, 0))
        self.app.btn(wrap, i18n._t("det_btn_finder"), self.app.details_ctrl.open_audio_path_in_finder, quiet=True).pack(side="left", padx=(SPACE_XS, 0))
        return wrap

    def _create_status_row(self, parent):
        wrap = tk.Frame(parent, bg=PANEL_2)
        self.detail_status_var = tk.StringVar(value="—")
        self.detail_status_chip = tk.Label(
            wrap, textvariable=self.detail_status_var,
            fg=TEXT, bg=PANEL, font=FONT_BOLD,
            padx=12, pady=5, bd=1, relief="solid"
        )
        self.detail_status_chip.pack(anchor="w", pady=(0, SPACE_SM))

        btn_row = tk.Frame(wrap, bg=PANEL_2)
        btn_row.pack(anchor="w")
        self.app.btn(btn_row, i18n._t("dash_stat_open"), lambda: self.app.details_ctrl.set_status_chip("in_progress"), quiet=True).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(btn_row, i18n._t("dash_stat_ready"), lambda: self.app.details_ctrl.set_status_chip("ready")).pack(side="left", padx=SPACE_XS)
        self.app.btn(btn_row, i18n._t("dash_stat_confirmed"), lambda: self.app.details_ctrl.set_status_chip("confirmed")).pack(side="left", padx=SPACE_XS)
        return wrap

    def _build_notes_card(self, right_card):
        AkmLabel(right_card.inner, text=i18n._t("det_label_notes_tags"), fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        self._right_intro_label = AkmSubLabel(
            right_card.inner,
            text=i18n._t("det_intro_right"),
            bg=PANEL_2,
            justify="left",
            wraplength=360,
        )
        self._right_intro_label.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        build_badge_strip(
            right_card.inner,
            ("Search tags", "Production notes", "Handoff ready"),
            active_indices={2},
            bg=PANEL_2,
            padx=CARD_PAD_X,
            pady=(0, SPACE_SM),
        )
        right_form = AkmForm(right_card.inner, padx=CARD_PAD_X, pady=0)
        right_form.pack(fill="both", expand=True)
        self.detail_tags = right_form.add_text(i18n._t("det_label_tags_hint"), height=4)
        self.detail_notes = right_form.add_text(i18n._t("det_label_notes"), height=12)

    def _build_bottom_actions(self):
        actions = AkmPanel(self)
        actions.pack(anchor="w", padx=SPACE_MD, pady=SPACE_SM)
        self.app.btn(actions, i18n._t("det_btn_save"), self.app.details_ctrl.save_details, primary=True, width=118).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(actions, i18n._t("det_btn_clear"), self.app.details_ctrl.clear_details_form, quiet=True, width=118).pack(side="left", padx=SPACE_XS)

    def _on_responsive_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        if not hasattr(self, "_detail_cards"):
            return
        left_card, right_card = self._detail_cards
        self._detail_layout_mode = ui_patterns.apply_widget_layout(
            width,
            self.STACK_BREAKPOINT,
            self._detail_layout_mode,
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

    def _apply_status_actions_layout(self, width):
        if not hasattr(self, "_status_action_buttons"):
            return
        self._status_action_mode = ui_patterns.apply_button_bar_layout(
            self._status_action_bar,
            self._status_action_buttons,
            width,
            self.ACTION_STACK_BREAKPOINT,
            self._status_action_mode,
            row_spacing=SPACE_XS,
            anchor="e",
        )

    def _update_wraplengths(self, width):
        column_width = width if self._detail_layout_mode == "stack" else max(340, (width - CARD_GAP) // 2)
        fit_wraplength(self._header_intro_label, width, padding=120, minimum=280, maximum=780)
        fit_wraplength(self.details_status_label, width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self.details_hint_label, width, padding=260, minimum=260, maximum=620)
        fit_wraplength(self.details_context_label, width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self._left_intro_label, column_width, padding=80, minimum=260, maximum=460)
        fit_wraplength(self._right_intro_label, column_width, padding=80, minimum=260, maximum=460)

    def _setup_state_traces(self):
        tracked = []
        for key in ("title", "audio_path", "composer", "duration", "year"):
            if key in self.detail_vars:
                tracked.append(self.detail_vars[key])
        tracked.append(self.detail_instrumental_var)
        tracked.append(self.detail_status_var)

        for var in tracked:
            var.trace_add("write", lambda *args: self._update_detail_radar())

    def _detail_value(self, key):
        var = self.detail_vars.get(key)
        if not var:
            return ""
        return (var.get() or "").strip()

    def get_form_vars(self):
        return self.detail_vars

    def set_title_options(self, titles):
        self.detail_title_combo.config(values=titles)

    def get_notes_text(self):
        return self.detail_notes.get("1.0", "end-1c").strip()

    def set_notes_text(self, text):
        self.detail_notes.delete("1.0", tk.END)
        self.detail_notes.insert("1.0", text or "")

    def clear_notes(self):
        self.detail_notes.delete("1.0", tk.END)

    def get_tags_text(self):
        return self.detail_tags.get("1.0", "end-1c").strip()

    def set_tags_text(self, text):
        self.detail_tags.delete("1.0", tk.END)
        self.detail_tags.insert("1.0", text or "")

    def clear_tags(self):
        self.detail_tags.delete("1.0", tk.END)

    def get_instrumental(self):
        return bool(self.detail_instrumental_var.get())

    def set_instrumental(self, value):
        self.detail_instrumental_var.set(bool(value))

    def set_status_chip_display(self, status_key, status_label):
        self.detail_status_var.set(status_label)
        ui_patterns.style_chip_label(self.detail_status_chip, status_key, status_label)

    def _update_detail_radar(self):
        radar_state = detail_view_tools.build_detail_radar_state(
            title=self._detail_value("title"),
            audio_path=self._detail_value("audio_path"),
            composer=self._detail_value("composer"),
            duration=self._detail_value("duration"),
            year=self._detail_value("year"),
            instrumental=bool(self.detail_instrumental_var.get()),
            status_text=self.detail_status_var.get().strip() if self.detail_status_var.get() else "—",
        )
        self.details_status_label.config(text=radar_state["headline"])
        self.details_context_label.config(text=radar_state["context_text"])
        self.details_hint_label.config(text=radar_state["hint_text"])
