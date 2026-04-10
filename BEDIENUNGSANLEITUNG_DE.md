# Funky Moose Release Forge – Bedienungsanleitung

**Funky Moose Release Forge** ist eine macOS-Desktop-App für Werke, Loudness, Cover und Release-Vorbereitung. Die App bündelt Eingabe, Excel-Import, Batch-Kopierhilfe, Übersicht, Loudness-Analyse und Release-Export in einer Oberfläche.

## Installation und Start
1. Öffne den Ordner `dist` im Projektverzeichnis.
2. Ziehe `Funky Moose Release Forge.app` optional in den Programme-Ordner.
3. Starte die App per Doppelklick auf `Funky Moose Release Forge.app`.

## Aufbau der App
Die App hat mehrere Arbeitsbereiche:

### 1. Schnellstart
- **Titel eingeben:** Trage einen neuen Werktitel ein.
- **Add:** Legt das Werk neu an.
- **Bereit / Gemeldet / Bestätigt:** Setzt direkt den Status des aktuell eingetragenen Titels.
- **Import Excel:** Importiert Titel aus einer Excel-Datei.
- **Log:** Zeigt an, was importiert, kopiert oder geändert wurde.

### 2. Batch
- Der Batch zeigt nur Werke mit Status `in_progress` oder `ready`.
- **Copy:** Kopiert pro Klick genau einen Wert in die Zwischenablage:
  zuerst den `Titel` ohne Feldnamen, beim nächsten Klick die `Dauer`. Danach springt der Batch automatisch zum nächsten Werk und beginnt wieder bei `Titel`.
- **Submitted:** Markiert den aktuellen Batch-Eintrag als `submitted`.
- **Skip:** Springt zum nächsten offenen Eintrag.
- **Reload:** Lädt die offenen Batch-Daten neu aus dem Speicher.
- Unter dem Titel siehst du Zusatzinfos wie Komponist und Dauer sowie den aktuellen Fortschritt.

### 3. Übersicht
- Zeigt alle gespeicherten Werke mit Status an.
- Wenn Dauer oder Komponist vorhanden sind, werden sie in der Liste mit angezeigt.
- **Im Batch öffnen:** Öffnet den markierten Titel direkt im Batch-Tab, sofern das Werk noch offen ist.
- **In Eingabe übernehmen:** Übernimmt den markierten Titel in das Eingabefeld des Schnellstart-Tabs.
- Doppelklick auf einen Eintrag öffnet ihn ebenfalls direkt im Batch.
- Werke mit Status `submitted` oder `confirmed` werden nicht in den offenen Batch übernommen; stattdessen erscheint ein Hinweis im Log.

### 4. Lautheit
- Übernimmt ausgewählte oder gefilterte Werke direkt in die Loudness-Liste.
- Führt eine **Lautheits-Analyse** über die verknüpften Audio-Dateien aus.
- Zeigt LUFS, Peak, Gain-Empfehlung und Match-Status in einer Tabelle.
- Exportiert gematchte Dateien gesammelt in einen Ausgabeordner.

### 5. Release
- Sammelt Werke oder Audio-Dateien für ein Release.
- Unterstützt Drag&Drop für gematchte Audio-Dateien.
- Erstellt Cover-Previews in verschiedenen Layouts und Formaten.
- Baut einen Distro-Export mit Tracklist, Audios und Checkliste.

## Excel-Import
Der Import akzeptiert `.xlsx`- und `.xls`-Dateien.

Unterstützte Spaltennamen:
- `Titel` oder `Title`
- `Dauer`, `Duration` oder `Length`
- `Komponist` oder `Composer`

Wenn keine Kopfzeile erkannt wird, verwendet die App:
- Spalte 1 für den Titel
- Spalte 2 für die Dauer
- Spalte 3 für den Komponisten

Import-Verhalten:
- Neue Titel werden direkt mit Status `ready` angelegt.
- Bestehende Titel werden aktualisiert, wenn neue Dauer- oder Komponisten-Daten vorhanden sind.
- Bereits vorhandene offene Titel können beim Import von `in_progress` auf `ready` angehoben werden.

## Status-System
Die App verwendet diese internen Status:
- `in_progress`
- `ready`
- `submitted`
- `confirmed`

In der Oberfläche werden sie sprachabhängig lesbar angezeigt, z. B. `in Arbeit`, `bereit`, `gemeldet`, `bestätigt`.

## Speicherorte
Die App speichert ihre Daten lokal im Benutzerordner:

- Daten: `~/akm_assistant/data.json`
- Backup: `~/akm_assistant/data_backup.json`
- Spracheinstellung: `~/akm_assistant/lang.txt`
- Einstellungen: `~/akm_assistant/settings.json`

## Hinweise
- Beim Start zeigt der Schnellstart im Log das zuletzt noch offene Werk an, falls eines existiert.
- Der Batch ist als Kopierhilfe gedacht und meldet nichts automatisch im Browser.
- Der Standard-Artist fuer neue Releases kann optional in `~/akm_assistant/settings.json` gesetzt werden, z. B. ueber `"release_default_artist": "Mein Projekt"`.

Viel Freude mit Funky Moose Release Forge.
