import tkinter as tk
from tkinter import ttk
from .theme import *

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
        foreground=[("selected", "#000000"), ("active", TEXT)],
    )
    
    style.configure(
        "TProgressbar",
        thickness=8,
        troughcolor="#333333",
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


