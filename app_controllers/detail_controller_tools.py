def populate_detail_view(detail_vars, item):
    for key, var in (detail_vars or {}).items():
        var.set(str((item or {}).get(key, "")))


def build_detail_text_state(item):
    raw_tags = (item or {}).get("tags", [])
    tags_text = ", ".join(raw_tags) if isinstance(raw_tags, list) else str(raw_tags)
    return {
        "notes_text": (item or {}).get("notes", ""),
        "tags_text": tags_text,
        "instrumental": bool((item or {}).get("instrumental", False)),
        "status": (item or {}).get("status", "in_progress"),
        "title": (item or {}).get("title", ""),
    }
