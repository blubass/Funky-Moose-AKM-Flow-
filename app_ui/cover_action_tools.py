import os

from app_ui import cover_view_tools


def analyze_cover_drop_files(
    files,
    find_supported_artwork_path_fn=cover_view_tools.first_supported_artwork_path,
):
    items = list(files or [])
    target_path = find_supported_artwork_path_fn(items)
    if target_path:
        return {
            "target_path": target_path,
            "ignored_message": "",
        }
    if items:
        return {
            "target_path": "",
            "ignored_message": (
                f"Artwork-DnD ignoriert: kein gueltiges Bild in {len(items)} Datei(en)."
            ),
        }
    return {
        "target_path": "",
        "ignored_message": "",
    }


def prepare_cover_load(path, is_supported_path_fn=cover_view_tools.is_supported_artwork_path):
    normalized = (path or "").strip()
    if not is_supported_path_fn(normalized):
        return {
            "ok": False,
            "error_message": "ARTWORK NICHT GEFUNDEN",
        }
    return {
        "ok": True,
        "path": normalized,
        "log_message": f"Cover geladen: {os.path.basename(normalized)}",
    }


def prepare_cover_assignment(path, exists_fn=os.path.exists):
    normalized = (path or "").strip()
    if not normalized or not exists_fn(normalized):
        return {
            "ok": False,
            "error_message": "KEIN ARTWORK ZUM ZUWEISEN",
        }
    return {
        "ok": True,
        "path": normalized,
    }


def build_cover_export_request(path, title, exists_fn=os.path.exists):
    normalized = (path or "").strip()
    if not normalized or not exists_fn(normalized):
        return {
            "ok": False,
            "error_message": "KEIN MASTER-ARTWORK GELADEN",
        }
    return {
        "ok": True,
        "path": normalized,
        "dialog_options": {
            "defaultextension": ".jpg",
            "filetypes": [("JPEG", "*.jpg"), ("PNG", "*.png")],
            "initialdir": os.path.dirname(normalized),
            "initialfile": f"Cover_{(title or '').replace(' ', '_')}.jpg",
        },
    }


def build_cover_export_success_state(path):
    normalized = (path or "").strip()
    return {
        "log_message": f"Cover exportiert: {os.path.basename(normalized)}",
        "toast_message": "COVER ERFOLGREICH EXPORTIERT",
    }
