# Funky Moose Release Forge auf Windows installieren

Diese Anleitung ist fuer Empfaenger der fertigen Windows-ZIP gedacht.

## Was du bekommst

Du erhaeltst in der Regel diese Datei:

- `Funky-Moose-Release-Forge-Windows.zip`

Darin liegt ein Ordner mit:

- `Funky Moose Release Forge.exe`
- allen benoetigten Laufzeitdateien

## Wichtig vorab

- Es ist **keine Python-Installation** noetig.
- Es muessen **keine Pakete oder Libraries** installiert werden.
- Beim ersten Start kann Windows SmartScreen warnen, weil die App nicht code-signiert ist.

## Installation

1. Lade die ZIP-Datei herunter.
2. Entpacke sie komplett in einen normalen Ordner, zum Beispiel:
   - `Downloads\Funky Moose Release Forge`
   - `Desktop\Funky Moose Release Forge`
   - einen eigenen Arbeitsordner
3. Starte `Funky Moose Release Forge.exe`.

## Wenn Windows warnt

Falls SmartScreen die App blockiert:

1. Klicke auf `Weitere Informationen`
2. Klicke auf `Trotzdem ausfuehren`

## Wo die App ihre Daten speichert

Die App speichert ihre Daten lokal im Benutzerordner:

- Daten: `~/akm_assistant/data.json`
- Backup: `~/akm_assistant/data_backup.json`
- Sprache: `~/akm_assistant/lang.txt`
- Einstellungen: `~/akm_assistant/settings.json`

## Update auf eine neue Version

1. Alte App schliessen
2. Neue ZIP entpacken
3. Alten App-Ordner durch den neuen ersetzen
4. Die gespeicherten Daten bleiben erhalten
