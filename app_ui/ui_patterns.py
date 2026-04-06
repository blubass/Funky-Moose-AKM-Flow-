import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import pyperclip
import tkinter.font as tkfont
from tkinter import colorchooser

# --- UI CONSTANTS ---
# --- THEME (PERMANENT OBSIDIAN 2026) ---
IS_DARK = True 

BG = "#040405"          # Absolute Pitch Black
PANEL = "#1A1A1D"       # Deep Iron Gray (Cards)
PANEL_2 = "#222225"     # Sub-Panels
BORDER = "#2D2D33"      # Machine Seams
TEXT = "#CBD5E1"        # Slated Steel (Muted)
SUBTLE = "#64748B"      # Darkened Industrial Slate

ACCENT = "#FF8C00"      # Hyper-Orange
FLAVOR_INFO = "#22D3EE" # Cyan-Glow
FLAVOR_WARN = "#FBBF24"
FLAVOR_SUCCESS = "#10B981"
FLAVOR_ERROR = "#F43F5E"

FIELD_BG = "#0D0D0F"
FIELD_FG = "#CBD5E1"
LOG_BG = "#020202"
LOG_FG = "#22D3EE"

# Fallbacks for runtime
ACCENT_SOFT = "#2A1B0A"

def update_global_constants(is_dark):
    """Runtime update (Stub for permanent theme)."""
    pass
    
    # Update Status Palettes for real-time reactivity
    global STATUS_PALETTES
    if is_dark:
        STATUS_PALETTES["in_progress"] = {"bg": "#1E1B16", "fg": "#FBBF24", "accent": "#FBBF24"}
        STATUS_PALETTES["ready"] = {"bg": "#171B22", "fg": "#38BDF8", "accent": "#38BDF8"}
        STATUS_PALETTES["submitted"] = {"bg": "#141C19", "fg": "#10B981", "accent": "#10B981"}
        STATUS_PALETTES["confirmed"] = {"bg": "#151B14", "fg": "#A3E635", "accent": "#A3E635"}
    else:
        STATUS_PALETTES["in_progress"] = {"bg": "#FEF3C7", "fg": "#92400E", "accent": "#92400E"}
        STATUS_PALETTES["ready"] = {"bg": "#E0F2FE", "fg": "#075985", "accent": "#075985"}
        STATUS_PALETTES["submitted"] = {"bg": "#D1FAE5", "fg": "#065F46", "accent": "#065F46"}
        STATUS_PALETTES["confirmed"] = {"bg": "#ECFCCB", "fg": "#3F6212", "accent": "#3F6212"}

    # Debug info
    print(f"Theme 2026 updated: {'Dark' if is_dark else 'Light'} - BG: {BG}")

SPACE_XS = 6
SPACE_SM = 10
SPACE_MD = 14
SPACE_LG = 18
SPACE_XL = 24
CARD_GAP = 10
CARD_PAD_X = 14
CARD_PAD_Y = 12

# --- 2026 TYPOGRAPHY ---
def get_font(size, bold=False, italic=False):
    """Factory for modern variables fonts."""
    family = "Montserrat" if "mac" in str(os.uname()).lower() else "Inter"
    style = []
    if bold: style.append("bold")
    if italic: style.append("italic")
    return (family, size, " ".join(style))

FONT_SM = get_font(10)
FONT_BOLD = get_font(10, bold=True)
FONT_MD = get_font(11)
FONT_MD_BOLD = get_font(11, bold=True)
FONT_LG = get_font(14, bold=True)
FONT_XL = get_font(18)
FONT_XXL = get_font(22, bold=True)
FONT_XXXL = get_font(28, bold=True)
FONT_ITALIC = get_font(10, italic=True)
FONT_LOG = ("JetBrains Mono", 10) if "mac" in str(os.uname()).lower() else ("Courier New", 10)

# --- STATUS PALETTES & TEXTS ---
STATUS_PALETTES = {
    "all": {"bg": "#36312b", "fg": "#f7e6d6", "accent": "#ffcb97"},
    "open": {"bg": "#423021", "fg": "#ffd9b7", "accent": "#ffb975"},
    "in_progress": {
        "bg": "#4a3324",
        "fg": "#ffd8b5",
        "accent": "#ffaf63",
    },
    "ready": {"bg": "#1f3a4b", "fg": "#d6ecff", "accent": "#84cfff"},
    "submitted": {"bg": "#1f3f31", "fg": "#d5f4df", "accent": "#71da9b"},
    "confirmed": {"bg": "#314224", "fg": "#e7ffd0", "accent": "#b7eb6c"},
}

SOURCE_PALETTES = {
    "Werk": {"accent": "#71da9b"},
    "Datei\u2192Werk": {"accent": "#84cfff"},
    "Datei": {"accent": "#ffcb97"},
}

STATUS_LABELS = {
    "de": {
        "all": "Alle",
        "open": "Offen",
        "in_progress": "In Arbeit",
        "ready": "Bereit",
        "submitted": "Gemeldet",
        "confirmed": "Bestätigt",
    },
    "en": {
        "all": "All",
        "open": "Open",
        "in_progress": "In Progress",
        "ready": "Ready",
        "submitted": "Submitted",
        "confirmed": "Confirmed",
    },
}

# --- COLOR UTILS ---
def hex_to_rgb(value):
    raw = value.lstrip("#")
    return tuple(int(raw[index : index + 2], 16) for index in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def blend_color(base_color, target_color, ratio):
    base_rgb = hex_to_rgb(base_color)
    target_rgb = hex_to_rgb(target_color)
    ratio = max(0.0, min(1.0, ratio))
    mixed = tuple(
        int(round(base + (target - base) * ratio))
        for base, target in zip(base_rgb, target_rgb)
    )
    return rgb_to_hex(mixed)

# --- STYLE CONFIGURATION ---
def apply_ttk_styles():
    """Applies the current theme constants (BG, PANEL, etc.) to the ttk engine."""
    style = ttk.Style()
    style.theme_use("default")
    
    # Global root style refresh
    style.configure(".", background=BG, foreground=TEXT, font=FONT_MD)
    
    style.configure("TNotebook", background=BG, borderwidth=0, padding=0)
    style.map("TNotebook", background=[("active", BG), ("!active", BG)]) # Force background
    
    style.configure(
        "TNotebook.Tab",
        background=PANEL,
        foreground=TEXT,
        padding=(16, 10),
        font=FONT_MD_BOLD,
        borderwidth=0
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT), ("active", PANEL_2)],
        foreground=[("selected", "#000000" if not IS_DARK else "#1a1a1a"), ("active", TEXT)],
    )
    
    style.configure(
        "TProgressbar",
        thickness=8,
        troughcolor="#333333" if IS_DARK else "#d1d1d1",
        background=ACCENT,
        borderwidth=0
    )
    
    style.configure(
        "Treeview",
        background=FIELD_BG,
        fieldbackground=FIELD_BG,
        foreground=FIELD_FG,
        rowheight=24,
        borderwidth=0,
        font=FONT_SM,
    )
    style.configure(
        "Treeview.Heading",
        background=PANEL_2,
        foreground=TEXT,
        relief="flat",
        font=FONT_BOLD,
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "black")],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", ACCENT)],
        foreground=[("active", "black")],
    )
    
    style.configure(
        "TCombobox",
        fieldbackground=FIELD_BG,
        background=PANEL_2,
        foreground=FIELD_FG,
        arrowcolor=ACCENT,
        arrowsize=18,
        borderwidth=0,
        relief="flat"
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", FIELD_BG)],
        foreground=[("readonly", FIELD_FG)],
    )

    style.configure(
        "AKM.TButton",
        background="#ece7e1",
        foreground="#151515",
        padding=(14, 8),
        font=FONT_BOLD,
        borderwidth=0,
        focusthickness=0,
        focuscolor="none",
        relief="flat",
    )
    style.map(
        "AKM.TButton",
        background=[
            ("disabled", "#d7d7d7"),
            ("pressed", "#ddd3c8"),
            ("active", "#e8ddd2"),
        ],
        foreground=[
            ("disabled", "#666666"),
            ("pressed", "#151515"),
            ("active", "#151515"),
        ],
    )
    
    style.configure(
        "AKMQuiet.TButton",
        background=PANEL_2,
        foreground=TEXT,
        padding=(12, 8),
        font=FONT_SM,
        borderwidth=0,
        focusthickness=0,
        focuscolor="none",
        relief="flat",
    )
    style.map(
        "AKMQuiet.TButton",
        background=[
            ("disabled", "#313131"),
            ("pressed", "#353535"),
            ("active", "#3a3a3a"),
        ],
        foreground=[
            ("disabled", "#7a7a7a"),
            ("pressed", TEXT),
            ("active", TEXT),
        ],
    )
    
    style.configure(
        "AKMPrimary.TButton",
        background=ACCENT,
        foreground="black",
        padding=(14, 8),
        font=FONT_BOLD,
        borderwidth=0,
        focusthickness=0,
        focuscolor="none",
        relief="flat",
    )
    style.map(
        "AKMPrimary.TButton",
        background=[
            ("disabled", "#d9bca0"),
            ("pressed", "#ffb066"),
            ("active", "#ffb066"),
        ],
        foreground=[
            ("disabled", "#666666"),
            ("pressed", "black"),
            ("active", "black"),
        ],
    )

# --- UI COMPONENT HELPERS ---
def create_btn(parent, text, cmd, primary=False, quiet=False, width=None, accent_color=None):
    """
    2026 Rounded Hardware Button (Dynamic Version).
    """
    base_bg = accent_color if accent_color else ACCENT
    base_fg = "#000000"
    radius = 16 if not quiet else 10
    
    if quiet:
        base_bg = PANEL_2
        base_fg = SUBTLE

    # Dynamic Size Calculation based on text length
    fixed_width = width if width else (200 if not quiet else 160)
    btn_font = FONT_BOLD if not (primary or accent_color) else FONT_MD_BOLD
    if len(text) > 18: 
        btn_font = FONT_SM # Auto-shrink 
        if not width: fixed_width = 220 # Auto-expand

    cv = tk.Canvas(parent, bg=parent["bg"], highlightthickness=0, borderwidth=0, 
                   width=fixed_width, height=44 if not quiet else 32)
    
    def _draw(state="normal"):
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 10: w = fixed_width
        if h < 10: h = 44 if not quiet else 32
        
        # Shadow/Highlight Bevel (Pill)
        sh_col = blend_color(base_bg, "#000000", 0.6) if state == "normal" else blend_color(base_bg, "#FFFFFF", 0.4)
        hi_col = blend_color(base_bg, "#FFFFFF", 0.5) if state == "normal" else blend_color(base_bg, "#000000", 0.5)
        bg_col = base_bg if state == "normal" else blend_color(base_bg, "#000000", 0.2)
        
        draw_rounded_rect(cv, 0, 0, w, h, radius, fill=sh_col)
        draw_rounded_rect(cv, 0, 0, w-2, h-2, radius, fill=hi_col)
        draw_rounded_rect(cv, 1, 1, w-2, h-4, radius, fill=bg_col)
        
        cv.create_text(w/2, h/2, text=text.upper(), fill=base_fg, font=btn_font)

    cv.bind("<Enter>", lambda e: _draw("hover"))
    cv.bind("<Leave>", lambda e: _draw("normal"))
    cv.bind("<Button-1>", lambda e: (cmd(), _draw("pressed")))
    cv.bind("<ButtonRelease-1>", lambda e: _draw("normal"))
    cv.bind("<Configure>", lambda e: _draw())
    
    return cv

def style_chip_label(widget, status, text, active=False):
    palette = STATUS_PALETTES.get(status, STATUS_PALETTES["all"])
    if active:
        widget.config(
            text=text,
            bg=palette["accent"],
            fg="#141414",
            relief="flat",
            bd=0,
        )
        return

    widget.config(
        text=text,
        bg=palette["bg"],
        fg=palette["fg"],
        relief="solid",
        bd=1,
    )

def get_status_chip_text(status, lang="de"):
    return STATUS_LABELS.get(lang, STATUS_LABELS["de"]).get(status, status)

def get_source_accent(source):
    return SOURCE_PALETTES.get(source or "", {"accent": "#d9d4cf"})["accent"]

# --- SYSTEM HELPERS ---
def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        return True, None
    except Exception as exc:
        return False, str(exc)

def open_in_finder(path):
    try:
        subprocess.run(["open", "-R", path], check=False)
        return True, None
    except Exception as exc:
        return False, str(exc)

def get_row_color(status, is_source=False, ratio=0.16):
    if is_source:
        accent = get_source_accent(status)
    else:
        palette = STATUS_PALETTES.get(status, STATUS_PALETTES["all"])
        accent = palette["accent"]
    
    return blend_color(FIELD_BG, accent, ratio)

# --- THEMED WIDGETS ---
# --- ROUNDED UI ENGINE (2026) ---
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draws a high-fidelity rounded rectangle path on a Canvas."""
    points = [
        x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1,
        x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2,
        x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,
        x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

class AkmRoundedFrame(tk.Canvas):
    """A futuristic rounded container with persistent geometry awareness."""
    def __init__(self, parent, bg_color=PANEL, radius=36, border_color="#2D2D33", **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, borderwidth=0, **kwargs)
        self.radius = radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.bind("<Configure>", self._redraw)
        
    def _redraw(self, event=None):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < self.radius*2 or h < self.radius*2: return
        # Bevel highlight & Shadow
        draw_rounded_rect(self, 2, 2, w-2, h-2, self.radius, fill=self.border_color)
        draw_rounded_rect(self, 1, 1, w-1, h-2, self.radius, fill=self.bg_color)

class AkmPanel(tk.Frame):
    """Base layout frame."""
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", BG)
        super().__init__(parent, **kwargs)

class AkmCard(AkmRoundedFrame):
    """Hardware Card with organic rounded corners."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.inner = tk.Frame(self, bg=self.bg_color)
        self.inner.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.88, anchor="center")

class AkmScrollablePanel(tk.Frame):
    """
    A scrollable container that maintains the industrial design aesthetic.
    Uses a Canvas and Scrollbar to enable scrolling for its interior frame.
    """
    def __init__(self, parent, **kwargs):
        bg_target = kwargs.pop("bg", BG)
        super().__init__(parent, bg=bg_target, **kwargs)
        
        self.canvas = tk.Canvas(self, bg=bg_target, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, 
                                     bg=bg_target, troughcolor="#111111" if IS_DARK else "#d1d1d1",
                                     width=10, relief="flat")
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_target)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mousewheel support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel) # Linux support
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        # Update the width of the scrollable frame to match the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if not self.winfo_exists(): return
        # Handle different mousewheel event formats
        if event.num == 4: # Linux
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: # Linux
            self.canvas.yview_scroll(1, "units")
        else: # macOS / Windows
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class AkmLabel(tk.Label):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL)
        kwargs.setdefault("fg", TEXT)
        kwargs.setdefault("font", FONT_SM)
        super().__init__(parent, **kwargs)

class AkmSubLabel(tk.Label):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL)
        kwargs.setdefault("fg", SUBTLE)
        kwargs.setdefault("font", FONT_SM)
        super().__init__(parent, **kwargs)

class AkmHeader(tk.Label):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL)
        kwargs.setdefault("fg", TEXT)
        kwargs.setdefault("font", FONT_XL)
        super().__init__(parent, **kwargs)

class AkmAccentHeader(tk.Label):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", BG)
        kwargs.setdefault("fg", ACCENT)
        kwargs.setdefault("font", FONT_XXXL)
        super().__init__(parent, **kwargs)

# --- MICRO-ANIMATIONS & FEEDBACK ---
class PulseLabel(tk.Label):
    """A label that pulses between two colors to indicate activity."""
    def __init__(self, parent, base_color=PANEL, pulse_color=ACCENT_SOFT, **kwargs):
        kwargs.setdefault("bg", base_color)
        super().__init__(parent, **kwargs)
        self.base_color = base_color
        self.pulse_color = pulse_color
        self._running = False
        self._phase = 0

    def start(self):
        if not self._running:
            self._running = True
            self._animate()

    def stop(self):
        self._running = False
        self.config(bg=self.base_color)

    def _animate(self):
        if not self._running: return
        self._phase = (self._phase + 0.1) % (2 * 3.14159)
        ratio = (1 + (0.5 * (1 + 0.5 * (1 + 0.5 * (1 + 0.5))))) # Simplified pulse
        # Use a simpler ratio for now
        ratio = 0.5 + 0.5 * (1 if self._phase < 3.14 else 0) # Just a simple blink for now
        color = blend_color(self.base_color, self.pulse_color, 0.4 if self._phase < 3.14 else 0)
        self.config(bg=color)
        self.after(200, self._animate)

class AkmToast(tk.Label):
    """A self-dismissing popup notification."""
    def __init__(self, parent, text, duration=2500, color=ACCENT, **kwargs):
        super().__init__(parent, text=text, bg=PANEL_2, fg=color, 
                         font=FONT_MD_BOLD, padx=20, pady=10, 
                         relief="solid", bd=1, **kwargs)
        self.place(relx=0.5, rely=0.1, anchor="center")
        self.after(duration, self.destroy)

def add_hover(widget, enter_color, leave_color):
    """Binds hover event to a widget."""
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_color))

class AkmBadge(tk.Label):
    """A small glowing status indicator badge."""
    def __init__(self, parent, text, **kwargs):
        kwargs.setdefault("bg", "#111111")
        kwargs.setdefault("fg", "#333333")
        kwargs.setdefault("font", ("Helvetica", 9, "bold"))
        kwargs.setdefault("padx", 8)
        kwargs.setdefault("pady", 2)
        kwargs.setdefault("relief", "flat")
        super().__init__(parent, text=text.upper(), **kwargs)
        self.active_color = ACCENT
        self.inactive_color = "#333333"

    def set_active(self, active=True):
        self.config(fg=self.active_color if active else self.inactive_color)
        if active: self.config(highlightbackground=ACCENT, highlightthickness=1)
        else: self.config(highlightthickness=0)

class AkmSuccessIndicator(tk.Label):
    """A small glowing green dot (indicator) for successful states."""
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", "transparent" if "bg" not in kwargs else kwargs["bg"])
        kwargs.setdefault("fg", FLAVOR_SUCCESS)
        kwargs.setdefault("text", "●") # Circle bullet
        kwargs.setdefault("font", ("Helvetica", 14, "bold"))
        super().__init__(parent, **kwargs)

# --- SPECIALIZED THEMED WIDGETS ---

# --- SPECIALIZED THEMED WIDGETS ---
class AkmEntry(tk.Entry):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", FIELD_BG)
        kwargs.setdefault("fg", FIELD_FG)
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("insertbackground", "black")
        kwargs.setdefault("font", FONT_MD)
        super().__init__(parent, **kwargs)

class AkmText(tk.Text):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", FIELD_BG)
        kwargs.setdefault("fg", FIELD_FG)
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("insertbackground", "black")
        kwargs.setdefault("font", FONT_SM)
        kwargs.setdefault("padx", 4)
        kwargs.setdefault("pady", 4)
        super().__init__(parent, **kwargs)

class AkmCheckbutton(tk.Checkbutton):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL_2)
        kwargs.setdefault("fg", TEXT)
        kwargs.setdefault("activebackground", PANEL_2)
        kwargs.setdefault("activeforeground", TEXT)
        kwargs.setdefault("selectcolor", "#111111")
        kwargs.setdefault("font", FONT_SM)
        super().__init__(parent, **kwargs)

# --- FORM BUILDER ---
class AkmForm(tk.Frame):
    """
    Standardized Grid-based Form Builder.
    Simplifies creation of label+field pairs with consistent styling.
    """
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL_2)
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        self._current_row = 0

    def add_row(self, label_text, widget_creation_func=None):
        """Adds a generic row with a label and space for a widget."""
        AkmLabel(
            self,
            text=label_text + ":",
            bg=self["bg"],
        ).grid(row=self._current_row, column=0, sticky="nw", padx=(0, SPACE_SM), pady=SPACE_XS)
        
        container = tk.Frame(self, bg=self["bg"])
        container.grid(row=self._current_row, column=1, sticky="ew", pady=SPACE_XS)
        
        widget = None
        if widget_creation_func:
            widget = widget_creation_func(container)
            if widget:
                widget.pack(side="left", fill="x", expand=True)
        
        self._current_row += 1
        return widget, container

    def add_entry(self, label_text, variable=None, **kwargs):
        """Convenience method to add a labeled AkmEntry."""
        AkmLabel(
            self,
            text=label_text + ":",
            bg=self["bg"],
        ).grid(row=self._current_row, column=0, sticky="w", padx=(0, SPACE_SM), pady=SPACE_XS)
        
        entry = AkmEntry(self, textvariable=variable, **kwargs)
        entry.grid(row=self._current_row, column=1, sticky="ew", pady=SPACE_XS)
        self._current_row += 1
        return entry

    def add_text(self, label_text, height=3, **kwargs):
        """Convenience method to add a labeled AkmText area."""
        AkmLabel(
            self,
            text=label_text + ":",
            bg=self["bg"],
        ).grid(row=self._current_row, column=0, sticky="nw", padx=(0, SPACE_SM), pady=(SPACE_XS + 2, 0))
        
        text_widget = AkmText(self, height=height, **kwargs)
        text_widget.grid(row=self._current_row, column=1, sticky="ew", pady=SPACE_XS)
        self._current_row += 1
        return text_widget

    def add_checkbox(self, label_text, variable=None, **kwargs):
        """Convenience method to add an AkmCheckbutton."""
        cb = AkmCheckbutton(self, text=label_text, variable=variable, **kwargs)
        cb.grid(row=self._current_row, column=1, sticky="w", pady=SPACE_XS)
        self._current_row += 1
        return cb

    def add_header(self, text, color=ACCENT):
        """Adds a sectional header within the form."""
        AkmLabel(
            self,
            text=text,
            fg=color,
            bg=self["bg"],
            font=FONT_LG,
        ).grid(row=self._current_row, column=0, columnspan=2, sticky="w", pady=(SPACE_MD, SPACE_SM))
        self._current_row += 1

    def add_combobox(self, label_text, variable, values, **kwargs):
        """Adds a labeled ttk.Combobox."""
        AkmLabel(
            self, text=label_text + ":", bg=self["bg"]
        ).grid(row=self._current_row, column=0, sticky="w", padx=(0, SPACE_SM), pady=SPACE_XS)
        
        cb = ttk.Combobox(self, textvariable=variable, values=values, **kwargs)
        cb.grid(row=self._current_row, column=1, sticky="ew", pady=SPACE_XS)
        self._current_row += 1
        return cb

    def add_color_field(self, label_text, variable):
        """Adds a field with a color picker button."""
        AkmLabel(
            self, text=label_text + ":", bg=self["bg"]
        ).grid(row=self._current_row, column=0, sticky="w", padx=(0, SPACE_SM), pady=SPACE_XS)
        
        container = tk.Frame(self, bg=self["bg"])
        container.grid(row=self._current_row, column=1, sticky="ew", pady=SPACE_XS)
        
        entry = AkmEntry(container, textvariable=variable, font=FONT_SM)
        entry.pack(side="left", fill="x", expand=True)

        def _pick():
            c = colorchooser.askcolor(title=f"Wähle {label_text}")
            if c[1]: variable.set(c[1])
        
        btn = create_btn(container, "Spectrum", _pick, quiet=True)
        btn.pack(side="left", padx=(SPACE_XS, 0))
        
        self._current_row += 1
        return entry

def refresh_ui_hierarchy(root):
    """
    Absolutely re-colors every widget in the hierarchy based on the current global constants.
    """
    name = str(root).lower()
    
    try:
        # 1. Determine Role-based colors
        if "akmcard" in name or "akmform" in name:
            bg_target, fg_target = PANEL_2, TEXT
        elif "akmheader" in name:
            bg_target, fg_target = (root.master.cget("bg") if root.master else BG), ACCENT
        elif "akmlabel" in name and "akmsublabel" not in name:
            bg_target, fg_target = (root.master.cget("bg") if root.master else BG), TEXT
        elif "akmsublabel" in name:
            bg_target, fg_target = (root.master.cget("bg") if root.master else BG), SUBTLE
        elif "log" in name:
            bg_target, fg_target = LOG_BG, LOG_FG
        elif "akmpanel" in name or "tab" in name:
            bg_target, fg_target = BG, TEXT
        else:
            # Absolute fallback to current module state
            bg_target = BG
            fg_target = TEXT

        # 2. Apply to standard Tkinter widgets
        if isinstance(root, (tk.Frame, tk.Label, tk.Canvas, tk.Button)):
            root.configure(bg=bg_target)
            if isinstance(root, (tk.Label, tk.Button)):
                # Preserve accent and success colors
                curr_fg = root.cget("fg").lower()
                if curr_fg not in (ACCENT.lower(), FLAVOR_SUCCESS.lower(), FLAVOR_ERROR.lower()):
                    root.configure(fg=fg_target)
        
        # 3. Entries & Text boxes
        if isinstance(root, (tk.Entry, tk.Text)):
            root.configure(bg=FIELD_BG, fg=FIELD_FG, insertbackground=FIELD_FG, highlightbackground=BORDER)

        # 4. Listbox specials
        if isinstance(root, tk.Listbox):
            root.configure(bg=FIELD_BG, fg=FIELD_FG, selectbackground=ACCENT)

    except Exception:
        pass
        
    for child in root.winfo_children():
        refresh_ui_hierarchy(child)
# --- PROJECT SAVE/LOAD DIALOGS ---
class AkmSaveDialog(tk.Toplevel):
    def __init__(self, parent, title, directory, extension=".akm"):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x550")
        self.transient(parent)
        self.grab_set()
        
        self.directory = directory
        self.extension = extension
        self.result = None
        
        # Ensure directory exists
        os.makedirs(self.directory, exist_ok=True)
        
        self.configure(bg=BG)
        self._build_ui()
        self._refresh_list()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=SPACE_MD, pady=SPACE_MD)
        tk.Label(hdr, text="PROJEKT SPEICHERN", bg=BG, fg=ACCENT, font=FONT_XL).pack(side="left")
        
        # Main Card
        container = AkmCard(self)
        container.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_MD))
        
        AkmLabel(container, text="VORHANDENE PROJEKTE", font=FONT_MD_BOLD, fg=ACCENT).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        
        # Listbox for existing projects
        list_frame = AkmPanel(container)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X)
        
        self.listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, font=FONT_MD,
            selectbackground=ACCENT, selectforeground="black",
            borderwidth=0, highlightthickness=1, highlightbackground=BORDER
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)
        
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        
        # Entry for new name
        entry_frame = AkmPanel(container)
        entry_frame.pack(fill="x", padx=CARD_PAD_X, pady=SPACE_MD)
        
        AkmLabel(entry_frame, text="PROJEKTNAME:").pack(side="left")
        self.name_var = tk.StringVar()
        self.entry = AkmEntry(entry_frame, textvariable=self.name_var)
        self.entry.pack(side="left", fill="x", expand=True, padx=(SPACE_SM, 0))
        self.entry.bind("<Return>", lambda e: self._save())
        
        # Buttons
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_MD))
        
        create_btn(btn_row, "DURCHSUCHEN...", self._browse, quiet=True).pack(side="left")
        create_btn(btn_row, "SPEICHERN", self._save, primary=True).pack(side="right")
        create_btn(btn_row, "ABBRECHEN", self.destroy, quiet=True).pack(side="right", padx=SPACE_SM)

    def _browse(self):
        path = filedialog.asksaveasfilename(
            initialdir=self.directory,
            title="Projekt Speichern unter",
            filetypes=[("AKM Projekt", f"*{self.extension}"), ("Alle Dateien", "*.*")],
            defaultextension=self.extension
        )
        if path:
            self.result = path
            self.destroy()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        if not os.path.exists(self.directory): return
        
        files = [f for f in os.listdir(self.directory) if f.endswith(self.extension)]
        for f in sorted(files):
            name = f[:-len(self.extension)]
            self.listbox.insert(tk.END, name)

    def _on_select(self, event):
        idx = self.listbox.curselection()
        if idx:
            self.name_var.set(self.listbox.get(idx[0]))

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Eingabe", "Bitte gib einen Namen ein.")
            return
        
        self.result = os.path.join(self.directory, name + self.extension)
        if os.path.exists(self.result):
            if not messagebox.askyesno("Überschreiben", f"'{name}' existiert bereits. Überschreiben?"):
                return
        
        self.wait_window_success = True
        self.destroy()

class AkmLoadDialog(tk.Toplevel):
    def __init__(self, parent, title, directory, extension=".akm"):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x550")
        self.transient(parent)
        self.grab_set()
        
        self.directory = directory
        self.extension = extension
        self.result = None
        
        self.configure(bg=BG)
        self._build_ui()
        self._refresh_list()
        
        # Center on parent
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=SPACE_MD, pady=SPACE_MD)
        tk.Label(hdr, text="PROJEKT LADEN", bg=BG, fg=ACCENT, font=FONT_XL).pack(side="left")
        
        # Main Card
        container = AkmCard(self)
        container.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_MD))
        
        AkmLabel(container, text="GESPEICHERTE PROJEKTE", font=FONT_MD_BOLD, fg=ACCENT).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        
        # Listbox
        list_frame = AkmPanel(container)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        
        self.listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, font=FONT_MD,
            selectbackground=ACCENT, selectforeground="black",
            borderwidth=0, highlightthickness=1, highlightbackground=BORDER
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)
        
        self.listbox.bind("<Double-Button-1>", lambda e: self._load())
        
        # Buttons
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_MD))
        
        create_btn(btn_row, "DURCHSUCHEN...", self._browse, quiet=True).pack(side="left")
        create_btn(btn_row, "LADEN", self._load, primary=True).pack(side="right")
        create_btn(btn_row, "ABBRECHEN", self.destroy, quiet=True).pack(side="right", padx=SPACE_SM)

    def _browse(self):
        path = filedialog.askopenfilename(
            initialdir=self.directory,
            title="Projekt Laden",
            filetypes=[("AKM Projekt", f"*{self.extension}"), ("Alle Dateien", "*.*")]
        )
        if path:
            self.result = path
            self.destroy()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        if not os.path.exists(self.directory): return
        
        files = [f for f in os.listdir(self.directory) if f.endswith(self.extension)]
        for f in sorted(files):
            name = f[:-len(self.extension)]
            self.listbox.insert(tk.END, name)

    def _load(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Auswahl", "Bitte wähle ein Projekt aus.")
            return
        
        name = self.listbox.get(idx[0])
        self.result = os.path.join(self.directory, name + self.extension)
        self.destroy()
