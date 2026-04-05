import csv
import datetime
import json
import os
import re

DATA_FILE = "akm_data.json"
BACKUP_FILE = "akm_data_backup.json"

STATUS_KEYS = {"ready", "submitted", "confirmed", "in_progress"}


class DataFileError(RuntimeError):
    pass


def _clean_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _today():
    return datetime.date.today().isoformat()


def _read_json_list(path, strict=False):
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as exc:
        if strict:
            raise DataFileError(
                f"{os.path.basename(path)} konnte nicht gelesen werden: {exc}"
            ) from exc
        return []
    except json.JSONDecodeError as exc:
        if strict:
            raise DataFileError(
                f"{os.path.basename(path)} ist beschädigt (Zeile {exc.lineno}, Spalte {exc.colno})."
            ) from exc
        return []

    if not isinstance(data, list):
        if strict:
            raise DataFileError(f"{os.path.basename(path)} hat ein ungültiges Format.")
        return []

    return data


def load_data(strict=False):
    raw_data = _read_json_list(DATA_FILE, strict=strict)
    data = []
    for entry in raw_data:
        normalized = _normalize_entry(entry)
        if normalized["title"]:
            data.append(normalized)
    return data


def save_data(data):
    normalized = []
    for entry in data:
        item = _normalize_entry(entry)
        if item["title"]:
            normalized.append(item)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)


def find_entry(data, title):
    norm_title = _clean_text(title).lower()
    for entry in data:
        if _clean_text(entry.get("title", "")).lower() == norm_title:
            return entry
    return None


def _normalize_entry(entry):
    item = dict(entry) if isinstance(entry, dict) else {}
    item["title"] = _clean_text(item.get("title"))
    item["status"] = item.get("status", "in_progress")
    item["date"] = item.get("date", _today())
    item["last_change"] = item.get("last_change", item["date"])
    item["duration"] = _clean_text(item.get("duration"))
    item["composer"] = _clean_text(item.get("composer"))
    item["production"] = _clean_text(item.get("production"))
    item["year"] = _clean_text(item.get("year"))
    item["instrumental"] = bool(item.get("instrumental", False))
    item["notes"] = _clean_text(item.get("notes"))
    tags = item.get("tags", [])
    if isinstance(tags, str):
        tags = [part.strip() for part in tags.split(",") if part.strip()]
    elif not isinstance(tags, list):
        tags = []
    item["tags"] = [_clean_text(tag) for tag in tags if _clean_text(tag)]
    return item


def add_entry(
    title,
    lang,
    duration="",
    composer="",
    production="",
    year="",
    instrumental=False,
    notes="",
    tags=None,
    status="in_progress",
):
    del lang
    title = _clean_text(title)
    if not title:
        return False, "empty_title"

    status = _clean_text(status) or "in_progress"
    if status not in STATUS_KEYS:
        return False, "invalid_status"

    data = load_data(strict=True)
    if find_entry(data, title):
        return False, "duplicate"

    now = _today()
    clean_tags = []
    for tag in tags or []:
        cleaned = _clean_text(tag)
        if cleaned:
            clean_tags.append(cleaned)

    entry = {
        "title": title,
        "status": status,
        "date": now,
        "last_change": now,
        "duration": _clean_text(duration),
        "composer": _clean_text(composer),
        "production": _clean_text(production),
        "year": _clean_text(year),
        "instrumental": bool(instrumental),
        "notes": _clean_text(notes),
        "tags": clean_tags,
    }

    data.append(entry)
    save_data(data)
    return True, entry


def update_status(title, status, lang):
    del lang
    status = status.lower()
    if status not in STATUS_KEYS:
        return False, "invalid_status"

    data = load_data(strict=True)
    entry = find_entry(data, title)
    if not entry:
        return False, "not_found"

    if entry.get("status") == status:
        return True, entry

    entry["status"] = status
    entry["last_change"] = _today()
    save_data(data)
    return True, entry


def get_all_entries():
    return load_data(strict=True)


def get_last_open():
    entries = get_all_entries()
    open_entries = [e for e in entries if e.get("status") != "confirmed"]
    if not open_entries:
        return None
    sorted_entries = sorted(
        open_entries, key=lambda e: e.get("last_change", e.get("date", "")), reverse=True
    )
    return sorted_entries[0]


def import_excel(file_path):
    import openpyxl

    if not os.path.exists(file_path):
        return []

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active

    data = load_data(strict=True)
    now = _today()
    touched = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        track = {
            "title": str(row[0]).strip(),
            "duration": str(row[1]).strip() if row[1] else "",
            "composer": str(row[2]).strip() if row[2] else "",
            "production": str(row[3]).strip() if len(row) > 3 and row[3] else "",
            "year": str(row[4]).strip() if len(row) > 4 and row[4] else "",
            "notes": str(row[5]).strip() if len(row) > 5 and row[5] else "",
        }
        title = track["title"]
        duration = track.get("duration", "")
        composer = track.get("composer", "")
        production = track.get("production", "")
        year = track.get("year", "")
        notes = track.get("notes", "")

        existing = find_entry(data, title)
        if existing:
            entry_changed = False
            if duration and duration != existing.get("duration", ""):
                existing["duration"] = duration
                entry_changed = True
            if composer and composer != existing.get("composer", ""):
                existing["composer"] = composer
                entry_changed = True
            if production and production != existing.get("production", ""):
                existing["production"] = production
                entry_changed = True
            if year and year != existing.get("year", ""):
                existing["year"] = year
                entry_changed = True
            if notes and notes != existing.get("notes", ""):
                existing["notes"] = notes
                entry_changed = True
            if entry_changed:
                existing["last_change"] = now

            touched.append(
                {
                    "title": existing.get("title", ""),
                    "duration": existing.get("duration", ""),
                    "composer": existing.get("composer", ""),
                    "production": existing.get("production", ""),
                    "year": existing.get("year", ""),
                    "notes": existing.get("notes", ""),
                    "status": existing.get("status", ""),
                }
            )
        else:
            entry = {
                "title": title,
                "status": "ready",
                "date": now,
                "last_change": now,
                "duration": duration,
                "composer": composer,
                "production": production,
                "year": year,
                "instrumental": False,
                "notes": notes,
                "tags": [],
            }
            data.append(entry)
            touched.append(
                {
                    "title": title,
                    "duration": duration,
                    "composer": composer,
                    "production": production,
                    "year": year,
                    "notes": notes,
                    "status": "ready",
                }
            )

    save_data(data)
    return touched


def export_csv(lang, path=None):
    del lang
    data = load_data(strict=True)
    if path is None:
        path = "akm_export.csv"

    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "title",
                "status",
                "date",
                "last_change",
                "duration",
                "composer",
                "production",
                "year",
                "instrumental",
                "notes",
                "tags",
            ],
        )
        writer.writeheader()
        for item in data:
            writer.writerow(
                {
                    "title": item.get("title", ""),
                    "status": item.get("status", ""),
                    "date": item.get("date", ""),
                    "last_change": item.get("last_change", ""),
                    "duration": item.get("duration", ""),
                    "composer": item.get("composer", ""),
                    "production": item.get("production", ""),
                    "year": item.get("year", ""),
                    "instrumental": "yes" if item.get("instrumental") else "no",
                    "notes": item.get("notes", ""),
                    "tags": ", ".join(item.get("tags", [])),
                }
            )
    return path


def backup_data():
    import shutil

    if os.path.exists(DATA_FILE):
        load_data(strict=True)
        shutil.copy2(DATA_FILE, BACKUP_FILE)


def restore_data():
    import shutil

    if os.path.exists(BACKUP_FILE):
        _read_json_list(BACKUP_FILE, strict=True)
        shutil.copy2(BACKUP_FILE, DATA_FILE)
        return True
    return False


def update_entry(title, updates):
    data = load_data(strict=True)
    entry = find_entry(data, title)
    if not entry:
        return False, "not_found"

    allowed_fields = {
        "title",
        "duration",
        "composer",
        "production",
        "year",
        "instrumental",
        "notes",
        "tags",
        "status",
    }

    normalized_title = None
    if "title" in (updates or {}):
        normalized_title = _clean_text(updates.get("title"))
        if not normalized_title:
            return False, "empty_title"

        existing = find_entry(data, normalized_title)
        if existing is not None and existing is not entry:
            return False, "duplicate"

    changed = False
    for key, value in (updates or {}).items():
        if key not in allowed_fields:
            continue

        if key == "title":
            normalized_value = normalized_title
        elif key == "instrumental":
            normalized_value = bool(value)
        elif key == "tags":
            normalized_value = []
            for tag in value or []:
                cleaned = _clean_text(tag)
                if cleaned:
                    normalized_value.append(cleaned)
        elif key == "status":
            normalized_value = value if value in STATUS_KEYS else entry.get("status", "in_progress")
        else:
            normalized_value = _clean_text(value)

        if entry.get(key) != normalized_value:
            entry[key] = normalized_value
            changed = True

    if not changed:
        return True, entry

    entry["last_change"] = _today()
    save_data(data)
    return True, entry



def get_dashboard_stats():
    entries = load_data(strict=True)
    total = len(entries)
    confirmed = sum(1 for item in entries if item.get("status") == "confirmed")
    ready = sum(1 for item in entries if item.get("status") == "ready")
    submitted = sum(1 for item in entries if item.get("status") == "submitted")
    in_progress = sum(1 for item in entries if item.get("status") == "in_progress")
    instrumental = sum(1 for item in entries if item.get("instrumental"))
    with_production = sum(1 for item in entries if item.get("production"))
    with_notes = sum(1 for item in entries if item.get("notes"))

    return {
        "total": total,
        "open": total - confirmed,
        "ready": ready,
        "submitted": submitted,
        "in_progress": in_progress,
        "confirmed": confirmed,
        "instrumental": instrumental,
        "with_production": with_production,
        "with_notes": with_notes,
    }
