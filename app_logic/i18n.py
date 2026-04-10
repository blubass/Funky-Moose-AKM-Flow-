import os
from app_logic.config import cfg

# Registry for all user-facing strings
STRINGS = {
    "de": {
        # Status Signals
        "status_in_progress": "🟡 in Arbeit",
        "status_ready": "🔵 bereit",
        "status_submitted": "🟢 gemeldet",
        "status_confirmed": "✅ bestätigt",
        
        # Dashboard Tab
        "dash_header_title": "Dashboard",
        "dash_header_subtitle": "Schneller Blick auf Status, Vollständigkeit und Arbeitsstand.",
        "dash_radar_title": "Operations Radar",
        "dash_radar_empty": "Noch keine Werke im Katalog",
        "dash_radar_hint": "Importiere ein Werk oder lege direkt einen neuen Titel an, um loszulegen.",
        "dash_btn_refresh": "Dashboard aktualisieren",
        "dash_stat_total": "Gesamt",
        "dash_stat_open": "Offen",
        "dash_stat_ready": "Bereit",
        "dash_stat_submitted": "Gemeldet",
        "dash_stat_confirmed": "Bestätigt",
        "dash_stat_instrumental": "Instrumental",
        "dash_stat_with_production": "Mit Produktion",
        "dash_stat_with_notes": "Mit Notizen",
        "dash_chip_hint": "Statuschips springen direkt in die gefilterte Übersicht.",

        # Assistant Tab
        "ash_header_title": "AKM Schnellstart",
        "ash_header_subtitle": "Neue Werke anlegen, Status setzen und Excel-Import direkt starten.",
        "ash_radar_title": "Quick Launch Radar",
        "ash_radar_ready": "Schnellstart bereit",
        "ash_radar_hint": "Gib einen Titel ein, importiere Excel oder nutze die Status-Aktionen.",
        "ash_radar_context_empty": "Keine Eingabe aktiv | Excel-Import und Statuswechsel bereit",
        "ash_btn_create": "Werk anlegen",
        "ash_btn_import": "Excel importieren",
        "ash_btn_loudness": "Lautheit",
        "ash_intake_title": "Titel eingeben",
        "ash_intake_hint": "Hier startet der schnelle Workflow für neue Werke.",
        "ash_log_title": "AKM Log",
        "ash_log_subtitle": "Importe, Speicheraktionen und Hintergrundläufe.",

        # Import & Export Logic
        "log_import_done": "Excel-Import abgeschlossen: {count} Einträge",
        "log_import_none": "Excel-Import: keine verwertbaren Titel gefunden.",
        "log_project_saved": "Projekt erfolgreich gespeichert: {name}",
        "log_project_load_error": "FEHLER beim Laden: {error}",
        "log_export_ready": "Distro-Export bereit: {path} | Tracks: {count} | Audio: {copied}",
        "log_export_error": "Fehler beim Export: {error}",
        
        # General
        "task_active": "TASK AKTIV",
        "task_ready": "SYSTEM BEREIT",
        "task_busy_text": "Hintergrundjob läuft",
        "task_idle_text": "System bereit",
        "workspace_ready": "Workspace bereit",
    },
    "en": {
        # Status Signals
        "status_in_progress": "🟡 in progress",
        "status_ready": "🔵 ready",
        "status_submitted": "🟢 submitted",
        "status_confirmed": "✅ confirmed",
        
        # UI Labels & Messages
        "msg_project_saved": "PROJECT SAVED",
        "msg_project_loaded": "PROJECT LOADED",
        "msg_beenden": "Quit",
        "msg_beenden_confirm": "Do you want to save before quitting? \nOnly saving as a project (.akm) preserves all current settings.",
        
        # Error Messages
        "err_project_load": "Could not load project",
        "err_excel_import": "Excel import failed",
        "err_cover_not_found": "Cover file not found",
        "err_invalid_track_data": "Invalid track data",
        "err_file_not_found": "File not found",
        "err_audio_not_found": "NO AUDIO FILE FOUND",

        # Tasks
        "task_active": "TASK ACTIVE",
        "task_ready": "SYSTEM READY",
        "task_busy_text": "Background job running",
        "task_idle_text": "System ready",
        "workspace_ready": "Workspace ready",
    }
}

_current_lang = "de"

def set_language(lang: str):
    global _current_lang
    if lang in STRINGS:
        _current_lang = lang

def get_language() -> str:
    return _current_lang

def _t(key: str, default: str = None) -> str:
    """Translates a key into the current language."""
    return STRINGS.get(_current_lang, {}).get(key, default or key)

def get_status_chip_text(status: str) -> str:
    """Helper for status chips based on the current language."""
    key = f"status_{status}"
    return _t(key)
