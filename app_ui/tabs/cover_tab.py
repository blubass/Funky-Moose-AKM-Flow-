import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
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

class CoverTab(AkmPanel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._current_image = None
        self._photo = None
        
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
        
        # Image & UI Transformation
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.ui_preview_zoom_var = tk.IntVar(value=400) # Default UI height
        
        # General Colors
        self.bg_color_var = tk.StringVar(value="#181818")
        self.accent_color_var = tk.StringVar(value="#ff9a3c")
        
        self.pack(fill="both", expand=True)
        self.build_ui()
        self._setup_dnd()
        self._setup_traces()

    def build_ui(self):
        import tkinter.font as tkfont
        sys_fonts = sorted(tkfont.families())
        
        AkmHeader(self, text="Cover Management").pack(anchor="w", padx=SPACE_MD, pady=(SPACE_MD, SPACE_XS))
        AkmSubLabel(self, text="Zentrale Verwaltung fuer Artwork, Layout-Vorgaben und Grafik-Details.").pack(anchor="w", padx=SPACE_MD, pady=(0, SPACE_SM))

        content = AkmPanel(self)
        content.pack(fill="both", expand=True, padx=SPACE_MD, pady=0)

        left_side = AkmPanel(content)
        # Use scrollable panel for the right side
        scroll_container = AkmScrollablePanel(content, bg=PANEL) 
        right_side = scroll_container.scrollable_frame
        
        left_side.pack(side="left", fill="both", expand=True, padx=(0, CARD_GAP // 2))
        scroll_container.pack(side="left", fill="both", expand=True, padx=(CARD_GAP // 2, 0))

        # LEFT: PREVIEW & VARIATION LIST
        preview_card = AkmCard(left_side)
        preview_card.pack(fill="both", expand=True, pady=(0, CARD_GAP))
        
        AkmLabel(preview_card, text="Vorschau", fg=ACCENT, bg=PANEL_2, font=FONT_MD_BOLD).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_SM))
        
        self.preview_box = AkmPanel(preview_card, bg="#111111", height=320)
        self.preview_box.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        self.preview_box.pack_propagate(False)
        
        # Inner container for actual image/placeholders
        self.preview_inner = tk.Label(self.preview_box, bg="#111111")
        self.preview_inner.pack(fill="both", expand=True)
        
        self._show_placeholders()

        # RIGHT: METADATA & FILES
        meta_card = AkmCard(right_side)
        meta_card.pack(fill="both", expand=True)

        form = AkmForm(meta_card, padx=CARD_PAD_X, pady=CARD_PAD_Y)
        form.pack(fill="both", expand=True)
        
        # TYPOGRAPHY & POSITIONS (COMPACT VERSION)
        def _add_pos_form(header, font_var, color_var, size_var, bold_var, case_var, x_var, y_var):
            form.add_header(header, color=ACCENT if header == "Titel (Title)" else SUBTLE)
            
            # Row 1: Font & Size & Color
            row_main = tk.Frame(form, bg=PANEL_2)
            row_main.grid(row=form._current_row, column=0, columnspan=2, sticky="ew", pady=(0, 2))
            
            tk.Label(row_main, text="Font:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
            ttk.Combobox(row_main, textvariable=font_var, values=sys_fonts, width=15).pack(side="left", padx=5)
            
            tk.Label(row_main, text="Size:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left", padx=(5, 0))
            tk.Entry(row_main, textvariable=size_var, width=4, bg=FIELD_BG, fg=FIELD_FG, bd=0).pack(side="left", padx=5)
            
            def _pick():
                from tkinter import colorchooser
                c = colorchooser.askcolor(title=f"Farbe {header}")
                if c[1]: color_var.set(c[1])
            
            btn = tk.Label(row_main, text="🎨", bg=PANEL_2, fg=ACCENT, cursor="hand2")
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

        _add_pos_form("Interpret (Artist)", self.artist_font_var, self.artist_color_var, self.artist_size_var, self.artist_bold_var, self.artist_case_var, self.artist_x_var, self.artist_y_var)
        _add_pos_form("Titel (Title)", self.title_font_var, self.title_color_var, self.title_size_var, self.title_bold_var, self.title_case_var, self.title_x_var, self.title_y_var)
        _add_pos_form("Untertitel (Subtitle)", self.subtitle_font_var, self.subtitle_color_var, self.subtitle_size_var, self.subtitle_bold_var, self.subtitle_case_var, self.subtitle_x_var, self.subtitle_y_var)

        # COVER CONTENT (Compact Entries)
        header_content = AkmLabel(form, text="EINGABE-TEXTE", fg=ACCENT, bg=PANEL_2, font=FONT_MD_BOLD)
        header_content.grid(row=form._current_row, column=0, columnspan=2, sticky="w", pady=(10, 5))
        form._current_row += 1
        
        form.add_entry("Interpret", self.artist_var)
        form.add_entry("Album Titel", self.title_var)
        form.add_entry("Sub-Text", self.subtitle_var)

        # LAYOUT SPECS & ZOOM
        header_style = AkmLabel(form, text="STIL & BILD", fg=ACCENT, bg=PANEL_2, font=FONT_MD_BOLD)
        header_style.grid(row=form._current_row, column=0, columnspan=2, sticky="w", pady=(10, 5))
        form._current_row += 1

        # Zoom & UI Size Row
        row_final = tk.Frame(form, bg=PANEL_2)
        row_final.grid(row=form._current_row, column=0, columnspan=2, sticky="ew")
        
        tk.Label(row_final, text="Bild-Zoom:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left")
        tk.Scale(row_final, from_=1.0, to=5.0, variable=self.zoom_var, resolution=0.1, orient="horizontal", 
                 bg=PANEL_2, fg=TEXT, highlightthickness=0, length=60, showvalue=False).pack(side="left", padx=2)
        
        tk.Label(row_final, text="Fenster-Zoom:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left", padx=(5, 0))
        tk.Scale(row_final, from_=300, to=800, variable=self.ui_preview_zoom_var, resolution=10, orient="horizontal", 
                 bg=PANEL_2, fg=TEXT, highlightthickness=0, length=60, showvalue=False).pack(side="left", padx=2)

        tk.Label(row_final, text="Preset:", bg=PANEL_2, fg=SUBTLE, font=FONT_SM).pack(side="left", padx=(5, 0))
        ttk.Combobox(row_final, textvariable=self.layout_var, values=["manual", "bottom", "center"], width=8).pack(side="left", padx=2)

        form._current_row += 1
        form.add_color_field("Hauptfarbe", self.bg_color_var)
        form.add_color_field("Akzentfarbe", self.accent_color_var)
        form.add_entry("Moose Logo-Variante", tk.StringVar(value="Forge Standard (Orange)"))

        # QUALITY CHECK & MONITOR
        form.add_header("Technische Abnahme & Monitor")
        
        # Design Health Monitor (The Cool Feature)
        monitor_frame = tk.Frame(meta_card, bg=PANEL_2)
        monitor_frame.pack(fill="x", padx=CARD_PAD_X, pady=(0, SPACE_SM))
        
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

        # MASTER FILES
        form.add_header("Finaler Export")
        def _choose_path():
            from tkinter import filedialog
            p = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.jpeg *.bmp *.tiff")])
            if p: self.load_cover(p)

        def _create_file_row(parent, var):
            wrap = tk.Frame(parent, bg=PANEL_2)
            AkmEntry(wrap, textvariable=var, font=FONT_SM).pack(side="left", fill="x", expand=True)
            self.app.btn(wrap, "Pfade", _choose_path, quiet=True).pack(side="left", padx=(SPACE_XS, 0))
            return wrap

        form.add_row("Master Artwork", lambda p: _create_file_row(p, self.artwork_path_var))

        # BUTTON BAR
        btn_bar = AkmPanel(self)
        btn_bar.pack(fill="x", padx=SPACE_MD, pady=SPACE_SM)
        self.app.btn(btn_bar, "Zuweisen zu Release", self._assign_to_release, primary=True).pack(side="left")
        self.app.btn(btn_bar, "Cover exportieren", self.export_cover, primary=True).pack(side="left", padx=SPACE_SM)
        self.app.btn(btn_bar, "Projekt speichern", self.save_project_locally, quiet=True).pack(side="left", padx=SPACE_SM)
        self.app.btn(btn_bar, "Zertifikat erstellen", lambda: None, quiet=True).pack(side="left", padx=SPACE_SM)

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
        
        self.after(200, self.refresh_preview)

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
        self.preview_inner.configure(image="")
        
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
        if not os.path.isfile(path): return
        
        self.artwork_path_var.set(path)
        self.app.append_log(f"Cover geladen: {os.path.basename(path)}")
        self.refresh_preview()

    def _setup_traces(self):
        """Triggers preview refresh on variable changes."""
        vars_to_trace = [
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
            self.bg_color_var, self.accent_color_var
        ]
        for var in vars_to_trace:
            var.trace_add("write", lambda *a: self.refresh_preview())

    def refresh_preview(self):
        """Renders the current text onto the cover image for preview."""
        path = self.artwork_path_var.get()
        if not path or not os.path.exists(path):
            return

        def _render_task():
            from app_logic import cover_tools
            from PIL import Image, ImageDraw
            
            # Load original
            with Image.open(path) as img:
                # Working on a reasonably sized high-quality draft (1800px)
                zoom_val = self.zoom_var.get()
                draft = cover_tools.resize_cover_canvas(img, 1800, 1800, zoom=zoom_val)
                
                def _fmt(txt, case):
                    return txt.upper() if case == "uppercase" else txt

                # Setup stacked configs
                font_configs = [
                    {
                        "text": _fmt(self.artist_var.get(), self.artist_case_var.get()), 
                        "size": int(self.artist_size_var.get() or 60), 
                        "font": self.artist_font_var.get(), 
                        "bold": self.artist_bold_var.get(),
                        "color": self.artist_color_var.get(),
                        "x": int(self.artist_x_var.get() or 900),
                        "y": int(self.artist_y_var.get() or 1400)
                    },
                    {
                        "text": _fmt(self.title_var.get(), self.title_case_var.get()), 
                        "size": int(self.title_size_var.get() or 140), 
                        "font": self.title_font_var.get(), 
                        "bold": self.title_bold_var.get(), 
                        "color": self.title_color_var.get(),
                        "x": int(self.title_x_var.get() or 900),
                        "y": int(self.title_y_var.get() or 1500)
                    },
                    {
                        "text": _fmt(self.subtitle_var.get(), self.subtitle_case_var.get()), 
                        "size": int(self.subtitle_size_var.get() or 40), 
                        "font": self.subtitle_font_var.get(), 
                        "bold": self.subtitle_bold_var.get(),
                        "color": self.subtitle_color_var.get(),
                        "x": int(self.subtitle_x_var.get() or 900),
                        "y": int(self.subtitle_y_var.get() or 1600)
                    }
                ]
                
                # Image
                image = draft.convert("RGBA")
                draw = ImageDraw.Draw(image, "RGBA")
                width, height = image.size
                
                # Options for layouts
                options = {
                    "bg_color": self.bg_color_var.get(),
                    "accent_color": self.accent_color_var.get(),
                    "style": self.style_var.get(),
                }
                
                # Centralized Rendering or Layout Presets
                layout = self.layout_var.get()
                if layout == "manual":
                    cover_tools.render_manual_layout(draw, width, height, font_configs, zoom=zoom_val)
                elif layout == "bottom":
                    image = cover_tools._build_release_cover_variant_bottom(draft, self.title_var.get().upper(), self.artist_var.get().upper(), None, options, subtitle=self.subtitle_var.get())
                elif layout == "center":
                    image = cover_tools._build_release_cover_variant_center_band(draft, self.title_var.get().upper(), self.artist_var.get().upper(), None, options, subtitle=self.subtitle_var.get())
                else:
                    cover_tools.render_manual_layout(draw, width, height, font_configs, zoom=zoom_val)

                return image.convert("RGB")

        self.app.tasks.run(_render_task, self._on_preview_rendered, busy_text=None)

    def _on_preview_rendered(self, img):
        """Updates the UI with the newly rendered preview image, respecting the UI Zoom."""
        if not img: return
        
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
        
        self.preview_inner.configure(image=self._photo)

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
        from tkinter import filedialog
        
        path = self.artwork_path_var.get()
        if not path or not os.path.exists(path):
            AkmToast(self, "KEIN MASTER-ARTWORK GELADEN", color="#FF3B30")
            return

        out_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")],
            initialfile=f"Cover_{self.title_var.get().replace(' ', '_')}.jpg"
        )
        
        if not out_path: return

        def _render_full():
            from app_logic import cover_tools
            from PIL import Image, ImageDraw
            
            with Image.open(path) as img:
                # Full size output (usually 3000x3000px if original is large enough)
                zoom_val = self.zoom_var.get()
                # Determine target size based on requirements (3000x3000px)
                # But here we use a fixed 3000px target for 'Premium' output
                full = cover_tools.resize_cover_canvas(img, 3000, 3000, zoom=zoom_val)
                
                def _fmt(txt, case):
                    return txt.upper() if case == "uppercase" else txt

                font_configs = [
                    {
                        "text": _fmt(self.artist_var.get(), self.artist_case_var.get()), 
                        "size": int(int(self.artist_size_var.get() or 60) * (3000 / 1800)), 
                        "font": self.artist_font_var.get(), 
                        "bold": self.artist_bold_var.get(),
                        "color": self.artist_color_var.get(),
                        "x": int(int(self.artist_x_var.get() or 900) * (3000 / 1800)),
                        "y": int(int(self.artist_y_var.get() or 1400) * (3000 / 1800))
                    },
                    {
                        "text": _fmt(self.title_var.get(), self.title_case_var.get()), 
                        "size": int(int(self.title_size_var.get() or 140) * (3000 / 1800)), 
                        "font": self.title_font_var.get(), 
                        "bold": self.title_bold_var.get(),
                        "color": self.title_color_var.get(),
                        "x": int(int(self.title_x_var.get() or 900) * (3000 / 1800)),
                        "y": int(int(self.title_y_var.get() or 1500) * (3000 / 1800))
                    },
                    {
                        "text": _fmt(self.subtitle_var.get(), self.subtitle_case_var.get()), 
                        "size": int(int(self.subtitle_size_var.get() or 40) * (3000 / 1800)), 
                        "font": self.subtitle_font_var.get(), 
                        "bold": self.subtitle_bold_var.get(),
                        "color": self.subtitle_color_var.get(),
                        "x": int(int(self.subtitle_x_var.get() or 900) * (3000 / 1800)),
                        "y": int(int(self.subtitle_y_var.get() or 1600) * (3000 / 1800))
                    }
                ]
                
                image = full.convert("RGBA")
                draw = ImageDraw.Draw(image, "RGBA")
                cover_tools.render_manual_layout(draw, 3000, 3000, font_configs, zoom=zoom_val)
                
                final = image.convert("RGB")
                final.save(out_path, quality=95, subsampling=0)
                return out_path

        def _done(res):
            if res:
                self.app.append_log(f"Cover exportiert: {os.path.basename(res)}")
                AkmToast(self, "COVER ERFOLGREICH EXPORTIERT")
            else:
                AkmToast(self, "FEHLER BEIM EXPORT", color="#FF3B30")

        self.app.tasks.run(_render_full, _done, busy_text="Exportiere hochauflösendes Cover...")

