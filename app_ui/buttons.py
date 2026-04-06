import tkinter as tk
from .theme import *

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
