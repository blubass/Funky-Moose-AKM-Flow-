import os


DEFAULT_COVER_FORMATS = ["square", "portrait", "landscape"]
DEFAULT_COVER_LAYOUTS = ["bottom", "topleft", "center"]
DEFAULT_COVER_STYLE = "clean"
DEFAULT_COVER_SIZE = "medium"
DEFAULT_COVER_OFFSET = "normal"
DEFAULT_COVER_OVERLAY = "medium"


def release_cover_output_dir(export_dir, cover_path):
    export_dir = (export_dir or "").strip()
    cover_path = (cover_path or "").strip()

    if export_dir:
        return os.path.join(export_dir, "cover_previews")
    if cover_path:
        return os.path.join(os.path.dirname(cover_path), "cover_previews")
    return ""


def selected_release_cover_formats(value):
    value = (value or "").strip()
    if value == "all":
        return list(DEFAULT_COVER_FORMATS)
    if value in {"square", "portrait", "landscape"}:
        return [value]
    return list(DEFAULT_COVER_FORMATS)


def selected_release_cover_layouts(layout_map):
    selected = []
    for key in DEFAULT_COVER_LAYOUTS:
        raw = layout_map.get(key)
        is_enabled = bool(raw.get()) if hasattr(raw, "get") else bool(raw)
        if is_enabled:
            selected.append(key)
    return selected or list(DEFAULT_COVER_LAYOUTS)


def selected_release_cover_style(value):
    value = (value or "").strip()
    if value in {"clean", "bold", "cinematic"}:
        return value
    return DEFAULT_COVER_STYLE


def selected_release_cover_size(value):
    value = (value or "").strip()
    if value in {"small", "medium", "large"}:
        return value
    return DEFAULT_COVER_SIZE


def selected_release_cover_offset(value):
    value = (value or "").strip()
    if value in {"high", "normal", "low"}:
        return value
    return DEFAULT_COVER_OFFSET


def selected_release_cover_overlay(value):
    value = (value or "").strip()
    if value in {"soft", "medium", "strong"}:
        return value
    return DEFAULT_COVER_OVERLAY


def build_release_track_row_label(index, item):
    details = []
    if item.get("duration"):
        details.append(item["duration"])
    if item.get("production"):
        details.append(item["production"])
    if item.get("year"):
        details.append(item["year"])
    if item.get("source"):
        details.append(item.get("source"))
    suffix = f" | {' | '.join(details)}" if details else ""
    return f"{index:02d}. {item.get('title', '')}{suffix}"


def build_release_source_counts(tracks):
    counts = {"Werk": 0, "Datei→Werk": 0, "Datei": 0}
    for item in tracks:
        source = item.get("source") or ""
        if source in counts:
            counts[source] += 1
    return counts


def build_release_action_hint(counts):
    return (
        f"Werk {counts['Werk']}  •  "
        f"Datei→Werk {counts['Datei→Werk']}  •  "
        f"Datei {counts['Datei']}"
    )


def build_release_status_text(track_count, cover_set, export_set, drop_enabled):
    drop_info = " | Drag&Drop aktiv" if drop_enabled else " | Drag&Drop aus"
    return (
        f"{track_count} Tracks im Release | "
        f"Cover: {'Ja' if cover_set else 'Nein'} | "
        f"Export-Ordner: {'Ja' if export_set else 'Nein'}"
        f"{drop_info}"
    )


def build_cover_preview_status_text(created_count, style_label, size_label, offset_label, overlay_label):
    return (
        f"Cover-Previews bereit: {created_count} Datei(en) "
        f"in cover_previews | Stil: {style_label} | Größe: {size_label} "
        f"| Position: {offset_label} | Overlay: {overlay_label}"
    )
