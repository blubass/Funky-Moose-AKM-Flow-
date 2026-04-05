import os

from app_logic import release_tools


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def clean_release_drop_paths(raw_paths):
    paths = []
    seen = set()
    for raw in raw_paths or []:
        cleaned = _clean_text(raw).strip("{}")
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        paths.append(cleaned)
    return paths


def copy_work_to_release_track(item, audio_path=None, source="Werk"):
    return {
        "title": _clean_text((item or {}).get("title")),
        "duration": _clean_text((item or {}).get("duration")),
        "production": _clean_text((item or {}).get("production")),
        "year": _clean_text((item or {}).get("year")),
        "audio_path": _clean_text(audio_path) if audio_path is not None else _clean_text((item or {}).get("audio_path")),
        "source": source,
    }


def build_file_release_track(path, duration=""):
    title = os.path.splitext(os.path.basename(path or ""))[0]
    return {
        "title": title,
        "duration": _clean_text(duration),
        "production": "",
        "year": "",
        "audio_path": _clean_text(path),
        "source": "Datei",
    }


def build_release_track_from_match(path, exact_work=None, title_work=None, duration=""):
    if exact_work is not None:
        return copy_work_to_release_track(
            exact_work,
            audio_path=path,
            source="Werk",
        )
    if title_work is not None:
        return copy_work_to_release_track(
            title_work,
            audio_path=path,
            source="Datei→Werk",
        )
    return build_file_release_track(path, duration=duration)


def collect_release_track_identities(tracks):
    identities = set()
    for item in tracks or []:
        identity = release_tools.release_track_identity(item)
        if identity is not None:
            identities.add(identity)
    return identities


def append_unique_release_tracks(existing_tracks, candidate_tracks):
    updated_tracks = list(existing_tracks or [])
    existing_identities = collect_release_track_identities(updated_tracks)
    added_tracks = []
    duplicate_tracks = []

    for track in candidate_tracks or []:
        identity = release_tools.release_track_identity(track)
        if identity is not None and identity in existing_identities:
            duplicate_tracks.append(track)
            continue
        updated_tracks.append(track)
        added_tracks.append(track)
        if identity is not None:
            existing_identities.add(identity)

    return {
        "tracks": updated_tracks,
        "added": added_tracks,
        "duplicates": duplicate_tracks,
    }


def remove_release_track_at(tracks, index):
    if index is None or index < 0 or index >= len(tracks or []):
        return list(tracks or []), None

    updated_tracks = list(tracks or [])
    removed = updated_tracks.pop(index)
    return updated_tracks, removed


def move_release_track(tracks, index, direction):
    updated_tracks = list(tracks or [])
    if index is None or index < 0 or index >= len(updated_tracks):
        return updated_tracks, None

    target_index = index + direction
    if target_index < 0 or target_index >= len(updated_tracks):
        return updated_tracks, None

    updated_tracks[index], updated_tracks[target_index] = (
        updated_tracks[target_index],
        updated_tracks[index],
    )
    return updated_tracks, target_index


def safe_release_directory_name(title):
    safe_name = "".join(
        ch if ch.isalnum() or ch in "-_ " else "_"
        for ch in _clean_text(title)
    ).strip()
    return safe_name or "Release"


def build_release_export_preserve_paths(cover_path, tracks):
    preserve_paths = []
    if _clean_text(cover_path):
        preserve_paths.append(_clean_text(cover_path))
    preserve_paths.extend(
        _clean_text(item.get("audio_path"))
        for item in (tracks or [])
        if _clean_text(item.get("audio_path"))
    )
    return preserve_paths


def build_release_info_lines(metadata):
    values = metadata or {}
    return [
        f"Release Title: {_clean_text(values.get('title'))}",
        f"Artist: {_clean_text(values.get('artist'))}",
        f"Type: {_clean_text(values.get('type'))}",
        f"Release Date: {_clean_text(values.get('release_date'))}",
        f"Genre: {_clean_text(values.get('genre'))}",
        f"Subgenre: {_clean_text(values.get('subgenre'))}",
        f"Label: {_clean_text(values.get('label'))}",
        f"Copyright: {_clean_text(values.get('copyright_line'))}",
        f"Cover Path: {_clean_text(values.get('cover_path'))}",
    ]


def build_release_track_csv_rows(tracks):
    rows = [["Track Number", "Title", "Duration", "Production", "Year", "Audio Path"]]
    for index, item in enumerate(tracks or [], start=1):
        rows.append(
            [
                index,
                _clean_text(item.get("title")),
                _clean_text(item.get("duration")),
                _clean_text(item.get("production")),
                _clean_text(item.get("year")),
                _clean_text(item.get("audio_path")),
            ]
        )
    return rows


def build_release_audio_target_name(index, item, audio_path):
    stem = os.path.splitext(os.path.basename(audio_path or ""))[0]
    ext = os.path.splitext(audio_path or "")[1]
    safe_track_name = "".join(
        ch if ch.isalnum() or ch in "-_ " else "_"
        for ch in _clean_text((item or {}).get("title")) or stem
    ).strip() or stem
    return f"{index:02d} - {safe_track_name}{ext}"


def build_release_checklist_lines(cover_path, tracks, copied_audio, missing_audio):
    return [
        f"Cover gesetzt: {'Ja' if _clean_text(cover_path) else 'Nein'}",
        f"Tracks im Release: {len(tracks or [])}",
        f"Audio-Dateien kopiert: {copied_audio}",
        f"Tracks ohne Audio-Pfad / Kopierfehler: {missing_audio}",
        "Lautheit schon geprüft: bitte prüfen",
        "Reihenfolge geprüft: bitte prüfen",
        "Release-Datum gesetzt: bitte prüfen",
    ]


def build_release_export_status_text(release_dir, tracks, copied_audio):
    return (
        f"Distro-Export bereit: {release_dir} | "
        f"Tracks: {len(tracks or [])} | "
        f"Audio kopiert: {copied_audio}"
    )
