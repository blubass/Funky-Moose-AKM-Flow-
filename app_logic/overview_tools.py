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


def build_overview_filter_counts(entries):
    return {
        "all": len(entries),
        "open": sum(1 for item in entries if item.get("status") != "confirmed"),
        "in_progress": sum(1 for item in entries if item.get("status") == "in_progress"),
        "ready": sum(1 for item in entries if item.get("status") == "ready"),
        "submitted": sum(1 for item in entries if item.get("status") == "submitted"),
        "confirmed": sum(1 for item in entries if item.get("status") == "confirmed"),
    }


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
            " ".join(item.get("tags", [])),
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

    suffix = f" | {' | '.join(details)}" if details else ""
    return f"{item['title']}{suffix}   •   {status_label}"


def _sort_value(item, sort_key, sort_desc):
    if sort_key == "status":
        return STATUS_SORT_ORDER.get(item.get("status", ""), 999)

    if sort_key == "year":
        year = str(item.get("year", "")).strip()
        if year.isdigit():
            return int(year)
        return -999999 if sort_desc else 999999

    if sort_key == "last_change":
        return item.get("last_change", "") or item.get("date", "")

    return str(item.get("title", "")).lower()
