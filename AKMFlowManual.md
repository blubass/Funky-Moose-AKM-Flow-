# 🦌 AKMFlow+ | Die Funky Moose Release Forge — Handbuch

Willkommen in der **AKMFlow+ Forge**. Dieses Dokument ist dein Guide für den effizienten Einsatz der Applikation im Musik-Management. Entwickelt für Geschwindigkeit, Präzision und eine industrielle High-Fidelity-Ästhetik.

---

## 🏗️ 1. Die Philosophie: Industrial Dark & Context-First
AKMFlow+ ist kein einfaches Tabellen-Tool. Es ist eine **Forge (Schmiede)**. 
- **Dark Mode**: Schont die Augen bei langen Sessions (Farben: Obsidian, Slate, Hyper-Orange).
- **Zustandslosigkeit**: Alle Tabs greifen auf einen zentralen `AppState` zu. Änderungen in den Details sind sofort in der Übersicht und im Batch sichtbar.
- **Background Actions**: Audio-Analysen blockieren niemals das UI. Der `TaskRunner` arbeitet im Hintergrund, während du weiter tippst.

---

## 🧩 2. Die Module (Die Tabs)

### 📊 Dashboard
Deine Kommandozentrale. Hier siehst du auf einen Blick, wie viele Werke in welchem Stadium sind.
- **Status-Chips**: Klicke auf "Offen" oder "Bereit", um die Übersicht sofort gefiltert nach diesem Status zu öffnen.
- **Statistiken**: Zählt automatisch Instrumental-Anteile, Notiz-Dichte und Produktions-Metadaten.
- **Jumping**: Nutze "Letztes offenes Werk", um ohne Suchen direkt dort weiterzumachen, wo die Arbeit fehlt.

### ⚡ Batch (Der High-Speed Workflow)
Optimiert für das manuelle Melden von Werken bei Verwertungsgesellschaften (AKM/GEMA/etc.).
- **Smart Copy**: Klicke auf "Titel kopieren". Der Button bekommt ein grünes Häkchen. Ein zweiter Klick kopiert (falls vorhanden) die Dauer oder den ISRC. 
- **Auto-Navigation**: "Weiter" springt zum nächsten offenen Werk in der Schlange.
- **Status-Link**: "Als gemeldet markieren" setzt den Status in Echtzeit um und leert die aktuelle Ansicht für den nächsten Track.

### 📋 Übersicht
Die Datenbank-Ansicht.
- **Suche & Filter**: Suche nach Titeln, Komponisten oder Notizen. Filterung nach Status-Chips ist jederzeit möglich.
- **Doppelklick**: Ein Doppelklick auf einen Eintrag in der Liste lädt dieses Werk sofort in den `Details`-Tab zur Bearbeitung.

### ✏️ Details
Präzisionsarbeit für einzelne Metadaten.
- **Audio-Link**: Ziehe eine Audio-Datei per **Drag-And-Drop** auf diesen Tab. Die Forge extrahiert automatisch:
    - Den Dateinamen als Titel-Vorschlag.
    - Die exakte Dauer (min:sec) per FFmpeg/Probe.
- **Tags & Notizen**: Verwalte Stichworte (komma-separiert) für besseres Filtern.
- **Status-Chips**: Setze das Werk hier manuell auf "Bereit" (Blau) oder "Bestätigt" (Grün).

### 🎚 Lautheit (Loudness Engine)
Integriertes EBU R128 Mastering-Tool.
- **Echtzeit-Analyse**: Analysiere LUFS (Integrated), Loudness Range (LRA) und True Peak.
- **Waveform**: Generiert visuelle Envelopes deiner Tracks zur schnellen Kontrolle.
- **Match-Export**: Exportiere normalisierte Versionen deiner Tracks (z.B. auf -14 LUFS oder -23 LUFS), um Industriestandards für Distribution zu entsprechen.

### 🚀 Release
Die Verpackungsstation für den finalen Export.
- **Assembly**: Stelle Tracks aus deiner Datenbank zu einem Release zusammen.
- **Metadata-Injection**: Generiert die notwendigen CSV/Excel-Listen für Distributoren.
- **Cover-Check**: Verknüpfe dein Artwork und lasse Previews generieren.

---

## ⚡ 3. Der "Moose-Standard" Workflow (Best Practice)

1. **Import**: Ziehe eine Excel-Liste deines Katalogs in den **Übersicht**-Tab (oder Batch-Tab).
2. **Review**: Gehe in den **Batch**-Tab. Nutze die Smart-Copy-Funktion, um deine Werke bei deiner Verwertungsgesellschaft einzutragen.
3. **Enhance**: Doppelklicke in der Übersicht auf Tracks, die noch keine exakte Dauer haben. Ziehe die finalen Master-Dateien per Drag-and-Drop in den **Details**-Tab.
4. **Finalize**: Sobald alle Tracks "Bereit" sind, wechsle zum **Release**-Tab, wähle das Cover und exportiere das fertige Distro-Paket.
5. **Backup**: Nutze `Dashboard -> Speichern`, um dein gesamtes Projekt als `.akm`-Datei zu sichern.

---

## 🛠 4. Technische Hinweise

### Tastenkürzel (Shortcuts)
- **Enter (in Details)**: Speichert das aktuelle Werk.
- **Enter (im Dashboard-Add)**: Legt ein neues leeres Werk an.
- **Cmd+S (macOS)**: Speichere das gesamte Projekt (System-Dialog).

### Datei-Kompatibilität
- **Audio**: WAV, MP3, AIFF, FLAC (via FFmpeg).
- **Listen**: XLSX, XLS (via openpyxl).
- **Projekt**: `.akm` (proprietäres Moose-Format, im Kern JSON).

---

> [!IMPORTANT]
> **FFmpeg** muss auf deinem System installiert sein (z.B. via `brew install ffmpeg`), damit die Lautheits-Analyse und die Waveform-Generierung funktionieren.

---

*Handbuch Version 1.1.0 | Stand: April 2026*
