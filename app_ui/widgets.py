import tkinter as tk
from tkinter import ttk, colorchooser
import subprocess
import pyperclip
from .theme import *
from .buttons import create_btn

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

def fit_wraplength(widget, width, padding=36, minimum=180, maximum=None):
    """Keep helper labels readable across wide and narrow card layouts."""
    target = max(minimum, int(width - padding))
    if maximum is not None:
        target = min(target, maximum)
    widget.config(wraplength=target)
    return target

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
    """Hardware Card with organic rounded corners and 3D light-catch edge."""
    def __init__(self, parent, **kwargs):
        self._auto_height = kwargs.pop("auto_height", "height" not in kwargs)
        self._min_height = kwargs.pop("min_height", 0)
        super().__init__(parent, **kwargs)
        self._inner_pad_x = CARD_PAD_X
        self._inner_pad_top = CARD_PAD_Y + 4
        self._inner_pad_bottom = CARD_PAD_Y
        self._auto_height_after = None
        self.inner = tk.Frame(self, bg=self.bg_color)
        # Use fixed insets instead of relative percentages so large forms can define
        # their own natural height and the card can grow with them when needed.
        self.inner.place(
            x=self._inner_pad_x,
            y=self._inner_pad_top,
            relwidth=1.0,
            width=-(self._inner_pad_x * 2),
            relheight=1.0,
            height=-(self._inner_pad_top + self._inner_pad_bottom),
        )
        
        # Add a subtle light-reflect edge at the top
        self.line = tk.Frame(self, bg="#1E1E22", height=1)
        self.line.place(
            x=self._inner_pad_x,
            y=CARD_PAD_Y // 2,
            relwidth=1.0,
            width=-(self._inner_pad_x * 2),
        )
        if self._auto_height:
            self.inner.bind("<Configure>", self._queue_auto_height, add="+")
            self.bind("<Map>", self._queue_auto_height, add="+")

    def _queue_auto_height(self, event=None):
        if not self._auto_height or not self.winfo_exists() or self._auto_height_after is not None:
            return
        self._auto_height_after = self.after_idle(self._apply_auto_height)

    def _apply_auto_height(self):
        self._auto_height_after = None
        if not self.winfo_exists():
            return
        target_height = self.inner.winfo_reqheight() + self._inner_pad_top + self._inner_pad_bottom
        if self._min_height:
            target_height = max(target_height, self._min_height)
        current_height = int(self.cget("height") or 0)
        if current_height != target_height:
            self.configure(height=target_height)

class AkmScrollablePanel(tk.Frame):
    """
    A scrollable container that maintains the industrial design aesthetic.
    Uses a Canvas and Scrollbar to enable scrolling for its interior frame.
    """
    def __init__(self, parent, **kwargs):
        bg_target = kwargs.pop("bg", BG)
        super().__init__(parent, bg=bg_target, **kwargs)
        self._mousewheel_bound = set()
        self._rebind_after = None
        
        self.canvas = tk.Canvas(self, bg=bg_target, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, 
                                     bg=bg_target, troughcolor="#111111",
                                     width=10, relief="flat")
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_target)

        self.scrollable_frame.bind(
            "<Configure>",
            self._on_frame_configure
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Proper local recursive binding instead of bind_all
        self._bind_mousewheel_recursive(self.canvas)
        self._bind_mousewheel_recursive(self.scrollable_frame)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Re-bind lazily so large panels don't walk the whole widget tree
        # multiple times while geometry is still settling.
        if self._rebind_after is None:
            self._rebind_after = self.after_idle(self._refresh_mousewheel_bindings)

    def _refresh_mousewheel_bindings(self):
        self._rebind_after = None
        self._bind_mousewheel_recursive(self.scrollable_frame)

    def _bind_mousewheel_recursive(self, widget):
        widget_id = str(widget)
        if widget_id not in self._mousewheel_bound:
            widget.bind("<MouseWheel>", self._on_mousewheel, add="+")
            widget.bind("<Button-4>", self._on_mousewheel, add="+")
            widget.bind("<Button-5>", self._on_mousewheel, add="+")
            self._mousewheel_bound.add(widget_id)
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)

    def _on_canvas_configure(self, event):
        # Update the width of the scrollable frame to match the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if not self.winfo_exists(): return
        
        # Scroll logic (no complex 'is_over' check needed as we use direct local binding)
        if event.num == 4: # Linux
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5: # Linux
            self.canvas.yview_scroll(1, "units")
        else: # macOS / Windows
            delta = event.delta
            if abs(delta) >= 120:
                self.canvas.yview_scroll(int(-1*(delta/120)), "units")
            else: # macOS often sends 1 or -1
                # Boost the scroll a bit for better feel on macOS canvas
                self.canvas.yview_scroll(int(-1*delta*2), "units") 

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

class PulseLabel(tk.Label):
    """A high-fidelity pulsing label with smooth sinus-based color transitions."""
    def __init__(self, parent, base_color=PANEL, pulse_color=ACCENT, **kwargs):
        kwargs.setdefault("bg", base_color)
        kwargs.setdefault("fg", TEXT)
        super().__init__(parent, **kwargs)
        self.base_color = base_color
        self.pulse_color = pulse_color
        self._running = False
        self._step = 0

    def start(self):
        if not self._running:
            self._running = True
            self._animate()

    def stop(self):
        self._running = False
        self.config(bg=self.base_color)

    def _animate(self):
        if not self._running: return
        import math
        self._step = (self._step + 1) % 20
        ratio = (math.sin(self._step * (math.pi / 10)) + 1) / 2
        color = blend_color(self.base_color, self.pulse_color, ratio * 0.4)
        self.config(bg=color)
        self.after(50, self._animate)

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
        cb = AkmCheckbutton(self, text=label_text, variable=variable, **kwargs)
        cb.grid(row=self._current_row, column=1, sticky="w", pady=SPACE_XS)
        self._current_row += 1
        return cb

    def add_header(self, text, color=ACCENT):
        AkmLabel(
            self,
            text=text,
            fg=color,
            bg=self["bg"],
            font=FONT_LG,
        ).grid(row=self._current_row, column=0, columnspan=2, sticky="w", pady=(SPACE_MD, SPACE_SM))
        self._current_row += 1

    def add_combobox(self, label_text, variable, values, **kwargs):
        AkmLabel(
            self, text=label_text + ":", bg=self["bg"]
        ).grid(row=self._current_row, column=0, sticky="w", padx=(0, SPACE_SM), pady=SPACE_XS)
        
        cb = ttk.Combobox(self, textvariable=variable, values=values, **kwargs)
        cb.grid(row=self._current_row, column=1, sticky="ew", pady=SPACE_XS)
        self._current_row += 1
        return cb

    def add_color_field(self, label_text, variable):
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
