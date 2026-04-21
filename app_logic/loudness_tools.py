import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
from typing import Dict, List, Optional
from app_logic import i18n

logger = logging.getLogger(__name__)

DEFAULT_TARGET_LUFS = -14.0
DEFAULT_TRUE_PEAK_CEILING_DB = -1.0
DEFAULT_LOUDNESS_RANGE_TARGET = 20.0
EXPORT_FORMAT_PRESETS = {
    "original": {
        "label_key": "loud_format_original",
        "extension": None,
        "sample_rate": None,
        "codec": None,
    },
    "wav_44100_24": {
        "label_key": "loud_format_wav_441_24",
        "extension": ".wav",
        "sample_rate": 44100,
        "codec": "pcm_s24le",
    },
    "wav_48000_24": {
        "label_key": "loud_format_wav_480_24",
        "extension": ".wav",
        "sample_rate": 48000,
        "codec": "pcm_s24le",
    },
    "wav_96000_24": {
        "label_key": "loud_format_wav_960_24",
        "extension": ".wav",
        "sample_rate": 96000,
        "codec": "pcm_s24le",
    },
    "wav_96000_32": {
        "label_key": "loud_format_wav_960_32",
        "extension": ".wav",
        "sample_rate": 96000,
        "codec": "pcm_f32le",
    },
}


def _ffmpeg_search_locations():
    common_paths = [
        getattr(sys, "_MEIPASS", ""),
        os.path.dirname(sys.executable),
        os.path.join(os.path.dirname(sys.executable), "ffmpeg"),
        os.path.join(os.path.dirname(sys.executable), "ffmpeg", "bin"),
        os.path.join(os.getcwd(), "ffmpeg"),
        os.path.join(os.getcwd(), "ffmpeg", "bin"),
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
    ]
    if os.name == "nt":
        common_paths.extend(
            [
                os.path.join(os.environ.get("ChocolateyInstall", ""), "bin"),
                os.path.join(os.environ.get("ProgramFiles", ""), "ffmpeg", "bin"),
                os.path.join(os.environ.get("ProgramFiles(x86)", ""), "ffmpeg", "bin"),
                os.path.join(os.environ.get("LocalAppData", ""), "Microsoft", "WinGet", "Links"),
            ]
        )
    return [path for path in common_paths if path]


def _ensure_ffmpeg_in_path():
    """Versucht ffmpeg an üblichen Stellen zu finden und zum PATH hinzuzufügen."""
    current_path = os.environ.get("PATH", "")
    current_entries = [entry for entry in current_path.split(os.pathsep) if entry]
    new_paths = []
    
    for p in _ffmpeg_search_locations():
        if os.path.exists(p) and p not in current_entries and p not in new_paths:
            new_paths.append(p)
            
    if new_paths:
        os.environ["PATH"] = os.pathsep.join(new_paths + current_entries)
        logger.debug("Expanded PATH with ffmpeg search locations: %s", new_paths)


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
        logger.debug("Command failed with code %s", result.returncode)
        if result.stderr:
            logger.debug("Command stderr: %s", result.stderr[:200])
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


def _extract_loudnorm_json(stderr_text: str) -> Optional[Dict]:
    matches = re.findall(r"(\{\s*\"input_i\".*?\})", stderr_text, flags=re.DOTALL)
    if not matches:
        return None

    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError:
        return None


def _coerce_float(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def measure_loudnorm_stats(
    path: str,
    target_lufs: float = DEFAULT_TARGET_LUFS,
    true_peak_ceiling_db: float = DEFAULT_TRUE_PEAK_CEILING_DB,
    loudness_range_target: float = DEFAULT_LOUDNESS_RANGE_TARGET,
) -> Optional[Dict]:
    if not os.path.exists(path) or not have_ffmpeg():
        return None

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-i",
        path,
        "-vn",
        "-af",
        (
            f"loudnorm=I={target_lufs}:"
            f"TP={true_peak_ceiling_db}:"
            f"LRA={loudness_range_target}:"
            "print_format=json"
        ),
        "-f",
        "null",
        "-",
    ]
    result = run_command(cmd)
    measurement = _extract_loudnorm_json(result.stderr or "")
    if not measurement:
        return None

    return {
        "input_i": _coerce_float(measurement.get("input_i")),
        "input_tp": _coerce_float(measurement.get("input_tp")),
        "input_lra": _coerce_float(measurement.get("input_lra")),
        "input_thresh": _coerce_float(measurement.get("input_thresh")),
        "target_offset": _coerce_float(measurement.get("target_offset")),
        "output_i": _coerce_float(measurement.get("output_i")),
        "output_tp": _coerce_float(measurement.get("output_tp")),
        "output_lra": _coerce_float(measurement.get("output_lra")),
        "output_thresh": _coerce_float(measurement.get("output_thresh")),
        "normalization_type": measurement.get("normalization_type"),
    }


def _build_two_pass_loudnorm_filter(
    measurement: Dict,
    target_lufs: float,
    true_peak_ceiling_db: float,
    loudness_range_target: float = DEFAULT_LOUDNESS_RANGE_TARGET,
) -> Optional[str]:
    required_values = (
        measurement.get("input_i"),
        measurement.get("input_tp"),
        measurement.get("input_lra"),
        measurement.get("input_thresh"),
        measurement.get("target_offset"),
    )
    if any(value is None for value in required_values):
        return None

    return (
        f"loudnorm=I={target_lufs}:"
        f"TP={true_peak_ceiling_db}:"
        f"LRA={loudness_range_target}:"
        f"measured_I={measurement['input_i']}:"
        f"measured_LRA={measurement['input_lra']}:"
        f"measured_TP={measurement['input_tp']}:"
        f"measured_thresh={measurement['input_thresh']}:"
        f"offset={measurement['target_offset']}:"
        "linear=true:"
        "print_format=summary"
    )


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


def get_export_format_key(label_or_key: Optional[str]) -> str:
    raw = (label_or_key or "").strip()
    if raw in EXPORT_FORMAT_PRESETS:
        return raw

    for key, preset in EXPORT_FORMAT_PRESETS.items():
        label = i18n._t(preset["label_key"], default=key)
        if raw == label:
            return key
    return "original"


def get_export_format_labels() -> List[str]:
    return [
        i18n._t(preset["label_key"], default=key)
        for key, preset in EXPORT_FORMAT_PRESETS.items()
    ]


def describe_export_format(key: Optional[str]) -> str:
    resolved_key = get_export_format_key(key)
    preset = EXPORT_FORMAT_PRESETS.get(resolved_key, EXPORT_FORMAT_PRESETS["original"])
    return i18n._t(preset["label_key"], default=resolved_key)


def _export_extension_for(source_path: str, export_format_key: Optional[str]) -> str:
    preset = EXPORT_FORMAT_PRESETS.get(
        get_export_format_key(export_format_key),
        EXPORT_FORMAT_PRESETS["original"],
    )
    extension = preset.get("extension")
    if extension:
        return extension
    _stem, ext = os.path.splitext(os.path.basename(source_path))
    return ext or ".wav"


def safe_output_path(
    output_dir: str,
    source_path: str,
    suffix: str = "_matched",
    export_format_key: Optional[str] = None,
) -> str:
    base = os.path.basename(source_path)
    stem, _ext = os.path.splitext(base)
    ext = _export_extension_for(source_path, export_format_key)
    return os.path.join(output_dir, f"{stem}{suffix}{ext}")


def _codec_args_for_output(output_path: str, export_format_key: Optional[str]) -> List[str]:
    preset = EXPORT_FORMAT_PRESETS.get(
        get_export_format_key(export_format_key),
        EXPORT_FORMAT_PRESETS["original"],
    )
    if preset.get("codec"):
        codec_args = ["-c:a", preset["codec"]]
        if preset.get("sample_rate"):
            codec_args += ["-ar", str(preset["sample_rate"])]
        return codec_args

    # Default selection for high-quality audio masters: 24-bit PCM
    codec_args = ["-c:a", "pcm_s24le"]
    ext = os.path.splitext(output_path)[1].lower()

    if ext == ".flac":
        codec_args = ["-c:a", "flac"]
    elif ext == ".mp3":
        codec_args = ["-c:a", "libmp3lame", "-b:a", "320k"]
    elif ext in {".m4a", ".aac"}:
        codec_args = ["-c:a", "aac", "-b:a", "320k"]
    elif ext in {".aif", ".aiff"}:
        codec_args = ["-c:a", "pcm_s24be"]
    elif ext == ".wav":
        codec_args = ["-c:a", "pcm_s24le"]
    return codec_args


def export_matched_file(
    source_path: str,
    output_path: str,
    gain_db: float,
    overwrite: bool = True,
    use_limiter: bool = False,
    true_peak_ceiling_db: float = -1.0,
    target_lufs: Optional[float] = None,
    export_format_key: Optional[str] = None,
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

    codec_args = _codec_args_for_output(output_path, export_format_key)

    filter_chain = f"volume={gain_db}dB"
    processing_mode = "gain"

    if use_limiter:
        loudnorm_filter = None
        if target_lufs is not None:
            measurement = measure_loudnorm_stats(
                source_path,
                target_lufs=target_lufs,
                true_peak_ceiling_db=true_peak_ceiling_db,
            )
            if measurement:
                loudnorm_filter = _build_two_pass_loudnorm_filter(
                    measurement,
                    target_lufs=target_lufs,
                    true_peak_ceiling_db=true_peak_ceiling_db,
                )

        if loudnorm_filter:
            filter_chain = loudnorm_filter
            processing_mode = "loudnorm"
        else:
            limit_linear = db_to_linear(true_peak_ceiling_db)
            filter_chain += f",alimiter=limit={limit_linear:.6f}:level=1"
            processing_mode = "soft-limiter"
            if target_lufs is not None:
                logger.debug(
                    "Falling back to soft limiter export for %s because two-pass loudnorm stats were unavailable.",
                    source_path,
                )

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

    verified_output = analyze_full_track(output_path) if result.returncode == 0 else None

    return {
        "ok": result.returncode == 0,
        "source": source_path,
        "output": output_path,
        "gain_db": gain_db,
        "use_limiter": use_limiter,
        "true_peak_ceiling_db": true_peak_ceiling_db,
        "target_lufs": target_lufs,
        "export_format_key": get_export_format_key(export_format_key),
        "export_format_label": describe_export_format(export_format_key),
        "processing_mode": processing_mode,
        "output_integrated_lufs": None if not verified_output else verified_output.get("integrated_lufs"),
        "output_true_peak_dbtp": None if not verified_output else verified_output.get("true_peak_dbtp"),
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
    
    # FFmpeg showwavespic colors can be picky about hexadecimal formats.
    # We use a solid named color to ensure the 'Bild-Fehler' is resolved.
    safe_color = "orange"
    
    # Force absolute paths
    abs_in = os.path.abspath(path)
    abs_out = os.path.abspath(out_path)
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", abs_in,
        "-filter_complex", f"showwavespic=s={width}x{height}:colors={safe_color}",
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
        logger.debug("Waveform generation timed out after 10s for %s", abs_in)
        return False
    except Exception as e:
        logger.exception("Waveform generation failed for %s: %s", abs_in, e)
        return False
