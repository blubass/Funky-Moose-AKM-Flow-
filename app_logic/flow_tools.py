from app_logic.text_utils import clean_text as _clean_text


BATCH_STATUSES = {"in_progress", "ready"}
DEFAULT_COPY_STAGE = "title"
EMPTY_FLOW_TITLE = "Keine offenen Meldungen"
EMPTY_FLOW_META = "Importiere Excel oder lege neue Werke an."
EMPTY_COPY_LABEL = "Titel kopieren"


def filter_batch_entries(entries):
    return [item for item in (entries or []) if item.get("status") in BATCH_STATUSES]


def clamp_flow_index(index, total):
    if total <= 0:
        return 0

    try:
        numeric_index = int(index)
    except Exception:
        numeric_index = 0
    return max(0, min(numeric_index, total - 1))


def find_flow_index_by_title(entries, title):
    wanted = _clean_text(title)
    if not wanted:
        return None

    for index, item in enumerate(entries or []):
        if _clean_text(item.get("title")) == wanted:
            return index
    return None


def resolve_flow_index(entries, current_index=0, previous_title=None, preferred_index=None):
    total = len(entries or [])
    if total <= 0:
        return 0

    matched_index = find_flow_index_by_title(entries, previous_title)
    if matched_index is not None:
        return matched_index

    if preferred_index is not None:
        return clamp_flow_index(preferred_index, total)

    return clamp_flow_index(current_index, total)


def current_flow_item(entries, index):
    if not entries:
        return None, 0

    resolved_index = clamp_flow_index(index, len(entries))
    return entries[resolved_index], resolved_index


def build_flow_meta_text(item):
    if not item:
        return EMPTY_FLOW_META

    parts = []
    composer = _clean_text(item.get("composer"))
    duration = _clean_text(item.get("duration"))
    production = _clean_text(item.get("production"))
    year = _clean_text(item.get("year"))

    if composer:
        parts.append(f"Komponist: {composer}")
    if duration:
        parts.append(f"Dauer: {duration}")
    if production:
        parts.append(f"Produktion: {production}")
    if year:
        parts.append(f"Jahr: {year}")

    return "   ".join(parts) if parts else "Keine Zusatzdaten"


def build_flow_progress(index, total):
    if total <= 0:
        return "0 / 0", 0

    resolved_index = clamp_flow_index(index, total)
    current = resolved_index + 1
    return f"{current} / {total}", (current / total) * 100


def build_copy_button_label(item, copy_stage):
    if item and copy_stage == "duration" and _clean_text(item.get("duration")):
        return "Dauer kopieren"
    return EMPTY_COPY_LABEL


def build_flow_queue_counts(entries):
    counts = {"in_progress": 0, "ready": 0}
    for item in entries or []:
        status = item.get("status")
        if status in counts:
            counts[status] += 1
    return counts


def build_flow_status_text(entries, flow_state):
    if not flow_state.get("has_item"):
        return "Keine offenen Batch-Werke"

    total = len(entries or [])
    return f"{flow_state.get('progress_text', '0 / 0')} im Fokus | {flow_state.get('current_title') or '—'}"


def build_flow_hint_text(entries, flow_state, copy_stage):
    if not flow_state.get("has_item"):
        return "Importiere Excel oder lege neue Werke an, dann füllt sich die Queue automatisch."

    item = flow_state.get("item") or {}
    has_duration = bool(_clean_text(item.get("duration")))
    if copy_stage == "duration" and has_duration:
        return "Titel ist kopiert. Jetzt kannst du die Dauer übernehmen oder direkt als gemeldet markieren."
    if has_duration:
        return "Starte mit dem Titel. Danach springt der Copy-Button automatisch auf die Dauer."
    return "Dieses Werk hat noch keine Dauer. Du kannst direkt melden oder zum nächsten offenen Titel gehen."


def build_flow_meta_summary(entries):
    counts = build_flow_queue_counts(entries)
    total = len(entries or [])
    return (
        f"In Arbeit: {counts['in_progress']}"
        f"   •   Bereit: {counts['ready']}"
        f"   •   Queue: {total}"
    )


def resolve_copy_action(item, copy_stage):
    if not item:
        return {
            "value": "",
            "copied_label": "Titel",
            "next_stage": DEFAULT_COPY_STAGE,
            "advance_after_copy": False,
        }

    if copy_stage == "duration":
        duration = _clean_text(item.get("duration"))
        if duration:
            return {
                "value": duration,
                "copied_label": "Dauer",
                "next_stage": DEFAULT_COPY_STAGE,
                "advance_after_copy": True,
            }

    next_stage = "duration" if _clean_text(item.get("duration")) else DEFAULT_COPY_STAGE
    return {
        "value": _clean_text(item.get("title")),
        "copied_label": "Titel",
        "next_stage": next_stage,
        "advance_after_copy": next_stage == DEFAULT_COPY_STAGE,
    }


def build_flow_state(entries, index, copy_stage):
    item, resolved_index = current_flow_item(entries, index)
    total = len(entries or [])

    if not item:
        progress_text, progress_value = build_flow_progress(0, 0)
        return {
            "has_item": False,
            "has_duration": False,
            "item": None,
            "resolved_index": 0,
            "current_title": None,
            "title_text": EMPTY_FLOW_TITLE,
            "meta_text": EMPTY_FLOW_META,
            "progress_text": progress_text,
            "progress_value": progress_value,
            "copy_button_label": EMPTY_COPY_LABEL,
        }

    progress_text, progress_value = build_flow_progress(resolved_index, total)
    return {
        "has_item": True,
        "has_duration": bool(_clean_text(item.get("duration"))),
        "item": item,
        "resolved_index": resolved_index,
        "current_title": _clean_text(item.get("title")) or None,
        "title_text": _clean_text(item.get("title")) or "—",
        "meta_text": build_flow_meta_text(item),
        "progress_text": progress_text,
        "progress_value": progress_value,
        "copy_button_label": build_copy_button_label(item, copy_stage),
    }


def next_flow_index(index, total):
    if total <= 0:
        return 0
    return (clamp_flow_index(index, total) + 1) % total


def can_open_in_batch(item):
    return (item or {}).get("status") in BATCH_STATUSES
