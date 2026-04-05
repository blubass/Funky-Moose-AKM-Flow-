# Funky Moose Release Forge auf macOS installieren

Diese Anleitung ist fuer Empfaenger der fertigen ZIP-Datei gedacht.

## Was du bekommst

Du erhaeltst in der Regel diese Datei:

- `Funky Moose Release Forge.zip`

Darin liegt die eigentliche App:

- `Funky Moose Release Forge.app`

## Wichtig vorab

- Es ist **keine Python-Installation** noetig.
- Es muessen **keine Pakete oder Libraries** installiert werden.
- Die App ist aktuell **nicht von Apple notarisiert**, weil kein bezahlter Apple-Developer-Account verwendet wurde.
- Deshalb kann macOS beim ersten Start eine Sicherheitswarnung anzeigen. Das ist erwartbar.

## Normale Installation

1. Lade `Funky Moose Release Forge.zip` auf den Mac.
2. Oeffne die ZIP per Doppelklick.
3. Ziehe `Funky Moose Release Forge.app` an einen sinnvollen Ort, zum Beispiel:
   - `Programme`
   - `Schreibtisch`
   - einen eigenen Arbeitsordner
4. Starte die App.

## Wenn macOS die App blockiert

Falls beim ersten Start eine Meldung wie "kann nicht geoeffnet werden" oder "Apple konnte nicht ueberpruefen..." erscheint:

### Variante A: Rechtsklick und Oeffnen

1. Schließe die Warnmeldung.
2. Rechtsklick auf `Funky Moose Release Forge.app`
3. `Oeffnen` waehlen
4. Im naechsten Dialog erneut `Oeffnen` bestaetigen

Das ist meist der einfachste Weg.

### Variante B: Ueber Datenschutz & Sicherheit

1. Versuche die App einmal normal zu starten.
2. Oeffne danach:
   - `Systemeinstellungen`
   - `Datenschutz & Sicherheit`
3. Scrolle nach unten zum Sicherheits-Hinweis.
4. Klicke auf `Trotzdem oeffnen`
5. Bestaetige den naechsten Dialog.

## Fortgeschrittene Variante per Terminal

Nur noetig, wenn die grafischen Wege nicht funktionieren.

1. Terminal oeffnen
2. Diesen Befehl ausfuehren:

```bash
xattr -dr com.apple.quarantine "/Pfad/zu/Funky Moose Release Forge.app"
```

Beispiel:

```bash
xattr -dr com.apple.quarantine "/Applications/Funky Moose Release Forge.app"
```

Danach die App erneut starten.

## Wo die App ihre Daten speichert

Die App speichert ihre Daten lokal im Benutzerordner:

- Daten: `~/akm_assistant/data.json`
- Backup: `~/akm_assistant/data_backup.json`
- Sprache: `~/akm_assistant/lang.txt`
- Einstellungen: `~/akm_assistant/settings.json`

## Update auf eine neue Version

1. Alte App schliessen
2. Neue ZIP entpacken
3. Alte `.app` durch die neue ersetzen
4. Die gespeicherten Daten bleiben erhalten, weil sie ausserhalb der App liegen

## Typische Fragen

### Muss ich Python installieren?

Nein.

### Muss ich etwas im Terminal installieren?

Nein. Normalerweise reicht Entpacken und Oeffnen.

### Brauche ich Admin-Rechte?

Meistens nicht. Nur wenn du die App in einen geschuetzten Systemordner verschieben willst.

### Gehen meine Daten bei einem Update verloren?

Nein, solange dein Benutzerordner erhalten bleibt.

## Empfehlung fuer den Versand

Wenn du die App weitergibst, versende am besten:

- `Funky Moose Release Forge.zip`
- plus diese Anleitung `INSTALL_MAC.md`

So haben Empfaenger sofort die passenden Schritte zur Hand.
