# AKMFlow+ | Der Musik-Assistant 🦌🔥

![Header](input_file_0.png)

**AKMFlow+** ist die ultimative Zentrale für deinen Release-Workflow. In einer hochmodernen, industriellen "Dark Mode" Umgebung orchestriert diese Forge deine Musik-Metadaten, optimiert die Lautheit deiner Tracks und bereitet deine Releases für den perfekten Export vor.

---

## 💎 Features & Highlights

- **AESTHETIC DASHBOARD**: Behalte den Überblick über alle offenen, gemeldeten und bestätigten Werke mit leuchtenden Status-Chips und Echtzeit-Statistiken.
- **BATCH WORKFLOW**: Melde deine Werke in Sekunden: Ein Klick kopiert den Titel, ein zweiter die Dauer, und der dritte setzt den Status. Nie war AKM/GEMA-Arbeit fokussierter.
- **LOUDNESS OPTIMIZER**: Integriertes LUFS- & True Peak-Mastering. Analysiere deinen gesamten Katalog und exportiere pefekt gepegelte Match-Dateien.
- **RELEASE FORGE**: Baue vollständige Release-Pakete inkl. Metadata-Validierung, Cover-Preview und Distribution-Export.
- **PREMIUM UI**: Vollständige "Industrial Dark" Ästhetik mit sanften Mikro-Animationen, Hover-Feedback und transienten Notification-Toasts.

---

## 🎨 Visual Preview

![Dashboard Mockup](akm_flow_plus_ui_dashboard_1775377055436.png)
*Beispiel des neuen High-Fidelity UI-Designs mit Fokus auf maximale Übersicht und haptisches Feedback.*

---

## 🛠 Tech-Stack

- **Core**: Python 3.11+
- **UI**: Custom Tkinter-Engine mit "Industrial Dark" Design-System
- **Logic**: Modularer AppState (Zentraler Store) & Threaded TaskRunner
- **Audio**: EBU R128 Loudness Analysis & Digital Peak Tracking
- **Data**: Excel-Auto-Mapping & JSON Persistence

---

## 🚀 Schnellstart

1.  **Repository klonen**
2.  **Abhängigkeiten installieren**: `pip install tkinterdnd2 openpyxl pyloudnorm` (oder entsprechende Module)
3.  **Starten**: `python3 akm_app.py`

---

## 🧹 Architektur-Refactor Summary

In der aktuellen Version wurde das System komplett entkoppelt. Das modernisierte **AppState-Modell** sorgt für konsistente Daten in allen Tabs, während der **TaskRunner** rechenintensive Aufgaben (wie Audio-Analyse) in den Hintergrund verlagert, damit das UI jederzeit flüssig und "live" bleibt.

---

*Made with 🔥 and Focus. Keep context, keep flow.*
