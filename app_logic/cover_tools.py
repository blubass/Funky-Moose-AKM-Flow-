import os

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None
    ImageDraw = None
    ImageFont = None


COVER_PRESETS = {
    "square": (1800, 1800, "1:1"),
    "portrait": (1600, 2000, "4:5"),
    "landscape": (1920, 1080, "16:9"),
}


def have_pillow():
    return Image is not None and ImageDraw is not None and ImageFont is not None


def get_cover_presets():
    return dict(COVER_PRESETS)


def resize_cover_canvas(base_image, target_width, target_height):
    image = base_image.convert("RGBA")
    src_w, src_h = image.size
    if src_w <= 0 or src_h <= 0:
        return image

    scale = max(target_width / src_w, target_height / src_h)
    resized_w = max(1, int(round(src_w * scale)))
    resized_h = max(1, int(round(src_h * scale)))
    resized = image.resize((resized_w, resized_h), Image.LANCZOS)

    left = max(0, int((resized_w - target_width) / 2))
    top = max(0, int((resized_h - target_height) / 2))
    right = left + target_width
    bottom = top + target_height
    return resized.crop((left, top, right, bottom))


def release_cover_overlay_alpha(overlay, variant="default"):
    mapping = {
        "soft": {"default": 110, "card": 100, "line": 90},
        "medium": {"default": 150, "card": 145, "line": 120},
        "strong": {"default": 190, "card": 180, "line": 150},
    }
    current = mapping.get(overlay, mapping["medium"])
    return current.get(variant, current["default"])


def release_cover_vertical_shift(offset, height, variant="default"):
    if variant == "bottom":
        values = {
            "high": -max(12, int(height * 0.035)),
            "normal": 0,
            "low": max(12, int(height * 0.035)),
        }
    elif variant == "center":
        values = {
            "high": -max(16, int(height * 0.06)),
            "normal": 0,
            "low": max(16, int(height * 0.06)),
        }
    else:
        values = {
            "high": -max(8, int(height * 0.025)),
            "normal": 0,
            "low": max(8, int(height * 0.025)),
        }
    return values.get(offset, 0)


def get_release_cover_font(size, bold=False):
    if not have_pillow():
        return None

    if bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ]

    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue

    try:
        return ImageFont.load_default()
    except Exception:
        return None


def fit_release_cover_text(draw, text, max_width, start_size, min_size=18, bold=False):
    size = start_size
    while size >= min_size:
        font = get_release_cover_font(size, bold=bold)
        if font is None:
            return None
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            return font
        size -= 2
    return get_release_cover_font(min_size, bold=bold)


def draw_release_cover_text_block(
    draw,
    x,
    y,
    width,
    title,
    artist,
    title_size,
    artist_size,
    style="clean",
    size_mode="medium",
    align="center",
):
    size_factor_map = {
        "small": 0.88,
        "medium": 1.0,
        "large": 1.18,
    }
    size_factor = size_factor_map.get(size_mode, 1.0)
    title_size = max(18, int(title_size * size_factor))
    artist_size = max(14, int(artist_size * size_factor))

    title_bold = style in {"bold", "cinematic"}
    artist_bold = style == "bold"
    title_font = fit_release_cover_text(draw, title, width, title_size, min_size=22, bold=title_bold)
    artist_font = fit_release_cover_text(draw, artist, width, artist_size, min_size=16, bold=artist_bold)
    if title_font is None or artist_font is None:
        raise RuntimeError("Keine Schriftart für Cover-Rendering verfügbar.")

    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    artist_bbox = draw.textbbox((0, 0), artist, font=artist_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    artist_w = artist_bbox[2] - artist_bbox[0]
    artist_h = artist_bbox[3] - artist_bbox[1]

    if align == "left":
        tx_title = x
        tx_artist = x
    elif align == "right":
        tx_title = x + width - title_w
        tx_artist = x + width - artist_w
    else:
        tx_title = x + (width - title_w) / 2
        tx_artist = x + (width - artist_w) / 2

    if style == "bold":
        shadow_offset = 3
        title_fill = (255, 255, 255, 255)
        artist_fill = (255, 245, 230, 255)
        shadow_fill_title = (0, 0, 0, 210)
        shadow_fill_artist = (0, 0, 0, 190)
        extra_stroke = True
    elif style == "cinematic":
        shadow_offset = 4
        title_fill = (255, 248, 235, 255)
        artist_fill = (235, 235, 235, 255)
        shadow_fill_title = (0, 0, 0, 230)
        shadow_fill_artist = (0, 0, 0, 200)
        extra_stroke = True
    else:
        shadow_offset = 2
        title_fill = (255, 255, 255, 255)
        artist_fill = (245, 245, 245, 255)
        shadow_fill_title = (0, 0, 0, 180)
        shadow_fill_artist = (0, 0, 0, 170)
        extra_stroke = False

    draw.text((tx_title + shadow_offset, y + shadow_offset), title, font=title_font, fill=shadow_fill_title)
    if extra_stroke:
        draw.text((tx_title - 1, y), title, font=title_font, fill=shadow_fill_title)
        draw.text((tx_title + 1, y), title, font=title_font, fill=shadow_fill_title)
        draw.text((tx_title, y - 1), title, font=title_font, fill=shadow_fill_title)
        draw.text((tx_title, y + 1), title, font=title_font, fill=shadow_fill_title)
    draw.text((tx_title, y), title, font=title_font, fill=title_fill)

    artist_y = y + title_h + 12
    draw.text((tx_artist + shadow_offset, artist_y + shadow_offset), artist, font=artist_font, fill=shadow_fill_artist)
    if extra_stroke:
        draw.text((tx_artist - 1, artist_y), artist, font=artist_font, fill=shadow_fill_artist)
        draw.text((tx_artist + 1, artist_y), artist, font=artist_font, fill=shadow_fill_artist)
    draw.text((tx_artist, artist_y), artist, font=artist_font, fill=artist_fill)

    return title_h + 12 + artist_h


def save_release_cover_variant(image, output_path):
    target = image.convert("RGB") if image.mode != "RGB" else image
    target.save(output_path, quality=95)


def build_release_cover_variant(layout_key, base_image, title, artist, output_path, options):
    if layout_key == "bottom":
        return _build_release_cover_variant_bottom(base_image, title, artist, output_path, options)
    if layout_key == "topleft":
        return _build_release_cover_variant_top_left(base_image, title, artist, output_path, options)
    if layout_key == "center":
        return _build_release_cover_variant_center_band(base_image, title, artist, output_path, options)
    raise ValueError(f"Unbekanntes Layout: {layout_key}")


def generate_cover_variants(
    cover_path,
    title,
    artist,
    output_dir,
    selected_layouts,
    selected_formats,
    options=None,
    presets=None,
):
    if not have_pillow():
        raise RuntimeError("Pillow ist nicht installiert.")

    presets = presets or get_cover_presets()
    options = options or {}
    created_files = []
    cover_stem = os.path.splitext(os.path.basename(cover_path))[0]

    with Image.open(cover_path) as base_image:
        for format_key in selected_formats:
            target_width, target_height, format_label = presets[format_key]
            formatted_base = resize_cover_canvas(base_image, target_width, target_height)
            for layout_key in selected_layouts:
                output_name = f"{cover_stem}_{layout_key}_{format_label.replace(':', 'x')}.jpg"
                output_path = os.path.join(output_dir, output_name)
                build_release_cover_variant(
                    layout_key,
                    formatted_base,
                    title,
                    artist,
                    output_path,
                    options,
                )
                created_files.append(output_path)

    return created_files


def _build_release_cover_variant_bottom(base_image, title, artist, output_path, options):
    image = base_image.copy().convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    band_height = max(130, int(height * 0.20))
    margin_x = max(30, int(width * 0.06))
    band_top = height - band_height
    vertical_shift = release_cover_vertical_shift(options.get("offset", "normal"), height, "bottom")
    overlay_alpha = release_cover_overlay_alpha(options.get("overlay", "medium"), "default")

    draw.rectangle((0, band_top, width, height), fill=(0, 0, 0, overlay_alpha))
    draw_release_cover_text_block(
        draw,
        margin_x,
        band_top + max(18, int(band_height * 0.16)) + vertical_shift,
        width - margin_x * 2,
        title,
        artist,
        max(28, int(height * 0.07)),
        max(16, int(height * 0.038)),
        style=options.get("style", "clean"),
        size_mode=options.get("size_mode", "medium"),
        align="center",
    )
    save_release_cover_variant(image, output_path)


def _build_release_cover_variant_top_left(base_image, title, artist, output_path, options):
    image = base_image.copy().convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    box_x = max(20, int(width * 0.05))
    box_y = max(20, int(height * 0.05))
    box_w = int(width * 0.58)
    box_h = int(height * 0.24)
    vertical_shift = release_cover_vertical_shift(options.get("offset", "normal"), height, "card")
    overlay_alpha = release_cover_overlay_alpha(options.get("overlay", "medium"), "card")

    draw.rounded_rectangle(
        (box_x, box_y, box_x + box_w, box_y + box_h),
        radius=max(16, int(min(width, height) * 0.025)),
        fill=(0, 0, 0, overlay_alpha),
        outline=(255, 255, 255, 70),
        width=2,
    )
    draw_release_cover_text_block(
        draw,
        box_x + 20,
        box_y + 20 + vertical_shift,
        box_w - 40,
        title,
        artist,
        max(26, int(height * 0.062)),
        max(16, int(height * 0.034)),
        style=options.get("style", "clean"),
        size_mode=options.get("size_mode", "medium"),
        align="left",
    )
    save_release_cover_variant(image, output_path)


def _build_release_cover_variant_center_band(base_image, title, artist, output_path, options):
    image = base_image.copy().convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    band_h = max(120, int(height * 0.18))
    band_y = int((height - band_h) / 2)
    margin_x = max(28, int(width * 0.07))
    vertical_shift = release_cover_vertical_shift(options.get("offset", "normal"), height, "center")
    overlay_alpha = release_cover_overlay_alpha(options.get("overlay", "medium"), "default")
    line_alpha = release_cover_overlay_alpha(options.get("overlay", "medium"), "line")

    draw.rectangle((0, band_y, width, band_y + band_h), fill=(10, 10, 10, overlay_alpha))
    draw.line((margin_x, band_y + 18, width - margin_x, band_y + 18), fill=(255, 255, 255, line_alpha), width=2)
    draw.line((margin_x, band_y + band_h - 18, width - margin_x, band_y + band_h - 18), fill=(255, 255, 255, line_alpha), width=2)
    draw_release_cover_text_block(
        draw,
        margin_x,
        band_y + max(18, int(band_h * 0.16)) + vertical_shift,
        width - margin_x * 2,
        title,
        artist,
        max(28, int(height * 0.068)),
        max(16, int(height * 0.036)),
        style=options.get("style", "clean"),
        size_mode=options.get("size_mode", "medium"),
        align="center",
    )
    save_release_cover_variant(image, output_path)
