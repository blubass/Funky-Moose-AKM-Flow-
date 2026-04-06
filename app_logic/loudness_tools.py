import json
import math
import os
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional


def _ensure_ffmpeg_in_path():
    """Versucht ffmpeg an üblichen Stellen zu finden und zum PATH hinzuzufügen."""
    common_paths = [
        # 1. Prio: Bundled FFmpeg inside .app (PyInstaller MEIPASS)
        getattr(sys, "_MEIPASS", ""),
        os.path.dirname(sys.executable),
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/usr/sbin",
        "/sbin",
        "/opt/local/bin",
        "/sw/bin",
        os.path.expanduser("~/bin"),
        os.path.expanduser("~/.local/bin"),
        os.path.join(os.getcwd(), "ffmpeg")
    ]
    current_path = os.environ.get("PATH", "")
    new_paths = []
    
    for p in common_paths:
        if os.path.exists(p) and p not in current_path:
            new_paths.append(p)
            
    if new_paths:
        os.environ["PATH"] = ":".join(new_paths) + ":" + current_path
        print(f"DEBUG: PATH updated to include ffmpeg search locations: {new_paths}")


# Sofort beim Import versuchen PATH zu fixen
_ensure_ffmpeg_in_path()


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def run_command(cmd: List[str]) -> subprocess.CompletedProcess:
    executable = shutil.which(cmd[0])
    if executable:
        cmd[0] = executable
    
    # We use shell=False for safety, but ensure all args are strings
    safe_cmd = [str(arg) for arg in cmd]
    
    result = subprocess.run(
        safe_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"DEBUG: Command failed with code {result.returncode}")
        if result.stderr:
            print(f"DEBUG STDEERR: {result.stderr[:200]}")
    return result


def probe_duration(path: str) -> Optional[float]:
    if not os.path.exists(path):
        return None

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        path,
    ]
    result = run_command(cmd)
    if result.returncode != 0:
        return None

    try:
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        return duration
    except Exception:
        return None


def format_seconds(seconds: Optional[float]) -> str:
    if seconds is None:
        return ""
    total = int(round(seconds))
    minutes = total // 60
    secs = total % 60
    return f"{minutes}:{secs:02d}"


def _extract_summary_value(stderr_text: str, label: str):
    """
    Liest Werte robust aus dem ffmpeg/ebur128-Output.
    Beispiele:
    'I:         -14.3 LUFS'
    'Peak:       -1.2 dBFS'
    'True peak:  -0.8 dBFS'
    'TP:         -0.8 dBFS'
    """
    patterns = [
        rf"{re.escape(label)}\s*:\s*(-?\d+(?:\.\d+)?)",
        rf"{re.escape(label)}\s+(-?\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, stderr_text, flags=re.IGNORECASE)
        if matches:
            try:
                return float(matches[-1])
            except Exception:
                pass
    return None


def _extract_true_peak(stderr_text: str):
    candidates = [
        "True peak",
        "True Peak",
        "TP",
        "Tpk",
        "Peak",
    ]

    for label in candidates:
        value = _extract_summary_value(stderr_text, label)
        if value is not None:
            return value
    return None


def analyze_full_track(path: str) -> Dict:
    """
    Misst komplette Datei mit ffmpeg ebur128.
    Gibt zurück:
    - filename
    - path
    - duration_seconds
    - duration_display
    - integrated_lufs
    - true_peak_dbtp (falls verfügbar)
    - sample_peak_dbfs
    - ok
    - error
    """
    result_data = {
        "filename": os.path.basename(path),
        "path": path,
        "duration_seconds": probe_duration(path),
        "duration_display": "",
        "integrated_lufs": None,
        "true_peak_dbtp": None,
        "sample_peak_dbfs": None,
        "ok": False,
        "error": "",
    }

    result_data["duration_display"] = format_seconds(result_data["duration_seconds"])

    if not os.path.exists(path):
        result_data["error"] = "Datei nicht gefunden."
        return result_data

    if not have_ffmpeg():
        result_data["error"] = "ffmpeg/ffprobe nicht gefunden."
        return result_data

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i",
        path,
        "-filter_complex",
        "ebur128=peak=true",
        "-f",
        "null",
        "-",
    ]
    result = run_command(cmd)
    stderr_text = result.stderr or ""

    if result.returncode != 0 and "I:" not in stderr_text:
        result_data["error"] = stderr_text.strip() or "Analyse fehlgeschlagen."
        return result_data

    integrated_lufs = _extract_summary_value(stderr_text, "I")
    true_peak = _extract_true_peak(stderr_text)
    sample_peak = _extract_summary_value(stderr_text, "Peak")

    result_data["integrated_lufs"] = integrated_lufs
    result_data["true_peak_dbtp"] = true_peak
    result_data["sample_peak_dbfs"] = sample_peak
    result_data["ok"] = integrated_lufs is not None

    if not result_data["ok"]:
        result_data["error"] = "Konnte LUFS nicht auslesen."

    return result_data


def calculate_gain_to_target(measured_lufs: Optional[float], target_lufs: float) -> Optional[float]:
    if measured_lufs is None:
        return None
    return round(target_lufs - measured_lufs, 2)


def db_to_linear(db_value: float) -> float:
    return 10 ** (db_value / 20.0)


def sanitize_output_path(output_path: str) -> str:
    directory = os.path.dirname(output_path)
    filename = os.path.basename(output_path)
    stem, ext = os.path.splitext(filename)
    if not ext:
        ext = ".wav"
    return os.path.join(directory, f"{stem}{ext.lower()}")


def predict_true_peak_after_gain(current_true_peak_dbtp, gain_db):
    if current_true_peak_dbtp is None or gain_db is None:
        return None
    return round(current_true_peak_dbtp + gain_db, 2)


def get_status_for_match(
    measured_lufs: Optional[float],
    gain_db: Optional[float],
    predicted_true_peak: Optional[float],
    true_peak_ceiling: float = -1.0,
) -> str:
    if measured_lufs is None or gain_db is None:
        return "Analyse fehlt"

    if predicted_true_peak is not None and predicted_true_peak > true_peak_ceiling:
        return "Peak Warnung"

    if abs(gain_db) < 0.3:
        return "OK"

    if gain_db > 0:
        return "Zu leise"

    return "Zu laut"


def safe_output_path(output_dir: str, source_path: str, suffix: str = "_matched") -> str:
    base = os.path.basename(source_path)
    stem, ext = os.path.splitext(base)
    if not ext:
        ext = ".wav"
    return os.path.join(output_dir, f"{stem}{suffix}{ext}")


def export_matched_file(
    source_path: str,
    output_path: str,
    gain_db: float,
    overwrite: bool = True,
    use_limiter: bool = False,
    true_peak_ceiling_db: float = -1.0,
) -> Dict:
    """
    Rendert neue Datei mit Gain-Anpassung.
    Optional mit Limiter, wenn Peak-Warnungen abgefangen werden sollen.
    Original bleibt unangetastet.
    """
    output_path = sanitize_output_path(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not os.path.exists(source_path):
        return {
            "ok": False,
            "source": source_path,
            "output": output_path,
            "gain_db": gain_db,
            "use_limiter": use_limiter,
            "true_peak_ceiling_db": true_peak_ceiling_db,
            "error": "Quelldatei nicht gefunden.",
        }

    codec_args = ["-c:a", "pcm_s16le"]
    ext = os.path.splitext(output_path)[1].lower()

    if ext == ".flac":
        codec_args = ["-c:a", "flac"]
    elif ext == ".mp3":
        codec_args = ["-c:a", "libmp3lame", "-b:a", "320k"]
    elif ext in {".m4a", ".aac"}:
        codec_args = ["-c:a", "aac", "-b:a", "320k"]
    elif ext in {".aif", ".aiff"}:
        codec_args = ["-c:a", "pcm_s16be"]

    filter_chain = f"volume={gain_db}dB"
    if use_limiter:
        limit_linear = db_to_linear(true_peak_ceiling_db)
        filter_chain += f",alimiter=limit={limit_linear:.6f}:level=1"

    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-hide_banner",
        "-i",
        source_path,
        "-vn",
        "-filter:a",
        filter_chain,
        *codec_args,
        output_path,
    ]
    result = run_command(cmd)

    return {
        "ok": result.returncode == 0,
        "source": source_path,
        "output": output_path,
        "gain_db": gain_db,
        "use_limiter": use_limiter,
        "true_peak_ceiling_db": true_peak_ceiling_db,
        "error": "" if result.returncode == 0 else (result.stderr.strip() or "Export fehlgeschlagen."),
    }


def analyze_many(paths: List[str], target_lufs: float = -14.0, true_peak_ceiling: float = -1.0) -> List[Dict]:
    results = []

    for path in paths:
        item = analyze_full_track(path)
        gain_db = calculate_gain_to_target(item.get("integrated_lufs"), target_lufs)
        peak_source = item.get("true_peak_dbtp")
        if peak_source is None:
            peak_source = item.get("sample_peak_dbfs")
        predicted_tp = predict_true_peak_after_gain(peak_source, gain_db)
        status = get_status_for_match(
            item.get("integrated_lufs"),
            gain_db,
            predicted_tp,
            true_peak_ceiling=true_peak_ceiling,
        )

        item["target_lufs"] = target_lufs
        item["gain_to_target_db"] = gain_db
        item["predicted_true_peak_after_gain"] = predicted_tp
        item["match_status"] = status
        results.append(item)

    return results


def generate_waveform_image(path: str, out_path: str, width: int = 800, height: int = 120, hex_color: str = "#ff9a3c") -> bool:
    """
    Generiert eine Wellenform-Grafik via ffmpeg showwavespic.
    Nutzt timeout=10 um Aufhaenger zu vermeiden.
    """
    if not have_ffmpeg():
        return False
    
    # Simple color name for better compatibility
    color_val = "orange"
    
    # Force absolute paths
    abs_in = os.path.abspath(path)
    abs_out = os.path.abspath(out_path)
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", abs_in,
        "-filter_complex", f"showwavespic=s={width}x{height}:colors={color_val}",
        "-frames:v", "1",
        abs_out
    ]
    
    try:
        # Run with timeout to prevent hanging UI
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        return result.returncode == 0 and os.path.exists(abs_out)
    except subprocess.TimeoutExpired:
        print("DEBUG: Waveform generation timed out after 10s")
        return False
    except Exception as e:
        print(f"DEBUG: Waveform generation error: {e}")
        return False
