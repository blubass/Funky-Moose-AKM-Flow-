import os


def collect_importable_overview_audio(records, exists_fn=None):
    if exists_fn is None:
        exists_fn = os.path.exists

    collected = []
    for item in records or []:
        audio_path = str(item.get("audio_path") or "").strip()
        if not audio_path or not exists_fn(audio_path):
            continue
        collected.append(
            {
                "name": item.get("title") or os.path.basename(audio_path),
                "path": audio_path,
            }
        )
    return collected


def build_loaded_files_state(paths):
    normalized_paths = [str(path).strip() for path in (paths or []) if str(path).strip()]
    return {
        "hint_text": "Dateien geladen. Jetzt Analyse starten oder weitere Werke aus der Übersicht übernehmen.",
        "status_text": f"{len(normalized_paths)} Dateien geladen. Bereit für Analyse.",
        "log_lines": [
            f"Dateien geladen: {len(normalized_paths)}",
            *[f"  + {os.path.basename(path)}" for path in normalized_paths],
        ],
    }


def build_selected_work_import_state(title, audio_path):
    return {
        "hint_text": "Ein Werk liegt bereit. Analyse starten, um LUFS und Match-Werte zu berechnen.",
        "status_text": f"Werk übernommen: {title}",
        "log_lines": [f"Aus Werk übernommen: {title} -> {audio_path}"],
    }


def build_filtered_works_import_state(items):
    return {
        "paths": [item["path"] for item in items],
        "hint_text": "Mehrere Werke geladen. Analyse starten und danach die Zeilen im Ergebnisbereich prüfen.",
        "status_text": f"{len(items)} Werke in Lautheit übernommen.",
        "log_lines": [
            f"Aus Werken übernommen: {len(items)} Dateien",
            *[f"  + {item['name']} -> {item['path']}" for item in items],
        ],
    }


def enrich_analysis_item(item, target_lufs, peak_ceiling, loudness_module):
    enriched = dict(item)
    gain_db = loudness_module.calculate_gain_to_target(
        enriched.get("integrated_lufs"),
        target_lufs,
    )
    peak_source = enriched.get("true_peak_dbtp")
    if peak_source is None:
        peak_source = enriched.get("sample_peak_dbfs")
    predicted_tp = loudness_module.predict_true_peak_after_gain(
        peak_source,
        gain_db,
    )
    status = loudness_module.get_status_for_match(
        enriched.get("integrated_lufs"),
        gain_db,
        predicted_tp,
        true_peak_ceiling=peak_ceiling,
    )

    enriched["target_lufs"] = target_lufs
    enriched["gain_to_target_db"] = gain_db
    enriched["predicted_true_peak_after_gain"] = predicted_tp
    enriched["match_status"] = status
    enriched["export_info"] = "Bereit" if enriched.get("ok") else "Analyse fehlt"
    return enriched


def build_analysis_log(item):
    return (
        f"Analyse: {item.get('filename', '')} | "
        f"LUFS={item.get('integrated_lufs')} | "
        f"Gain={item.get('gain_to_target_db')} | "
        f"Status={item.get('match_status')}"
    )


def summarize_analysis_results(results):
    return {
        "total": len(results),
        "ok_count": sum(1 for item in results if item.get("ok")),
        "warn_count": sum(
            1 for item in results if item.get("match_status") == "Peak Warnung"
        ),
    }


def build_analysis_status_text(results):
    summary = summarize_analysis_results(results)
    return (
        f"{summary['total']} Dateien analysiert | "
        f"OK: {summary['ok_count']} | Peak-Warnungen: {summary['warn_count']}"
    )


def build_tree_row(item):
    export_info = item.get("export_info", "")
    if not export_info and item.get("ok"):
        export_info = "Bereit"

    limiter_label = "Ja" if item.get("used_limiter") else "Nein"
    if not item.get("used_limiter") and item.get("match_status") == "Peak Warnung":
        limiter_label = "Auto"

    row_tags = ()
    if export_info == "Exportiert":
        row_tags = ("exported",)
    elif export_info == "Fehler":
        row_tags = ("error",)
    elif item.get("match_status") == "Peak Warnung":
        row_tags = ("peak_warn",)
    elif item.get("match_status") in {"Match", "OK", "Bereit"}:
        row_tags = ("match_ok",)

    return {
        "values": (
            item.get("filename", ""),
            item.get("duration_display", ""),
            _format_optional_float(item.get("integrated_lufs")),
            _format_optional_float(item.get("true_peak_dbtp")),
            _format_optional_float(item.get("sample_peak_dbfs")),
            _format_optional_float(item.get("gain_to_target_db")),
            _format_optional_float(item.get("predicted_true_peak_after_gain")),
            item.get("match_status", ""),
            limiter_label,
            export_info,
        ),
        "tags": row_tags,
    }


def export_result_item(
    item,
    output_dir,
    peak_ceiling,
    use_limiter,
    loudness_module,
    export_format_key="original",
):
    filename = item.get("filename", "")
    gain_db = item.get("gain_to_target_db")
    source_path = item.get("path")

    if gain_db is None or not source_path:
        return {
            "exported_increment": 0,
            "warning_increment": 1,
            "update": {
                "path": source_path,
                "export_info": "Übersprungen",
            },
            "logs": [f"Übersprungen: {filename} (keine Analyse)"],
        }

    output_path = loudness_module.safe_output_path(
        output_dir,
        source_path,
        export_format_key=export_format_key,
    )
    apply_limiter = bool(use_limiter)
    result = loudness_module.export_matched_file(
        source_path,
        output_path,
        gain_db,
        use_limiter=apply_limiter,
        true_peak_ceiling_db=peak_ceiling,
        target_lufs=item.get("target_lufs"),
        export_format_key=export_format_key,
    )

    if result.get("ok"):
        limiter_info = ""
        if apply_limiter:
            limiter_info = f" | {result.get('processing_mode', 'Limiter')}"
        format_info = ""
        if result.get("export_format_label"):
            format_info = f" | {result['export_format_label']}"
        verified_info = ""
        if result.get("output_integrated_lufs") is not None:
            verified_info = (
                f" | Output {result['output_integrated_lufs']:.2f} LUFS"
            )
            if result.get("output_true_peak_dbtp") is not None:
                verified_info += f" / TP {result['output_true_peak_dbtp']:.2f} dBTP"
        return {
            "exported_increment": 1,
            "warning_increment": 0,
            "update": {
                "path": source_path,
                "output": result.get("output", output_path),
                "used_limiter": apply_limiter,
                "export_info": "Exportiert",
                "output_integrated_lufs": result.get("output_integrated_lufs"),
                "output_true_peak_dbtp": result.get("output_true_peak_dbtp"),
                "export_format_label": result.get("export_format_label"),
            },
            "logs": [
                f"Exportiert: {os.path.basename(output_path)} | "
                f"Gain {gain_db:.2f} dB{limiter_info}{format_info}{verified_info}"
            ],
        }

    logs = [
        f"Export fehlgeschlagen: {filename} | {result.get('error', '')}",
    ]
    if apply_limiter:
        logs.append("Tipp: Limiter testweise deaktivieren oder anderes Zielformat wählen.")
    return {
        "exported_increment": 0,
        "warning_increment": 1,
        "update": {
            "path": source_path,
            "export_info": "Fehler",
            "error": result.get("error", ""),
        },
        "logs": logs,
    }


def apply_export_updates(results, updates):
    update_map = {item.get("path"): item for item in updates}
    merged_results = []

    for item in results:
        updated = dict(item)
        update = update_map.get(item.get("path"))
        if update:
            updated["export_info"] = update.get(
                "export_info",
                updated.get("export_info", ""),
            )
            updated["used_limiter"] = update.get(
                "used_limiter",
                updated.get("used_limiter", False),
            )
            if update.get("output"):
                updated["exported_output"] = update.get("output")
            if update.get("output_integrated_lufs") is not None:
                updated["output_integrated_lufs"] = update.get("output_integrated_lufs")
            if update.get("output_true_peak_dbtp") is not None:
                updated["output_true_peak_dbtp"] = update.get("output_true_peak_dbtp")
            if update.get("export_format_label"):
                updated["export_format_label"] = update.get("export_format_label")
        merged_results.append(updated)

    return merged_results


def build_export_status_text(payload, auto_link, export_format_label=""):
    link_info = " | Rückverlinkung aktiv" if auto_link else ""
    format_info = f" | Format: {export_format_label}" if export_format_label else ""
    return (
        f"Export fertig: {payload.get('exported', 0)} Dateien | "
        f"Warnungen: {payload.get('warnings', 0)} | "
        f"True-Peak-Schutz fuer Export aktiv{format_info}{link_info}"
    )


def _format_optional_float(value):
    if value is None:
        return ""
    return f"{value:.2f}"
