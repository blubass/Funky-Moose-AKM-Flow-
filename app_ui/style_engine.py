import tkinter as tk
from tkinter import ttk
from .theme import *

def apply_ttk_styles():
    """Applies the current theme constants (BG, PANEL, etc.) to the ttk engine."""
    style = ttk.Style()
    style.theme_use("default")
    
    # Global root style refresh
    style.configure(".", background=BG, foreground=TEXT, font=FONT_MD)
    
    style.configure(
        "TNotebook",
        background=blend_color(PANEL, METAL_HI, 0.10),
        borderwidth=0,
        padding=0,
        tabmargins=(SPACE_MD, SPACE_SM, SPACE_MD, 0),
    )
    style.map(
        "TNotebook",
        background=[
            ("active", blend_color(PANEL, METAL_HI, 0.10)),
            ("!active", blend_color(PANEL, METAL_HI, 0.10)),
        ],
    )
    
    style.configure(
        "TNotebook.Tab",
        background=PANEL_2,
        foreground=SUBTLE,
        padding=(20, 13),
        font=FONT_MD_BOLD,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", blend_color(PANEL_3, ACCENT_COOL, 0.18)),
            ("active", blend_color(PANEL_2, "#FFFFFF", 0.10)),
        ],
        foreground=[("selected", ACCENT_COOL_GLOW), ("active", TEXT)],
    )
    
    style.configure(
        "TProgressbar",
        thickness=10,
        troughcolor=blend_color(PANEL_2, BG, 0.28),
        background=blend_color(ACCENT_COOL, ACCENT, 0.42),
        borderwidth=0,
    )
    
    style.configure(
        "Treeview",
        background=FIELD_BG,
        fieldbackground=FIELD_BG,
        foreground=FIELD_FG,
        rowheight=28,
        borderwidth=0,
        font=FONT_SM,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        background=PANEL_2,
        foreground=TEXT,
        relief="flat",
        font=FONT_BOLD,
        padding=(10, 8),
    )
    style.map(
        "Treeview",
        background=[("selected", blend_color(FIELD_BG, ACCENT_COOL, 0.32))],
        foreground=[("selected", TEXT)],
    )
    style.map(
        "Treeview.Heading",
        background=[("active", blend_color(PANEL_2, ACCENT_COOL, 0.14))],
        foreground=[("active", ACCENT_COOL_GLOW)],
    )
    
    style.configure(
        "TCombobox",
        fieldbackground=FIELD_BG,
        background=PANEL_2,
        foreground=FIELD_FG,
        arrowcolor=ACCENT_COOL,
        arrowsize=18,
        borderwidth=0,
        relief="flat",
        padding=6,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", FIELD_BG)],
        foreground=[("readonly", FIELD_FG)],
        background=[("readonly", PANEL)],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=PANEL_2,
        troughcolor=BG,
        borderwidth=0,
        arrowcolor=SUBTLE,
        gripcount=0,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", blend_color(PANEL_2, ACCENT_COOL, 0.20))],
        arrowcolor=[("active", ACCENT_COOL_GLOW)],
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
