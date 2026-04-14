import os


def _format_missing_fields(missing_fields):
    if not missing_fields:
        return ""
    if len(missing_fields) == 1:
        return missing_fields[0]
    if len(missing_fields) == 2:
        return f"{missing_fields[0]} und {missing_fields[1]}"
    return f"{', '.join(missing_fields[:-1])} und {missing_fields[-1]}"


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
    missing_fields = []
    if composer:
        context_parts.append(f"Komponist: {composer}")
    elif title or audio_path:
        missing_fields.append("Komponist")
    if duration:
        context_parts.append(f"Dauer: {duration}")
    elif title or audio_path:
        missing_fields.append("Dauer")
    if year:
        context_parts.append(f"Jahr: {year}")
    elif title or audio_path:
        missing_fields.append("Jahr")
    context_parts.append(f"Instrumental: {'Ja' if instrumental else 'Nein'}")

    if audio_path:
        audio_name = os.path.basename(audio_path)
        if exists_fn(audio_path):
            context_parts.insert(0, f"Audio: {audio_name}")
        else:
            context_parts.insert(0, f"Audio fehlt: {audio_name}")
    else:
        context_parts.insert(0, "Audio: keines")

    if missing_fields:
        context_parts.append(f"Fehlt: {_format_missing_fields(missing_fields)}")

    if not title and not audio_path:
        hint = "Wähle ein bestehendes Werk oder ziehe eine Audiodatei hier hinein, damit Titel und Dauer schneller zusammenfinden."
    elif audio_path and not exists_fn(audio_path):
        hint = "Der gesetzte Audio-Pfad existiert nicht mehr. Prüfe die Datei oder verknüpfe das Werk neu."
    elif title and not audio_path:
        hint = "Die Metadaten stehen schon. Wenn du Audio verknüpfst, kann die App Dauer und Pfad direkt mitziehen."
    elif audio_path and not title:
        hint = "Audio ist da – gib dem Werk jetzt noch Titel, Credits und Status, dann ist der Datensatz rund."
    elif missing_fields:
        hint = f"Werk und Audio sind verbunden. Ergänze noch {_format_missing_fields(missing_fields)}, dann wirkt der Datensatz vollständig."
    else:
        hint = "Werk und Audio sind verbunden. Jetzt noch Notizen, Tags oder letzte Status-Checks nachziehen und sauber speichern."

    return {
        "headline": headline,
        "context_text": "   •   ".join(context_parts),
        "hint_text": hint,
    }
