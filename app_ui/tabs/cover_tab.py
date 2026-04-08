import tkinter as tk
from tkinter import filedialog, ttk
import os
from PIL import Image, ImageTk
import app_ui.ui_patterns as ui_patterns
from app_ui import release_view_tools
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm, AkmEntry, AkmText, AkmBadge,
    AkmScrollablePanel, AkmToast,
    fit_wraplength,
    ACCENT, PANEL, PANEL_2, SUBTLE, TEXT, FIELD_BG, FIELD_FG, 
    SPACE_MD, SPACE_SM, SPACE_XS, CARD_GAP, CARD_PAD_X, CARD_PAD_Y,
    FONT_BOLD, FONT_SM, FONT_MD, FONT_MD_BOLD, FONT_XL, FONT_LG, FONT_XXL
)

try:
    from tkinterdnd2 import DND_FILES
except ImportError:
    DND_FILES = None


IMAGE_FILETYPES = [
    ("Bilder", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
    ("Alle Dateien", "*.*"),
]
_SYSTEM_FONTS = None
COVER_STATE_SPECS = (
    ("artwork_path", tk.StringVar, ""),
    ("artist", tk.StringVar, "MARIO MUSTERMANN"),
    ("title", tk.StringVar, "DER GROSSE WURF"),
    ("subtitle", tk.StringVar, "Digital Deluxe Edition"),
    ("artist_font", tk.StringVar, "Helvetica Neue"),
    ("artist_color", tk.StringVar, "#FFFFFF"),
    ("artist_bold", tk.BooleanVar, False),
    ("artist_case", tk.StringVar, "uppercase"),
    ("title_font", tk.StringVar, "Helvetica Neue"),
    ("title_color", tk.StringVar, "#FFFFFF"),
    ("title_bold", tk.BooleanVar, True),
    ("title_case", tk.StringVar, "uppercase"),
    ("subtitle_font", tk.StringVar, "Inter Mono"),
    ("subtitle_color", tk.StringVar, "#D2D2D2"),
    ("subtitle_bold", tk.BooleanVar, False),
    ("subtitle_case", tk.StringVar, "normal"),
    ("artist_size", tk.StringVar, "60"),
    ("artist_x", tk.StringVar, "900"),
    ("artist_y", tk.StringVar, "1400"),
    ("title_size", tk.StringVar, "140"),
    ("title_x", tk.StringVar, "900"),
    ("title_y", tk.StringVar, "1500"),
    ("subtitle_size", tk.StringVar, "40"),
    ("subtitle_x", tk.StringVar, "900"),
    ("subtitle_y", tk.StringVar, "1650"),
    ("layout", tk.StringVar, "manual"),
    ("style", tk.StringVar, "bold"),
    ("size_mode", tk.StringVar, "medium"),
    ("overlay", tk.StringVar, "medium"),
    ("offset", tk.StringVar, "normal"),
    ("zoom", tk.DoubleVar, 1.0),
    ("ui_preview_zoom", tk.IntVar, 260),
    ("bg_color", tk.StringVar, "#181818"),
    ("accent_color", tk.StringVar, "#ff9a3c"),
)


def _friendly_layout_name(layout_key):
    mapping = {
        "manual": "Manual",
        "bottom": "Bottom Band",
        "topleft": "Top Left Card",
        "center": "Center Band",
    }
    return mapping.get(layout_key, "Manual")


def _get_system_fonts():
    global _SYSTEM_FONTS
    if _SYSTEM_FONTS is None:
        import tkinter.font as tkfont
        _SYSTEM_FONTS = sorted(tkfont.families())
    return _SYSTEM_FONTS

class CoverTab(AkmPanel):
    STACK_BREAKPOINT = 1320
    ACTION_STACK_BREAKPOINT = 760
    MEDIA_STACK_BREAKPOINT = 980

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._cover_layout_mode = None
        self._cover_action_mode = None
        self._status_action_mode = None
        self._cover_media_mode = None
        self._current_image = None
        self._photo = None
        self._is_rendering = False
        self._last_preview_error = ""
        self._open_zoom_when_ready = False
        self._artwork_meta_path = None
        self._artwork_meta = None
        self._init_state_vars()
        self._preview_refresh_after = None
        self._preview_dimensions = None
        
        self.pack(fill="both", expand=True)
        self.build_ui()
        self._setup_dnd()
        self._setup_traces()

    def refresh_view(self):
        """Refresh cover status UI and lazily recover preview rendering when needed."""
        self._update_cover_dashboard()
        artwork_path = self.artwork_path_var.get().strip()
        if (
            artwork_path
            and os.path.exists(artwork_path)
            and self._current_image is None
            and not self._is_rendering
            and self._preview_refresh_after is None
        ):
            self._schedule_preview_refresh(delay_ms=40)

    def _init_state_vars(self):
        cache = getattr(self.app, "cover_state_cache", {}) or {}
        self._cover_state_vars = {}
        for key, var_cls, default in COVER_STATE_SPECS:
            var = var_cls(value=cache.get(key, default))
            self._cover_state_vars[key] = var
            setattr(self, f"{key}_var", var)
        self._sync_cover_state_cache()

    def _sync_cover_state_cache(self):
        if hasattr(self.app, "cover_state_cache"):
            self.app.cover_state_cache = self.get_state()

    def _on_cover_state_changed(self, *_args):
        self._sync_cover_state_cache()
        self._sync_preview_stage_height()
        self._schedule_preview_refresh()

    def build_ui(self):
        sys_fonts = _get_system_fonts()
        scroll_root = AkmScrollablePanel(self)
        scroll_root.pack(fill="both", expand=True)
        self._page_scroll_root = scroll_root
        scroll_root.canvas.bind("<Configure>", self._on_page_resize, add="+")
        page = scroll_root.scrollable_frame
        
        AkmHeader(page, text="Cover Forge").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        self._header_intro_label = AkmSubLabel(
            page,
            text="Artwork, Typografie und Export in einer durchgaengigen Live-Ansicht. Alles, was nach Release riechen soll, sitzt hier.",
            justify="left",
        )
        self._header_intro_label.pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(page, min_height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Cover Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.cover_status_label = AkmLabel(
            status_left,
            text="Kein Master-Artwork geladen",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
            justify="left",
        )
        self.cover_status_label.pack(fill="x", pady=(2, 2))
        self.cover_meta_label = AkmSubLabel(
            status_left,
            text="Layout: Manual | Stil: bold | Vorschau: 260 px",
            bg=PANEL_2,
            anchor="w",
            justify="left",
        )
        self.cover_meta_label.pack(fill="x")

        self._status_primary_button = self.app.btn(
            status_right,
            "Artwork laden",
            self._choose_artwork_path,
            primary=True,
            width=150,
        )
        self._status_primary_button.pack(anchor="e", pady=(0, SPACE_XS))
        status_action_row = tk.Frame(status_right, bg=PANEL_2)
        status_action_row.pack(anchor="e")
        self._status_action_bar = status_action_row
        self._status_action_buttons = (
            self.app.btn(status_action_row, "Zu Release", self._assign_to_release, quiet=True, width=104),
            self.app.btn(status_action_row, "Export", self.export_cover, quiet=True, width=96),
            self.app.btn(status_action_row, "Finder", self._open_artwork_in_finder, quiet=True, width=86),
        )

        content = AkmPanel(page)
        content.pack(fill="both", expand=True, padx=SPACE_MD, pady=0)

        left_side = AkmPanel(content)
        # Use scrollable panel for the right side
        scroll_container = AkmScrollablePanel(content, bg=PANEL) 
        right_side = scroll_container.scrollable_frame
        
        left_side.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        scroll_container.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))
        self._cover_split_widgets = (left_side, scroll_container)
        content.bind("<Configure>", self._on_responsive_resize, add="+")
        self.after_idle(lambda: self._apply_responsive_layout(scroll_root.canvas.winfo_width()))

        # LEFT: PREVIEW & MASTER ASSET
        media_row = AkmPanel(left_side)
        media_row.pack(fill="x", pady=(0, CARD_GAP))
        preview_card = AkmCard(media_row)
        asset_card = AkmCard(media_row, width=320)
        self._cover_media_widgets = (preview_card, asset_card)
        media_row.bind("<Configure>", self._on_cover_media_resize, add="+")
        self.after_idle(lambda: self._apply_cover_media_layout(media_row.winfo_width()))
        
        AkmLabel(preview_card.inner, text="Live-Vorschau", fg=ACCENT, bg=PANEL_2, font=FONT_MD_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        self.cover_preview_caption = AkmSubLabel(
            preview_card.inner,
            text="Die Cover-Buehne zeigt das komplette Cover live und gibt dir sofort ein sauberes Gefuehl fuer Typo, Layout und Balance.",
            bg=PANEL_2,
            justify="left",
            wraplength=420,
        )
        self.cover_preview_caption.pack(anchor="w", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        
        preview_shell = tk.Frame(
            preview_card.inner,
            bg="#0A0A0D",
            highlightbackground="#2C3139",
            highlightthickness=1,
        )
        preview_shell.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.preview_box = AkmPanel(preview_shell, bg="#111111", height=280)
        self.preview_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.preview_box.pack_propagate(False)
        
        # Inner container for actual image/placeholders
        self.preview_inner = tk.Frame(self.preview_box, bg="#111111")
        self.preview_inner.pack(fill="both", expand=True)
        self.preview_box.bind("<Configure>", self._on_preview_box_configure, add="+")
        self.preview_box.bind("<Double-Button-1>", self._open_preview_zoom, add="+")
        self.preview_inner.bind("<Double-Button-1>", self._open_preview_zoom, add="+")

        preview_info = tk.Frame(preview_card.inner, bg=PANEL_2)
        preview_info.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.cover_preview_info_label = AkmLabel(
            preview_info,
            text="Master: keiner | Render: wartet",
            bg=PANEL_2,
            anchor="w",
        )
        self.cover_preview_info_label.pack(fill="x")
        self.cover_preview_hint_label = AkmSubLabel(
            preview_info,
            text="Manual erlaubt freie Platzierung. Presets bauen automatisch Layout-Baender und Textkarten.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
            wraplength=420,
        )
        self.cover_preview_hint_label.pack(fill="x", pady=(2, 0))

        AkmLabel(asset_card.inner, text="Master Asset", fg=ACCENT, bg=PANEL_2, font=FONT_MD_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        self.cover_asset_name_label = AkmLabel(
            asset_card.inner,
            text="Kein Artwork geladen",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
            justify="left",
        )
        self.cover_asset_name_label.pack(fill="x", padx=CARD_PAD_X)
        self.cover_asset_meta_label = AkmSubLabel(
            asset_card.inner,
            text="Zieh ein Cover direkt auf die Vorschau oder lade es hier.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
        )
        self.cover_asset_meta_label.pack(fill="x", padx=CARD_PAD_X, pady=(2, 0))
        self.cover_asset_path_label = AkmSubLabel(
            asset_card.inner,
            text="Unterstuetzt: JPG, PNG, WEBP, TIFF, BMP",
            bg=PANEL_2,
            anchor="w",
            justify="left",
        )
        self.cover_asset_path_label.pack(fill="x", padx=CARD_PAD_X, pady=(SPACE_XS, SPACE_SM))

        asset_button_bar = tk.Frame(asset_card.inner, bg=PANEL_2)
        asset_button_bar.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        self.app.btn(asset_button_bar, "Waehlen", self._choose_artwork_path, primary=True, width=112).pack(fill="x")
        self.app.btn(asset_button_bar, "Aus Release", self._load_artwork_from_release, quiet=True, width=112).pack(fill="x", pady=(SPACE_XS, 0))
        self.app.btn(asset_button_bar, "Finder", self._open_artwork_in_finder, quiet=True, width=112).pack(fill="x", pady=(SPACE_XS, 0))
        self.app.btn(asset_button_bar, "Leeren", self._clear_artwork, quiet=True, width=112).pack(fill="x", pady=(SPACE_XS, 0))

        self.cover_asset_hint_label = AkmSubLabel(
            asset_card.inner,
            text="Das Master bleibt links im Blick, waehrend die tieferen Art-Direction-Regler rechts sitzen.",
            bg=PANEL_2,
            anchor="w",
            justify="left",
        )
        self.cover_asset_hint_label.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))

        # RIGHT: METADATA & FILES
        meta_card = AkmCard(right_side)
        meta_card.pack(fill="both", expand=True)

        form = AkmForm(meta_card.inner, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        form.pack(fill="both", expand=True)
        self._meta_card = meta_card
        
        # TYPOGRAPHY & POSITIONS (COMPACT VERSION)
        def _add_pos_form(header, font_var, color_var, size_var, bold_var, case_var, x_var, y_var):
            form.add_header(header, color=ACCENT if header == "Title Layer" else SUBTLE)
            
            # Row 1: Font & Size & Color
            row_main = tk.Frame(form, bg=PANEL_2)
            row_main.grid(row=form._current_row, column=0, columnspan=2, sticky="ew", pady=(0, 2))
            
            tk.Label(row_main, text="Font:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
            ttk.Combobox(row_main, textvariable=font_var, values=sys_fonts, width=16).pack(side="left", padx=5)
            
            tk.Label(row_main, text="Size:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left", padx=(5, 0))
            tk.Entry(row_main, textvariable=size_var, width=4, bg=FIELD_BG, fg=FIELD_FG, bd=0).pack(side="left", padx=5)
            
            def _pick():
                from tkinter import colorchooser
                c = colorchooser.askcolor(title=f"Farbe {header}")
                if c[1]: color_var.set(c[1])
            
            btn = tk.Label(row_main, text="Color", bg=PANEL_2, fg=ACCENT, cursor="hand2", font=FONT_SM)
            btn.pack(side="left", padx=5)
            btn.bind("<Button-1>", lambda e: _pick())
            
            # Add a small preview of the color
            color_preview = tk.Frame(row_main, width=12, height=12, bg=color_var.get(), highlightthickness=1, highlightbackground=SUBTLE)
            color_preview.pack(side="left", padx=2)
            def _update_cp(*a): color_preview.config(bg=color_var.get())
            color_var.trace_add("write", _update_cp)
            
            # --- BOLD & CAPS ---
            tk.Label(row_main, text="Bold:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left", padx=(10, 0))
            tk.Checkbutton(row_main, variable=bold_var, bg=PANEL_2, activebackground=PANEL_2, selectcolor="#111111", bd=0).pack(side="left")
            
            tk.Label(row_main, text="ABC:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left", padx=(5, 0))
            ttk.Combobox(row_main, textvariable=case_var, values=["normal", "uppercase"], width=6).pack(side="left", padx=2)
            
            form._current_row += 1
            
            # Row 2: X & Y Sliders (Compact side-by-side)
            row_coords = tk.Frame(form, bg=PANEL_2)
            row_coords.grid(row=form._current_row, column=0, columnspan=2, sticky="ew", pady=(0, 10))
            
            # X
            tk.Label(row_coords, text="X", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
            tk.Scale(row_coords, from_=0, to=1800, variable=x_var, orient="horizontal", 
                     bg=PANEL_2, fg=TEXT, highlightthickness=0, resolution=10,
                     showvalue=False, length=80).pack(side="left", padx=(2, 10))
            
            # Y
            tk.Label(row_coords, text="Y", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
            tk.Scale(row_coords, from_=0, to=1800, variable=y_var, orient="horizontal", 
                     bg=PANEL_2, fg=TEXT, highlightthickness=0, resolution=10,
                     showvalue=False, length=80).pack(side="left", padx=2)
            
            # Value display labels
            tk.Label(row_coords, textvariable=x_var, bg=PANEL_2, fg=ACCENT, font=FONT_SM, width=4).pack(side="left", padx=(5, 0))
            tk.Label(row_coords, text=",", bg=PANEL_2, fg=SUBTLE).pack(side="left")
            tk.Label(row_coords, textvariable=y_var, bg=PANEL_2, fg=ACCENT, font=FONT_SM, width=4).pack(side="left")

            form._current_row += 1

        form.add_header("Art Direction")
        form.add_row("Artwork", self._create_artwork_row)
        form.add_row("Direction", self._create_direction_row)
        form.add_row("Render", self._create_render_row)
        form.add_color_field("Hauptfarbe", self.bg_color_var)
        form.add_color_field("Akzentfarbe", self.accent_color_var)

        form.add_header("Cover Content")
        form.add_entry("Interpret", self.artist_var)
        form.add_entry("Titel", self.title_var)
        form.add_entry("Untertitel", self.subtitle_var)

        form.add_header("Typography")
        self._typography_hint_label = AkmSubLabel(
            form,
            text="Manual nutzt die X/Y-Werte. Bei Bottom, Top Left und Center wird die Typografie aus dem Preset gebaut.",
            bg=PANEL_2,
            justify="left",
            wraplength=420,
        )
        self._typography_hint_label.grid(row=form._current_row, column=0, columnspan=2, sticky="w", pady=(0, SPACE_SM))
        form._current_row += 1

        _add_pos_form("Artist Layer", self.artist_font_var, self.artist_color_var, self.artist_size_var, self.artist_bold_var, self.artist_case_var, self.artist_x_var, self.artist_y_var)
        _add_pos_form("Title Layer", self.title_font_var, self.title_color_var, self.title_size_var, self.title_bold_var, self.title_case_var, self.title_x_var, self.title_y_var)
        _add_pos_form("Subtitle Layer", self.subtitle_font_var, self.subtitle_color_var, self.subtitle_size_var, self.subtitle_bold_var, self.subtitle_case_var, self.subtitle_x_var, self.subtitle_y_var)

        # QUALITY CHECK & MONITOR
        form.add_header("Technische Abnahme & Monitor")
        
        # Design Health Monitor (The Cool Feature)
        monitor_frame = tk.Frame(form, bg=PANEL_2)
        monitor_frame.grid(row=form._current_row, column=0, columnspan=2, sticky="w", pady=(0, SPACE_SM))
        form._current_row += 1
        
        b1 = AkmBadge(monitor_frame, "3000px")
        b1.pack(side="left", padx=(0, 4))
        b2 = AkmBadge(monitor_frame, "RGB")
        b2.pack(side="left", padx=4)
        b3 = AkmBadge(monitor_frame, "Bleed")
        b3.pack(side="left", padx=4)
        
        v1 = tk.BooleanVar()
        v2 = tk.BooleanVar()
        v3 = tk.BooleanVar()
        form.add_checkbox("3000 x 3000 px @ 300 DPI", variable=v1)
        form.add_checkbox("RGB Farbraum (Digital)", variable=v2)
        form.add_checkbox("Keine Anschnittfehler", variable=v3)

        # Linking
        v1.trace_add("write", lambda *a: b1.set_active(v1.get()))
        v2.trace_add("write", lambda *a: b2.set_active(v2.get()))
        v3.trace_add("write", lambda *a: b3.set_active(v3.get()))

        # BUTTON BAR
        btn_bar = AkmPanel(meta_card.inner, bg=PANEL_2)
        btn_bar.pack(fill="x", padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self._cover_button_bar = btn_bar
        self._cover_button_widgets = (
            self.app.btn(btn_bar, "Release zuweisen", self._assign_to_release, primary=True, width=146),
            self.app.btn(btn_bar, "Cover exportieren", self.export_cover, primary=True, width=146),
            self.app.btn(btn_bar, "Projekt speichern", self.save_project_locally, quiet=True, width=138),
            self.app.btn(btn_bar, "Im Finder", self._open_artwork_in_finder, quiet=True, width=104),
        )
        meta_card.bind("<Configure>", self._on_action_bar_resize, add="+")
        self.after_idle(lambda: self._apply_cover_action_layout(meta_card.winfo_width()))
        self.after_idle(lambda: self._update_wraplengths(content.winfo_width(), meta_card.winfo_width()))

        self._show_placeholders()
        self._update_cover_dashboard()

    def _on_responsive_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _on_page_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _on_cover_media_resize(self, event):
        self._apply_cover_media_layout(event.width)

    def _apply_responsive_layout(self, width):
        if not hasattr(self, "_cover_split_widgets"):
            return
        target_mode = "stack" if width and width < self.STACK_BREAKPOINT else "split"
        if target_mode != self._cover_layout_mode:
            self._cover_layout_mode = target_mode

            left_side, scroll_container = self._cover_split_widgets
            left_side.pack_forget()
            scroll_container.pack_forget()

            if target_mode == "stack":
                left_side.pack(side="top", fill="x", expand=False, pady=(0, CARD_GAP))
                scroll_container.pack(side="top", fill="both", expand=True)
            else:
                left_side.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
                scroll_container.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))

        meta_width = self._meta_card.winfo_width() if hasattr(self, "_meta_card") else width
        self._apply_status_actions_layout(width)
        self._update_wraplengths(width, meta_width)

    def _apply_cover_media_layout(self, width):
        if not hasattr(self, "_cover_media_widgets"):
            return
        target_mode = "stack" if width and width < self.MEDIA_STACK_BREAKPOINT else "row"
        if target_mode == self._cover_media_mode:
            return
        self._cover_media_mode = target_mode

        preview_card, asset_card = self._cover_media_widgets
        preview_card.pack_forget()
        asset_card.pack_forget()

        if target_mode == "stack":
            preview_card.pack(fill="x", pady=(0, CARD_GAP))
            asset_card.pack(fill="x")
            return

        preview_card.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        asset_card.pack(side="left", fill="both", expand=False, padx=(CARD_GAP // 2, 0))

    def _on_action_bar_resize(self, event):
        content_width = self._cover_split_widgets[0].master.winfo_width() if hasattr(self, "_cover_split_widgets") else event.width
        self._update_wraplengths(content_width, event.width)
        self._apply_cover_action_layout(event.width)

    def _apply_cover_action_layout(self, width):
        if not hasattr(self, "_cover_button_widgets"):
            return
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if target_mode == self._cover_action_mode:
            return
        self._cover_action_mode = target_mode

        for button in self._cover_button_widgets:
            button.pack_forget()

        if target_mode == "stack":
            for index, button in enumerate(self._cover_button_widgets):
                button.pack(fill="x", pady=(0, SPACE_XS if index < len(self._cover_button_widgets) - 1 else 0))
            return

        for index, button in enumerate(self._cover_button_widgets):
            pad_left = 0 if index == 0 else SPACE_SM
            button.pack(side="left", padx=(pad_left, 0))

    def _apply_status_actions_layout(self, width):
        if not hasattr(self, "_status_action_buttons"):
            return
        target_mode = "stack" if width and width < self.ACTION_STACK_BREAKPOINT else "row"
        if target_mode == self._status_action_mode:
            return
        self._status_action_mode = target_mode

        self._status_primary_button.pack_forget()
        for button in self._status_action_buttons:
            button.pack_forget()

        if target_mode == "stack":
            self._status_primary_button.pack(anchor="e", fill="x", pady=(0, SPACE_XS))
            self._status_action_bar.pack(anchor="e", fill="x")
            for index, button in enumerate(self._status_action_buttons):
                button.pack(anchor="e", fill="x", pady=(0, SPACE_XS if index < len(self._status_action_buttons) - 1 else 0))
            return

        self._status_primary_button.pack(anchor="e", pady=(0, SPACE_XS))
        self._status_action_bar.pack(anchor="e")
        for index, button in enumerate(self._status_action_buttons):
            button.pack(side="left", padx=(0, SPACE_XS if index < len(self._status_action_buttons) - 1 else 0))

    def _update_wraplengths(self, content_width, meta_width):
        split_mode = self._cover_layout_mode or "split"
        preview_width = content_width if split_mode == "stack" else max(360, (content_width - CARD_GAP) // 2)
        media_mode = self._cover_media_mode or "row"
        asset_width = preview_width if media_mode == "stack" else max(260, min(340, preview_width // 2))
        preview_text_width = preview_width if media_mode == "stack" else max(260, preview_width - asset_width - CARD_GAP)
        form_width = meta_width if meta_width else preview_width
        fit_wraplength(self._header_intro_label, content_width, padding=120, minimum=300, maximum=900)
        fit_wraplength(self.cover_status_label, content_width, padding=280, minimum=260, maximum=620)
        fit_wraplength(self.cover_meta_label, content_width, padding=260, minimum=260, maximum=560)
        fit_wraplength(self.cover_preview_caption, preview_text_width, padding=90, minimum=240, maximum=420)
        fit_wraplength(self.cover_preview_hint_label, preview_text_width, padding=90, minimum=240, maximum=420)
        if hasattr(self, "cover_asset_name_label"):
            fit_wraplength(self.cover_asset_name_label, asset_width, padding=90, minimum=220, maximum=300)
        if hasattr(self, "cover_asset_meta_label"):
            fit_wraplength(self.cover_asset_meta_label, asset_width, padding=90, minimum=220, maximum=300)
        if hasattr(self, "cover_asset_path_label"):
            fit_wraplength(self.cover_asset_path_label, asset_width, padding=90, minimum=220, maximum=300)
        if hasattr(self, "cover_asset_hint_label"):
            fit_wraplength(self.cover_asset_hint_label, asset_width, padding=90, minimum=220, maximum=300)
        fit_wraplength(self._typography_hint_label, form_width, padding=90, minimum=280, maximum=500)
        if hasattr(self, "_artwork_hint_label"):
            fit_wraplength(self._artwork_hint_label, form_width, padding=180, minimum=220, maximum=360)
        if hasattr(self, "_direction_hint_label"):
            fit_wraplength(self._direction_hint_label, form_width, padding=90, minimum=260, maximum=460)

    def _choose_artwork_path(self):
        path = filedialog.askopenfilename(filetypes=IMAGE_FILETYPES)
        if path:
            self.load_cover(path)

    def _clear_artwork(self):
        self.artwork_path_var.set("")
        self._current_image = None
        self._photo = None
        self._is_rendering = False
        self._open_zoom_when_ready = False
        self._last_preview_error = ""
        self._artwork_meta_path = None
        self._artwork_meta = None
        self._show_placeholders()
        self._update_cover_dashboard()

    def _load_artwork_from_release(self):
        release_vars = getattr(self.app, "release_vars", {}) or {}
        cover_var = release_vars.get("cover_path")
        path = cover_var.get().strip() if cover_var and hasattr(cover_var, "get") else ""
        if not path:
            AkmToast(self, "RELEASE HAT NOCH KEIN COVER", color=ui_patterns.FLAVOR_ERROR)
            return
        if not os.path.isfile(path):
            AkmToast(self, "RELEASE-COVER NICHT GEFUNDEN", color=ui_patterns.FLAVOR_ERROR)
            return
        self.load_cover(path)
        self.app.append_log(f"Artwork aus Release uebernommen: {os.path.basename(path)}")

    def _open_artwork_in_finder(self):
        path = self.artwork_path_var.get().strip()
        if not path or not os.path.exists(path):
            AkmToast(self, "KEIN MASTER-ARTWORK IM FINDER", color=ui_patterns.FLAVOR_ERROR)
            return
        ui_patterns.open_in_finder(path)

    def _create_artwork_row(self, parent):
        wrap = tk.Frame(parent, bg=PANEL_2)

        row_main = tk.Frame(wrap, bg=PANEL_2)
        row_main.pack(fill="x")
        AkmEntry(row_main, textvariable=self.artwork_path_var, font=FONT_SM).pack(side="left", fill="x", expand=True)
        self.app.btn(row_main, "Waehlen", self._choose_artwork_path, primary=True, width=92).pack(side="left", padx=(SPACE_XS, 0))
        self.app.btn(row_main, "Finder", self._open_artwork_in_finder, quiet=True, width=84).pack(side="left", padx=(SPACE_XS, 0))

        row_aux = tk.Frame(wrap, bg=PANEL_2)
        row_aux.pack(fill="x", pady=(SPACE_XS, 0))
        self.app.btn(row_aux, "Aus Release", self._load_artwork_from_release, quiet=True, width=108).pack(side="left")
        self.app.btn(row_aux, "Leeren", self._clear_artwork, quiet=True, width=84).pack(side="left", padx=(SPACE_XS, 0))
        self._artwork_hint_label = AkmSubLabel(
            row_aux,
            text="JPG, PNG, WEBP, TIFF oder BMP. Direkt auf die Vorschau ziehen geht auch.",
            bg=PANEL_2,
            justify="left",
        )
        self._artwork_hint_label.pack(side="left", padx=(SPACE_SM, 0), fill="x", expand=True)
        return wrap

    def _create_direction_row(self, parent):
        wrap = tk.Frame(parent, bg=PANEL_2)

        row_main = tk.Frame(wrap, bg=PANEL_2)
        row_main.pack(fill="x")
        tk.Label(row_main, text="Layout", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        ttk.Combobox(
            row_main,
            textvariable=self.layout_var,
            values=["manual", "bottom", "topleft", "center"],
            state="readonly",
            width=11,
        ).pack(side="left", padx=(SPACE_XS, SPACE_SM))
        tk.Label(row_main, text="Stil", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        ttk.Combobox(
            row_main,
            textvariable=self.style_var,
            values=["clean", "bold", "cinematic"],
            state="readonly",
            width=11,
        ).pack(side="left", padx=(SPACE_XS, 0))

        self._direction_hint_label = AkmSubLabel(
            wrap,
            text="Manual nutzt deine X/Y-Werte. Bottom, Top Left und Center bauen automatisch saubere Text-Frames.",
            bg=PANEL_2,
            justify="left",
            wraplength=420,
        )
        self._direction_hint_label.pack(anchor="w", pady=(SPACE_XS, 0))
        return wrap

    def _create_render_row(self, parent):
        wrap = tk.Frame(parent, bg=PANEL_2)

        row_main = tk.Frame(wrap, bg=PANEL_2)
        row_main.pack(fill="x")
        tk.Label(row_main, text="Vorschau", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        tk.Scale(
            row_main,
            from_=220,
            to=520,
            resolution=20,
            variable=self.ui_preview_zoom_var,
            orient="horizontal",
            bg=PANEL_2,
            fg=TEXT,
            highlightthickness=0,
            showvalue=False,
            length=120,
        ).pack(side="left", padx=(SPACE_XS, 0))
        tk.Label(row_main, textvariable=self.ui_preview_zoom_var, bg=PANEL_2, fg=ACCENT, font=FONT_SM, width=4).pack(side="left", padx=(SPACE_XS, 0))
        tk.Label(row_main, text="px", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left", padx=(0, SPACE_SM))
        self.app.btn(row_main, "Zoom-Fenster", self._open_preview_zoom, quiet=True, width=118).pack(side="left", padx=(0, SPACE_SM))

        tk.Label(row_main, text="Zoom", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        tk.Scale(
            row_main,
            from_=0.8,
            to=1.4,
            resolution=0.05,
            variable=self.zoom_var,
            orient="horizontal",
            bg=PANEL_2,
            fg=TEXT,
            highlightthickness=0,
            showvalue=False,
            length=120,
        ).pack(side="left", padx=(SPACE_XS, 0))

        row_aux = tk.Frame(wrap, bg=PANEL_2)
        row_aux.pack(fill="x", pady=(SPACE_XS, 0))
        tk.Label(row_aux, text="Groesse", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        ttk.Combobox(
            row_aux,
            textvariable=self.size_mode_var,
            values=["small", "medium", "large"],
            state="readonly",
            width=9,
        ).pack(side="left", padx=(SPACE_XS, SPACE_SM))
        tk.Label(row_aux, text="Overlay", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        ttk.Combobox(
            row_aux,
            textvariable=self.overlay_var,
            values=["soft", "medium", "strong"],
            state="readonly",
            width=9,
        ).pack(side="left", padx=(SPACE_XS, SPACE_SM))
        tk.Label(row_aux, text="Offset", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        ttk.Combobox(
            row_aux,
            textvariable=self.offset_var,
            values=["high", "normal", "low"],
            state="readonly",
            width=9,
        ).pack(side="left", padx=(SPACE_XS, 0))
        return wrap

    def _on_preview_box_configure(self, event):
        dims = (max(0, int(event.width)), max(0, int(event.height)))
        if dims == self._preview_dimensions:
            return
        self._preview_dimensions = dims
        if self._current_image is not None and not self._is_rendering:
            self._display_preview_image()
        self._update_cover_dashboard()

    def _sync_preview_stage_height(self):
        if not hasattr(self, "preview_box"):
            return
        target_h = max(220, int(self.ui_preview_zoom_var.get()))
        stage_h = max(280, target_h + 20)
        current_h = int(self.preview_box.cget("height"))
        if current_h != stage_h:
            self.preview_box.configure(height=stage_h)

    def _normalized_layout(self):
        raw = (self.layout_var.get() or "manual").strip().lower().replace("_", "").replace("-", "").replace(" ", "")
        if raw in {"bottom", "center", "topleft"}:
            return raw
        return "manual"

    def _format_cover_text(self, text, case_mode):
        text = (text or "").strip()
        if case_mode == "uppercase":
            return text.upper()
        return text

    def _read_artwork_meta(self, path):
        if not path or not os.path.isfile(path):
            self._artwork_meta_path = path
            self._artwork_meta = None
            return None
        if path == self._artwork_meta_path:
            return self._artwork_meta

        details = {
            "ext": os.path.splitext(path)[1].replace(".", "").upper() or "Datei",
            "size_text": "",
            "dimensions": None,
        }
        try:
            size_bytes = os.path.getsize(path)
            details["size_text"] = self._format_file_size(size_bytes)
        except Exception:
            details["size_text"] = ""
        try:
            with Image.open(path) as image:
                details["dimensions"] = image.size
        except Exception:
            details["dimensions"] = None

        self._artwork_meta_path = path
        self._artwork_meta = details
        return details

    def _format_file_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def _build_cover_options(self):
        return {
            "bg_color": self.bg_color_var.get().strip() or "#181818",
            "accent_color": self.accent_color_var.get().strip() or "#ff9a3c",
            "style": release_view_tools.selected_release_cover_style(self.style_var.get()),
            "size_mode": release_view_tools.selected_release_cover_size(self.size_mode_var.get()),
            "overlay": release_view_tools.selected_release_cover_overlay(self.overlay_var.get()),
            "offset": release_view_tools.selected_release_cover_offset(self.offset_var.get()),
        }

    def _safe_int(self, value, fallback):
        try:
            return int(float(value))
        except Exception:
            return fallback

    def _build_font_configs(self, target_size):
        scale = target_size / 1800.0
        return [
            {
                "text": self._format_cover_text(self.artist_var.get(), self.artist_case_var.get()),
                "size": max(12, int(self._safe_int(self.artist_size_var.get(), 60) * scale)),
                "font": self.artist_font_var.get(),
                "bold": self.artist_bold_var.get(),
                "color": self.artist_color_var.get(),
                "x": int(self._safe_int(self.artist_x_var.get(), 900) * scale),
                "y": int(self._safe_int(self.artist_y_var.get(), 1400) * scale),
            },
            {
                "text": self._format_cover_text(self.title_var.get(), self.title_case_var.get()),
                "size": max(12, int(self._safe_int(self.title_size_var.get(), 140) * scale)),
                "font": self.title_font_var.get(),
                "bold": self.title_bold_var.get(),
                "color": self.title_color_var.get(),
                "x": int(self._safe_int(self.title_x_var.get(), 900) * scale),
                "y": int(self._safe_int(self.title_y_var.get(), 1500) * scale),
            },
            {
                "text": self._format_cover_text(self.subtitle_var.get(), self.subtitle_case_var.get()),
                "size": max(12, int(self._safe_int(self.subtitle_size_var.get(), 40) * scale)),
                "font": self.subtitle_font_var.get(),
                "bold": self.subtitle_bold_var.get(),
                "color": self.subtitle_color_var.get(),
                "x": int(self._safe_int(self.subtitle_x_var.get(), 900) * scale),
                "y": int(self._safe_int(self.subtitle_y_var.get(), 1600) * scale),
            },
        ]

    def _render_cover_image(self, target_size, output_path=None):
        from PIL import ImageDraw
        from app_logic import cover_tools

        if not cover_tools.have_pillow():
            raise RuntimeError("Pillow ist fuer das Cover-Rendering nicht verfuegbar.")

        path = self.artwork_path_var.get().strip()
        if not path or not os.path.isfile(path):
            raise FileNotFoundError("Kein gueltiges Master-Artwork vorhanden.")

        zoom_val = self.zoom_var.get()
        layout = self._normalized_layout()
        options = self._build_cover_options()
        title = self._format_cover_text(self.title_var.get(), self.title_case_var.get())
        artist = self._format_cover_text(self.artist_var.get(), self.artist_case_var.get())
        subtitle = self._format_cover_text(self.subtitle_var.get(), self.subtitle_case_var.get()) or None

        with Image.open(path) as original:
            base = cover_tools.resize_cover_canvas(original, target_size, target_size, zoom=zoom_val)
            if layout == "manual":
                image = base.convert("RGBA")
                draw = ImageDraw.Draw(image, "RGBA")
                cover_tools.render_manual_layout(
                    draw,
                    target_size,
                    target_size,
                    self._build_font_configs(target_size),
                    zoom=zoom_val,
                )
                return cover_tools.save_release_cover_variant(image, output_path)

            image = cover_tools.build_release_cover_variant(
                layout,
                base,
                title,
                artist,
                output_path,
                options,
                subtitle=subtitle,
            )
            return image.convert("RGB") if image.mode != "RGB" else image

    def _schedule_preview_refresh(self, delay_ms=120):
        if self._preview_refresh_after is not None:
            try:
                self.after_cancel(self._preview_refresh_after)
            except Exception:
                pass
        self._preview_refresh_after = self.after(delay_ms, self.refresh_preview)

    def _update_cover_dashboard(self):
        layout = self._normalized_layout()
        style = release_view_tools.selected_release_cover_style(self.style_var.get())
        size_mode = release_view_tools.selected_release_cover_size(self.size_mode_var.get())
        overlay = release_view_tools.selected_release_cover_overlay(self.overlay_var.get())
        offset = release_view_tools.selected_release_cover_offset(self.offset_var.get())
        preview_height = self.ui_preview_zoom_var.get()
        artwork_path = self.artwork_path_var.get().strip()
        artwork_name = os.path.basename(artwork_path) if artwork_path else "keiner"
        artwork_meta = self._read_artwork_meta(artwork_path)

        if not artwork_path or not os.path.exists(artwork_path):
            status_text = "Kein Master-Artwork geladen"
        elif self._last_preview_error:
            status_text = "Artwork geladen, aber Rendering hat gehuestelt"
        elif self._is_rendering:
            status_text = f"{_friendly_layout_name(layout)} wird neu gerendert"
        elif layout == "manual":
            status_text = "Manual bereit fuer freie Typografie"
        else:
            status_text = f"{_friendly_layout_name(layout)} bereit fuer Export"

        self.cover_status_label.config(text=status_text)
        self.cover_meta_label.config(
            text=(
                f"Layout: {_friendly_layout_name(layout)} | Stil: {style} | Textblock: {size_mode} "
                f"| Overlay: {overlay} | Offset: {offset} | Vorschau: {preview_height} px"
            )
        )

        if self._current_image is not None:
            render_w, render_h = self._current_image.size
            info_text = f"Master: {artwork_name} | Render: {render_w}x{render_h}"
        elif self._is_rendering:
            info_text = f"Master: {artwork_name} | Render: arbeitet"
        elif self._last_preview_error:
            info_text = f"Master: {artwork_name} | Render: Fehler"
        else:
            info_text = "Master: keiner | Render: wartet"

        if self._preview_dimensions:
            info_text += f" | Stage: {self._preview_dimensions[0]}x{self._preview_dimensions[1]}"
        self.cover_preview_info_label.config(text=info_text)

        hints = {
            "manual": "Manual erlaubt freie Platzierung mit X/Y und individuellen Fonts pro Layer.",
            "bottom": "Bottom Band legt ein dunkles Fussband an und zentriert den Textblock fuer Release-Cover.",
            "topleft": "Top Left Card setzt eine Typo-Karte oben links mit Akzentkante und mehr Editorial-Vibe.",
            "center": "Center Band baut einen horizontalen Mittelstreifen mit klarer, symmetrischer Titelbuehne.",
        }
        hint_text = hints.get(layout, hints["manual"])
        if self._last_preview_error:
            hint_text = f"{hint_text} Letzter Fehler: {self._last_preview_error}"
        self.cover_preview_hint_label.config(text=hint_text)

        if not artwork_path or not os.path.exists(artwork_path):
            asset_name = "Kein Artwork geladen"
            asset_meta = "Quadratisches Master-Artwork laden und links sofort gegen die Typografie pruefen."
            asset_path = "Unterstuetzt: JPG, PNG, WEBP, TIFF, BMP"
        else:
            dims = ""
            if artwork_meta and artwork_meta.get("dimensions"):
                dims = f"{artwork_meta['dimensions'][0]}x{artwork_meta['dimensions'][1]} px"
            size_text = artwork_meta.get("size_text", "") if artwork_meta else ""
            ext = artwork_meta.get("ext", "Datei") if artwork_meta else "Datei"
            meta_parts = [part for part in (dims, size_text, ext) if part]
            asset_name = artwork_name
            asset_meta = " | ".join(meta_parts) if meta_parts else "Master-Artwork geladen"
            asset_path = artwork_path

        self.cover_asset_name_label.config(text=asset_name)
        self.cover_asset_meta_label.config(text=asset_meta)
        self.cover_asset_path_label.config(text=asset_path)

    def get_state(self):
        """Returns the current state of all cover configuration variables."""
        return {key: var.get() for key, var in self._cover_state_vars.items()}

    def set_state(self, state):
        """Restores the UI state from a dictionary."""
        if not state: return
        for key, value in state.items():
            if key in self._cover_state_vars:
                self._cover_state_vars[key].set(value)

        self._sync_cover_state_cache()
        self._schedule_preview_refresh(delay_ms=160)

    def save_project_locally(self):
        """Convenience wrapper to trigger the application-wide project save."""
        if hasattr(self.app, "save_project"):
            self.app.save_project()
        else:
            AkmToast(self, "Master-Speicherung nicht verfügbar")

    def _show_placeholders(self):
        """Restores the industrial placeholder view."""
        self._sync_preview_stage_height()
        for child in self.preview_inner.winfo_children():
            child.destroy()
        self._photo = None
        AkmLabel(self.preview_inner, text="3000 x 3000 px", bg="#111111", fg="#2a2a2a", font=FONT_XXL).pack(expand=True)
        AkmSubLabel(self.preview_inner, text="Bild hier hineinziehen", bg="#111111", fg=SUBTLE).pack(pady=(0, 20))

    def _setup_dnd(self):
        """Standard registration on the main container."""
        if DND_FILES:
            try:
                self.preview_box.drop_target_register(DND_FILES)
                self.preview_box.dnd_bind('<<Drop>>', self._handle_drop)
                self.preview_inner.drop_target_register(DND_FILES)
                self.preview_inner.dnd_bind('<<Drop>>', self._handle_drop)
                self.app.append_log("Drag-In bereit.")
            except Exception as e:
                self.app.append_log(f"Fehler bei DnD-Registrierung: {e}")
        else:
            self.app.append_log("DnD System nicht geladen (DND_FILES=None)")

    def _handle_drop(self, event):
        """Ultra-robust path parsing with logging."""
        data = event.data
        if not data: return
        
        self.app.append_log(f"DRAG DATA: {data}")
        
        try:
            # 1. Clean braces (common on macOS for single files)
            if isinstance(data, str):
                if data.startswith('{') and data.endswith('}'):
                    data = data[1:-1]
                
                # 2. Try splitlist first (standard Tk way)
                files = self.preview_box.tk.splitlist(data)
                
                # 3. If splitlist failed or is empty, try manual split
                if not files:
                    import re
                    # Fallback for complex paths with spaces: 
                    # Match everything inside {} or space-separated if not inside {}
                    files = re.findall(r'\{.*?\}|\S+', data)
                    # Clean the {} from those
                    files = [f[1:-1] if f.startswith('{') else f for f in files]

                if files:
                    target = files[0]
                    # Cleanup any leading/trailing trash
                    target = target.strip('"\'')
                    
                    if os.path.exists(target) and os.path.isfile(target):
                        ext = os.path.splitext(target.lower())[1]
                        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                            self.load_cover(target)
                        else:
                            self.app.append_log(f"Falsches Format: {ext}")
                    else:
                        self.app.append_log(f"Datei nicht gefunden: {target}")
        except Exception as e:
            self.app.append_log(f"Internal DnD Error: {e}")
            import traceback
            print(traceback.format_exc())

    def load_cover(self, path):
        """Simplest path to set the base artwork and start previewing."""
        if not os.path.isfile(path):
            AkmToast(self, "ARTWORK NICHT GEFUNDEN", color=ui_patterns.FLAVOR_ERROR)
            return

        self._artwork_meta_path = None
        self._artwork_meta = None
        self.artwork_path_var.set(path)
        self._last_preview_error = ""
        self.app.append_log(f"Cover geladen: {os.path.basename(path)}")
        self._schedule_preview_refresh(delay_ms=40)

    def _setup_traces(self):
        """Triggers preview refresh on variable changes."""
        for var in self._cover_state_vars.values():
            var.trace_add("write", self._on_cover_state_changed)

    def refresh_preview(self):
        """Renders the current text onto the cover image for preview."""
        self._preview_refresh_after = None
        path = self.artwork_path_var.get()
        if not path or not os.path.exists(path):
            self._current_image = None
            self._is_rendering = False
            self._last_preview_error = ""
            self._show_placeholders()
            self._update_cover_dashboard()
            return

        self._is_rendering = True
        self._last_preview_error = ""
        self._update_cover_dashboard()

        self.app.tasks.run(
            lambda: self._render_cover_image(1800),
            self._on_preview_rendered,
            self._on_preview_error,
            busy_text=None,
        )

    def _on_preview_rendered(self, img):
        """Updates the UI with the newly rendered preview image, respecting the UI Zoom."""
        if not img:
            return

        self._is_rendering = False
        self._last_preview_error = ""
        self._current_image = img
        self._display_preview_image()
        self._update_cover_dashboard()
        if self._open_zoom_when_ready:
            self._open_zoom_when_ready = False
            self._open_preview_zoom()

    def _open_preview_zoom(self, _event=None):
        if self._is_rendering:
            AkmToast(self, "VORSCHAU WIRD GERADE AKTUALISIERT", color=ACCENT)
            return

        if self._current_image is not None:
            from app_ui.dialogs import AkmRenderedImageZoomDialog

            title = self.title_var.get().strip() or "Cover"
            AkmRenderedImageZoomDialog(self, self._current_image, title=f"{title} Zoom")
            return

        artwork_path = self.artwork_path_var.get().strip()
        if not artwork_path or not os.path.exists(artwork_path):
            AkmToast(self, "KEIN COVER FUER ZOOM GELADEN", color=ui_patterns.FLAVOR_ERROR)
            return

        self._open_zoom_when_ready = True
        AkmToast(self, "VORSCHAU WIRD ZUERST GERENDERT", color=ACCENT)
        self.refresh_preview()

    def _display_preview_image(self):
        """Fits the rendered cover into the visible preview stage without clipping."""
        if self._current_image is None:
            return

        self._sync_preview_stage_height()
        stage_w = self.preview_inner.winfo_width() or self.preview_box.winfo_width()
        stage_h = self.preview_inner.winfo_height() or self.preview_box.winfo_height()
        stage_w = max(1, int(stage_w) - 8)
        stage_h = max(1, int(stage_h) - 8)

        target_h = max(1, int(self.ui_preview_zoom_var.get()))
        w, h = self._current_image.size
        fit_ratio = min(stage_w / w, stage_h / h, target_h / h)
        fit_ratio = max(fit_ratio, 1 / max(w, h))
        new_w = max(1, int(w * fit_ratio))
        new_h = max(1, int(h * fit_ratio))

        preview_img = self._current_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(preview_img)

        for child in self.preview_inner.winfo_children():
            child.destroy()

        image_label = tk.Label(self.preview_inner, image=self._photo, bg="#111111", bd=0, highlightthickness=0)
        image_label.pack(expand=True)
        image_label.bind("<Double-Button-1>", self._open_preview_zoom, add="+")

    def _on_preview_error(self, error_msg):
        self._is_rendering = False
        self._open_zoom_when_ready = False
        self._current_image = None
        self._last_preview_error = error_msg
        self.app.append_log(f"Preview-Rendering fehlgeschlagen: {error_msg}")
        self._show_placeholders()
        self._update_cover_dashboard()

    def _assign_to_release(self):
        """Transfers the current artwork path to the Release tab's metadata."""
        path = self.artwork_path_var.get()
        if not path or not os.path.exists(path):
            AkmToast(self, "KEIN ARTWORK ZUM ZUWEISEN", color="#FF3B30")
            return

        if hasattr(self.app, "release_state_cache"):
            self.app.release_state_cache["cover_path"] = path
        if hasattr(self.app, "release_vars") and "cover_path" in self.app.release_vars:
            self.app.release_vars["cover_path"].set(path)
        if hasattr(self.app, "release_ctrl"):
            self.app.release_ctrl.refresh_view(force=True)
        self.app.select_tab_by_id("release")
        AkmToast(self.app, "COVER IN RELEASE ÜBERNOMMEN", color=ACCENT)

    def export_cover(self):
        """Final high-quality render and save to file."""
        path = self.artwork_path_var.get()
        if not path or not os.path.exists(path):
            AkmToast(self, "KEIN MASTER-ARTWORK GELADEN", color="#FF3B30")
            return

        out_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")],
            initialdir=os.path.dirname(path),
            initialfile=f"Cover_{self.title_var.get().replace(' ', '_')}.jpg"
        )
        
        if not out_path:
            return

        def _render_full():
            self._render_cover_image(3000, output_path=out_path)
            return out_path

        def _done(res):
            if res:
                self.app.append_log(f"Cover exportiert: {os.path.basename(res)}")
                AkmToast(self, "COVER ERFOLGREICH EXPORTIERT")
            else:
                AkmToast(self, "FEHLER BEIM EXPORT", color="#FF3B30")

        self.app.tasks.run(
            _render_full,
            _done,
            lambda error_msg: AkmToast(self, f"EXPORT-FEHLER: {error_msg}", color=ui_patterns.FLAVOR_ERROR),
            busy_text="Exportiere hochaufloesendes Cover...",
        )
