# Release Notes v1.0.8

## 🚀 Neuheiten & Upgrades

### Loudness Engine 2.0 (Linear Logic)
Der Loudness Desk wurde grundlegend überarbeitet, um für Musik-Mastering absolut vorhersehbare Ergebnisse zu liefern.
- **Soft-Limiter Matching**: Die App nutzt nun standardmäßig linearen Gain + Soft-Limiter. Das verhindert das "Pumpen" und dynamische Sprünge, die durch den vorherigen R128-Loudnorm-Filter entstehen konnten.
- **High-Res Export**: 
    - **96 kHz / 24-bit** wurde als neues Standard-Mastering-Format hinzugefügt.
    - **96 kHz / 32-bit float** ist nun klarer beschriftet und voll funktionsfähig.
- **Qualitätssicherung**: Ein kritischer Bug wurde behoben, der alle Exporte im "Originalformat" fälschlicherweise auf 16-Bit reduzierte. Alle WAV/AIFF Exporte erfolgen nun standardmäßig in **24-Bit PCM**.

## 🛠 Fixes & Verbesserungen
- **Audio-Präzision**: Bessere Behandlung von Headroom und Clipping-Schutz während des Match-Vorgangs.
- **i18n**: Neue Übersetzungen für alle High-Res Formate in Deutsch und Englisch.
- **LRA-Target**: Das Standard-LRA (Loudness Range) Target wurde auf 20.0 erhöht, um musikalische Dynamik unangetastet zu lassen.

---
**Funky Moose Release Forge** - *Stay Funky, Release Safe.*
