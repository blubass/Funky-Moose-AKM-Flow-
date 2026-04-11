import tkinter as tk
from tkinter import ttk
from app_logic import flow_tools
import app_ui.ui_patterns as ui_patterns
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmEntry, AkmSuccessIndicator, AkmScrollablePanel, AkmBadge,
    ACCENT, PANEL, PANEL_2, TEXT,
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_XL, FONT_LG, FONT_XXL, fit_wraplength, apply_button_bar_layout
)


class BatchTab(AkmPanel):
    ACTION_STACK_BREAKPOINT = 780

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.copy_stage = flow_tools.DEFAULT_COPY_STAGE
        self._batch_action_buttons = []
        self._status_action_mode = None
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
        AkmHeader(page, text="AKM Batch").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text="Arbeite fokussiert durch offene Werke: Titel kopieren, Dauer mitnehmen und danach direkt als gemeldet markieren.",
            wraplength=760,
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))
        signal_row = AkmPanel(page)
        signal_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        for index, text in enumerate(("Queue", "Clipboard", "Submit", "Next")):
            badge = AkmBadge(signal_row, text)
            badge.pack(side="left", padx=(0 if index == 0 else SPACE_XS, 0))
            badge.set_active(index < 2)

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
        AkmLabel(parent, text="Flow Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        AkmSubLabel(
            parent,
            text="BATCH CONTROL  •  One title in focus, one clean move after another",
            bg=PANEL_2,
            anchor="w",
        ).pack(fill="x", pady=(1, 1))
        self.batch_status_label = AkmLabel(
            parent,
            text="Keine offenen Batch-Werke",
            fg=TEXT,
            bg=PANEL_2,
            font=FONT_BOLD,
            anchor="w",
        )
        self.batch_status_label.pack(fill="x", pady=(2, 2))
        self.batch_hint_label = AkmSubLabel(
            parent,
            text="Importiere Excel oder lege neue Werke an, dann füllt sich die Queue automatisch.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=560,
        )
        self.batch_hint_label.pack(fill="x")
        self.batch_meta_label = AkmSubLabel(
            parent,
            text="In Arbeit: 0   •   Bereit: 0   •   Queue: 0",
            bg=PANEL_2,
            anchor="w",
        )
        self.batch_meta_label.pack(fill="x", pady=(2, 0))

    def _build_status_actions(self, parent):
        self._reload_status_button = self.app.btn(parent, "Neu laden", self.app.batch_ctrl.reload_flow_data, primary=True, width=118)
        self._reload_status_button.pack(anchor="e", pady=(0, SPACE_XS))
        status_actions = tk.Frame(parent, bg=PANEL_2)
        status_actions.pack(anchor="e")
        self._status_action_bar = status_actions
        self._status_action_buttons = (
            self.app.btn(status_actions, "Excel importieren", self.app.import_excel, quiet=True, width=132),
            self.app.btn(status_actions, "Werk anlegen", lambda: self.app.add(self.get_quick_add_title()), quiet=True, width=126),
        )

    def _build_focus_card(self, page):
        focus_card = AkmCard(page)
        focus_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(focus_card.inner, text="Aktuelles Werk", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 0)
        )
        self._focus_strip = tk.Frame(focus_card.inner, bg=PANEL_2)
        self._focus_strip.pack(fill="x", padx=CARD_PAD_X, pady=(SPACE_XS, SPACE_XS))
        for index, text in enumerate(("Title", "Duration", "Submit", "Advance")):
            badge = AkmBadge(self._focus_strip, text)
            badge.pack(side="left", padx=(0 if index == 0 else SPACE_XS, 0))
            badge.set_active(index == 0)
        self.flow_title = AkmHeader(focus_card.inner, text="Lade Werk...", fg=ACCENT, bg=PANEL_2)
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
        self.copy_button = self.app.btn(btn_row, "Titel kopieren", self.app.batch_ctrl.flow_copy, primary=True)
        self._batch_action_buttons.append(self.copy_button)
        submit_button = self.app.btn(btn_row, "Als gemeldet", self.app.batch_ctrl.flow_submit, primary=True)
        self._batch_action_buttons.append(submit_button)
        next_button = self.app.btn(btn_row, "Weiter →", self.app.batch_ctrl.flow_next, primary=True)
        self._batch_action_buttons.append(next_button)
        reload_button = self.app.btn(btn_row, "Neu laden", self.app.batch_ctrl.reload_flow_data, quiet=True)
        self._focus_action_buttons = (
            self.copy_button,
            submit_button,
            next_button,
            reload_button,
        )

    def _build_progress_card(self, page):
        progress_card = AkmCard(page)
        progress_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        AkmLabel(progress_card.inner, text="Fortschritt", fg=ACCENT, bg=PANEL_2, font=FONT_BOLD).pack(
            anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS)
        )
        AkmSubLabel(
            progress_card.inner,
            text="Queue-Tempo und Durchlauf bleiben hier sofort sichtbar.",
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
        self.batch_entry = AkmEntry(add_row, width=40)
        self.batch_entry.bind("<Return>", lambda _event: self.app.add(self.get_quick_add_title()))
        self._quick_add_button = self.app.btn(add_row, "+ Werk anlegen", lambda: self.app.add(self.get_quick_add_title()), primary=True)

    def _on_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        self._apply_button_bar(self._status_action_bar, self._status_action_buttons, width, "_status_action_mode")
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
        fit_wraplength(self._quick_add_intro_label, width, padding=120, minimum=280, maximum=620)

    def get_quick_add_title(self):
        return self.batch_entry.get().strip()

    def get_copy_stage(self):
        return self.copy_stage

    def set_copy_stage(self, stage):
        self.copy_stage = stage or flow_tools.DEFAULT_COPY_STAGE

    def render_flow_state(self, *, title_text, meta_text, progress_value, progress_text, copy_button_label, status_text, hint_text, meta_summary, enabled):
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
        self.flow_title.config(text="Alle Werke erledigt ✓")
        self.flow_meta.config(text="Keine offenen Einträge in der Queue.")
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
        state = "normal" if enabled else "disabled"
        for button in self._batch_action_buttons:
            try:
                button.config(state=state)
            except Exception:
                pass

    def _set_batch_buttons_enabled(self, enabled):
        self.set_batch_buttons_enabled(enabled)
