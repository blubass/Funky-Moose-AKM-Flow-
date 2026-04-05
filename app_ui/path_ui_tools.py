import os


AUDIO_FILETYPES = [
    ("Audio", "*.wav *.aiff *.aif *.mp3 *.flac *.m4a"),
    ("Alle Dateien", "*.*"),
]
IMAGE_FILETYPES = [
    ("Bilder", "*.jpg *.jpeg *.png *.webp"),
    ("Alle Dateien", "*.*"),
]


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def validate_existing_path(path, empty_message, missing_prefix, exists_fn=os.path.exists):
    normalized = _clean_text(path)
    if not normalized:
        return normalized, empty_message
    if not exists_fn(normalized):
        return normalized, f"{missing_prefix}: {normalized}"
    return normalized, None


def build_file_set_message(prefix, path):
    normalized = _clean_text(path)
    return f"{prefix}: {os.path.basename(normalized)}"


def build_folder_set_message(prefix, folder):
    return f"{prefix}: {_clean_text(folder)}"


def build_finder_opened_message(prefix, path):
    normalized = _clean_text(path)
    return f"{prefix}: {os.path.basename(normalized)}"


def build_finder_error_message(exc):
    return f"Finder-Öffnen fehlgeschlagen: {exc}"
