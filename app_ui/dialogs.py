import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from .theme import *
from .buttons import create_btn
from .widgets import AkmCard, AkmLabel, AkmPanel, AkmEntry, AkmSubLabel

class AkmSaveDialog(tk.Toplevel):
    def __init__(self, parent, title, directory, extension=".akm"):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x550")
        self.transient(parent)
        self.grab_set()
        
        self.directory = directory
        self.extension = extension
        self.result = None
        
        os.makedirs(self.directory, exist_ok=True)
        self.configure(bg=BG)
        self._build_ui()
        self._refresh_list()
        
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=SPACE_MD, pady=SPACE_MD)
        tk.Label(hdr, text="PROJEKT SPEICHERN", bg=BG, fg=ACCENT, font=FONT_XL).pack(side="left")
        
        container = AkmCard(self)
        container.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_MD))
        
        AkmLabel(container, text="VORHANDENE PROJEKTE", font=FONT_MD_BOLD, fg=ACCENT).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        
        list_frame = AkmPanel(container)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X)
        
        self.listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, font=FONT_MD,
            selectbackground=ACCENT, selectforeground="black",
            borderwidth=0, highlightthickness=1, highlightbackground=BORDER
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)
        
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        
        entry_frame = AkmPanel(container)
        entry_frame.pack(fill="x", padx=CARD_PAD_X, pady=SPACE_MD)
        
        AkmLabel(entry_frame, text="PROJEKTNAME:").pack(side="left")
        self.name_var = tk.StringVar()
        self.entry = AkmEntry(entry_frame, textvariable=self.name_var)
        self.entry.pack(side="left", fill="x", expand=True, padx=(SPACE_SM, 0))
        self.entry.bind("<Return>", lambda e: self._save())
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_MD))
        
        create_btn(btn_row, "DURCHSUCHEN...", self._browse, quiet=True).pack(side="left")
        create_btn(btn_row, "SPEICHERN", self._save, primary=True).pack(side="right")
        create_btn(btn_row, "ABBRECHEN", self.destroy, quiet=True).pack(side="right", padx=SPACE_SM)

    def _browse(self):
        path = filedialog.asksaveasfilename(
            initialdir=self.directory,
            title="Projekt Speichern unter",
            filetypes=[("AKM Projekt", f"*{self.extension}"), ("Alle Dateien", "*.*")],
            defaultextension=self.extension
        )
        if path:
            self.result = path
            self.destroy()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        if not os.path.exists(self.directory): return
        
        files = [f for f in os.listdir(self.directory) if f.endswith(self.extension)]
        for f in sorted(files):
            name = f[:-len(self.extension)]
            self.listbox.insert(tk.END, name)

    def _on_select(self, event):
        idx = self.listbox.curselection()
        if idx:
            self.name_var.set(self.listbox.get(idx[0]))

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Eingabe", "Bitte gib einen Namen ein.")
            return
        
        self.result = os.path.join(self.directory, name + self.extension)
        if os.path.exists(self.result):
            if not messagebox.askyesno("Überschreiben", f"'{name}' existiert bereits. Überschreiben?"):
                return
        
        self.wait_window_success = True
        self.destroy()

class AkmLoadDialog(tk.Toplevel):
    def __init__(self, parent, title, directory, extension=".akm"):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x550")
        self.transient(parent)
        self.grab_set()
        
        self.directory = directory
        self.extension = extension
        self.result = None
        
        self.configure(bg=BG)
        self._build_ui()
        self._refresh_list()
        
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=SPACE_MD, pady=SPACE_MD)
        tk.Label(hdr, text="PROJEKT LADEN", bg=BG, fg=ACCENT, font=FONT_XL).pack(side="left")
        
        container = AkmCard(self)
        container.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_MD))
        
        AkmLabel(container, text="GESPEICHERTE PROJEKTE", font=FONT_MD_BOLD, fg=ACCENT).pack(anchor="w", padx=CARD_PAD_X, pady=(CARD_PAD_Y, SPACE_XS))
        
        list_frame = AkmPanel(container)
        list_frame.pack(fill="both", expand=True, padx=CARD_PAD_X, pady=(0, CARD_PAD_Y))
        
        self.listbox = tk.Listbox(
            list_frame, bg=FIELD_BG, fg=FIELD_FG, font=FONT_MD,
            selectbackground=ACCENT, selectforeground="black",
            borderwidth=0, highlightthickness=1, highlightbackground=BORDER
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)
        
        self.listbox.bind("<Double-Button-1>", lambda e: self._load())
        
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=SPACE_MD, pady=(0, SPACE_MD))
        
        create_btn(btn_row, "DURCHSUCHEN...", self._browse, quiet=True).pack(side="left")
        create_btn(btn_row, "LADEN", self._load, primary=True).pack(side="right")
        create_btn(btn_row, "ABBRECHEN", self.destroy, quiet=True).pack(side="right", padx=SPACE_SM)

    def _browse(self):
        path = filedialog.askopenfilename(
            initialdir=self.directory,
            title="Projekt Laden",
            filetypes=[("AKM Projekt", f"*{self.extension}"), ("Alle Dateien", "*.*")]
        )
        if path:
            self.result = path
            self.destroy()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        if not os.path.exists(self.directory): return
        
        files = [f for f in os.listdir(self.directory) if f.endswith(self.extension)]
        for f in sorted(files):
            name = f[:-len(self.extension)]
            self.listbox.insert(tk.END, name)

    def _load(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Auswahl", "Bitte wähle ein Projekt aus.")
            return
        
        name = self.listbox.get(idx[0])
        self.result = os.path.join(self.directory, name + self.extension)
        self.destroy()

class AkmImagePreviewDialog(tk.Toplevel):
    """A premium, dedicated window to preview images (like cover art)."""
    def __init__(self, parent, image_path, title="Vorschau"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.transient(parent)
        self.grab_set()
        
        self.image_path = image_path
        self._photo = None
        
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=SPACE_MD, pady=SPACE_MD)
        tk.Label(hdr, text=title.upper(), bg=BG, fg=ACCENT, font=FONT_LG).pack(side="left")
        
        self.card = AkmCard(self, bg_color="#08080A")
        self.card.pack(fill="both", expand=True, padx=SPACE_MD, pady=(0, SPACE_MD))
        
        self.img_label = tk.Label(self.card.inner, bg="#08080A")
        self.img_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.info_label = AkmSubLabel(self, text=os.path.basename(image_path), bg=BG)
        self.info_label.pack(pady=(0, SPACE_SM))
        
        create_btn(self, "SCHLIESSEN", self.destroy, quiet=True, width=120).pack(pady=(0, SPACE_MD))
        
        self._load_image()
        
        self.update_idletasks()
        w, h = 500, 600
        self.geometry(f"{w}x{h}")
        
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _load_image(self):
        if not os.path.exists(self.image_path):
            self.img_label.config(text="BILD NICHT GEFUNDEN", fg=FLAVOR_ERROR)
            return
            
        try:
            from PIL import Image, ImageTk
            with Image.open(self.image_path) as img:
                max_w, max_h = 440, 440
                img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                self._photo = ImageTk.PhotoImage(img)
                self.img_label.config(image=self._photo)
        except Exception as e:
            self.img_label.config(text=f"FEHLER: {str(e)}", fg=FLAVOR_ERROR)
