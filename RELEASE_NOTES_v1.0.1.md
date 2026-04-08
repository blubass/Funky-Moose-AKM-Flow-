# v1.0.1 — Workflow Radar, mehr Flow, mehr Liebe

Funky Moose Release Forge bekommt mit `v1.0.1` einen grossen UI- und Workflow-Polish: klarere Orientierung, konsistentere Bedienung und robustere Ablaeufe ueber die komplette App.

## Highlights

- Einheitlicher Radar-/Cockpit-Look ueber alle Hauptbereiche
- Deutlich bessere Statusfuehrung und Empty States
- Konsistenterer Flow zwischen Uebersicht, Details, Cover, Loudness und Release
- Stabilere Batch-, Import- und Export-Ablaufe
- Erweiterte Regressionstests und erfolgreicher macOS-Build

## Neu & verbessert

### Global

- Neuer, konsistenter Header mit sichtbarem Systemstatus
- Bessere visuelle Hierarchie und klarere Aktionsbereiche
- Mehr "ein Guss", weniger verstreute Einzeloberflaechen

### Dashboard

- Neues `Operations Radar`
- Fokus-Hinweise und Meta-Kennzahlen fuer den aktuellen Arbeitsstand
- Schnellere Navigation in die naechsten sinnvollen Schritte

### Uebersicht

- Neues `Catalog Radar`
- Bessere Filter-, Such- und Empty-State-Kommunikation
- Direktere Aktionen fuer Details, Audio-Preview und Loudness
- Doppelklick oeffnet jetzt sauber die Details

### Werkdetails

- Neues `Werk Radar`
- Live-Kontext fuer Titel, Audio, Status und Instrumental-Flag
- Klarere Hinweise je nach Datenzustand
- Insgesamt deutlich besser lesbare Arbeitsansicht

### Cover Forge

- Konsistentes Preview-/Export-Rendering
- Verbesserte Preset-Layouts inklusive `Top Left`
- Besserer Artwork-Flow mit Release-Uebergabe, Finder und Live-Radar
- Neue Render-Parameter werden gespeichert und sauber wiederhergestellt

### Release

- Klarere Release-Zusammenstellung
- Smartere Dateizuordnung und Dublettenbehandlung
- Aufgeraeumterer Export-Workflow
- Alte generierte Export-Artefakte werden vor Neubau sauber bereinigt

### Loudness

- Verbesserte Status- und Hinweisfuehrung
- Konsistentere Uebergaben aus Uebersicht und Dateiauswahl
- Bessere Sichtbarkeit von Workflow-Zustaenden

### Assistant & Batch

- Beide Bereiche jetzt mit eigenem Radar statt blanker Controls
- Klarere Queue-/Eingabe-Kommunikation
- Getrennte Eingabefelder statt gegenseitigem Ueberschreiben
- Batch-Flow robuster und besser gefuehrt

## Stabilitaet & Qualitaet

- Regressionstest-Suite modernisiert und erweitert
- `45/45` Tests erfolgreich
- GUI-Smoke-Test erfolgreich
- PyInstaller-Build fuer macOS erfolgreich

## Build-Artefakte

- `Funky Moose Release Forge.app`
- `Funky Moose Release Forge.zip`

## Hinweis fuer macOS

Da der Build aktuell nicht codesigned/notarized ist, kann macOS beim ersten Start noch einen Sicherheitsdialog anzeigen.

Danke fuers Testen, Weiterbauen und Schoenmachen. Diese Version ist deutlich runder, klarer und einfach angenehmer im taeglichen Flow.
