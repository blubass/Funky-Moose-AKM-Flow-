import tkinter as tk
from tkinter import filedialog, ttk
import os
from PIL import Image, ImageTk
import app_ui.ui_patterns as ui_patterns
from app_ui import release_view_tools
from app_ui.ui_patterns import (
    AkmPanel, AkmCard, AkmLabel, AkmSubLabel, AkmHeader, AkmForm, AkmEntry, AkmText, AkmBadge,
    AkmScrollablePanel, AkmToast,
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


def _friendly_layout_name(layout_key):
    mapping = {
        "manual": "Manual",
        "bottom": "Bottom Band",
        "topleft": "Top Left Card",
        "center": "Center Band",
    }
    return mapping.get(layout_key, "Manual")

class CoverTab(AkmPanel):
    STACK_BREAKPOINT = 1320
    ACTION_STACK_BREAKPOINT = 760

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._cover_layout_mode = None
        self._cover_action_mode = None
        self._current_image = None
        self._photo = None
        self._is_rendering = False
        self._last_preview_error = ""
        
        # State Variables
        self.artwork_path_var = tk.StringVar()
        self.artist_var = tk.StringVar(value="MARIO MUSTERMANN")
        self.title_var = tk.StringVar(value="DER GROSSE WURF")
        self.subtitle_var = tk.StringVar(value="Digital Deluxe Edition")
        
        # Font Configuration (One per layer)
        self.artist_font_var = tk.StringVar(value="Helvetica Neue")
        self.artist_color_var = tk.StringVar(value="#FFFFFF")
        self.artist_bold_var = tk.BooleanVar(value=False)
        self.artist_case_var = tk.StringVar(value="uppercase")
        
        self.title_font_var = tk.StringVar(value="Helvetica Neue")
        self.title_color_var = tk.StringVar(value="#FFFFFF")
        self.title_bold_var = tk.BooleanVar(value=True)
        self.title_case_var = tk.StringVar(value="uppercase")
        
        self.subtitle_font_var = tk.StringVar(value="Inter Mono")
        self.subtitle_color_var = tk.StringVar(value="#D2D2D2")
        self.subtitle_bold_var = tk.BooleanVar(value=False)
        self.subtitle_case_var = tk.StringVar(value="normal")
        
        # Font Sizes & Positions
        self.artist_size_var = tk.StringVar(value="60")
        self.artist_x_var = tk.StringVar(value="900")
        self.artist_y_var = tk.StringVar(value="1400")
        
        self.title_size_var = tk.StringVar(value="140")
        self.title_x_var = tk.StringVar(value="900")
        self.title_y_var = tk.StringVar(value="1500")
        
        self.subtitle_size_var = tk.StringVar(value="40")
        self.subtitle_x_var = tk.StringVar(value="900")
        self.subtitle_y_var = tk.StringVar(value="1650")
        
        # Layout Defaults
        self.layout_var = tk.StringVar(value="manual")
        self.style_var = tk.StringVar(value="bold")
        self.size_mode_var = tk.StringVar(value="medium")
        self.overlay_var = tk.StringVar(value="medium")
        self.offset_var = tk.StringVar(value="normal")
        
        # Image & UI Transformation
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.ui_preview_zoom_var = tk.IntVar(value=400) # Default UI height
        
        # General Colors
        self.bg_color_var = tk.StringVar(value="#181818")
        self.accent_color_var = tk.StringVar(value="#ff9a3c")
        self._preview_refresh_after = None
        self._preview_dimensions = None
        
        self.pack(fill="both", expand=True)
        self.build_ui()
        self._setup_dnd()
        self._setup_traces()

    def build_ui(self):
        import tkinter.font as tkfont
        sys_fonts = sorted(tkfont.families())
        
        AkmHeader(self, text="Cover Forge").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(
            self,
            text="Artwork, Typografie und Export in einer durchgaengigen Live-Ansicht. Alles, was nach Release riechen soll, sitzt hier.",
        ).pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        status_card = AkmCard(self, height=118)
        status_card.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_SM))
        status_left = tk.Frame(status_card.inner, bg=PANEL_2)
        status_left.pack(side="left", fill="both", expand=True, padx=(CARD_PAD_X, SPACE_SM), pady=CARD_PAD_Y)
        status_right = tk.Frame(status_card.inner, bg=PANEL_2)
        status_right.pack(side="right", padx=(SPACE_SM, CARD_PAD_X), pady=CARD_PAD_Y)

        AkmLabel(status_left, text="Art Direction Radar", fg=ACCENT, bg=PANEL_2, font=FONT_LG).pack(anchor="w")
        self.cover_status_label = AkmLabel(
            status_left,
            text="Kein Master-Artwork geladen",
            bg=PANEL_2,
            anchor="w",
            font=FONT_MD_BOLD,
        )
        self.cover_status_label.pack(fill="x", pady=(2, 2))
        self.cover_meta_label = AkmSubLabel(
            status_left,
            text="Layout: manual | Stil: bold | Preview: 400 px",
            bg=PANEL_2,
            anchor="w",
        )
        self.cover_meta_label.pack(fill="x")

        self.app.btn(status_right, "Artwork laden", self._choose_artwork_path, primary=True, width=150).pack(anchor="e", pady=(0, SPACE_XS))
        status_action_row = tk.Frame(status_right, bg=PANEL_2)
        status_action_row.pack(anchor="e")
        self.app.btn(status_action_row, "Zu Release", self._assign_to_release, quiet=True, width=104).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(status_action_row, "Export", self.export_cover, quiet=True, width=96).pack(side="left", padx=(0, SPACE_XS))
        self.app.btn(status_action_row, "Finder", self._open_artwork_in_finder, quiet=True, width=86).pack(side="left")

        content = AkmPanel(self)
        content.pack(fill="both", expand=True, padx=SPACE_MD, pady=0)

        left_side = AkmPanel(content)
        # Use scrollable panel for the right side
        scroll_container = AkmScrollablePanel(content, bg=PANEL) 
        right_side = scroll_container.scrollable_frame
        
        left_side.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        scroll_container.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))
        self._cover_split_widgets = (left_side, scroll_container)
        content.bind("<Configure>", self._on_responsive_resize, add="+")
        self.after_idle(lambda: self._apply_responsive_layout(content.winfo_width()))

        # LEFT: PREVIEW & VARIATION LIST
        preview_card = AkmCard(left_side)
        preview_card.pack(fill="both", expand=True, pady=(0, CARD_GAP))
        
        AkmLabel(preview_card.inner, text="Live Preview", fg=ACCENT, bg=PANEL_2, font=FONT_MD_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, 2))
        self.cover_preview_caption = AkmSubLabel(
            preview_card.inner,
            text="Geladenes Artwork wird hier sofort mit dem aktuellen Typo-Setup gerendert.",
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
        preview_shell.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, SPACE_SM))

        self.preview_box = AkmPanel(preview_shell, bg="#111111", height=420)
        self.preview_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.preview_box.pack_propagate(False)
        
        # Inner container for actual image/placeholders
        self.preview_inner = tk.Frame(self.preview_box, bg="#111111")
        self.preview_inner.pack(fill="both", expand=True)
        self.preview_box.bind("<Configure>", self._on_preview_box_configure, add="+")

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

        # RIGHT: METADATA & FILES
        meta_card = AkmCard(right_side)
        meta_card.pack(fill="both", expand=True)

        form = AkmForm(meta_card.inner, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        form.pack(fill="both", expand=True)
        
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

        form.add_header("Master Asset")
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
        AkmSubLabel(
            form,
            text="Manual nutzt die X/Y-Werte. Bei Bottom, Top Left und Center wird die Typografie aus dem Preset gebaut.",
            bg=PANEL_2,
            justify="left",
            wraplength=420,
        ).grid(row=form._current_row, column=0, columnspan=2, sticky="w", pady=(0, SPACE_SM))
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

        self._show_placeholders()
        self._update_cover_dashboard()

    def _on_responsive_resize(self, event):
        self._apply_responsive_layout(event.width)

    def _apply_responsive_layout(self, width):
        if not hasattr(self, "_cover_split_widgets"):
            return
        target_mode = "stack" if width and width < self.STACK_BREAKPOINT else "split"
        if target_mode == self._cover_layout_mode:
            return
        self._cover_layout_mode = target_mode

        left_side, scroll_container = self._cover_split_widgets
        left_side.pack_forget()
        scroll_container.pack_forget()

        if target_mode == "stack":
            left_side.pack(side="top", fill="x", expand=False, pady=(0, CARD_GAP))
            scroll_container.pack(side="top", fill="both", expand=True)
            return

        left_side.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        scroll_container.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))

    def _on_action_bar_resize(self, event):
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

    def _choose_artwork_path(self):
        path = filedialog.askopenfilename(filetypes=IMAGE_FILETYPES)
        if path:
            self.load_cover(path)

    def _clear_artwork(self):
        self.artwork_path_var.set("")
        self._current_image = None
        self._photo = None
        self._is_rendering = False
        self._last_preview_error = ""
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
        AkmSubLabel(
            row_aux,
            text="JPG, PNG, WEBP, TIFF oder BMP. Drag & Drop auf die Preview geht auch.",
            bg=PANEL_2,
        ).pack(side="left", padx=(SPACE_SM, 0))
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

        AkmSubLabel(
            wrap,
            text="Manual nutzt deine X/Y-Werte. Bottom, Top Left und Center bauen automatisch saubere Text-Frames.",
            bg=PANEL_2,
            justify="left",
            wraplength=420,
        ).pack(anchor="w", pady=(SPACE_XS, 0))
        return wrap

    def _create_render_row(self, parent):
        wrap = tk.Frame(parent, bg=PANEL_2)

        row_main = tk.Frame(wrap, bg=PANEL_2)
        row_main.pack(fill="x")
        tk.Label(row_main, text="Preview", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        tk.Scale(
            row_main,
            from_=320,
            to=640,
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
        self._update_cover_dashboard()

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

        if not artwork_path or not os.path.exists(artwork_path):
            status_text = "Kein Master-Artwork geladen"
        elif self._last_preview_error:
            status_text = "Artwork geladen, aber Rendering hat gehuestelt"
        elif self._is_rendering:
            status_text = f"{_friendly_layout_name(layout)} wird neu gerendert"
        elif layout == "manual":
            status_text = "Manual Layout bereit fuer freie Typografie"
        else:
            status_text = f"{_friendly_layout_name(layout)} bereit fuer Export"

        self.cover_status_label.config(text=status_text)
        self.cover_meta_label.config(
            text=(
                f"Layout: {_friendly_layout_name(layout)} | Stil: {style} | Textblock: {size_mode} "
                f"| Overlay: {overlay} | Offset: {offset} | Preview: {preview_height} px"
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

    def get_state(self):
        """Returns the current state of all cover configuration variables."""
        return {
            "artwork_path": self.artwork_path_var.get(),
            "artist": self.artist_var.get(),
            "title": self.title_var.get(),
            "subtitle": self.subtitle_var.get(),
            "artist_font": self.artist_font_var.get(),
            "artist_color": self.artist_color_var.get(),
            "artist_size": self.artist_size_var.get(),
            "artist_x": self.artist_x_var.get(),
            "artist_y": self.artist_y_var.get(),
            "title_font": self.title_font_var.get(),
            "title_color": self.title_color_var.get(),
            "title_size": self.title_size_var.get(),
            "title_x": self.title_x_var.get(),
            "title_y": self.title_y_var.get(),
            "subtitle_font": self.subtitle_font_var.get(),
            "subtitle_color": self.subtitle_color_var.get(),
            "subtitle_size": self.subtitle_size_var.get(),
            "subtitle_x": self.subtitle_x_var.get(),
            "subtitle_y": self.subtitle_y_var.get(),
            "layout": self.layout_var.get(),
            "style": self.style_var.get(),
            "size_mode": self.size_mode_var.get(),
            "overlay": self.overlay_var.get(),
            "offset": self.offset_var.get(),
            "zoom": self.zoom_var.get(),
            "ui_preview_zoom": self.ui_preview_zoom_var.get(),
            "artist_case": self.artist_case_var.get(),
            "artist_bold": self.artist_bold_var.get(),
            "title_case": self.title_case_var.get(),
            "title_bold": self.title_bold_var.get(),
            "subtitle_case": self.subtitle_case_var.get(),
            "subtitle_bold": self.subtitle_bold_var.get(),
            "bg_color": self.bg_color_var.get(),
            "accent_color": self.accent_color_var.get(),
        }

    def set_state(self, state):
        """Restores the UI state from a dictionary."""
        if not state: return
        
        lookup = {
            "artwork_path": self.artwork_path_var,
            "artist": self.artist_var,
            "title": self.title_var,
            "subtitle": self.subtitle_var,
            "artist_font": self.artist_font_var,
            "artist_color": self.artist_color_var,
            "artist_size": self.artist_size_var,
            "artist_x": self.artist_x_var,
            "artist_y": self.artist_y_var,
            "title_font": self.title_font_var,
            "title_color": self.title_color_var,
            "title_size": self.title_size_var,
            "title_x": self.title_x_var,
            "title_y": self.title_y_var,
            "subtitle_font": self.subtitle_font_var,
            "subtitle_color": self.subtitle_color_var,
            "subtitle_size": self.subtitle_size_var,
            "subtitle_x": self.subtitle_x_var,
            "subtitle_y": self.subtitle_y_var,
            "layout": self.layout_var,
            "style": self.style_var,
            "size_mode": self.size_mode_var,
            "overlay": self.overlay_var,
            "offset": self.offset_var,
            "zoom": self.zoom_var,
            "ui_preview_zoom": self.ui_preview_zoom_var,
            "artist_case": self.artist_case_var,
            "artist_bold": self.artist_bold_var,
            "title_case": self.title_case_var,
            "title_bold": self.title_bold_var,
            "subtitle_case": self.subtitle_case_var,
            "subtitle_bold": self.subtitle_bold_var,
            "bg_color": self.bg_color_var,
            "accent_color": self.accent_color_var,
        }
        
        for key, value in state.items():
            if key in lookup:
                lookup[key].set(value)

        self._schedule_preview_refresh(delay_ms=160)

    def save_project_locally(self):
        """Convenience wrapper to trigger the application-wide project save."""
        if hasattr(self.app, "save_project"):
            self.app.save_project()
        else:
            AkmToast(self, "Master-Speicherung nicht verfügbar")

    def _show_placeholders(self):
        """Restores the industrial placeholder view."""
        for child in self.preview_inner.winfo_children():
            child.destroy()
        self._photo = None
        AkmLabel(self.preview_inner, text="3000 x 3000 px", bg="#111111", fg="#2a2a2a", font=FONT_XXL).pack(expand=True)
        AkmSubLabel(self.preview_inner, text="Drag & Drop Image Here", bg="#111111", fg=SUBTLE).pack(pady=(0, 20))

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

        self.artwork_path_var.set(path)
        self._last_preview_error = ""
        self.app.append_log(f"Cover geladen: {os.path.basename(path)}")
        self._schedule_preview_refresh(delay_ms=40)

    def _setup_traces(self):
        """Triggers preview refresh on variable changes."""
        vars_to_trace = [
            self.artwork_path_var,
            self.title_var, self.artist_var, self.subtitle_var,
            self.artist_font_var, self.title_font_var, self.subtitle_font_var,
            self.artist_color_var, self.title_color_var, self.subtitle_color_var,
            self.artist_bold_var, self.title_bold_var, self.subtitle_bold_var,
            self.artist_case_var, self.title_case_var, self.subtitle_case_var,
            self.artist_size_var, self.title_size_var, self.subtitle_size_var,
            self.artist_x_var, self.artist_y_var, 
            self.title_x_var, self.title_y_var,
            self.subtitle_x_var, self.subtitle_y_var,
            self.zoom_var, self.ui_preview_zoom_var, self.layout_var, self.style_var,
            self.size_mode_var, self.overlay_var, self.offset_var,
            self.bg_color_var, self.accent_color_var
        ]
        for var in vars_to_trace:
            var.trace_add("write", lambda *a: self._schedule_preview_refresh())

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

        # Scale for UI based on Fenster-Zoom slider
        target_h = self.ui_preview_zoom_var.get()
        w, h = img.size
        ratio = target_h / h
        new_w = int(w * ratio)
        
        preview_img = img.resize((new_w, target_h), Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(preview_img)
        
        # Clear placeholders
        for child in self.preview_inner.winfo_children():
            child.destroy()
        
        tk.Label(self.preview_inner, image=self._photo, bg="#111111", bd=0, highlightthickness=0).pack(expand=True)
        self._update_cover_dashboard()

    def _on_preview_error(self, error_msg):
        self._is_rendering = False
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
            
        if hasattr(self.app, "release_vars") and "cover_path" in self.app.release_vars:
            self.app.release_vars["cover_path"].set(path)
            self.app.select_tab_by_id("release")
            AkmToast(self.app, "COVER IN RELEASE ÜBERNOMMEN", color=ACCENT)
        else:
            AkmToast(self, "RELEASE-TAB NICHT BEREIT", color="#FF3B30")

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
