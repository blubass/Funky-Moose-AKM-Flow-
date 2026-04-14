import tkinter as tk
from tkinter import ttk, colorchooser
import os
import platform
import subprocess
import pyperclip
from .theme import *
from .buttons import create_btn
from app_logic import i18n

def style_chip_label(widget, status, text, active=False):
    palette = STATUS_PALETTES.get(status, STATUS_PALETTES["all"])
    if active:
        widget.config(
            text=text,
            bg=palette["accent"],
            fg="#111111",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=blend_color(palette["accent"], "#FFFFFF", 0.12),
            highlightcolor=blend_color(palette["accent"], "#FFFFFF", 0.12),
        )
        return

    widget.config(
        text=text,
        bg=palette["bg"],
        fg=palette["fg"],
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=blend_color(palette["bg"], "#FFFFFF", 0.08),
        highlightcolor=blend_color(palette["accent"], "#FFFFFF", 0.10),
    )

def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        return True, None
    except Exception as exc:
        return False, str(exc)

def open_in_finder(path):
    try:
        system = platform.system()
        if system == "Windows":
            normalized = os.path.normpath(path)
            if os.path.isdir(normalized):
                subprocess.run(["explorer", normalized], check=False)
            else:
                subprocess.run(["explorer", f"/select,{normalized}"], check=False)
        elif system == "Darwin":
            subprocess.run(["open", "-R", path], check=False)
        else:
            target = path if os.path.isdir(path) else os.path.dirname(path) or "."
            subprocess.run(["xdg-open", target], check=False)
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
        radius = min(self.radius, max(8, min((w - 10) // 2, (h - 12) // 2)))
        if w < radius * 2 + 8 or h < radius * 2 + 12:
            return

        drop_far = blend_color(self.bg_color, BG, 0.82)
        drop_mid = blend_color(self.bg_color, BG, 0.70)
        drop_near = blend_color(self.bg_color, BG, 0.58)
        seam_outer = blend_color(self.border_color, "#FFFFFF", 0.14)
        seam_inner = blend_color(self.bg_color, "#FFFFFF", 0.08)
        face_lift = blend_color(self.bg_color, "#FFFFFF", 0.04)
        lower_lip = blend_color(self.bg_color, BG, 0.28)
        top_glow = blend_color(self.bg_color, "#FFFFFF", 0.16)
        accent_glow = blend_color(ACCENT, self.bg_color, 0.76)
        cool_glow = blend_color(self.bg_color, ACCENT_COOL, 0.20)
        cool_trace = blend_color(self.bg_color, ACCENT_COOL, 0.14)
        grid_trace = blend_color(self.bg_color, GRID_LINE, 0.26)
        warm_trace = blend_color(self.bg_color, ACCENT, 0.16)

        draw_rounded_rect(self, 6, 11, w - 5, h - 1, radius, fill=drop_far, outline="")
        draw_rounded_rect(self, 4, 8, w - 4, h - 3, radius, fill=drop_mid, outline="")
        draw_rounded_rect(self, 2, 5, w - 2, h - 5, radius, fill=drop_near, outline="")
        draw_rounded_rect(self, 1, 1, w - 1, h - 7, radius, fill=seam_outer, outline="")
        draw_rounded_rect(self, 2, 2, w - 2, h - 8, radius, fill=seam_inner, outline="")
        draw_rounded_rect(self, 3, 3, w - 3, h - 9, radius, fill=face_lift, outline="")
        draw_rounded_rect(self, 3, 4, w - 3, h - 10, radius, fill=self.bg_color, outline="")
        self.create_line(
            radius + 4,
            8,
            w - radius - 4,
            8,
            fill=top_glow,
            width=1,
            capstyle="round",
        )
        self.create_line(
            radius + 12,
            11,
            w - radius - 12,
            11,
            fill=accent_glow,
            width=1,
            capstyle="round",
        )
        self.create_line(
            radius + 20,
            14,
            w - radius - 32,
            14,
            fill=cool_glow,
            width=1,
            capstyle="round",
        )
        self.create_line(
            9,
            radius + 4,
            9,
            h - radius - 14,
            fill=blend_color(self.bg_color, "#FFFFFF", 0.06),
            width=1,
            capstyle="round",
        )
        self.create_line(
            radius + 10,
            h - 16,
            w - radius - 10,
            h - 16,
            fill=lower_lip,
            width=1,
            capstyle="round",
        )
        self.create_line(
            16,
            16,
            30,
            16,
            fill=cool_trace,
            width=1,
            capstyle="round",
        )
        self.create_line(
            16,
            16,
            16,
            30,
            fill=cool_trace,
            width=1,
            capstyle="round",
        )
        self.create_line(
            w - 16,
            h - 18,
            w - 30,
            h - 18,
            fill=warm_trace,
            width=1,
            capstyle="round",
        )
        self.create_line(
            w - 16,
            h - 18,
            w - 16,
            h - 32,
            fill=warm_trace,
            width=1,
            capstyle="round",
        )
        self.create_line(
            22,
            h - 26,
            w - 22,
            h - 26,
            fill=grid_trace,
            width=1,
            capstyle="round",
        )

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
        self.inner = tk.Frame(
            self,
            bg=self.bg_color,
            highlightthickness=1,
            highlightbackground=blend_color(self.bg_color, METAL_HI, 0.16),
        )
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
        self.line = tk.Frame(self, bg=blend_color(self.bg_color, ACCENT, 0.22), height=1)
        self.line.place(
            x=self._inner_pad_x,
            y=CARD_PAD_Y // 2,
            relwidth=1.0,
            width=-(self._inner_pad_x * 2),
        )
        self.line_cool = tk.Frame(self, bg=blend_color(self.bg_color, ACCENT_COOL, 0.22), height=1)
        self.line_cool.place(
            x=self._inner_pad_x,
            y=(CARD_PAD_Y // 2) + 1,
            relwidth=1.0,
            width=-(self._inner_pad_x * 2),
        )
        self.line_shadow = tk.Frame(self, bg=blend_color(self.bg_color, BG, 0.26), height=1)
        self.line_shadow.place(
            x=self._inner_pad_x,
            y=(CARD_PAD_Y // 2) + 3,
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
        
        self.canvas = tk.Canvas(self, bg=bg_target, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            bg=PANEL_2,
            activebackground=blend_color(PANEL_2, ACCENT_COOL, 0.20),
            troughcolor=BG,
            width=10,
            relief="flat",
            highlightthickness=0,
            bd=0,
        )
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

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Update the width of the scrollable frame to match the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

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
        super().__init__(
            parent,
            text=text,
            bg=PANEL,
            fg=color,
            font=FONT_MD_BOLD,
            padx=20,
            pady=10,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=blend_color(color, "#FFFFFF", 0.14),
            **kwargs,
        )
        self.place(relx=0.5, rely=0.1, anchor="center")
        self.after(duration, self.destroy)

def add_hover(widget, enter_color, leave_color):
    """Binds hover event to a widget."""
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_color))

class AkmBadge(tk.Label):
    """A small glowing status indicator badge."""
    def __init__(self, parent, text, **kwargs):
        kwargs.setdefault("bg", FIELD_BG)
        kwargs.setdefault("fg", SUBTLE)
        kwargs.setdefault("font", FONT_BOLD)
        kwargs.setdefault("padx", 9)
        kwargs.setdefault("pady", 3)
        kwargs.setdefault("relief", "flat")
        super().__init__(parent, text=text.upper(), **kwargs)
        self.active_color = ACCENT
        self.inactive_color = SUBTLE

    def set_active(self, active=True):
        self.config(fg=self.active_color if active else self.inactive_color)
        if active:
            self.config(
                bg=blend_color(FIELD_BG, ACCENT, 0.16),
                highlightbackground=blend_color(ACCENT, "#FFFFFF", 0.10),
                highlightthickness=1,
            )
        else:
            self.config(bg=FIELD_BG, highlightthickness=0)


def build_badge_strip(parent, labels, active_indices=(), bg=None, padx=0, pady=0):
    """Create a consistent horizontal badge strip and return the row plus badge refs."""
    row_bg = bg or parent.cget("bg")
    row = AkmPanel(parent, bg=row_bg)
    row.pack(fill="x", padx=padx, pady=pady)
    badges = []
    active_set = set(active_indices or ())
    for index, text in enumerate(labels):
        badge = AkmBadge(row, text)
        badge.pack(side="left", padx=(0 if index == 0 else SPACE_XS, 0))
        badge.set_active(index in active_set)
        badges.append(badge)
    return row, badges


def build_radar_summary(
    parent,
    *,
    title,
    mode_text,
    status_text,
    hint_text,
    context_text="",
    bg=None,
    title_fg=ACCENT,
    status_fg=TEXT,
    title_font=FONT_LG,
    status_font=FONT_MD_BOLD,
    hint_wrap=560,
):
    """Create the repeated radar/status summary pattern used across primary tabs."""
    summary_bg = bg or parent.cget("bg")
    title_label = AkmLabel(parent, text=title, fg=title_fg, bg=summary_bg, font=title_font)
    title_label.pack(anchor="w")
    mode_label = AkmSubLabel(
        parent,
        text=mode_text,
        bg=summary_bg,
        anchor="w",
    )
    mode_label.pack(fill="x", pady=(1, 1))
    status_label = AkmLabel(
        parent,
        text=status_text,
        fg=status_fg,
        bg=summary_bg,
        anchor="w",
        font=status_font,
        justify="left",
    )
    status_label.pack(fill="x", pady=(2, 2))
    hint_label = AkmSubLabel(
        parent,
        text=hint_text,
        bg=summary_bg,
        anchor="w",
        justify="left",
        wraplength=hint_wrap,
    )
    hint_label.pack(fill="x")
    context_label = AkmSubLabel(
        parent,
        text=context_text,
        bg=summary_bg,
        anchor="w",
        justify="left",
    )
    context_label.pack(fill="x", pady=(2, 0))
    return {
        "title_label": title_label,
        "mode_label": mode_label,
        "status_label": status_label,
        "hint_label": hint_label,
        "context_label": context_label,
    }


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
        kwargs.setdefault("insertbackground", FIELD_FG)
        kwargs.setdefault("insertwidth", 2)
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", blend_color(BORDER, FIELD_BG, 0.22))
        kwargs.setdefault("highlightcolor", blend_color(ACCENT, "#FFFFFF", 0.18))
        kwargs.setdefault("selectbackground", blend_color(ACCENT, BG, 0.34))
        kwargs.setdefault("selectforeground", TEXT)
        kwargs.setdefault("disabledbackground", blend_color(FIELD_BG, BG, 0.08))
        kwargs.setdefault("disabledforeground", SUBTLE)
        kwargs.setdefault("readonlybackground", blend_color(FIELD_BG, "#FFFFFF", 0.04))
        kwargs.setdefault("font", FONT_MD)
        super().__init__(parent, **kwargs)

class AkmText(tk.Text):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", FIELD_BG)
        kwargs.setdefault("fg", FIELD_FG)
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("insertbackground", FIELD_FG)
        kwargs.setdefault("insertwidth", 2)
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", blend_color(BORDER, FIELD_BG, 0.22))
        kwargs.setdefault("highlightcolor", blend_color(ACCENT, "#FFFFFF", 0.18))
        kwargs.setdefault("selectbackground", blend_color(ACCENT, BG, 0.34))
        kwargs.setdefault("selectforeground", TEXT)
        kwargs.setdefault("font", FONT_SM)
        kwargs.setdefault("padx", 8)
        kwargs.setdefault("pady", 8)
        super().__init__(parent, **kwargs)

class AkmCheckbutton(tk.Checkbutton):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", PANEL_2)
        kwargs.setdefault("fg", TEXT)
        kwargs.setdefault("activebackground", PANEL_2)
        kwargs.setdefault("activeforeground", TEXT)
        kwargs.setdefault("selectcolor", FIELD_BG)
        kwargs.setdefault("highlightthickness", 0)
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
            c = colorchooser.askcolor(title=i18n._t("ui_title_preview") + f" {label_text}")
            if c[1]: variable.set(c[1])
        
        btn = create_btn(container, "Spectrum", _pick, quiet=True)
        btn.pack(side="left", padx=(SPACE_XS, 0))
        
        self._current_row += 1
        return entry
