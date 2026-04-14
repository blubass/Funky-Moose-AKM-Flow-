import os
from app_logic import i18n

from app_ui import release_view_tools


FRIENDLY_LAYOUT_NAMES = {
    "manual": "Manual",
    "bottom": "Bottom Band",
    "topleft": "Top Left Card",
    "center": "Center Band",
}
LAYOUT_HINTS = {
    "manual": i18n._t("cov_hint_direction"),
    "bottom": i18n._t("cov_hint_direction_bottom", default="Bottom Band legt ein dunkles Fussband an und zentriert den Textblock fuer Release-Cover."),
    "topleft": i18n._t("cov_hint_direction_topleft", default="Top Left Card setzt eine Typo-Karte oben links mit Akzentkante und mehr Editorial-Vibe."),
    "center": i18n._t("cov_hint_direction_center", default="Center Band baut einen horizontalen Mittelstreifen mit klarer, symmetrischer Titelbuehne."),
}
SUPPORTED_ARTWORK_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".webp",
}


def friendly_layout_name(layout_key):
    return FRIENDLY_LAYOUT_NAMES.get(layout_key, FRIENDLY_LAYOUT_NAMES["manual"])


def normalize_cover_layout(value):
    raw = (value or "manual").strip().lower()
    normalized = raw.replace("_", "").replace("-", "").replace(" ", "")
    if normalized in {"bottom", "center", "topleft"}:
        return normalized
    return "manual"


def format_cover_text(text, case_mode):
    value = (text or "").strip()
    if case_mode == "uppercase":
        return value.upper()
    return value


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def is_supported_artwork_path(path, is_file_fn=os.path.isfile):
    normalized = (path or "").strip()
    if not normalized or not is_file_fn(normalized):
        return False
    return os.path.splitext(normalized)[1].lower() in SUPPORTED_ARTWORK_EXTENSIONS


def first_supported_artwork_path(paths, is_file_fn=os.path.isfile):
    for path in paths or []:
        normalized = (path or "").strip()
        if is_supported_artwork_path(normalized, is_file_fn=is_file_fn):
            return normalized
    return ""


def resolve_release_cover_path(release_tab=None, release_state=None):
    if release_tab is not None and hasattr(release_tab, "get_form_value"):
        return (release_tab.get_form_value("cover_path") or "").strip()
    return ((release_state or {}).get("cover_path") or "").strip()


def build_cover_render_options(
    bg_color,
    accent_color,
    style_value,
    size_mode_value,
    overlay_value,
    offset_value,
):
    return {
        "bg_color": (bg_color or "").strip() or "#181818",
        "accent_color": (accent_color or "").strip() or "#ff9a3c",
        "style": release_view_tools.selected_release_cover_style(style_value),
        "size_mode": release_view_tools.selected_release_cover_size(size_mode_value),
        "overlay": release_view_tools.selected_release_cover_overlay(overlay_value),
        "offset": release_view_tools.selected_release_cover_offset(offset_value),
    }


def build_cover_dashboard_state(
    *,
    layout_value,
    style_value,
    size_mode_value,
    overlay_value,
    offset_value,
    preview_height,
    artwork_path,
    artwork_meta,
    current_image_size=None,
    preview_dimensions=None,
    is_rendering=False,
    last_preview_error="",
):
    layout = normalize_cover_layout(layout_value)
    style = release_view_tools.selected_release_cover_style(style_value)
    size_mode = release_view_tools.selected_release_cover_size(size_mode_value)
    overlay = release_view_tools.selected_release_cover_overlay(overlay_value)
    offset = release_view_tools.selected_release_cover_offset(offset_value)
    layout_label = friendly_layout_name(layout)
    artwork_name = os.path.basename(artwork_path) if artwork_path else i18n._t("ash_radar_context_empty").split("|")[0].strip().lower()

    if not artwork_path or not os.path.exists(artwork_path):
        status_text = i18n._t("cov_radar_empty")
    elif last_preview_error:
        status_text = i18n._t("cov_status_error")
    elif is_rendering:
        status_text = i18n._t("cov_status_rendering", layout=layout_label)
    elif layout == "manual":
        status_text = i18n._t("cov_status_ready", layout="Manual")
    else:
        status_text = i18n._t("cov_status_ready", layout=layout_label)

    meta_text = i18n._t("cov_radar_context", layout=layout_label, style=style, zoom=preview_height)

    if current_image_size is not None:
        render_w, render_h = current_image_size
        info_text = f"Master: {artwork_name} | Render: {render_w}x{render_h}"
    elif is_rendering:
        info_text = f"Master: {artwork_name} | Render: arbeitet" # Keep working/Render: arbeitet for now or add to i18n
    elif last_preview_error:
        info_text = f"Master: {artwork_name} | Render: Fehler"
    else:
        info_text = "Master: keiner | Render: wartet"

    if preview_dimensions:
        info_text += f" | Stage: {preview_dimensions[0]}x{preview_dimensions[1]}"

    hint_text = LAYOUT_HINTS.get(layout, LAYOUT_HINTS["manual"])
    if last_preview_error:
        hint_text = f"{hint_text} Letzter Fehler: {last_preview_error}"

    if not artwork_path or not os.path.exists(artwork_path):
        asset_name = i18n._t("cov_radar_empty")
        asset_meta = i18n._t("cov_hint_preview")
        asset_path = i18n._t("cov_hint_asset")
    else:
        dims = ""
        if artwork_meta and artwork_meta.get("dimensions"):
            dims = (
                f"{artwork_meta['dimensions'][0]}x"
                f"{artwork_meta['dimensions'][1]} px"
            )
        size_text = artwork_meta.get("size_text", "") if artwork_meta else ""
        ext = artwork_meta.get("ext", "Datei") if artwork_meta else "Datei"
        meta_parts = [part for part in (dims, size_text, ext) if part]
        asset_name = artwork_name
        asset_meta = " | ".join(meta_parts) if meta_parts else "Master-Artwork geladen"
        asset_path = artwork_path

    return {
        "status_text": status_text,
        "meta_text": meta_text,
        "info_text": info_text,
        "hint_text": hint_text,
        "asset_name": asset_name,
        "asset_meta": asset_meta,
        "asset_path": asset_path,
    }
