import os


def build_detail_radar_state(
    *,
    title="",
    audio_path="",
    composer="",
    duration="",
    year="",
    instrumental=False,
    status_text="—",
    exists_fn=os.path.exists,
):
    title = (title or "").strip()
    audio_path = (audio_path or "").strip()
    composer = (composer or "").strip()
    duration = (duration or "").strip()
    year = (year or "").strip()
    status_text = (status_text or "").strip() or "—"

    if title:
        headline = f"{title} | Status: {status_text}"
    else:
        headline = f"Noch kein Werk geladen | Status: {status_text}"

    context_parts = []
    if composer:
        context_parts.append(f"Komponist: {composer}")
    if duration:
        context_parts.append(f"Dauer: {duration}")
    if year:
        context_parts.append(f"Jahr: {year}")
    context_parts.append(f"Instrumental: {'Ja' if instrumental else 'Nein'}")

    if audio_path:
        audio_name = os.path.basename(audio_path)
        if exists_fn(audio_path):
            context_parts.insert(0, f"Audio: {audio_name}")
        else:
            context_parts.insert(0, f"Audio fehlt: {audio_name}")
    else:
        context_parts.insert(0, "Audio: keines")

    if not title and not audio_path:
        hint = "Wähle ein bestehendes Werk oder ziehe eine Audiodatei hier hinein, damit Titel und Dauer schneller zusammenfinden."
    elif audio_path and not exists_fn(audio_path):
        hint = "Der gesetzte Audio-Pfad existiert nicht mehr. Prüfe die Datei oder verknüpfe das Werk neu."
    elif title and not audio_path:
        hint = "Die Metadaten stehen schon. Wenn du Audio verknüpfst, kann die App Dauer und Pfad direkt mitziehen."
    elif audio_path and not title:
        hint = "Audio ist da – gib dem Werk jetzt noch Titel, Credits und Status, dann ist der Datensatz rund."
    else:
        hint = "Werk und Audio sind verbunden. Jetzt noch Notizen, Tags oder Status nachziehen und sauber speichern."

    return {
        "headline": headline,
        "context_text": "   •   ".join(context_parts),
        "hint_text": hint,
    }
