import os


AUDIO_EXTENSIONS = {".wav", ".aiff", ".aif", ".mp3", ".flac", ".m4a"}
RELEASE_COVER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
REMOVABLE_RELEASE_FILENAMES = {
    "release_info.txt",
    "tracklist.csv",
    "tracklist.xlsx",
    "checklist.txt",
}
AUTO_NOTE_PREFIXES = ("Matched Export:", "Limiter:")


def normalize_release_match_text(text):
    value = (text or "").strip().lower()
    for token in ["_matched", "-matched", " matched", "_master", "-master", " master"]:
        value = value.replace(token, "")
    value = value.replace("_", " ").replace("-", " ")
    value = " ".join(value.split())
    if value[:2].isdigit() and len(value) > 3 and value[2] in {" ", "."}:
        value = value[3:].strip()
    return value


def is_supported_audio_path(path):
    normalized = (path or "").strip()
    if not normalized or not os.path.isfile(normalized):
        return False
    return os.path.splitext(normalized)[1].lower() in AUDIO_EXTENSIONS


def normalized_path(path):
    try:
        return os.path.normcase(os.path.abspath(path))
    except Exception:
        return None


def is_release_export_asset(path):
    if not os.path.isfile(path):
        return False

    name = os.path.basename(path)
    lower_name = name.lower()
    if lower_name in REMOVABLE_RELEASE_FILENAMES:
        return True

    ext = os.path.splitext(lower_name)[1]
    if ext in RELEASE_COVER_EXTENSIONS:
        return True

    return len(name) >= 5 and name[:2].isdigit() and name[2:5] == " - " and ext in AUDIO_EXTENSIONS


def cleanup_release_export_dir(release_dir, preserve_paths=None):
    protected_paths = {
        normalized
        for normalized in (normalized_path(path) for path in (preserve_paths or []))
        if normalized
    }
    removed_count = 0
    errors = []

    if not os.path.isdir(release_dir):
        return removed_count, errors

    for name in os.listdir(release_dir):
        path = os.path.join(release_dir, name)
        if not is_release_export_asset(path):
            continue
        if normalized_path(path) in protected_paths:
            continue
        try:
            os.remove(path)
            removed_count += 1
        except OSError as exc:
            errors.append((path, str(exc)))

    return removed_count, errors


def release_track_identity(item):
    title = normalize_release_match_text(item.get("title", ""))
    source = (item.get("source") or "").strip()
    if title and source in {"Werk", "Datei→Werk"}:
        return ("title", title)

    audio_path = (item.get("audio_path") or "").strip()
    if audio_path:
        normalized = normalized_path(audio_path)
        if normalized is not None:
            return ("path", normalized)

    if title:
        return ("title", title)

    return None


def find_work_by_exact_audio_path(entries, path):
    target = normalized_path(path)
    if target is None or entries is None:
        return None

    for item in entries:
        audio_path = (item.get("audio_path") or "").strip()
        if not audio_path:
            continue
        if normalized_path(audio_path) == target:
            return item
    return None


def find_work_by_title_like_audio_path(entries, path):
    stem = os.path.splitext(os.path.basename(path))[0]
    normalized_stem = normalize_release_match_text(stem)
    if not normalized_stem or entries is None:
        return None

    for item in entries:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        normalized_title = normalize_release_match_text(title)
        if normalized_title == normalized_stem:
            return item
    return None


def merge_export_notes(old_notes, export_path, used_limiter):
    retained_lines = []
    for line in (old_notes or "").splitlines():
        stripped = line.strip()
        if any(stripped.startswith(prefix) for prefix in AUTO_NOTE_PREFIXES):
            continue
        retained_lines.append(line.rstrip())

    while retained_lines and not retained_lines[-1].strip():
        retained_lines.pop()

    if retained_lines:
        retained_lines.append("")

    retained_lines.append(f"Matched Export: {export_path}")
    retained_lines.append(f"Limiter: {'Ja' if used_limiter else 'Nein'}")
    return "\n".join(retained_lines)
