# Release Notes v1.0.9

## Release Readiness & Packaging

Diese Version macht die Forge sauberer fuer den echten Versand und stabiler in den letzten Metern vor dem Release.

- **Komplettere i18n-Abdeckung**: Fehlende Uebersetzungen in Schnellstart, Katalog, Details, Cover und Release-Umgebung wurden geschlossen. Sichtbare Roh-Keys im UI tauchen dort jetzt nicht mehr auf.
- **Sauberer Release-Export**: Der Export-Flow fuer Release-Pakete wurde erneut praktisch geprueft. Audio, Cover, `release_info.txt`, `tracklist.csv`, `tracklist.xlsx` und `checklist.txt` werden konsistent erzeugt.
- **macOS Versandpaket vorbereitet**: Die App ist weiter als ZIP-freundliches macOS-Bundle verpackbar, inklusive Installationsanleitung fuer Systeme ohne Apple-Notarisierung.

## Fixes & Verbesserungen

- **UI-Texte vervollstaendigt**: Fehlende Labels und Action-Texte fuer Filter, Suche, Sortierung, Listenaktionen und Cover-Hinweise sind jetzt in Deutsch und Englisch vorhanden.
- **Release-Check stabilisiert**: Der aktuelle Build wurde erneut mit Tests, Bundle-Start und Export-Smoke abgesichert.
- **Lokale Release-Artefakte aus Git rausgehalten**: `release-assets/` wird jetzt ignoriert, damit Verpackungsordner nicht versehentlich im Repo landen.

## Build & Distribution

- Der Tag `v1.0.9` ist fuer den bestehenden GitHub-Release-Workflow vorbereitet.
- Die Release-Pipeline baut weiterhin **macOS** und **Windows** Pakete automatisch.

---
**Funky Moose Release Forge** - *Ship it clean, keep it funky.*
