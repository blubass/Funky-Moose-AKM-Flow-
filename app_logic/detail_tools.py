from app_logic.text_utils import clean_mapping_values, clean_text as _clean_text


DETAIL_FIELD_LABELS = [
    ("title", "Titel"),
    ("duration", "Dauer"),
    ("composer", "Komponist"),
    ("production", "Produktion"),
    ("year", "Jahr"),
    ("audio_path", "Audio-Pfad"),
]
DETAIL_FIELD_KEYS = tuple(key for key, _label in DETAIL_FIELD_LABELS)
DEFAULT_DETAIL_STATUS = "in_progress"


def empty_detail_item(title=""):
    return {
        "title": _clean_text(title),
        "status": DEFAULT_DETAIL_STATUS,
        "duration": "",
        "composer": "",
        "production": "",
        "year": "",
        "audio_path": "",
        "instrumental": False,
        "notes": "",
        "tags": [],
    }


def find_detail_item(entries, title):
    wanted = _clean_text(title)
    if not wanted or entries is None:
        return None

    for item in entries:
        if _clean_text(item.get("title")) == wanted:
            return item
    return None


def detail_form_state_from_item(item=None):
    source = item or {}
    values = clean_mapping_values(source, DETAIL_FIELD_KEYS)

    raw_tags = source.get("tags") or []
    if isinstance(raw_tags, (str, bytes)):
        raw_tags = [raw_tags]

    tags = []
    for tag in raw_tags:
        text = _clean_text(tag)
        if text:
            tags.append(text)

    title = values.get("title") or None
    return {
        "original_title": title,
        "current_title": title,
        "values": values,
        "instrumental": bool(source.get("instrumental")),
        "status": source.get("status") or DEFAULT_DETAIL_STATUS,
        "tags_text": ", ".join(tags),
        "notes": _clean_text(source.get("notes")),
    }


def parse_detail_tags(tags_text):
    return [_clean_text(part) for part in (tags_text or "").split(",") if _clean_text(part)]


def build_detail_updates(detail_values, tags_text, notes_text, status, instrumental):
    updates = clean_mapping_values(detail_values, DETAIL_FIELD_KEYS)
    updates["status"] = status or DEFAULT_DETAIL_STATUS
    updates["instrumental"] = bool(instrumental)
    updates["notes"] = _clean_text(notes_text)
    updates["tags"] = parse_detail_tags(tags_text)
    return updates


def resolve_original_title(original_title, title, existing_entries=None):
    resolved = _clean_text(original_title)
    if resolved:
        return resolved

    candidate = _clean_text(title)
    if not candidate:
        return ""

    existing = find_detail_item(existing_entries, candidate)
    if existing:
        return _clean_text(existing.get("title")) or candidate
    return candidate


def resolve_saved_detail_state(result, fallback_title, fallback_status):
    if isinstance(result, dict):
        return (
            result.get("title", fallback_title),
            result.get("status", fallback_status),
        )
    return fallback_title, fallback_status
