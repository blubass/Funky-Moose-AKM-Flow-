import tkinter as tk
from tkinter import ttk
import os
import subprocess
import pyperclip
import tkinter.font as tkfont
from tkinter import colorchooser

# --- UI CONSTANTS ---
# --- THEME DETECTION ---
def get_macos_appearance():
    """Detects if macOS is in Dark Mode or Light Mode."""
    try:
        cmd = ["defaults", "read", "-g", "AppleInterfaceStyle"]
        res = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        return "Dark" if "Dark" in res else "Light"
    except:
        return "Light"

IS_DARK = get_macos_appearance() == "Dark"

# --- ADAPTIVE COLOR PALETTES ---
def get_palette(is_dark=True):
    """Returns the set of colors for the given theme."""
    if is_dark:
        return {
            "BG": "#181818", "PANEL": "#232323", "PANEL_2": "#2b2b2b",
            "TEXT": "#f3f3f3", "SUBTLE": "#b5b5b5", "FIELD_BG": "#f7f7f7", "FIELD_FG": "#111111",
            "LOG_BG": "#101010", "LOG_FG": "#7CFFB2", "BORDER": "#3a3a3a",
            "ACCENT_SOFT": "#3a2a1c", "SUCCESS": "#71da9b"
        }
    else: # LIGHT MODE ("Industrial Paper" Look)
        return {
            "BG": "#f2ede7", "PANEL": "#ffffff", "PANEL_2": "#e6e1da",
            "TEXT": "#1a1a1a", "SUBTLE": "#666666", "FIELD_BG": "#ffffff", "FIELD_FG": "#000000",
            "LOG_BG": "#ffffff", "LOG_FG": "#1a1a1a", "BORDER": "#d9d4cf",
            "ACCENT_SOFT": "#f5e6d8", "SUCCESS": "#28a745"
        }

IS_DARK = get_macos_appearance() == "Dark"
_pal = get_palette(IS_DARK)

BG = _pal["BG"]; PANEL = _pal["PANEL"]; PANEL_2 = _pal["PANEL_2"]
TEXT = _pal["TEXT"]; SUBTLE = _pal["SUBTLE"]; FIELD_BG = _pal["FIELD_BG"]; FIELD_FG = _pal["FIELD_FG"]
LOG_BG = _pal["LOG_BG"]; LOG_FG = _pal["LOG_FG"]; BORDER = _pal["BORDER"]
ACCENT = "#ff9a3c"
ACCENT_SOFT = _pal["ACCENT_SOFT"]
FLAVOR_WARN = "#ffcb97"; FLAVOR_INFO = "#84cfff"; FLAVOR_SUCCESS = _pal["SUCCESS"]; FLAVOR_ERROR = "#ff9b7f"

def update_global_constants(is_dark):
    """Helper to update global style constants at runtime."""
    global BG, PANEL, PANEL_2, TEXT, SUBTLE, FIELD_BG, FIELD_FG, LOG_BG, LOG_FG, BORDER, ACCENT_SOFT, FLAVOR_SUCCESS, IS_DARK
    IS_DARK = is_dark
    p = get_palette(is_dark)
    BG = p["BG"]; PANEL = p["PANEL"]; PANEL_2 = p["PANEL_2"]
    TEXT = p["TEXT"]; SUBTLE = p["SUBTLE"]; FIELD_BG = p["FIELD_BG"]; FIELD_FG = p["FIELD_FG"]
    LOG_BG = p["LOG_BG"]; LOG_FG = p["LOG_FG"]; BORDER = p["BORDER"]
    ACCENT_SOFT = p["ACCENT_SOFT"]; FLAVOR_SUCCESS = p["SUCCESS"]
    
    # Debug info
    print(f"Theme updated: {'Dark' if is_dark else 'Light'} - BG: {BG}, PANEL: {PANEL}")

SPACE_XS = 6
SPACE_SM = 10
SPACE_MD = 14
SPACE_LG = 18
SPACE_XL = 24
CARD_GAP = 10
CARD_PAD_X = 14
CARD_PAD_Y = 12

# --- FONTS ---
FONT_SM = ("Helvetica", 10)
FONT_BOLD = ("Helvetica", 10, "bold")
FONT_MD = ("Helvetica", 11)
FONT_MD_BOLD = ("Helvetica", 11, "bold")
FONT_LG = ("Helvetica", 13, "bold")
FONT_XL = ("Helvetica", 14)
FONT_XXL = ("Helvetica", 20, "bold")
FONT_XXXL = ("Helvetica", 22, "bold")
FONT_ITALIC = ("Helvetica", 10, "italic")
FONT_LOG = ("Courier", 10)

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
def create_btn(parent, text, cmd, primary=False, quiet=False):
    """
    A Label-based custom button for perfect aesthetic control on all platforms.
    Avoids the platform-specific styling limitations of standard tk.Button.
    """
    if primary:
        bg_color, fg_color = ACCENT, "#111111"
        hov_bg = blend_color(bg_color, "#ffffff", 0.15)
        hov_fg = "#000000"
    elif quiet:
        bg_color, fg_color = PANEL_2, TEXT
        hov_bg = blend_color(bg_color, BORDER, 0.5)
        hov_fg = TEXT
    else:
        bg_color, fg_color = "#3a3a3a", TEXT
        hov_bg = blend_color(bg_color, "#ffffff", 0.15)
        hov_fg = TEXT

    btn = tk.Label(
        parent,
        text=text.upper() if not quiet else text,
        bg=bg_color,
        fg=fg_color,
        font=FONT_BOLD if not (primary or quiet) else (FONT_MD_BOLD if primary else FONT_SM),
        padx=20, # Uniform horizontal padding
        pady=10, # Uniform vertical padding (same height)
        cursor="hand2",
        relief="flat",
        bd=0,
        width=18 if not quiet else 0 # Apply base width to standard buttons
    )

    def _on_enter(e): btn.config(bg=hov_bg, fg=hov_fg)
    def _on_leave(e): btn.config(bg=bg_color, fg=fg_color)
    def _on_click(e): 
        btn.config(bg=blend_color(bg_color, "#000000", 0.2))
        parent.after(100, lambda: cmd())
        parent.after(150, lambda: btn.config(bg=bg_color))

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    btn.bind("<Button-1>", _on_click)
    
    return btn

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
class AkmPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL)
        super().__init__(parent, **kwargs)

class AkmCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL_2)
        kwargs.setdefault("bd", 1)
        kwargs.setdefault("relief", "solid")
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(parent, **kwargs)

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

