# Standalone-Build auf macOS

## Voraussetzungen
- Python 3.11
- PyInstaller
- Die versionierte Build-Datei `FunkyMooseReleaseForge.spec` liegt im Projektordner
- Das Icon `akm_icon.icns` liegt im Projektordner

## Build-Befehl

```bash
python3 -m PyInstaller --clean --noconfirm 'FunkyMooseReleaseForge.spec'
```

## Ergebnis
- Das App-Bundle liegt anschließend unter `dist/Funky Moose Release Forge.app`.
- Die entpackte Build-Struktur liegt zusätzlich unter `dist/Funky Moose Release Forge`.
- Fuer Endnutzer ist **keine Python- oder Paket-Installation mehr noetig**. Weitergegeben wird nur `dist/Funky Moose Release Forge.app`.

## Hinweise
- Der Build verwendet ausschliesslich die versionierte Spec-Datei `FunkyMooseReleaseForge.spec`.
- Das Icon wird über `akm_icon.icns` eingebunden.
- Der aktuelle Build ist bereits auf unnoetige grosse Pakete wie `pandas`, `matplotlib` und `numpy` fuer diese App reduziert.
- Die Spec-Datei nimmt die benoetigten `tkinterdnd2`-/`tkdnd`-Runtime-Dateien fuer macOS mit ins Bundle.
- Wenn PyInstaller in einer Sandbox an Berechtigungen für den Cache scheitert, muss der Build außerhalb der Sandbox ausgeführt werden.
- Fuer moeglichst reibungslosen Versand sollte die `.app` vor dem Teilen als `.zip` verpackt werden.
- Ohne Codesigning/Notarisierung kann macOS beim ersten Start noch einen Sicherheitsdialog zeigen. Fuer ein wirklich friktionsfreies Ausliefern waeren Codesigning und Notarisierung der naechste Schritt.
