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


def build_release_preflight_text(track_count, release_title, cover_set, export_set, counts):
    counts = counts or {"Werk": 0, "Datei→Werk": 0, "Datei": 0}
    blockers = []
    if track_count <= 0:
        blockers.append("Tracks fehlen")
    if not (release_title or "").strip():
        blockers.append("Release-Titel fehlt")
    if not cover_set:
        blockers.append("Cover fehlt")
    if not export_set:
        blockers.append("Export-Ordner fehlt")
    if counts.get("Datei", 0):
        blockers.append(f"{counts['Datei']} ohne Werk-Match")

    if blockers:
        return f"Preflight: {' • '.join(blockers)}"

    ready_parts = [f"{track_count} Tracks bereit"]
    if counts.get("Datei→Werk", 0):
        ready_parts.append(f"{counts['Datei→Werk']} gemappt")
    ready_parts.append("AKM-Flow bereit")
    if cover_set and export_set:
        ready_parts.append("Export bereit")
    return f"Preflight OK: {' • '.join(ready_parts)}"


def build_release_flow_hint(track_count, release_title, cover_set, export_set, counts):
    counts = counts or {"Werk": 0, "Datei→Werk": 0, "Datei": 0}
    if track_count <= 0:
        return "Ziehe Audiodateien in die Drop Zone. Gematchte Werke bringen Dauer, Produktion und Jahr direkt mit."

    if not (release_title or "").strip():
        return "Release-Titel fehlt noch. Danach kannst du direkt in AKM laden oder den Distro-Export starten."

    if counts.get("Datei", 0):
        source_hint = f"{counts['Datei']} Datei(en) sind noch ohne Werk-Match."
    elif counts.get("Datei→Werk", 0):
        source_hint = f"{counts['Datei→Werk']} Datei(en) wurden automatisch auf Werke gemappt."
    else:
        source_hint = "Alle Tracks kommen direkt aus vorhandenen Werken."

    if not export_set and not cover_set:
        return f"{source_hint} In AKM laden geht schon jetzt; für den Distro-Export fehlen noch Cover und Export-Ordner."
    if not export_set:
        return f"{source_hint} In AKM laden geht schon jetzt; für den Distro-Export fehlt noch der Export-Ordner."
    if not cover_set:
        return f"{source_hint} Export und AKM-Flow sind bereit, fürs Paket fehlt nur noch das Cover."
    return f"{source_hint} Export erstellt Paket, Excel und lädt die Titel danach direkt in Batch."


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


def build_release_selection_hint(track_count, selected_indices):
    selection = tuple(selected_indices or ())
    if track_count <= 0:
        return "Noch keine Tracks im Release. Ziehe Dateien hinein oder übernimm gematchte Werke."

    if not selection:
        return f"{track_count} Tracks bereit. Mehrfachauswahl ist möglich; Reihenfolge und Entfernen arbeiten auf die Auswahl."

    selected_count = len(selection)
    if selected_count > 1:
        return f"{selected_count} Tracks ausgewählt. Entfernen arbeitet auf die gesamte Auswahl."

    index = selection[0]
    actions = []
    if index > 0:
        actions.append("Nach oben")
    if index < track_count - 1:
        actions.append("Nach unten")
    actions.append("Entfernen")
    return f"1 Track ausgewählt. Verfügbar: {' • '.join(actions)}."
