ASSISTANT_STATUS_ACTIONS = [
    ("Bereit", "ready"),
    ("Gemeldet", "submitted"),
    ("Bestätigt", "confirmed"),
]


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_assistant_title(value):
    return _clean_text(value)


def build_import_log_messages(imported_items):
    items = list(imported_items or [])
    if not items:
        return ["Excel-Import: keine verwertbaren Titel gefunden."]

    messages = [f"Excel-Import abgeschlossen: {len(items)} Einträge"]
    for item in items:
        marker = {"added": "+", "updated": "~", "unchanged": "="}.get(
            item.get("action"),
            "-",
        )
        details = []
        duration = _clean_text(item.get("duration"))
        composer = _clean_text(item.get("composer"))
        if duration:
            details.append(duration)
        if composer:
            details.append(composer)
        info = f" ({' | '.join(details)})" if details else ""
        messages.append(f"  {marker} {_clean_text(item.get('title'))}{info}")
    return messages


def build_add_result_message(title, ok, result):
    if ok:
        return f"Neu angelegt: {title}"

    messages = {
        "already_exists": f"Schon vorhanden: {title}",
        "empty_title": "Titel darf nicht leer sein.",
    }
    return messages.get(result, str(result))


def build_status_result_message(title, ok, status_text, result, status_value):
    if ok:
        return f"Status gesetzt: {title} -> {status_text}"

    messages = {
        "not_found": f"Nicht gefunden: {title}",
        "invalid_status": f"Ungültiger Status: {status_value}",
    }
    return messages.get(result, str(result))


def build_copy_preview_message(text):
    return f"Zwischenablage:\n{text}"


def build_continue_work_message(title, status_text):
    return f"Weiter bei: {title} ({status_text})"


def build_loudness_tab_open_state(loudness_available):
    if loudness_available:
        status = "Lautheit-Tab offen. Dateien wählen oder Analyse starten."
    else:
        status = "Lautheit-Tab offen. Hinweis: loudness_tools.py konnte nicht geladen werden."
    return {
        "status_text": status,
        "hint_text": "Dateien laden oder direkt Werke aus der aktuellen Übersicht übernehmen.",
        "log_message": "Lautheit-Tab wurde geöffnet.",
    }


def build_use_selected_title_message(title):
    return f"In Eingabe übernommen: {title}"
