import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from openpyxl import Workbook

import akm_app
from app_logic import akm_core
from app_logic import assistant_tools
from app_logic import cover_tools
from app_logic import detail_tools
from app_logic import flow_tools
from app_logic import overview_tools
from app_logic import release_tools
from app_logic import akm_core as package_akm_core
from app_ui import path_ui_tools
from app_ui import release_view_tools
from app_workflows import loudness_workflows
from app_workflows import release_workflows
from app_controllers.batch_controller import BatchController
from app_controllers.details_controller import DetailsController
from app_controllers.loudness_controller import LoudnessController
from app_controllers.overview_controller import OverviewController
from app_controllers.project_controller import ProjectController
from app_controllers.release_controller import ReleaseController


class FakeVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeText:
    def __init__(self, value=""):
        self.value = value

    def get(self, *_args):
        return self.value

    def delete(self, *_args):
        self.value = ""

    def insert(self, *_args):
        if _args:
            self.value = _args[-1]


class FakeEntry:
    def __init__(self):
        self.value = ""
        self.focused = False

    def delete(self, *_args):
        self.value = ""

    def insert(self, _index, value):
        self.value = value

    def get(self):
        return self.value

    def focus_set(self):
        self.focused = True


class FakeTabs:
    def __init__(self, tab_ids=None):
        self.selected = None
        self.tab_ids = list(tab_ids or [])
        self.updated = False
        self.focused = False

    def select(self, value):
        self.selected = value

    def tabs(self):
        return list(self.tab_ids)

    def update_idletasks(self):
        self.updated = True

    def focus_set(self):
        self.focused = True


class FakeProgress:
    def __init__(self):
        self.options = {}

    def __setitem__(self, key, value):
        self.options[key] = value

    def __getitem__(self, key):
        return self.options.get(key)


class FakeLabel:
    def __init__(self):
        self.options = {}

    def config(self, **kwargs):
        self.options.update(kwargs)


class FakeBatchView:
    def __init__(self):
        self.flow_state = None
        self.empty_rendered = False
        self.copy_button_text = None

    def render_flow_state(self, **kwargs):
        self.flow_state = kwargs

    def render_empty_state(self):
        self.empty_rendered = True

    def set_copy_button_label(self, text):
        self.copy_button_text = text


class FakeMessagebox:
    def __init__(self, response):
        self.response = response

    def askyesnocancel(self, *_args, **_kwargs):
        return self.response


class FakeReleaseListbox:
    def __init__(self, selection=()):
        self.selection = tuple(selection)
        self.selected_index = None
        self.items = []

    def curselection(self):
        return self.selection

    def selection_set(self, index):
        self.selected_index = index

    def delete(self, *_args):
        self.items = []

    def insert(self, _index, value):
        self.items.append(value)


class FakeReleaseView:
    def __init__(self, selection=(), form_state=None):
        self.selection = tuple(selection)
        self.selected_index = None
        self.track_labels = []
        self.action_hint = None
        self.status_text = None
        self.form_state = {
            "title": "",
            "artist": "",
            "type": "",
            "cover_path": "",
            "export_dir": "",
        }
        if form_state:
            self.form_state.update(form_state)

    def has_track_list(self):
        return True

    def render_release_state(self, track_labels, action_hint, status_text):
        self.track_labels = list(track_labels)
        self.action_hint = action_hint
        self.status_text = status_text

    def get_selected_track_indices(self):
        return self.selection

    def select_track_index(self, index):
        self.selected_index = index

    def get_form_state(self):
        return dict(self.form_state)

    def set_form_state(self, values):
        self.form_state.update(values or {})

    def get_form_value(self, key):
        return (self.form_state.get(key) or "").strip()

    def set_form_value(self, key, value):
        self.form_state[key] = value


class FakeOverviewView:
    def __init__(self, selection=()):
        self.selection = tuple(selection)
        self.list_items = []
        self.row_statuses = []
        self.summary_text = None
        self.status_text = None
        self.hint_text = None
        self.empty_text = None
        self.empty_visible = None
        self.filter_chip_texts = {}
        self.filter_chip_selected = {}

    def render_overview_records(self, labels, row_statuses):
        self.list_items = list(labels)
        self.row_statuses = list(row_statuses)

    def render_overview_meta(self, *, summary_text, status_text, hint_text, empty_text, show_empty):
        self.summary_text = summary_text
        self.status_text = status_text
        self.hint_text = hint_text
        self.empty_text = empty_text
        self.empty_visible = show_empty

    def update_filter_chip(self, status_key, text, selected=False):
        self.filter_chip_texts[status_key] = text
        self.filter_chip_selected[status_key] = selected

    def get_selected_indices(self):
        return self.selection


class FakeDetailsView:
    def __init__(self, form_vars=None):
        self.title_values = []
        self.form_vars = dict(form_vars or {})
        self.notes_text = ""
        self.tags_text = ""
        self.instrumental = False
        self.status_key = None
        self.status_text = None
        self.refresh_calls = 0

    def refresh_view(self):
        self.refresh_calls += 1

    def get_form_vars(self):
        return self.form_vars

    def set_title_options(self, titles):
        self.title_values = list(titles)

    def get_notes_text(self):
        return self.notes_text

    def set_notes_text(self, text):
        self.notes_text = text or ""

    def clear_notes(self):
        self.notes_text = ""

    def get_tags_text(self):
        return self.tags_text

    def set_tags_text(self, text):
        self.tags_text = text or ""

    def clear_tags(self):
        self.tags_text = ""

    def get_instrumental(self):
        return self.instrumental

    def set_instrumental(self, value):
        self.instrumental = bool(value)

    def set_status_chip_display(self, status_key, status_label):
        self.status_key = status_key
        self.status_text = status_label


class FakeListbox:
    def __init__(self, selection=()):
        self.selection = tuple(selection)
        self.items = []
        self.row_options = {}

    def delete(self, *_args):
        self.items = []

    def insert(self, _index, *values):
        self.items.extend(values)

    def itemconfig(self, index, **kwargs):
        self.row_options[index] = kwargs

    def curselection(self):
        return self.selection


class FakeWidgetNode:
    def __init__(self, name, registry, parent=None):
        self._name = name
        self._registry = registry
        self._parent = parent
        registry[name] = self

    def winfo_parent(self):
        return "" if self._parent is None else self._parent._name

    def nametowidget(self, name):
        return self._registry[name]


class FakeNativeScrollWidget(FakeWidgetNode):
    def __init__(self, name, registry, parent=None):
        super().__init__(name, registry, parent=parent)
        self.scroll_calls = []

    def yview_scroll(self, amount, units):
        self.scroll_calls.append((amount, units))


class FakeCanvas:
    def __init__(self):
        self.scroll_calls = []

    def yview_scroll(self, amount, units):
        self.scroll_calls.append((amount, units))


class FakeScrollablePanelWidget(FakeWidgetNode):
    def __init__(self, name, registry, parent=None):
        super().__init__(name, registry, parent=parent)
        self.canvas = FakeCanvas()


class ImmediateTaskRunner:
    def run(self, task_func, on_success=None, on_error=None, busy_text=None):
        del busy_text
        try:
            result = task_func()
        except Exception as exc:
            if on_error:
                on_error(str(exc))
                return
            raise
        if on_success:
            on_success(result)


class FakeState:
    def __init__(self, records=None, mtime=None):
        self._records = list(records or [])
        self.filtered_records = []
        self.batch_queue = []
        self.batch_index = 0
        self.release_tracks = []
        self.loudness_files = []
        self.loudness_results = []
        self.current_mtime = mtime
        self.invalidated = False

    def get_all_records(self, force=False, copy_data=False):
        del force
        if copy_data:
            return [dict(item) for item in self._records]
        return self._records

    def invalidate_cache(self):
        self.invalidated = True

    def _get_data_mtime(self):
        return self.current_mtime


class FakeLoudnessModule:
    @staticmethod
    def calculate_gain_to_target(measured_lufs, target_lufs):
        if measured_lufs is None:
            return None
        return round(target_lufs - measured_lufs, 2)

    @staticmethod
    def predict_true_peak_after_gain(current_true_peak_dbtp, gain_db):
        if current_true_peak_dbtp is None or gain_db is None:
            return None
        return round(current_true_peak_dbtp + gain_db, 2)

    @staticmethod
    def get_status_for_match(measured_lufs, gain_db, predicted_true_peak, true_peak_ceiling=-1.0):
        if measured_lufs is None or gain_db is None:
            return "Analyse fehlt"
        if predicted_true_peak is not None and predicted_true_peak > true_peak_ceiling:
            return "Peak Warnung"
        if abs(gain_db) < 0.3:
            return "OK"
        return "Zu leise" if gain_db > 0 else "Zu laut"

    @staticmethod
    def safe_output_path(output_dir, source_path, suffix="_matched"):
        stem, ext = os.path.splitext(os.path.basename(source_path))
        return os.path.join(output_dir, f"{stem}{suffix}{ext}")

    @staticmethod
    def export_matched_file(source_path, output_path, gain_db, use_limiter=False, true_peak_ceiling_db=-1.0):
        return {
            "ok": True,
            "source": source_path,
            "output": output_path,
            "gain_db": gain_db,
            "use_limiter": use_limiter,
            "true_peak_ceiling_db": true_peak_ceiling_db,
            "error": "",
        }


class TemporaryStorageTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        patch_values = dict(
            DATA_DIR=self.tempdir.name,
            DATA_FILE=os.path.join(self.tempdir.name, "data.json"),
            BACKUP_FILE=os.path.join(self.tempdir.name, "data_backup.json"),
            LANG_FILE=os.path.join(self.tempdir.name, "lang.txt"),
            SETTINGS_FILE=os.path.join(self.tempdir.name, "settings.json"),
        )
        self.storage_patcher = mock.patch.multiple(
            akm_core,
            **patch_values,
        )
        self.storage_patcher.start()
        self.addCleanup(self.storage_patcher.stop)
        self.package_storage_patcher = mock.patch.multiple(
            package_akm_core,
            **patch_values,
        )
        self.package_storage_patcher.start()
        self.addCleanup(self.package_storage_patcher.stop)

    def save_entries(self, entries):
        akm_core.save_data(entries)

    def load_entries(self):
        return akm_core.load_data(strict=True)


class ExcelImportTests(TemporaryStorageTestCase):
    def test_load_excel_tracks_rejects_unsupported_extension(self):
        invalid_path = os.path.join(self.tempdir.name, "tracks.xls")
        with open(invalid_path, "w", encoding="utf-8") as handle:
            handle.write("not a workbook")

        with self.assertRaisesRegex(
            akm_core.DataFileError,
            "Nicht unterstütztes Excel-Format",
        ):
            akm_core.load_excel_tracks(invalid_path)

    def test_load_excel_tracks_reads_supported_workbook(self):
        workbook_path = os.path.join(self.tempdir.name, "tracks.xlsx")
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Titel", "Dauer", "Komponist"])
        sheet.append(["Mein Song", "3:21", "Uwe"])
        workbook.save(workbook_path)
        workbook.close()

        tracks = akm_core.load_excel_tracks(workbook_path)

        self.assertEqual(1, len(tracks))
        self.assertEqual("Mein Song", tracks[0]["title"])
        self.assertEqual("3:21", tracks[0]["duration"])
        self.assertEqual("Uwe", tracks[0]["composer"])


class OverviewToolsTests(unittest.TestCase):
    def test_build_dashboard_stats_counts_key_fields(self):
        entries = [
            {"status": "in_progress", "instrumental": True, "production": "P1", "notes": ""},
            {"status": "ready", "instrumental": False, "production": "", "notes": "note"},
            {"status": "confirmed", "instrumental": False, "production": "", "notes": ""},
        ]

        stats = overview_tools.build_dashboard_stats(entries)

        self.assertEqual(3, stats["total"])
        self.assertEqual(2, stats["open"])
        self.assertEqual(1, stats["in_progress"])
        self.assertEqual(1, stats["ready"])
        self.assertEqual(1, stats["confirmed"])
        self.assertEqual(1, stats["instrumental"])
        self.assertEqual(1, stats["with_production"])
        self.assertEqual(1, stats["with_notes"])

    def test_dashboard_helpers_build_status_focus_and_meta_texts(self):
        stats = {
            "total": 8,
            "confirmed": 3,
            "ready": 2,
            "submitted": 1,
            "in_progress": 2,
            "with_production": 5,
            "with_notes": 4,
            "instrumental": 1,
        }

        self.assertEqual(38, overview_tools.build_dashboard_completion_percent(stats))
        self.assertEqual(
            "8 Werke | 38% bestätigt | 2 bereit | 2 in Arbeit",
            overview_tools.build_dashboard_status_text(stats),
        )
        self.assertIn("2 Werk(e) brauchen noch Feinschliff", overview_tools.build_dashboard_focus_text(stats))
        self.assertEqual(
            "Mit Produktion: 5   •   Mit Notizen: 4   •   Instrumental: 1",
            overview_tools.build_dashboard_meta_text(stats),
        )

    def test_filter_and_sort_entries_applies_query_filter_and_sorting(self):
        entries = [
            {"title": "Beta", "status": "confirmed", "year": "2021", "notes": "", "tags": []},
            {"title": "Alpha", "status": "ready", "year": "2024", "notes": "Synthwave", "tags": ["focus"]},
            {"title": "Gamma", "status": "in_progress", "year": "2023", "notes": "", "tags": []},
        ]

        filtered = overview_tools.filter_and_sort_entries(
            entries,
            query="focus",
            status_filter="open",
            sort_key="year",
            sort_desc=True,
        )

        self.assertEqual(["Alpha"], [item["title"] for item in filtered])

    def test_build_overview_summary_formats_human_readable_text(self):
        summary = overview_tools.build_overview_summary(
            5,
            status_filter="ready",
            query="mix",
            sort_key="last_change",
            sort_desc=True,
            status_label="Bereit",
        )

        self.assertEqual(
            "5 Treffer   •   Status: Bereit   •   Suche: mix   •   Sortierung: Änderung absteigend",
            summary,
        )

    def test_overview_helpers_describe_empty_and_filtered_states(self):
        self.assertEqual(
            "Noch keine Werke im Katalog",
            overview_tools.build_overview_status_text(0, 0),
        )
        self.assertEqual(
            "Keine Treffer im aktuellen Filter",
            overview_tools.build_overview_status_text(0, 8),
        )
        self.assertIn(
            "keine Treffer",
            overview_tools.build_overview_hint_text(0, 4, status_filter="ready", query="mix"),
        )


class DetailToolsTests(unittest.TestCase):
    def test_detail_form_state_from_item_normalizes_for_widgets(self):
        state = detail_tools.detail_form_state_from_item(
            {
                "title": "Song",
                "duration": "3:21",
                "composer": "Uwe",
                "production": "FM",
                "year": "2026",
                "audio_path": "/tmp/song.wav",
                "instrumental": 1,
                "status": "ready",
                "notes": "Notiz",
                "tags": [" synth ", "", "focus"],
            }
        )

        self.assertEqual("Song", state["original_title"])
        self.assertEqual("Song", state["current_title"])
        self.assertEqual("3:21", state["values"]["duration"])
        self.assertTrue(state["instrumental"])
        self.assertEqual("ready", state["status"])
        self.assertEqual("synth, focus", state["tags_text"])
        self.assertEqual("Notiz", state["notes"])

    def test_build_detail_updates_trims_text_and_splits_tags(self):
        updates = detail_tools.build_detail_updates(
            {
                "title": "  Song  ",
                "duration": " 3:33 ",
                "composer": " Uwe ",
                "production": " Prod ",
                "year": " 2026 ",
                "audio_path": " /tmp/song.wav ",
            },
            " synth, , focus ,",
            "  Notiz  ",
            "submitted",
            1,
        )

        self.assertEqual("Song", updates["title"])
        self.assertEqual("3:33", updates["duration"])
        self.assertEqual("Uwe", updates["composer"])
        self.assertEqual("Prod", updates["production"])
        self.assertEqual("2026", updates["year"])
        self.assertEqual("/tmp/song.wav", updates["audio_path"])
        self.assertEqual("submitted", updates["status"])
        self.assertTrue(updates["instrumental"])
        self.assertEqual("Notiz", updates["notes"])
        self.assertEqual(["synth", "focus"], updates["tags"])

    def test_resolve_original_title_prefers_loaded_then_existing_then_current(self):
        self.assertEqual(
            "Loaded Song",
            detail_tools.resolve_original_title(
                "Loaded Song",
                "Renamed Song",
                [{"title": "Renamed Song"}],
            ),
        )
        self.assertEqual(
            "Existing Song",
            detail_tools.resolve_original_title(
                "",
                "Existing Song",
                [{"title": "Existing Song"}],
            ),
        )
        self.assertEqual(
            "Fresh Song",
            detail_tools.resolve_original_title(
                None,
                "Fresh Song",
                [{"title": "Other Song"}],
            ),
        )


class AssistantToolsTests(unittest.TestCase):
    def test_build_import_log_messages_formats_summary_and_rows(self):
        messages = assistant_tools.build_import_log_messages(
            [
                {
                    "title": "Song A",
                    "action": "added",
                    "duration": "3:11",
                    "composer": "Uwe",
                },
                {
                    "title": "Song B",
                    "action": "unchanged",
                    "duration": "",
                    "composer": "",
                },
            ]
        )

        self.assertEqual("Excel-Import abgeschlossen: 2 Einträge", messages[0])
        self.assertEqual("  + Song A (3:11 | Uwe)", messages[1])
        self.assertEqual("  = Song B", messages[2])

    def test_build_status_and_add_messages_cover_success_and_errors(self):
        self.assertEqual(
            "Neu angelegt: Song A",
            assistant_tools.build_add_result_message("Song A", True, {"title": "Song A"}),
        )
        self.assertEqual(
            "Schon vorhanden: Song A",
            assistant_tools.build_add_result_message("Song A", False, "already_exists"),
        )
        self.assertEqual(
            "Status gesetzt: Song A -> Bereit",
            assistant_tools.build_status_result_message(
                "Song A",
                True,
                "Bereit",
                {"status": "ready"},
                "ready",
            ),
        )
        self.assertEqual(
            "Nicht gefunden: Song A",
            assistant_tools.build_status_result_message(
                "Song A",
                False,
                "Bereit",
                "not_found",
                "ready",
            ),
        )

    def test_build_loudness_tab_open_state_switches_by_tool_availability(self):
        available = assistant_tools.build_loudness_tab_open_state(True)
        missing = assistant_tools.build_loudness_tab_open_state(False)

        self.assertIn("Dateien wählen", available["status_text"])
        self.assertIn("konnte nicht geladen", missing["status_text"])
        self.assertEqual(
            "Dateien laden oder direkt Werke aus der aktuellen Übersicht übernehmen.",
            available["hint_text"],
        )

    def test_build_assistant_radar_state_handles_empty_and_filled_input(self):
        empty = assistant_tools.build_assistant_radar_state("")
        filled = assistant_tools.build_assistant_radar_state("Neuer Song")

        self.assertEqual("Schnellstart bereit", empty["status_text"])
        self.assertIn("Excel-Import", empty["meta_text"])
        self.assertEqual("Bereit für neuen Titel: Neuer Song", filled["status_text"])
        self.assertIn("2 Wort/Wörter", filled["meta_text"])


class FlowToolsTests(unittest.TestCase):
    def test_resolve_flow_index_prefers_previous_title_then_clamps(self):
        entries = [
            {"title": "Alpha"},
            {"title": "Beta"},
            {"title": "Gamma"},
        ]

        self.assertEqual(
            1,
            flow_tools.resolve_flow_index(
                entries,
                current_index=0,
                previous_title="Beta",
                preferred_index=2,
            ),
        )
        self.assertEqual(
            2,
            flow_tools.resolve_flow_index(
                entries,
                current_index=1,
                previous_title="Missing",
                preferred_index=99,
            ),
        )

    def test_build_flow_state_formats_meta_progress_and_copy_label(self):
        state = flow_tools.build_flow_state(
            [
                {
                    "title": "Song A",
                    "composer": "Uwe",
                    "duration": "3:11",
                    "production": "FM",
                    "year": "2026",
                }
            ],
            0,
            "duration",
        )

        self.assertTrue(state["has_item"])
        self.assertEqual("Song A", state["title_text"])
        self.assertEqual(
            "Komponist: Uwe   Dauer: 3:11   Produktion: FM   Jahr: 2026",
            state["meta_text"],
        )
        self.assertEqual("1 / 1", state["progress_text"])
        self.assertEqual(100.0, state["progress_value"])
        self.assertEqual("Dauer kopieren", state["copy_button_label"])

    def test_resolve_copy_action_cycles_title_then_duration(self):
        item = {"title": "Song A", "duration": "3:11"}

        title_step = flow_tools.resolve_copy_action(item, "title")
        duration_step = flow_tools.resolve_copy_action(item, "duration")

        self.assertEqual("Song A", title_step["value"])
        self.assertEqual("duration", title_step["next_stage"])
        self.assertFalse(title_step["advance_after_copy"])
        self.assertEqual("3:11", duration_step["value"])
        self.assertEqual("title", duration_step["next_stage"])
        self.assertTrue(duration_step["advance_after_copy"])

    def test_next_flow_index_wraps_at_end(self):
        self.assertEqual(0, flow_tools.next_flow_index(2, 3))
        self.assertEqual(1, flow_tools.next_flow_index(0, 3))

    def test_flow_dashboard_helpers_describe_queue_and_next_action(self):
        entries = [
            {"title": "Song A", "status": "in_progress", "duration": "3:11"},
            {"title": "Song B", "status": "ready"},
        ]
        flow_state = flow_tools.build_flow_state(entries, 0, "title")

        self.assertEqual(
            {"in_progress": 1, "ready": 1},
            flow_tools.build_flow_queue_counts(entries),
        )
        self.assertEqual(
            "1 / 2 im Fokus | Song A",
            flow_tools.build_flow_status_text(entries, flow_state),
        )
        self.assertIn(
            "Copy-Button automatisch auf die Dauer",
            flow_tools.build_flow_hint_text(entries, flow_state, "title"),
        )
        self.assertEqual(
            "In Arbeit: 1   •   Bereit: 1   •   Queue: 2",
            flow_tools.build_flow_meta_summary(entries),
        )


class ReleaseWorkflowTests(unittest.TestCase):
    def test_clean_release_drop_paths_dedupes_and_strips_braces(self):
        paths = release_workflows.clean_release_drop_paths(
            ["{/tmp/a.wav}", " /tmp/b.wav ", "/tmp/a.wav", ""]
        )

        self.assertEqual(["/tmp/a.wav", "/tmp/b.wav"], paths)

    def test_append_unique_release_tracks_skips_duplicates(self):
        result = release_workflows.append_unique_release_tracks(
            [{"title": "Song A", "source": "Werk", "audio_path": "/a.wav"}],
            [
                {"title": "Song A", "source": "Werk", "audio_path": "/a-other.wav"},
                {"title": "Song B", "source": "Datei", "audio_path": "/b.wav"},
            ],
        )

        self.assertEqual(2, len(result["tracks"]))
        self.assertEqual("Song B", result["added"][0]["title"])
        self.assertEqual("Song A", result["duplicates"][0]["title"])

    def test_move_release_track_and_target_name_helpers(self):
        moved, new_index = release_workflows.move_release_track(
            [{"title": "A"}, {"title": "B"}],
            0,
            1,
        )
        target_name = release_workflows.build_release_audio_target_name(
            2,
            {"title": "My:Song?"},
            "/tmp/source.wav",
        )

        self.assertEqual(1, new_index)
        self.assertEqual("B", moved[0]["title"])
        self.assertEqual("02 - My_Song_.wav", target_name)

    def test_build_release_export_text_helpers(self):
        info_lines = release_workflows.build_release_info_lines(
            {
                "title": "Release",
                "artist": "Artist",
                "type": "Album",
                "release_date": "2026-04-05",
                "genre": "Pop",
                "subgenre": "Indie",
                "label": "Label",
                "copyright_line": "C 2026",
                "cover_path": "/tmp/cover.jpg",
            }
        )
        checklist = release_workflows.build_release_checklist_lines(
            "/tmp/cover.jpg",
            [{"title": "Song"}],
            1,
            0,
        )

        self.assertEqual("Release Title: Release", info_lines[0])
        self.assertEqual("Cover gesetzt: Ja", checklist[0])
        self.assertEqual("Tracks im Release: 1", checklist[1])


class PathUiToolsTests(unittest.TestCase):
    def test_validate_existing_path_and_message_helpers(self):
        normalized, error = path_ui_tools.validate_existing_path(
            "",
            "Kein Pfad gesetzt.",
            "Datei nicht gefunden",
        )
        found_path, found_error = path_ui_tools.validate_existing_path(
            "/tmp/missing.wav",
            "Kein Pfad gesetzt.",
            "Datei nicht gefunden",
            exists_fn=lambda _path: False,
        )

        self.assertEqual("", normalized)
        self.assertEqual("Kein Pfad gesetzt.", error)
        self.assertEqual("/tmp/missing.wav", found_path)
        self.assertEqual("Datei nicht gefunden: /tmp/missing.wav", found_error)
        self.assertEqual(
            "Audio-Pfad gesetzt: song.wav",
            path_ui_tools.build_file_set_message("Audio-Pfad gesetzt", "/tmp/song.wav"),
        )


class LoudnessWorkflowTests(unittest.TestCase):
    def test_collect_importable_overview_audio_and_build_states(self):
        items = loudness_workflows.collect_importable_overview_audio(
            [
                {"title": "Song A", "audio_path": "/tmp/a.wav"},
                {"title": "Song B", "audio_path": "/tmp/missing.wav"},
            ],
            exists_fn=lambda path: path == "/tmp/a.wav",
        )
        loaded_state = loudness_workflows.build_loaded_files_state(
            ["/tmp/a.wav", "/tmp/b.wav"]
        )
        filtered_state = loudness_workflows.build_filtered_works_import_state(items)

        self.assertEqual([{"name": "Song A", "path": "/tmp/a.wav"}], items)
        self.assertEqual("2 Dateien geladen. Bereit für Analyse.", loaded_state["status_text"])
        self.assertEqual(["/tmp/a.wav"], filtered_state["paths"])
        self.assertEqual("1 Werke in Lautheit übernommen.", filtered_state["status_text"])

    def test_enrich_analysis_item_adds_match_fields(self):
        item = loudness_workflows.enrich_analysis_item(
            {
                "filename": "track.wav",
                "integrated_lufs": -16.0,
                "true_peak_dbtp": -2.0,
                "sample_peak_dbfs": -2.5,
                "ok": True,
            },
            -14.0,
            -1.0,
            FakeLoudnessModule,
        )

        self.assertEqual(2.0, item["gain_to_target_db"])
        self.assertEqual(0.0, item["predicted_true_peak_after_gain"])
        self.assertEqual("Peak Warnung", item["match_status"])
        self.assertEqual("Bereit", item["export_info"])

    def test_build_tree_row_formats_values_and_tags(self):
        row = loudness_workflows.build_tree_row(
            {
                "filename": "track.wav",
                "duration_display": "3:20",
                "integrated_lufs": -14.12,
                "true_peak_dbtp": -1.05,
                "sample_peak_dbfs": -1.4,
                "gain_to_target_db": 0.12,
                "predicted_true_peak_after_gain": -0.93,
                "match_status": "Peak Warnung",
                "export_info": "Bereit",
            }
        )

        self.assertEqual(("peak_warn",), row["tags"])
        self.assertEqual("track.wav", row["values"][0])
        self.assertEqual("-14.12", row["values"][2])
        self.assertEqual("Auto", row["values"][8])

    def test_export_result_item_marks_success_and_limiter_usage(self):
        result = loudness_workflows.export_result_item(
            {
                "filename": "track.wav",
                "path": "/tmp/track.wav",
                "gain_to_target_db": 1.5,
                "match_status": "Peak Warnung",
            },
            "/exports",
            -1.0,
            True,
            FakeLoudnessModule,
        )

        self.assertEqual(1, result["exported_increment"])
        self.assertEqual(0, result["warning_increment"])
        self.assertTrue(result["update"]["used_limiter"])
        self.assertEqual("Exportiert", result["update"]["export_info"])

    def test_apply_export_updates_merges_outputs_into_results(self):
        merged = loudness_workflows.apply_export_updates(
            [
                {"path": "/a.wav", "export_info": "Bereit"},
                {"path": "/b.wav", "export_info": "Bereit"},
            ],
            [
                {"path": "/b.wav", "export_info": "Exportiert", "output": "/out/b.wav"},
            ],
        )

        self.assertEqual("Bereit", merged[0]["export_info"])
        self.assertEqual("Exportiert", merged[1]["export_info"])
        self.assertEqual("/out/b.wav", merged[1]["exported_output"])


@unittest.skipUnless(cover_tools.have_pillow(), "Pillow not available")
class CoverToolsTests(unittest.TestCase):
    def test_resize_cover_canvas_returns_requested_size(self):
        image = cover_tools.Image.new("RGB", (400, 200), color="navy")

        resized = cover_tools.resize_cover_canvas(image, 300, 300)

        self.assertEqual((300, 300), resized.size)

    def test_generate_cover_variants_creates_expected_files(self):
        with tempfile.TemporaryDirectory() as tempdir:
            cover_path = os.path.join(tempdir, "cover.png")
            output_dir = os.path.join(tempdir, "out")
            os.makedirs(output_dir, exist_ok=True)

            image = cover_tools.Image.new("RGB", (800, 800), color="black")
            image.save(cover_path)

            created = cover_tools.generate_cover_variants(
                cover_path=cover_path,
                title="Test Release",
                artist="Test Artist",
                output_dir=output_dir,
                selected_layouts=["bottom", "topleft", "center"],
                selected_formats=["square"],
                options={
                    "style": "clean",
                    "size_mode": "medium",
                    "offset": "normal",
                    "overlay": "medium",
                },
            )

            self.assertEqual(3, len(created))
            self.assertTrue(created[0].endswith("cover_bottom_1x1.jpg"))
            self.assertTrue(created[1].endswith("cover_topleft_1x1.jpg"))
            self.assertTrue(created[2].endswith("cover_center_1x1.jpg"))
            for path in created:
                self.assertTrue(os.path.exists(path))


class ReleaseViewToolsTests(unittest.TestCase):
    def test_release_cover_output_dir_prefers_export_dir(self):
        output_dir = release_view_tools.release_cover_output_dir(
            "/tmp/export",
            "/tmp/source/cover.jpg",
        )

        self.assertEqual("/tmp/export/cover_previews", output_dir)

    def test_selected_release_cover_layouts_falls_back_to_defaults(self):
        selected = release_view_tools.selected_release_cover_layouts(
            {
                "bottom": False,
                "topleft": False,
                "center": False,
            }
        )

        self.assertEqual(["bottom", "topleft", "center"], selected)

    def test_build_release_track_row_label_and_status_text(self):
        label = release_view_tools.build_release_track_row_label(
            2,
            {
                "title": "Song",
                "duration": "3:12",
                "production": "Prod",
                "year": "2026",
                "source": "Werk",
            },
        )
        status = release_view_tools.build_release_status_text(
            4,
            True,
            False,
            True,
        )

        self.assertEqual("02. Song | 3:12 | Prod | 2026 | Werk", label)
        self.assertEqual(
            "4 Tracks im Release | Cover: Ja | Export-Ordner: Nein | Drag&Drop aktiv",
            status,
        )


class AppRegressionTests(TemporaryStorageTestCase):
    def make_app_stub(self, records=None, mtime=None):
        app = SimpleNamespace()
        app.logs = []
        app.toasts = []
        app.state = FakeState(records=records, mtime=mtime)
        app.tasks = ImmediateTaskRunner()
        app.tab_system = SimpleNamespace(_instances={})
        app.get_built_tab = lambda tab_id: app.tab_system._instances.get(tab_id)
        app.cover_state_cache = {}
        app.release_state_cache = {}
        app.append_log = app.logs.append
        app.select_tab_by_id = lambda tab_id: setattr(app, "selected_tab", tab_id)
        app.status_text = lambda status: status
        app.get_detail_form_vars = lambda: (
            app.tab_system._instances["details"].get_form_vars()
            if "details" in app.tab_system._instances
            and hasattr(app.tab_system._instances["details"], "get_form_vars")
            else getattr(app, "detail_vars", {})
        )
        app.get_release_form_vars = lambda: (
            app.tab_system._instances["release"].get_form_state()
            if "release" in app.tab_system._instances
            and hasattr(app.tab_system._instances["release"], "get_form_state")
            else dict(app.release_state_cache)
        )
        return app

    def test_batch_controller_update_flow_applies_meta_progress_and_copy_label(self):
        app = self.make_app_stub()
        app.state.batch_queue = [
            {
                "title": "Song A",
                "composer": "Uwe",
                "duration": "3:11",
                "production": "FM",
                "year": "2026",
            }
        ]
        app.copy_stage = "duration"
        batch_view = FakeBatchView()
        app.tab_system._instances["batch"] = batch_view

        controller = BatchController(app)
        controller.update_flow()

        self.assertEqual("Song A", app.current_title)
        self.assertEqual("Song A", batch_view.flow_state["title_text"])
        self.assertEqual(
            "Komponist: Uwe   Dauer: 3:11   Produktion: FM   Jahr: 2026",
            batch_view.flow_state["meta_text"],
        )
        self.assertEqual("1 / 1", batch_view.flow_state["progress_text"])
        self.assertEqual(100.0, batch_view.flow_state["progress_value"])
        self.assertEqual("Dauer kopieren", batch_view.flow_state["copy_button_label"])
        self.assertTrue(batch_view.flow_state["enabled"])

    def test_project_controller_import_done_logs_summary_and_refreshes_overview(self):
        app = self.make_app_stub()
        app.overview_ctrl = SimpleNamespace(
            refresh_list=lambda: setattr(app, "overview_refreshed", True)
        )
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = app.toasts.append

        controller._on_import_done(
            [
                {
                    "title": "Song A",
                    "action": "added",
                    "duration": "3:11",
                    "composer": "Uwe",
                },
                {
                    "title": "Song B",
                    "action": "updated",
                    "duration": "",
                    "composer": "",
                },
            ]
        )

        self.assertEqual("Excel-Import abgeschlossen: 2 Einträge", app.logs[0])
        self.assertEqual("  + Song A (3:11 | Uwe)", app.logs[1])
        self.assertEqual("  ~ Song B", app.logs[2])
        self.assertEqual("Excel-Import abgeschlossen: 2 Einträge", app.toasts[0])
        self.assertTrue(app.state.invalidated)
        self.assertTrue(app.overview_refreshed)

    def test_project_controller_add_entry_calls_core_without_legacy_language_arg(self):
        app = self.make_app_stub()
        app.overview_ctrl = SimpleNamespace(
            _on_g_done=lambda result, message: setattr(app, "done_payload", (result, message))
        )
        controller = ProjectController(app)

        with mock.patch(
            "app_controllers.project_controller.akm_core.add_entry",
            return_value=(True, {"title": "Song A"}),
        ) as add_entry:
            controller.add_entry("Song A")

        add_entry.assert_called_once_with("Song A")
        self.assertEqual("'Song A' angelegt", app.done_payload[1])

    def test_project_controller_save_project_returns_false_when_dialog_cancelled(self):
        app = self.make_app_stub()
        app.cover_tab = SimpleNamespace(get_state=lambda: {})
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = lambda message, **kwargs: app.toasts.append((message, kwargs))

        fake_dialog = SimpleNamespace(result=None)
        app.wait_window = lambda dialog: None

        with mock.patch(
            "app_controllers.project_controller.ui_patterns.AkmSaveDialog",
            return_value=fake_dialog,
        ):
            saved = controller.save_project()

        self.assertFalse(saved)
        self.assertIn("Speichervorgang abgebrochen.", app.logs)

    def test_project_controller_save_project_uses_cached_release_state_without_built_release_tab(self):
        app = self.make_app_stub()
        app.release_state_cache = {
            "artist": "Loaded Artist",
            "type": "EP",
            "cover_path": "/tmp/cover.png",
        }
        app.cover_tab = SimpleNamespace(get_state=lambda: {})
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = lambda message, **kwargs: app.toasts.append((message, kwargs))

        fake_dialog = SimpleNamespace(result=os.path.join(self.tempdir.name, "demo.akm"))
        app.wait_window = lambda dialog: None

        with mock.patch(
            "app_controllers.project_controller.ui_patterns.AkmSaveDialog",
            return_value=fake_dialog,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.PROJECTS_DIR",
            self.tempdir.name,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.save_project",
        ) as save_project:
            saved = controller.save_project()

        self.assertTrue(saved)
        release_state = save_project.call_args.args[3]
        self.assertEqual(app.release_state_cache, release_state["vars"])
        self.assertEqual([], release_state["tracks"])

    def test_project_controller_save_project_uses_cached_cover_state_without_built_cover_tab(self):
        app = self.make_app_stub()
        app.cover_state_cache = {
            "title": "Loaded Cover Title",
            "layout": "center",
            "accent_color": "#ffaa00",
        }
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = lambda message, **kwargs: app.toasts.append((message, kwargs))

        fake_dialog = SimpleNamespace(result=os.path.join(self.tempdir.name, "demo.akm"))
        app.wait_window = lambda dialog: None

        with mock.patch(
            "app_controllers.project_controller.ui_patterns.AkmSaveDialog",
            return_value=fake_dialog,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.PROJECTS_DIR",
            self.tempdir.name,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.save_project",
        ) as save_project:
            saved = controller.save_project()

        self.assertTrue(saved)
        cover_state = save_project.call_args.args[2]
        self.assertEqual(app.cover_state_cache, cover_state)

    def test_project_controller_save_project_prefers_built_cover_tab_state_over_cache(self):
        app = self.make_app_stub()
        app.cover_state_cache = {"title": "Stale Cached Title"}
        app.tab_system._instances["cover"] = SimpleNamespace(
            get_state=lambda: {"title": "Live Cover Title", "layout": "manual"}
        )
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = lambda message, **kwargs: app.toasts.append((message, kwargs))

        fake_dialog = SimpleNamespace(result=os.path.join(self.tempdir.name, "demo.akm"))
        app.wait_window = lambda dialog: None

        with mock.patch(
            "app_controllers.project_controller.ui_patterns.AkmSaveDialog",
            return_value=fake_dialog,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.PROJECTS_DIR",
            self.tempdir.name,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.save_project",
        ) as save_project:
            saved = controller.save_project()

        self.assertTrue(saved)
        cover_state = save_project.call_args.args[2]
        self.assertEqual({"title": "Live Cover Title", "layout": "manual"}, cover_state)
        self.assertEqual(cover_state, app.cover_state_cache)

    def test_project_controller_load_project_caches_cover_state_without_built_cover_tab(self):
        app = self.make_app_stub()
        app.overview_ctrl = SimpleNamespace(
            refresh_list=lambda: setattr(app, "overview_refreshed", True)
        )
        app.release_ctrl = SimpleNamespace(
            refresh_view=lambda force=False: setattr(app, "release_refresh_force", force)
        )
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = lambda message, **kwargs: app.toasts.append((message, kwargs))

        fake_dialog = SimpleNamespace(result=os.path.join(self.tempdir.name, "demo.akm"))
        app.wait_window = lambda dialog: None
        bundle = {
            "data": [{"title": "Song A"}],
            "cover": {"title": "Loaded Cover Title", "layout": "center"},
        }

        with mock.patch(
            "app_controllers.project_controller.ui_patterns.AkmLoadDialog",
            return_value=fake_dialog,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.PROJECTS_DIR",
            self.tempdir.name,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.load_project",
            return_value=bundle,
        ):
            controller.load_project_dialog()

        self.assertEqual(bundle["cover"], app.cover_state_cache)
        self.assertTrue(app.overview_refreshed)

    def test_project_controller_load_project_updates_built_cover_tab_state(self):
        app = self.make_app_stub()
        app.overview_ctrl = SimpleNamespace(
            refresh_list=lambda: setattr(app, "overview_refreshed", True)
        )
        app.release_ctrl = SimpleNamespace(
            refresh_view=lambda force=False: setattr(app, "release_refresh_force", force)
        )
        app.tab_system._instances["cover"] = SimpleNamespace(
            set_state=lambda state: setattr(app, "loaded_cover_state", state)
        )
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = lambda message, **kwargs: app.toasts.append((message, kwargs))

        fake_dialog = SimpleNamespace(result=os.path.join(self.tempdir.name, "demo.akm"))
        app.wait_window = lambda dialog: None
        bundle = {
            "data": [{"title": "Song A"}],
            "cover": {"title": "Loaded Cover Title", "layout": "center"},
        }

        with mock.patch(
            "app_controllers.project_controller.ui_patterns.AkmLoadDialog",
            return_value=fake_dialog,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.PROJECTS_DIR",
            self.tempdir.name,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.load_project",
            return_value=bundle,
        ):
            controller.load_project_dialog()

        self.assertEqual(bundle["cover"], app.cover_state_cache)
        self.assertEqual(bundle["cover"], app.loaded_cover_state)

    def test_project_controller_load_project_caches_release_state_without_built_release_tab(self):
        app = self.make_app_stub()
        app.overview_ctrl = SimpleNamespace(
            refresh_list=lambda: setattr(app, "overview_refreshed", True)
        )
        app.release_ctrl = SimpleNamespace(
            refresh_view=lambda force=False: setattr(app, "release_refresh_force", force)
        )
        controller = ProjectController(app)
        controller.log = app.logs.append
        controller.toast = lambda message, **kwargs: app.toasts.append((message, kwargs))

        fake_dialog = SimpleNamespace(result=os.path.join(self.tempdir.name, "demo.akm"))
        app.wait_window = lambda dialog: None
        bundle = {
            "data": [{"title": "Song A"}],
            "release": {
                "vars": {"artist": "Loaded Artist", "cover_path": "/tmp/cover.png"},
                "tracks": [{"title": "Song A", "audio_path": "/tmp/song.wav"}],
            },
        }

        with mock.patch(
            "app_controllers.project_controller.ui_patterns.AkmLoadDialog",
            return_value=fake_dialog,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.PROJECTS_DIR",
            self.tempdir.name,
        ), mock.patch(
            "app_controllers.project_controller.akm_core.load_project",
            return_value=bundle,
        ):
            controller.load_project_dialog()

        self.assertEqual(bundle["release"]["vars"], app.release_state_cache)
        self.assertEqual(bundle["release"]["tracks"], app.state.release_tracks)
        self.assertTrue(app.overview_refreshed)
        self.assertTrue(app.release_refresh_force)

    def test_on_closing_keeps_window_open_when_save_is_cancelled(self):
        app = SimpleNamespace(
            save_project=lambda: False,
            destroy=lambda: setattr(app, "destroyed", True),
        )
        app.destroyed = False

        with mock.patch.object(akm_app, "messagebox", FakeMessagebox(True)):
            akm_app.AKMApp.on_closing(app)

        self.assertFalse(app.destroyed)

    def test_on_closing_destroys_window_after_successful_save(self):
        app = SimpleNamespace(
            save_project=lambda: True,
            destroy=lambda: setattr(app, "destroyed", True),
        )
        app.destroyed = False

        with mock.patch.object(akm_app, "messagebox", FakeMessagebox(True)):
            akm_app.AKMApp.on_closing(app)

        self.assertTrue(app.destroyed)

    def test_refresh_all_tabs_includes_details_and_built_cover_refresh(self):
        app = SimpleNamespace(
            search_var=FakeVar("Song"),
            status_filter_var=FakeVar("ready"),
            sort_key_var=FakeVar("year"),
            sort_desc_var=FakeVar(True),
            state=FakeState(mtime=42),
            overview_ctrl=SimpleNamespace(
                refresh_list=lambda: setattr(app, "overview_refreshed", True),
                refresh_dashboard=lambda: setattr(app, "dashboard_refreshed", True),
            ),
            details_ctrl=SimpleNamespace(
                refresh_view=lambda: setattr(app, "details_refreshed", True)
            ),
            batch_ctrl=SimpleNamespace(
                reload_flow_data=lambda: setattr(app, "batch_refreshed", True)
            ),
            release_ctrl=SimpleNamespace(
                refresh_view=lambda: setattr(app, "release_refreshed", True)
            ),
            tab_system=SimpleNamespace(
                _instances={
                    "cover": SimpleNamespace(
                        refresh_view=lambda: setattr(app, "cover_refreshed", True)
                    )
                }
            ),
            _last_overview_refresh={
                "search": None,
                "filter": None,
                "sort": None,
                "desc": None,
                "mtime": None,
            },
            _last_dashboard_refresh={"mtime": None},
            _last_batch_refresh={"mtime": None},
        )
        app.overview_refreshed = False
        app.dashboard_refreshed = False
        app.details_refreshed = False
        app.batch_refreshed = False
        app.release_refreshed = False
        app.cover_refreshed = False

        akm_app.AKMApp.refresh_all_tabs(app)

        self.assertTrue(app.overview_refreshed)
        self.assertTrue(app.dashboard_refreshed)
        self.assertTrue(app.details_refreshed)
        self.assertTrue(app.batch_refreshed)
        self.assertTrue(app.release_refreshed)
        self.assertTrue(app.cover_refreshed)
        self.assertEqual(
            {
                "search": "song",
                "filter": "ready",
                "sort": "year",
                "desc": True,
                "mtime": 42,
            },
            app._last_overview_refresh,
        )
        self.assertEqual(42, app._last_dashboard_refresh["mtime"])
        self.assertEqual(42, app._last_batch_refresh["mtime"])

    def test_overview_controller_refresh_list_clears_stale_ui_when_no_records(self):
        app = self.make_app_stub(records=[], mtime=None)
        app.state.filtered_records = [{"title": "Veraltet"}]
        app.search_var = FakeVar("")
        app.status_filter_var = FakeVar("all")
        app.sort_key_var = FakeVar("title")
        app.sort_desc_var = FakeVar(False)
        overview_view = FakeOverviewView()
        overview_view.list_items = ["Stale Row"]
        app.tab_system._instances["overview"] = overview_view

        controller = OverviewController(app)
        controller.refresh_list()

        self.assertEqual([], app.state.filtered_records)
        self.assertEqual([], overview_view.list_items)
        self.assertEqual(
            "0 Treffer   •   Sortierung: Titel aufsteigend",
            overview_view.summary_text,
        )
        self.assertEqual("all  0", overview_view.filter_chip_texts["all"])
        self.assertTrue(overview_view.filter_chip_selected["all"])

    def test_details_controller_save_details_updates_loaded_record(self):
        self.save_entries(
            [
                {
                    "title": "Song A",
                    "status": "in_progress",
                    "date": "2026-01-01",
                    "last_change": "2026-01-01",
                    "duration": "",
                    "composer": "",
                    "production": "",
                    "year": "",
                    "instrumental": False,
                    "notes": "old A",
                    "audio_path": "",
                    "tags": [],
                },
                {
                    "title": "Song B",
                    "status": "in_progress",
                    "date": "2026-01-01",
                    "last_change": "2026-01-01",
                    "duration": "",
                    "composer": "",
                    "production": "",
                    "year": "",
                    "instrumental": False,
                    "notes": "old B",
                    "audio_path": "",
                    "tags": [],
                },
            ]
        )

        app = self.make_app_stub()
        app.detail_original_title = "Song A"
        app.current_detail_status = "ready"
        details_view = FakeDetailsView(
            form_vars={
            "title": FakeVar("Song A"),
            "duration": FakeVar(""),
            "composer": FakeVar(""),
            "production": FakeVar(""),
            "year": FakeVar(""),
            "audio_path": FakeVar(""),
            }
        )
        details_view.set_notes_text("updated A")
        details_view.set_tags_text("")
        details_view.set_instrumental(False)
        app.tab_system._instances["details"] = details_view
        app.overview_ctrl = SimpleNamespace(
            _on_g_done=lambda result, message: setattr(app, "saved_payload", (result, message))
        )

        controller = DetailsController(app)
        controller.save_details()

        entries = {item["title"]: item for item in self.load_entries()}
        self.assertEqual("updated A", entries["Song A"]["notes"])
        self.assertEqual("old B", entries["Song B"]["notes"])
        self.assertTrue(app.saved_payload[0][0])
        self.assertEqual("Gespeichert", app.saved_payload[1])

    def test_details_controller_set_status_chip_updates_public_state(self):
        app = self.make_app_stub()
        app.current_detail_status = "in_progress"
        details_view = FakeDetailsView()
        app.tab_system._instances["details"] = details_view
        app.status_text = lambda status: f"label:{status}"

        controller = DetailsController(app)
        controller.set_status_chip("ready")

        self.assertEqual("ready", app.current_detail_status)
        self.assertEqual("ready", details_view.status_key)
        self.assertEqual("label:ready", details_view.status_text)

    def test_loudness_controller_import_filtered_works_updates_state_and_labels(self):
        app = self.make_app_stub()
        app.state.filtered_records = [
            {"title": "Song A", "audio_path": "/tmp/a.wav"},
            {"title": "Song B", "audio_path": "/tmp/missing.wav"},
        ]
        app.loudness_hint_label = FakeLabel()
        app.loudness_status_label = FakeLabel()
        app.loudness_log = FakeText("")

        controller = LoudnessController(app)
        controller._pop_l_tree = lambda: setattr(app, "loudness_tree_cleared", True)
        controller.log = app.logs.append

        with mock.patch(
            "app_workflows.loudness_workflows.os.path.exists",
            side_effect=lambda path: path == "/tmp/a.wav",
        ):
            controller.import_filtered_works()

        self.assertEqual(["/tmp/a.wav"], app.state.loudness_files)
        self.assertEqual([], app.state.loudness_results)
        self.assertTrue(app.loudness_tree_cleared)
        self.assertEqual("1 Werke in Lautheit übernommen.", app.loudness_status_label.options["text"])
        self.assertEqual("loudness", app.selected_tab)
        self.assertIn("Aus Werken übernommen: 1 Dateien", app.logs)

    def test_release_controller_handle_drop_deduplicates_and_matches_titles(self):
        matched_path = os.path.join(self.tempdir.name, "01 - Intro_matched.wav")
        with open(matched_path, "wb") as handle:
            handle.write(b"audio")

        app = self.make_app_stub(
            records=[
                {
                    "title": "Intro",
                    "duration": "1:11",
                    "production": "Prod",
                    "year": "2026",
                    "audio_path": "",
                }
            ]
        )
        release_view = FakeReleaseView()
        app.tab_system._instances["release"] = release_view
        app.tasks.parse_dnd_files = lambda _data: [matched_path, matched_path]

        controller = ReleaseController(app)
        controller.log = app.logs.append
        controller.toast = app.toasts.append

        controller.handle_drop(SimpleNamespace(data="ignored"))

        self.assertEqual(1, len(app.state.release_tracks))
        self.assertEqual("Datei→Werk", app.state.release_tracks[0]["source"])
        self.assertEqual("01. Intro | 1:11 | Prod | 2026 | Datei→Werk", release_view.track_labels[0])
        self.assertIn("Release DnD: 1 Tracks hinzugefügt.", app.logs)
        self.assertEqual("1 TRACKS HINZUGEFÜGT", app.toasts[0])

    def test_loudness_controller_handle_drop_uses_shared_parser_and_skips_duplicates(self):
        first_path = os.path.join(self.tempdir.name, "first.wav")
        second_path = os.path.join(self.tempdir.name, "second.mp3")
        with open(first_path, "wb") as handle:
            handle.write(b"audio")
        with open(second_path, "wb") as handle:
            handle.write(b"audio")

        app = self.make_app_stub()
        app.state.loudness_files = [first_path]
        app.tasks.parse_dnd_files = lambda _data: [first_path, second_path, "/tmp/missing.flac"]
        controller = LoudnessController(app)
        controller._pop_l_tree = lambda: setattr(app, "loudness_tree_reloaded", True)
        controller._apply_workflow_state = lambda state: setattr(app, "workflow_state", state)
        controller.log = app.logs.append
        controller.toast = app.toasts.append

        controller.handle_drop(SimpleNamespace(data="ignored"))

        self.assertEqual([first_path, second_path], app.state.loudness_files)
        self.assertTrue(app.loudness_tree_reloaded)
        self.assertEqual("1 DATEIEN HINZUGEFÜGT", app.toasts[0])

    def test_release_title_matching_requires_exact_normalized_match(self):
        source_path = os.path.join(self.tempdir.name, "Intro.wav")
        with open(source_path, "wb") as handle:
            handle.write(b"audio")

        title_work = release_tools.find_work_by_title_like_audio_path(
            [
                {
                    "title": "Intro Remix",
                    "duration": "",
                    "production": "",
                    "year": "",
                    "audio_path": "",
                }
            ],
            source_path,
        )
        track = release_workflows.build_release_track_from_match(
            source_path,
            title_work=title_work,
        )

        self.assertIsNone(title_work)
        self.assertEqual("Datei", track["source"])
        self.assertEqual("Intro", track["title"])

    def test_release_title_matching_keeps_exact_normalized_matches(self):
        source_path = os.path.join(self.tempdir.name, "01 - Intro_matched.wav")
        with open(source_path, "wb") as handle:
            handle.write(b"audio")

        title_work = release_tools.find_work_by_title_like_audio_path(
            [
                {
                    "title": "Intro",
                    "duration": "1:11",
                    "production": "Prod",
                    "year": "2026",
                    "audio_path": "",
                }
            ],
            source_path,
        )
        track = release_workflows.build_release_track_from_match(
            source_path,
            title_work=title_work,
        )

        self.assertEqual("Datei→Werk", track["source"])
        self.assertEqual("Intro", track["title"])
        self.assertEqual("1:11", track["duration"])

    def test_root_mousewheel_routes_scroll_to_nearest_scrollable_panel(self):
        registry = {}
        panel = FakeScrollablePanelWidget("panel", registry)
        label = FakeWidgetNode("label", registry, parent=panel)
        app = SimpleNamespace(winfo_containing=lambda *_args: label)

        with mock.patch.object(
            akm_app.ui_patterns,
            "AkmScrollablePanel",
            FakeScrollablePanelWidget,
        ):
            akm_app.AKMApp._on_root_mousewheel(
                app,
                SimpleNamespace(x_root=12, y_root=18, num=4, delta=0),
            )

        self.assertEqual([(-1, "units")], panel.canvas.scroll_calls)

    def test_root_mousewheel_prefers_native_scrollable_widgets(self):
        registry = {}
        listbox = FakeNativeScrollWidget("listbox", registry)
        app = SimpleNamespace(winfo_containing=lambda *_args: listbox)

        with mock.patch.object(akm_app.tk, "Listbox", FakeNativeScrollWidget):
            akm_app.AKMApp._on_root_mousewheel(
                app,
                SimpleNamespace(x_root=8, y_root=10, num=0, delta=120),
            )

        self.assertEqual([(-1, "units")], listbox.scroll_calls)

    def test_merge_export_notes_replaces_previous_auto_lines(self):
        merged = release_tools.merge_export_notes(
            "Eigene Notiz\nMatched Export: alt.wav\nLimiter: Nein",
            "/tmp/neu.wav",
            True,
        )

        self.assertEqual(
            "Eigene Notiz\n\nMatched Export: /tmp/neu.wav\nLimiter: Ja",
            merged,
        )

    def test_start_distro_export_removes_old_release_artifacts_only(self):
        source_dir = os.path.join(self.tempdir.name, "source")
        export_root = os.path.join(self.tempdir.name, "exports")
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(export_root, exist_ok=True)

        cover_path = os.path.join(source_dir, "cover.jpg")
        audio_path = os.path.join(source_dir, "track.wav")
        with open(cover_path, "wb") as handle:
            handle.write(b"cover")
        with open(audio_path, "wb") as handle:
            handle.write(b"audio")

        release_dir = os.path.join(export_root, "My Release")
        os.makedirs(release_dir, exist_ok=True)
        obsolete_audio = os.path.join(release_dir, "09 - Old Track.wav")
        obsolete_cover = os.path.join(release_dir, "old_cover.jpg")
        obsolete_info = os.path.join(release_dir, "release_info.txt")
        keep_file = os.path.join(release_dir, "user_notes.txt")
        for path in (obsolete_audio, obsolete_cover, obsolete_info, keep_file):
            with open(path, "wb") as handle:
                handle.write(b"old")

        ok, _status = release_workflows.start_distro_export(
            {
                "title": "My Release",
                "artist": "Artist",
                "export_dir": export_root,
                "cover_path": cover_path,
                "type": "Album",
                "release_date": "2026-04-05",
                "genre": "Pop",
                "subgenre": "Indie",
                "label": "Label",
                "copyright_line": "C 2026",
            },
            [
                {
                    "title": "Fresh Track",
                    "duration": "3:45",
                    "production": "Prod",
                    "year": "2026",
                    "audio_path": audio_path,
                }
            ],
        )

        self.assertTrue(ok)
        self.assertFalse(os.path.exists(obsolete_audio))
        self.assertFalse(os.path.exists(obsolete_cover))
        self.assertTrue(os.path.exists(obsolete_info))
        self.assertTrue(os.path.exists(keep_file))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "01 - Fresh Track.wav")))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "cover.jpg")))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "tracklist.csv")))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "checklist.txt")))
        with open(obsolete_info, "r", encoding="utf-8") as handle:
            self.assertIn("Release Title: My Release", handle.read())


if __name__ == "__main__":
    unittest.main()
