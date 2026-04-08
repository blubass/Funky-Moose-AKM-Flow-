
# Kombinierte AKM Assistant & Flow App
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import pyperclip
import re
import akm_core

def clean_title(title):
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"\[.*?\]", "", title)
    title = re.sub(r"feat\..*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"radio edit", "", title, flags=re.IGNORECASE)
    return title.strip()

class AKMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AKM FLOW & ASSISTANT")
        self.root.geometry("700x800")
        self.tracks = []
        self.index = 0
        self.mode = "title"
        self.batch_running = False
        self.delay_ms = 900
        self.first_track = True
        self._after_id = None

        # Tabs
        self.tabs = ttk.Notebook(root)
        self.tab_flow = tk.Frame(self.tabs)
        self.tab_assist = tk.Frame(self.tabs)
        self.tabs.add(self.tab_flow, text="Flow Batch")
        self.tabs.add(self.tab_assist, text="Assistant")
        self.tabs.pack(expand=1, fill="both")

        # --- FLOW TAB ---
        tk.Label(self.tab_flow, text="AKM SMART FLOW+", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Button(self.tab_flow, text="📂 Excel laden", command=self.load_excel).pack(pady=5)
        self.track_var = tk.StringVar()
        tk.Label(self.tab_flow, textvariable=self.track_var, font=("Arial", 14)).pack(pady=5)
        self.progress = ttk.Progressbar(self.tab_flow, length=400, mode="determinate")
        self.progress.pack(pady=5)
        self.text_box = tk.Text(self.tab_flow, height=6, width=70, bg="#111", fg="#00ff88")
        self.text_box.pack(pady=10)
        self.status = tk.StringVar(value="Ready")
        tk.Label(self.tab_flow, textvariable=self.status, fg="#00ff88").pack(pady=5)
        speed_frame = tk.Frame(self.tab_flow)
        speed_frame.pack(pady=5)
        tk.Label(speed_frame, text="Speed (ms):").pack(side=tk.LEFT)
        self.speed_slider = tk.Scale(speed_frame, from_=300, to=15000, orient=tk.HORIZONTAL,
                         length=200, command=self.update_speed)
        self.speed_slider.set(self.delay_ms)
        self.speed_slider.pack(side=tk.LEFT, padx=5)
        btn_frame = tk.Frame(self.tab_flow)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="🚀 START", command=self.start_batch).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="⏹ STOP", command=self.stop_batch).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 RESTART", command=self.restart).pack(side=tk.LEFT, padx=5)

        # --- ASSISTANT TAB ---
        tk.Label(self.tab_assist, text="AKM Assistant", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Button(self.tab_assist, text="➕ Neues Werk", command=self.add_entry).pack(pady=5)
        tk.Button(self.tab_assist, text="📝 Status ändern", command=self.change_status).pack(pady=5)
        tk.Button(self.tab_assist, text="📋 Offene anzeigen", command=self.show_open).pack(pady=5)
        tk.Button(self.tab_assist, text="📦 Export (Excel)", command=self.export_csv).pack(pady=5)
        tk.Button(self.tab_assist, text="🔍 Suchen/Filtern", command=self.search_entries).pack(pady=5)
        tk.Button(self.tab_assist, text="💾 Backup", command=self.backup_data).pack(pady=5)
        tk.Button(self.tab_assist, text="♻️ Restore", command=self.restore_data).pack(pady=5)
        self.assist_box = tk.Text(self.tab_assist, height=18, width=80, bg="#222", fg="#00ff88")
        self.assist_box.pack(pady=10)

    # FLOW
    def update_speed(self, val):
        self.delay_ms = int(val)

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return
        try:
            self.tracks = akm_core.load_excel_tracks(file_path)
            self.index = 0
            self.mode = "title"
            self.first_track = True
            self.progress.configure(value=0)
            self.update_track()
            self.status.set(f"{len(self.tracks)} Tracks geladen")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_track(self):
        if not self.tracks or self.index >= len(self.tracks):
            self.track_var.set("✅ Fertig!")
            self.text_box.delete(1.0, tk.END)
            self.status.set("DONE")
            self.progress.configure(value=100)
            self.batch_running = False
            self.root.title("AKM SMART FLOW+ – DONE")
            return
        row = self.tracks[self.index]
        self.title = clean_title(row["title"])
        self.duration = row.get("duration") or "3:30"
        self.track_var.set(f"{self.index+1}/{len(self.tracks)} – {self.title}")
        self.progress.configure(value=(self.index / len(self.tracks)) * 100)
        self.root.title(f"AKM SMART FLOW+ – {self.index+1}/{len(self.tracks)}")

    def start_batch(self):
        if not self.tracks or self.batch_running:
            return
        self.batch_running = True
        self.mode = "title"
        self.run_batch()

    def stop_batch(self):
        self.batch_running = False
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        self.status.set("⏹ gestoppt")

    def restart(self):
        self.batch_running = False
        if self.tracks:
            self.index = 0
            self.mode = "title"
            self.first_track = True
            self.progress.configure(value=0)
            self.update_track()
            self.status.set("🔄 Neustart – bereit")

    def run_batch(self):
        if not self.batch_running:
            return
        if not self.tracks or self.index >= len(self.tracks):
            self.batch_running = False
            return
        if self.mode == "title":
            pyperclip.copy(self.title)
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, f"📋 TITEL → CMD+V\n{self.title}")
            self.status.set("TITEL → GO")
            self.mode = "duration"
        elif self.mode == "duration":
            pyperclip.copy(self.duration)
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, f"📋 DAUER → CMD+V\n{self.duration}")
            self.status.set("DAUER → GO")
            self.mode = "language"
        elif self.mode == "language":
            self.text_box.delete(1.0, tk.END)
            if self.first_track:
                self.text_box.insert(tk.END, "🌍 Sprache: Deutschsprachig\n🎵 Werkart: Populärmusik / Melody")
                self.first_track = False
            else:
                self.text_box.insert(tk.END, "🌍 Sprache: Deutschsprachig (Dropdown)")
            self.status.set("SPRACHE → CLICK")
            self.mode = "submit"
        elif self.mode == "submit":
            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, "➡️ WEITER klicken")
            self.status.set("WEITER → CLICK")
            self.mode = "title"
            self.index += 1
            self.update_track()
        self._after_id = self.root.after(self.delay_ms, self.run_batch)

    # ASSISTANT
    def add_entry(self):
        title = simpledialog.askstring("Neues Werk", "Titel:")
        if not title:
            return
        try:
            ok, res = akm_core.add_entry(title)
        except akm_core.DataFileError as exc:
            self.assist_box.insert(tk.END, f"❌ Anlegen blockiert: {exc}\n")
            return
        if ok:
            self.assist_box.insert(tk.END, f"✅ Neu angelegt: {title}\n")
        elif res == "already_exists":
            self.assist_box.insert(tk.END, f"⚠️ Schon vorhanden: {title}\n")
        elif res == "empty_title":
            self.assist_box.insert(tk.END, f"❗ Titel darf nicht leer sein!\n")

    def change_status(self):
        title = simpledialog.askstring("Status ändern", "Titel:")
        if not title:
            return
        lang = akm_core.get_lang()
        status_keys = akm_core.get_status_keys(lang)
        status_map = akm_core.get_status_map(lang)
        status = simpledialog.askstring("Status", f"Status ({', '.join(status_keys)}):")
        if not status:
            return
        try:
            ok, res = akm_core.update_status(title, status, lang)
        except akm_core.DataFileError as exc:
            self.assist_box.insert(tk.END, f"❌ Status-Update blockiert: {exc}\n")
            return
        if ok:
            self.assist_box.insert(tk.END, f"🔄 Aktualisiert: {title} → {status_map[status]}\n")
        elif res == "not_found":
            self.assist_box.insert(tk.END, f"❌ Nicht gefunden: {title}\n")
        elif res == "invalid_status":
            self.assist_box.insert(tk.END, f"❗ Ungültiger Status!\n")

    def show_open(self):
        lang = akm_core.get_lang()
        status_map = akm_core.get_status_map(lang)
        self.assist_box.insert(tk.END, "\n📋 Offene Werke:\n")
        try:
            entries = akm_core.get_all_entries()
        except akm_core.DataFileError as exc:
            self.assist_box.insert(tk.END, f"❌ Anzeigen blockiert: {exc}\n")
            return
        for item in entries:
            if item["status"] != "confirmed":
                self.assist_box.insert(tk.END, f"- {item['title']} ({status_map[item['status']]}) [{item.get('last_change', item['date'])}]\n")

    def export_csv(self):
        lang = akm_core.get_lang()
        try:
            path = akm_core.export_csv(lang)
        except akm_core.DataFileError as exc:
            self.assist_box.insert(tk.END, f"❌ Export blockiert: {exc}\n")
            return
        self.assist_box.insert(tk.END, f"📦 Exportiert nach: {path}\n")

    def search_entries(self):
        lang = akm_core.get_lang()
        status_map = akm_core.get_status_map(lang)
        term = simpledialog.askstring("Suchen/Filtern", "Suchbegriff oder Status:")
        self.assist_box.insert(tk.END, f"\n🔍 Ergebnisse für '{term}':\n")
        try:
            entries = akm_core.get_all_entries()
        except akm_core.DataFileError as exc:
            self.assist_box.insert(tk.END, f"❌ Suche blockiert: {exc}\n")
            return
        for item in entries:
            if not term or term.lower() in item["title"].lower() or term.lower() in item["status"]:
                self.assist_box.insert(tk.END, f"- {item['title']} ({status_map[item['status']]}) [{item.get('last_change', item['date'])}]\n")

    def backup_data(self):
        try:
            akm_core.backup_data()
        except akm_core.DataFileError as exc:
            self.assist_box.insert(tk.END, f"❌ Backup blockiert: {exc}\n")
            return
        self.assist_box.insert(tk.END, "💾 Backup gespeichert\n")

    def restore_data(self):
        try:
            restored = akm_core.restore_data()
        except akm_core.DataFileError as exc:
            self.assist_box.insert(tk.END, f"❌ Restore blockiert: {exc}\n")
            return
        if restored:
            self.assist_box.insert(tk.END, "♻️ Backup wiederhergestellt\n")
        else:
            self.assist_box.insert(tk.END, "❌ Kein Backup gefunden!\n")

# --- START ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AKMApp(root)
    root.mainloop()
