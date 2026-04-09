import os


WAVEFORM_PREVIEW_FILENAME = "preview.png"
WAVEFORM_PREVIEW_SIZE = (800, 220)


def waveform_preview_output_path(home_dir):
    return os.path.join(home_dir, ".akm_temp", WAVEFORM_PREVIEW_FILENAME)


def render_waveform_preview(
    source_path,
    home_dir,
    accent_color,
    generate_waveform_image,
    image_module,
    makedirs_fn=os.makedirs,
    exists_fn=os.path.exists,
):
    output_path = waveform_preview_output_path(home_dir)
    makedirs_fn(os.path.dirname(output_path), exist_ok=True)
    ok = generate_waveform_image(source_path, output_path, hex_color=accent_color)
    if not ok or not exists_fn(output_path):
        return None, "Bild-Fehler"

    with image_module.open(output_path) as image:
        resized = image.resize(WAVEFORM_PREVIEW_SIZE, image_module.Resampling.LANCZOS)
        return resized.copy(), None
