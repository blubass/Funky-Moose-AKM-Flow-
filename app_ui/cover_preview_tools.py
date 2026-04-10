import os

from app_ui import cover_view_tools


MANUAL_TEXT_LAYER_SPECS = (
    ("artist", 60, 900, 1400),
    ("title", 140, 900, 1500),
    ("subtitle", 40, 900, 1600),
)


def safe_int(value, fallback):
    try:
        return int(float(value))
    except Exception:
        return fallback


def safe_float(value, fallback):
    try:
        return float(value)
    except Exception:
        return fallback


def coerce_bool(value):
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    return bool(value)


def compute_preview_stage_height(preview_height, min_preview_height=220, min_stage_height=280, padding=20):
    target_height = max(min_preview_height, safe_int(preview_height, min_preview_height))
    return max(min_stage_height, target_height + padding)


def compute_preview_fit_size(image_size, stage_width, stage_height, target_height, padding=8):
    width, height = image_size
    stage_w = max(1, safe_int(stage_width, 1) - padding)
    stage_h = max(1, safe_int(stage_height, 1) - padding)
    max_height = max(1, safe_int(target_height, 1))

    fit_ratio = min(stage_w / width, stage_h / height, max_height / height)
    fit_ratio = max(fit_ratio, 1 / max(width, height))
    return (
        max(1, int(width * fit_ratio)),
        max(1, int(height * fit_ratio)),
    )


def read_artwork_meta(path, is_file_fn=os.path.isfile, getsize_fn=os.path.getsize, image_open=None):
    normalized = (path or "").strip()
    if not normalized or not is_file_fn(normalized):
        return None

    if image_open is None:
        from PIL import Image

        image_open = Image.open

    details = {
        "ext": os.path.splitext(normalized)[1].replace(".", "").upper() or "Datei",
        "size_text": "",
        "dimensions": None,
    }
    try:
        size_bytes = getsize_fn(normalized)
        details["size_text"] = cover_view_tools.format_file_size(size_bytes)
    except Exception:
        details["size_text"] = ""
    try:
        with image_open(normalized) as image:
            details["dimensions"] = image.size
    except Exception:
        details["dimensions"] = None
    return details


def resolve_preview_refresh_state(artwork_path, exists_fn=os.path.exists):
    normalized = (artwork_path or "").strip()
    return {
        "artwork_path": normalized,
        "can_render": bool(normalized and exists_fn(normalized)),
    }


def resolve_preview_zoom_action(
    *,
    is_rendering,
    has_current_image,
    artwork_path,
    exists_fn=os.path.exists,
):
    if is_rendering:
        return {
            "action": "busy",
            "toast_message": "VORSCHAU WIRD GERADE AKTUALISIERT",
        }

    if has_current_image:
        return {
            "action": "open",
            "toast_message": "",
        }

    refresh_state = resolve_preview_refresh_state(artwork_path, exists_fn=exists_fn)
    if not refresh_state["can_render"]:
        return {
            "action": "missing",
            "toast_message": "KEIN COVER FUER ZOOM GELADEN",
        }

    return {
        "action": "render_first",
        "toast_message": "VORSCHAU WIRD ZUERST GERENDERT",
    }


def build_manual_font_configs(state, target_size):
    values = state or {}
    scale = target_size / 1800.0
    configs = []

    for layer_name, default_size, default_x, default_y in MANUAL_TEXT_LAYER_SPECS:
        configs.append(
            {
                "text": cover_view_tools.format_cover_text(
                    values.get(layer_name),
                    values.get(f"{layer_name}_case"),
                ),
                "size": max(12, int(safe_int(values.get(f"{layer_name}_size"), default_size) * scale)),
                "font": values.get(f"{layer_name}_font") or "",
                "bold": coerce_bool(values.get(f"{layer_name}_bold")),
                "color": values.get(f"{layer_name}_color") or "",
                "x": int(safe_int(values.get(f"{layer_name}_x"), default_x) * scale),
                "y": int(safe_int(values.get(f"{layer_name}_y"), default_y) * scale),
            }
        )

    return configs


def build_cover_render_payload(state, target_size):
    values = state or {}
    subtitle = cover_view_tools.format_cover_text(
        values.get("subtitle"),
        values.get("subtitle_case"),
    ) or None

    return {
        "artwork_path": (values.get("artwork_path") or "").strip(),
        "zoom": safe_float(values.get("zoom"), 1.0),
        "layout": cover_view_tools.normalize_cover_layout(values.get("layout")),
        "options": cover_view_tools.build_cover_render_options(
            values.get("bg_color"),
            values.get("accent_color"),
            values.get("style"),
            values.get("size_mode"),
            values.get("overlay"),
            values.get("offset"),
        ),
        "title": cover_view_tools.format_cover_text(
            values.get("title"),
            values.get("title_case"),
        ),
        "artist": cover_view_tools.format_cover_text(
            values.get("artist"),
            values.get("artist_case"),
        ),
        "subtitle": subtitle,
        "font_configs": build_manual_font_configs(values, target_size),
    }
