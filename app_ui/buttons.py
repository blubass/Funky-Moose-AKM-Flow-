import tkinter as tk

from .theme import *


class AkmCanvasButton(tk.Canvas):
    """Custom forge button with dynamic redraw and basic text/state support."""

    def __init__(self, parent, text, cmd, primary=False, quiet=False, width=None, accent_color=None):
        self._quiet = bool(quiet)
        self._command = cmd
        self._text = text
        self._radius = 18 if not self._quiet else 12
        self._button_height = 46 if not self._quiet else 34
        self._base_bg = accent_color if accent_color else ACCENT
        self._base_fg = "#111111"
        self._state = "normal"
        self._hover = False
        self._pressed = False

        if self._quiet:
            self._base_bg = blend_color(PANEL_2, "#FFFFFF", 0.02)
            self._base_fg = TEXT

        self._font = FONT_BOLD if not (primary or accent_color) else FONT_MD_BOLD
        if len(text) > 18:
            self._font = FONT_SM

        _fallback_w = width if width else (200 if not self._quiet else 160)
        try:
            import tkinter.font as tkfont
            _f = tkfont.Font(font=self._font)
            _calc_w = _f.measure(str(text or "").upper()) + 36
            self._fixed_width = max(_calc_w, _fallback_w)
        except Exception:
            self._fixed_width = _fallback_w

        super().__init__(
            parent,
            bg=parent["bg"],
            highlightthickness=0,
            borderwidth=0,
            width=self._fixed_width,
            height=self._button_height,
            takefocus=0,
            cursor="hand2",
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_configure)
        self._draw()

    def _state_palette(self, visual_state):
        if self._quiet:
            fill = {
                "disabled": blend_color(self._base_bg, BG, 0.20),
                "normal": self._base_bg,
                "hover": blend_color(self._base_bg, ACCENT_COOL, 0.12),
                "pressed": blend_color(self._base_bg, "#000000", 0.12),
            }.get(visual_state, self._base_bg)
            outer = {
                "disabled": blend_color(BORDER, BG, 0.34),
                "normal": blend_color(BORDER, "#FFFFFF", 0.08),
                "hover": blend_color(ACCENT_COOL, "#FFFFFF", 0.18),
                "pressed": blend_color(BORDER, "#000000", 0.10),
            }.get(visual_state, BORDER)
            text_color = SUBTLE if visual_state == "disabled" else TEXT
            inner = blend_color(fill, "#FFFFFF", 0.10)
            shine = blend_color(fill, "#FFFFFF", 0.18)
            side_glow = blend_color(fill, ACCENT_COOL, 0.16)
            shadow_near = blend_color(fill, BG, 0.62)
            shadow_far = blend_color(fill, BG, 0.80)
            accent_strip = blend_color(fill, ACCENT_COOL, 0.28)
            lip = blend_color(fill, BG, 0.24)
            tracer = blend_color(fill, ACCENT_COOL, 0.34)
            tracer_hot = blend_color(fill, ACCENT_COOL_GLOW, 0.26)
        else:
            fill = {
                "disabled": blend_color(self._base_bg, BG, 0.28),
                "normal": self._base_bg,
                "hover": blend_color(self._base_bg, "#FFFFFF", 0.10),
                "pressed": blend_color(self._base_bg, "#000000", 0.10),
            }.get(visual_state, self._base_bg)
            outer = {
                "disabled": blend_color(self._base_bg, BG, 0.08),
                "normal": blend_color(self._base_bg, "#FFFFFF", 0.24),
                "hover": blend_color(self._base_bg, "#FFFFFF", 0.34),
                "pressed": blend_color(self._base_bg, "#000000", 0.12),
            }.get(visual_state, self._base_bg)
            text_color = blend_color(self._base_fg, BG, 0.45) if visual_state == "disabled" else self._base_fg
            inner = blend_color(fill, "#FFFFFF", 0.12)
            shine = blend_color(fill, "#FFFFFF", 0.22)
            side_glow = blend_color(fill, ACCENT_COOL, 0.18)
            shadow_near = blend_color(fill, BG, 0.70)
            shadow_far = blend_color(fill, BG, 0.86)
            accent_strip = blend_color(fill, ACCENT, 0.20)
            lip = blend_color(fill, BG, 0.28)
            tracer = blend_color(fill, ACCENT_COOL, 0.28)
            tracer_hot = blend_color(fill, ACCENT_COOL_GLOW, 0.22)
        return {
            "fill": fill,
            "outer": outer,
            "inner": inner,
            "text": text_color,
            "shine": shine,
            "side_glow": side_glow,
            "shadow_near": shadow_near,
            "shadow_far": shadow_far,
            "accent_strip": accent_strip,
            "lip": lip,
            "tracer": tracer,
            "tracer_hot": tracer_hot,
        }

    def _visual_state(self):
        if self._state == "disabled":
            return "disabled"
        if self._pressed:
            return "pressed"
        if self._hover:
            return "hover"
        return "normal"

    def _draw(self):
        self.delete("all")
        width = self.winfo_width() or self._fixed_width
        height = self.winfo_height() or self._button_height
        visual_state = self._visual_state()
        palette = self._state_palette(visual_state)
        press_offset = 2 if visual_state == "pressed" else 0
        face_top = 2 + press_offset
        face_bottom = height - 6 + press_offset
        radius = max(8, self._radius)

        draw_rounded_rect(self, 5, 10, width - 5, height, radius, fill=palette["shadow_far"], outline="")
        draw_rounded_rect(self, 4, 7, width - 4, height - 2, radius, fill=palette["shadow_near"], outline="")
        draw_rounded_rect(self, 1, face_top, width - 1, face_bottom + 2, radius, fill=palette["outer"], outline="")
        draw_rounded_rect(self, 2, face_top + 1, width - 2, face_bottom + 1, radius, fill=palette["inner"], outline="")
        draw_rounded_rect(self, 3, face_top + 2, width - 3, face_bottom, max(6, radius - 1), fill=palette["fill"], outline="")
        self.create_line(
            radius,
            face_top + 4,
            width - radius,
            face_top + 4,
            fill=palette["shine"],
            width=1,
            capstyle="round",
        )
        self.create_line(
            radius + 4,
            face_top + 7,
            width - radius - 4,
            face_top + 7,
            fill=palette["side_glow"],
            width=1,
            capstyle="round",
        )
        self.create_line(
            10,
            face_top + 7,
            10,
            max(face_top + 8, face_bottom - 8),
            fill=palette["side_glow"],
            width=1,
            capstyle="round",
        )
        self.create_line(
            radius + 4,
            face_bottom - 3,
            width - radius - 4,
            face_bottom - 3,
            fill=palette["lip"],
            width=1,
            capstyle="round",
        )
        self.create_line(
            radius + 2,
            face_bottom - 1,
            width - radius - 2,
            face_bottom - 1,
            fill=palette["accent_strip"],
            width=1,
            capstyle="round",
        )
        self.create_line(
            width - 10,
            face_top + 8,
            width - 10,
            max(face_top + 8, face_bottom - 7),
            fill=palette["tracer"],
            width=1,
            capstyle="round",
        )
        self.create_line(
            width - radius - 8,
            face_top + 8,
            width - 14,
            face_top + 8,
            fill=palette["tracer_hot"],
            width=1,
            capstyle="round",
        )
        self.create_line(
            14,
            face_bottom - 5,
            radius + 10,
            face_bottom - 5,
            fill=palette["accent_strip"],
            width=1,
            capstyle="round",
        )
        text_y = (height / 2) - 1 + press_offset
        self.create_text(
            width / 2,
            text_y + 1,
            text=(self._text or "").upper(),
            fill=blend_color(palette["text"], BG, 0.55),
            font=self._font,
        )
        self.create_text(
            width / 2,
            text_y,
            text=(self._text or "").upper(),
            fill=palette["text"],
            font=self._font,
        )
        self.configure(cursor="arrow" if self._state == "disabled" else "hand2")

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._pressed = False
        self._draw()

    def _on_press(self, _event):
        if self._state == "disabled":
            return
        self._pressed = True
        self._draw()

    def _on_release(self, event):
        if self._state == "disabled":
            return
        was_pressed = self._pressed
        self._pressed = False
        inside = 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()
        self._draw()
        if was_pressed and inside and callable(self._command):
            self._command()

    def _on_configure(self, _event):
        self._draw()

    def configure(self, cnf=None, **kwargs):
        options = {}
        if cnf:
            options.update(cnf)
        options.update(kwargs)

        redraw = False
        if "text" in options:
            self._text = options.pop("text")
            redraw = True
            try:
                import tkinter.font as tkfont
                _calc_w = tkfont.Font(font=self._font).measure(str(self._text or "").upper()) + 36
                if _calc_w > self._fixed_width and "width" not in options:
                    self._fixed_width = _calc_w
            except Exception:
                pass
        if "state" in options:
            self._state = options.pop("state")
            redraw = True
        if "command" in options:
            self._command = options.pop("command")
        if "width" in options:
            self._fixed_width = int(options["width"])
            redraw = True
        if "height" in options:
            self._button_height = int(options["height"])
            redraw = True

        result = super().configure(**options) if options else super().configure()
        if redraw:
            self._draw()
        return result

    config = configure

    def cget(self, key):
        if key == "text":
            return self._text
        if key == "state":
            return self._state
        return super().cget(key)

    def invoke(self):
        if self._state != "disabled" and callable(self._command):
            self._command()


def create_btn(parent, text, cmd, primary=False, quiet=False, width=None, accent_color=None):
    """Build a forge button that behaves close to a normal Tk widget."""
    return AkmCanvasButton(
        parent,
        text,
        cmd,
        primary=primary,
        quiet=quiet,
        width=width,
        accent_color=accent_color,
    )
