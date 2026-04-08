STATUS_SORT_ORDER = {
    "in_progress": 0,
    "ready": 1,
    "submitted": 2,
    "confirmed": 3,
}

SORT_LABELS = {
    "title": "Titel",
    "status": "Status",
    "year": "Jahr",
    "last_change": "Änderung",
}


def build_dashboard_stats(entries):
    total = len(entries)
    confirmed = sum(1 for item in entries if item.get("status") == "confirmed")
    ready = sum(1 for item in entries if item.get("status") == "ready")
    submitted = sum(1 for item in entries if item.get("status") == "submitted")
    in_progress = sum(1 for item in entries if item.get("status") == "in_progress")
    instrumental = sum(1 for item in entries if item.get("instrumental"))
    with_production = sum(1 for item in entries if item.get("production"))
    with_notes = sum(1 for item in entries if item.get("notes"))
    return {
        "total": total,
        "open": total - confirmed,
        "ready": ready,
        "submitted": submitted,
        "in_progress": in_progress,
        "confirmed": confirmed,
        "instrumental": instrumental,
        "with_production": with_production,
        "with_notes": with_notes,
    }


def build_dashboard_chip_counts(stats):
    return {
        "open": stats.get("open", 0),
        "in_progress": stats.get("in_progress", 0),
        "ready": stats.get("ready", 0),
        "submitted": stats.get("submitted", 0),
        "confirmed": stats.get("confirmed", 0),
    }


def build_dashboard_completion_percent(stats):
    total = stats.get("total", 0)
    confirmed = stats.get("confirmed", 0)
    if total <= 0:
        return 0
    return int(round((confirmed / total) * 100))


def build_dashboard_status_text(stats):
    total = stats.get("total", 0)
    if total <= 0:
        return "Noch keine Werke im Katalog"

    return (
        f"{total} Werke | "
        f"{build_dashboard_completion_percent(stats)}% bestätigt | "
        f"{stats.get('ready', 0)} bereit | "
        f"{stats.get('in_progress', 0)} in Arbeit"
    )


def build_dashboard_focus_text(stats):
    total = stats.get("total", 0)
    if total <= 0:
        return "Importiere ein Werk oder lege direkt einen neuen Titel an, um loszulegen."

    in_progress = stats.get("in_progress", 0)
    ready = stats.get("ready", 0)
    submitted = stats.get("submitted", 0)
    confirmed = stats.get("confirmed", 0)

    if in_progress:
        return f"Gerade am stärksten unter Spannung: {in_progress} Werk(e) brauchen noch Feinschliff."
    if ready:
        return f"Nächster sauberer Move: {ready} Werk(e) sind bereit für die Meldung."
    if submitted:
        return f"{submitted} Werk(e) warten auf Bestätigung – ideal zum Nachverfolgen."
    if confirmed == total:
        return "Alles bestätigt. Perfekter Moment, um neues Material anzulegen."
    return "Der Katalog ist in Bewegung – ein Blick in die Übersicht bringt dich direkt zum nächsten Schritt."


def build_dashboard_meta_text(stats):
    return (
        f"Mit Produktion: {stats.get('with_production', 0)}"
        f"   •   Mit Notizen: {stats.get('with_notes', 0)}"
        f"   •   Instrumental: {stats.get('instrumental', 0)}"
    )


def build_overview_status_text(result_count, total_count):
    if total_count <= 0:
        return "Noch keine Werke im Katalog"
    if result_count <= 0:
        return "Keine Treffer im aktuellen Filter"
    return f"{result_count} von {total_count} Werken sichtbar"


def build_overview_hint_text(result_count, total_count, status_filter="all", query=""):
    normalized_query = (query or "").strip()
    if total_count <= 0:
        return "Lege neue Werke an oder importiere eine Excel-Datei, damit sich die Übersicht füllt."
    if result_count <= 0:
        if normalized_query:
            return f"Für \"{normalized_query}\" gibt es im aktuellen Filter keine Treffer. Suche oder Status einmal lockern."
        if status_filter != "all":
            return "Der aktuelle Statusfilter zeigt gerade nichts. Wechsle den Filter oder öffne wieder alle Werke."
        return "Gerade ist nichts sichtbar. Prüfe Suche und Sortierung."
    return "Details öffnen springt in den Datensatz. Audio Preview und Loudness übernehmen direkt die aktuelle Auswahl."


def build_overview_filter_counts(entries):
    counts = {"all": len(entries), "open": 0, "in_progress": 0, "ready": 0, "submitted": 0, "confirmed": 0}
    for item in entries:
        st = item.get("status")
        if st != "confirmed": counts["open"] += 1
        if st in counts: counts[st] += 1
    return counts


def filter_and_sort_entries(entries, query="", status_filter="all", sort_key="title", sort_desc=False):
    filtered_records = []
    normalized_query = (query or "").strip().lower()

    for item in entries:
        haystack_parts = [
            item.get("title", ""),
            item.get("duration", ""),
            item.get("composer", ""),
            item.get("production", ""),
            item.get("year", ""),
            item.get("notes", ""),
            item.get("status", ""),
            ", ".join(item.get("tags", []) if isinstance(item.get("tags"), list) else []),
        ]
        haystack = " ".join(str(part) for part in haystack_parts if part).lower()
        item_status = item.get("status", "")

        if status_filter == "open" and item_status == "confirmed":
            continue
        if status_filter not in {"all", "open"} and item_status != status_filter:
            continue
        if normalized_query and normalized_query not in haystack:
            continue

        filtered_records.append(item)

    filtered_records.sort(
        key=lambda item: _sort_value(item, sort_key, sort_desc),
        reverse=sort_desc,
    )
    return filtered_records


def build_overview_summary(result_count, status_filter="all", query="", sort_key="title", sort_desc=False, status_label=None, open_label="Offen"):
    summary_parts = [f"{result_count} Treffer"]

    if status_filter == "open":
        summary_parts.append(f"Status: {open_label}")
    elif status_filter != "all":
        summary_parts.append(f"Status: {status_label or status_filter}")

    normalized_query = (query or "").strip().lower()
    if normalized_query:
        summary_parts.append(f"Suche: {normalized_query}")

    direction = "absteigend" if sort_desc else "aufsteigend"
    summary_parts.append(
        f"Sortierung: {SORT_LABELS.get(sort_key, sort_key)} {direction}"
    )
    return "   •   ".join(summary_parts)


def format_overview_list_label(item, status_label):
    details = []
    if item.get("duration"):
        details.append(item["duration"])
    if item.get("composer"):
        details.append(item["composer"])
    if item.get("production"):
        details.append(item["production"])
    if item.get("year"):
        details.append(item["year"])

    # Green indicator for success states
    success_indicator = "● " if item.get("status") in ["ready", "submitted", "confirmed"] else ""
    
    suffix = f" | {' | '.join(details)}" if details else ""
    return f"{success_indicator}{item['title']}{suffix}   •   {status_label}"


def _sort_value(item, sort_key, sort_desc):
    if sort_key == "status":
        return STATUS_SORT_ORDER.get(item.get("status", ""), 999)

    if sort_key == "year":
        year = str(item.get("year", "")).strip()
        if year.isdigit():
            return int(year)
        return -999999 if sort_desc else 999999

    if sort_key == "last_change":
        return item.get("last_change") or item.get("date") or ""

    return str(item.get("title", "")).lower()
