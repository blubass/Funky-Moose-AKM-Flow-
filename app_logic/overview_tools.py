from app_logic import i18n

STATUS_SORT_ORDER = {
    "in_progress": 0,
    "ready": 1,
    "submitted": 2,
    "confirmed": 3,
}

def get_sort_label(key: str) -> str:
    """Returns the translated label for a sort key."""
    key_map = {
        "title": "ovw_sort_title",
        "status": "ovw_sort_status",
        "year": "ovw_sort_year",
        "last_change": "ovw_sort_last_change",
    }
    return i18n._t(key_map.get(key, key), default=key)


def build_dashboard_stats(entries):
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


def build_dashboard_chip_counts(stats):
    return {
        "open": stats.get("open", 0),
        "in_progress": stats.get("in_progress", 0),
        "ready": stats.get("ready", 0),
        "submitted": stats.get("submitted", 0),
        "confirmed": stats.get("confirmed", 0),
    }


def build_dashboard_completion_percent(stats):
    total = stats.get("total", 0)
    confirmed = stats.get("confirmed", 0)
    if total <= 0:
        return 0
    return int(round((confirmed / total) * 100))


def build_dashboard_status_text(stats):
    total = stats.get("total", 0)
    if total <= 0:
        return i18n._t("dash_radar_empty")

    return i18n._t(
        "dash_status_catalog",
        total=total,
        percent=build_dashboard_completion_percent(stats),
        ready=stats.get("ready", 0),
        in_progress=stats.get("in_progress", 0),
    )


def build_dashboard_focus_text(stats):
    total = stats.get("total", 0)
    if total <= 0:
        return i18n._t("dash_radar_hint")

    in_progress = stats.get("in_progress", 0)
    ready = stats.get("ready", 0)
    submitted = stats.get("submitted", 0)
    confirmed = stats.get("confirmed", 0)

    if in_progress:
        return i18n._t("dash_focus_in_progress", count=in_progress)
    if ready:
        return i18n._t("dash_focus_ready", count=ready)
    if submitted:
        return i18n._t("dash_focus_submitted", count=submitted)
    if confirmed == total:
        return i18n._t("dash_focus_confirmed", count=total)
    return i18n._t("dash_focus_moving")


def build_dashboard_meta_text(stats):
    return i18n._t(
        "dash_meta_text",
        open=stats.get("open", 0),
        prod=stats.get("with_production", 0),
        notes=stats.get("with_notes", 0),
        inst=stats.get("instrumental", 0),
    )


def build_overview_status_text(result_count, total_count):
    if total_count <= 0:
        return i18n._t("ovw_status_empty")
    if result_count <= 0:
        return i18n._t("ovw_status_no_match")
    if result_count == total_count:
        return i18n._t("ovw_status_all_visible", total=total_count)
    return i18n._t("ovw_status_partial_visible", count=result_count, total=total_count)


def build_overview_hint_text(result_count, total_count, status_filter="all", query=""):
    normalized_query = (query or "").strip()
    if total_count <= 0:
        return i18n._t("ovw_hint_empty")
    if result_count <= 0:
        if normalized_query:
            return i18n._t("ovw_hint_no_match_query", query=normalized_query)
        if status_filter != "all":
            return i18n._t("ovw_hint_no_match_filter")
        return i18n._t("ovw_status_no_match")
    return i18n._t("ovw_hint_general")


def build_overview_filter_counts(entries):
    counts = {"all": len(entries), "open": 0, "in_progress": 0, "ready": 0, "submitted": 0, "confirmed": 0}
    for item in entries:
        st = item.get("status")
        if st != "confirmed": counts["open"] += 1
        if st in counts: counts[st] += 1
    return counts


def filter_and_sort_entries(entries, query="", status_filter="all", sort_key="title", sort_desc=False):
    filtered_records = []
    normalized_query = (query or "").strip().lower()

    for item in entries:
        haystack_parts = [
            item.get("title", ""),
            item.get("duration", ""),
            item.get("composer", ""),
            item.get("production", ""),
            item.get("year", ""),
            item.get("notes", ""),
            item.get("status", ""),
            ", ".join(item.get("tags", []) if isinstance(item.get("tags"), list) else []),
        ]
        haystack = " ".join(str(part) for part in haystack_parts if part).lower()
        item_status = item.get("status", "")

        if status_filter == "open" and item_status == "confirmed":
            continue
        if status_filter not in {"all", "open"} and item_status != status_filter:
            continue
        if normalized_query and normalized_query not in haystack:
            continue

        filtered_records.append(item)

    filtered_records.sort(
        key=lambda item: _sort_value(item, sort_key, sort_desc),
        reverse=sort_desc,
    )
    return filtered_records


def build_overview_summary(result_count, status_filter="all", query="", sort_key="title", sort_desc=False, status_label=None, open_label=None):
    summary_parts = [i18n._t("ovw_summary_hits", count=result_count)]

    if status_filter == "open":
        summary_parts.append(i18n._t("ovw_summary_status", status=open_label or "open"))
    elif status_filter != "all":
        summary_parts.append(i18n._t("ovw_summary_status", status=status_label or status_filter))

    normalized_query = (query or "").strip().lower()
    if normalized_query:
        summary_parts.append(i18n._t("ovw_summary_search", query=normalized_query))

    direction = i18n._t("ovw_sort_desc" if sort_desc else "ovw_sort_asc")
    summary_parts.append(
        i18n._t("ovw_summary_sort", key=get_sort_label(sort_key), dir=direction)
    )
    return "   •   ".join(summary_parts)


def format_overview_list_label(item, status_label):
    details = []
    if item.get("duration"):
        details.append(item["duration"])
    if item.get("composer"):
        details.append(item["composer"])
    if item.get("production"):
        details.append(item["production"])
    if item.get("year"):
        details.append(item["year"])

    # Green indicator for success states
    success_indicator = "● " if item.get("status") in ["ready", "submitted", "confirmed"] else ""
    
    suffix = f" | {' | '.join(details)}" if details else ""
    return f"{success_indicator}{item['title']}{suffix}   •   {status_label}"


def _sort_value(item, sort_key, sort_desc):
    if sort_key == "status":
        return STATUS_SORT_ORDER.get(item.get("status", ""), 999)

    if sort_key == "year":
        year = str(item.get("year", "")).strip()
        if year.isdigit():
            return int(year)
        return -999999 if sort_desc else 999999

    if sort_key == "last_change":
        return item.get("last_change") or item.get("date") or ""

    return str(item.get("title", "")).lower()
