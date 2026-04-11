import os
import tkinter.font as tkfont
import platform

# --- THEME (FORGE CONTROL ROOM 2026) ---

BG = "#070A0F"          # Furnace Black
PANEL = "#131820"       # Gunmetal Surface
PANEL_2 = "#1B212B"     # Raised Control Surface
PANEL_3 = "#232A35"     # Upper Bezel
BORDER = "#2A3442"      # Brushed Steel Seam
TEXT = "#E2E8F0"        # Frosted Steel
SUBTLE = "#8C98AB"      # Desaturated Slate

ACCENT = "#F59E0B"      # Forge Amber
ACCENT_COOL = "#45E6FF" # Tron Cyan
ACCENT_COOL_GLOW = "#A5F3FC"
ACCENT_COOL_SOFT = "#102A35"
FLAVOR_INFO = "#38BDF8" # Console Cyan
FLAVOR_WARN = "#FBBF24"
FLAVOR_SUCCESS = "#10B981"
FLAVOR_ERROR = "#F43F5E"

FIELD_BG = "#0C1118"
FIELD_FG = "#E2E8F0"
LOG_BG = "#06090F"
LOG_FG = "#7DD3FC"
METAL_HI = "#3B4758"
METAL_LOW = "#0F141B"
GRID_LINE = "#133548"

# Fallbacks for runtime
ACCENT_SOFT = "#2A1F10"

# STATUS PALETTES
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


SPACE_XS = 6
SPACE_SM = 10
SPACE_MD = 14
SPACE_LG = 18
SPACE_XL = 24
CARD_GAP = 10
CARD_PAD_X = 16
CARD_PAD_Y = 14

def get_font(size, bold=False, italic=False):
    """Factory for modern variables fonts."""
    family = "Montserrat" if platform.system() == "Darwin" else "Inter"
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
FONT_LOG = ("JetBrains Mono", 10) if platform.system() == "Darwin" else ("Courier New", 10)

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

def lighten_color(base_color, ratio):
    return blend_color(base_color, "#FFFFFF", ratio)

def darken_color(base_color, ratio, target_color=BG):
    return blend_color(base_color, target_color, ratio)

def get_status_chip_text(status, lang="de"):
    return STATUS_LABELS.get(lang, STATUS_LABELS["de"]).get(status, status)

def get_source_accent(source):
    return SOURCE_PALETTES.get(source or "", {"accent": "#d9d4cf"})["accent"]

def get_row_color(status, is_source=False, ratio=0.16):
    if is_source:
        accent = get_source_accent(status)
    else:
        palette = STATUS_PALETTES.get(status, STATUS_PALETTES["all"])
        accent = palette["accent"]
    
    return blend_color(FIELD_BG, accent, ratio)

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Draws a high-fidelity rounded rectangle path on a Canvas."""
    points = [
        x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1,
        x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2,
        x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,
        x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)
