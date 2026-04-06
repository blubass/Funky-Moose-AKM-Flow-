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
