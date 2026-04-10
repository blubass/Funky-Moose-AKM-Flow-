"""
Facade pattern for backwards compatibility.
The actual implementation has been modularized to improve readability and maintainability.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import pyperclip
import tkinter.font as tkfont
from tkinter import colorchooser

from .theme import *
from .style_engine import *
from .buttons import *
from .widgets import *
from .dialogs import *


def apply_button_bar_layout(container, buttons, width, breakpoint, mode, row_spacing=SPACE_XS, anchor="w"):
    """Apply a simple row/stack button layout and return the active mode."""
    target_mode = "stack" if width and width < breakpoint else "row"
    if mode == target_mode:
        return target_mode
    for button in buttons:
        button.pack_forget()
    if target_mode == "stack":
        container.pack(anchor=anchor, fill="x")
        for index, button in enumerate(buttons):
            button.pack(fill="x", pady=(0, SPACE_XS if index < len(buttons) - 1 else 0))
        return target_mode
    container.pack(anchor=anchor)
    for index, button in enumerate(buttons):
        pad_left = 0 if index == 0 else row_spacing
        button.pack(side="left", padx=(pad_left, 0))
    return target_mode


def resolve_layout_mode(width, breakpoint, narrow_mode="stack", wide_mode="row"):
    return narrow_mode if width and width < breakpoint else wide_mode


def repack_widgets(layout):
    seen = set()
    for widget, _pack_kwargs in layout:
        widget_id = id(widget)
        if widget_id in seen:
            continue
        seen.add(widget_id)
        widget.pack_forget()
    for widget, pack_kwargs in layout:
        widget.pack(**pack_kwargs)


def apply_widget_layout(width, breakpoint, mode, layout_map, narrow_mode="stack", wide_mode="row"):
    target_mode = resolve_layout_mode(width, breakpoint, narrow_mode, wide_mode)
    if mode == target_mode:
        return target_mode
    repack_widgets(layout_map[target_mode])
    return target_mode
