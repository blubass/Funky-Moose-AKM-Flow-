import os
import tempfile
import unittest
from unittest import mock

from openpyxl import Workbook

import akm_core
import assistant_tools
import cover_tools
import detail_tools
import flow_tools
import loudness_workflows
import overview_tools
import path_ui_tools
import release_tools
import release_view_tools
import release_workflows
from akm_app import AKMApp


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


class FakeReleaseListbox:
    def __init__(self, selection=()):
        self.selection = tuple(selection)
        self.selected_index = None

    def curselection(self):
        return self.selection

    def selection_set(self, index):
        self.selected_index = index


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
        self.storage_patcher = mock.patch.multiple(
            akm_core,
            DATA_DIR=self.tempdir.name,
            DATA_FILE=os.path.join(self.tempdir.name, "data.json"),
            BACKUP_FILE=os.path.join(self.tempdir.name, "data_backup.json"),
            LANG_FILE=os.path.join(self.tempdir.name, "lang.txt"),
            SETTINGS_FILE=os.path.join(self.tempdir.name, "settings.json"),
        )
        self.storage_patcher.start()
        self.addCleanup(self.storage_patcher.stop)

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
                selected_layouts=["bottom", "center"],
                selected_formats=["square"],
                options={
                    "style": "clean",
                    "size_mode": "medium",
                    "offset": "normal",
                    "overlay": "medium",
                },
            )

            self.assertEqual(2, len(created))
            self.assertTrue(created[0].endswith("cover_bottom_1x1.jpg"))
            self.assertTrue(created[1].endswith("cover_center_1x1.jpg"))
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
    def make_app_stub(self):
        app = AKMApp.__new__(AKMApp)
        app_logs = []
        app.append_log = app_logs.append
        app.append_core_error = lambda context, exc: app_logs.append(f"{context}: {exc}")
        app._invalidate_all_records_cache = lambda: None
        app._set_detail_status_chip = lambda status: setattr(app, "last_status", status)
        app.refresh_list = lambda: setattr(app, "refreshed", True)
        app.reload_flow_data = lambda preferred_title=None, preferred_index=None: setattr(
            app, "reloaded_title", preferred_title
        )
        app.entry = FakeEntry()
        app.tabs = FakeTabs()
        app.tab_details = "details-tab"
        app.logs = app_logs
        return app

    def test_load_item_into_details_applies_form_state_and_selects_tab(self):
        app = self.make_app_stub()
        app.detail_vars = {
            "title": FakeVar(""),
            "duration": FakeVar(""),
            "composer": FakeVar(""),
            "production": FakeVar(""),
            "year": FakeVar(""),
            "audio_path": FakeVar(""),
        }
        app.detail_tags = FakeText("")
        app.detail_notes = FakeText("")
        app.detail_instrumental_var = FakeVar(False)

        app.load_item_into_details(
            {
                "title": "Song A",
                "duration": "3:11",
                "composer": "Uwe",
                "production": "FM",
                "year": "2026",
                "audio_path": "/tmp/song-a.wav",
                "instrumental": True,
                "status": "ready",
                "notes": "Testnotiz",
                "tags": ["tag1", "tag2"],
            }
        )

        self.assertEqual("Song A", app.detail_original_title)
        self.assertEqual("Song A", app.current_title)
        self.assertEqual("3:11", app.detail_vars["duration"].get())
        self.assertTrue(app.detail_instrumental_var.get())
        self.assertEqual("ready", app.last_status)
        self.assertEqual("tag1, tag2", app.detail_tags.get())
        self.assertEqual("Testnotiz", app.detail_notes.get())
        self.assertEqual("details-tab", app.tabs.selected)

    def test_update_flow_applies_meta_progress_and_copy_label(self):
        app = self.make_app_stub()
        app.data = [
            {
                "title": "Song A",
                "composer": "Uwe",
                "duration": "3:11",
                "production": "FM",
                "year": "2026",
            }
        ]
        app.flow_index = 0
        app.copy_stage = "duration"
        app.flow_title = FakeLabel()
        app.flow_meta = FakeLabel()
        app.progress_label = FakeLabel()
        app.progress = FakeProgress()
        app.copy_button = FakeLabel()
        app._set_batch_buttons_enabled = lambda enabled: setattr(app, "batch_enabled", enabled)

        app.update_flow()

        self.assertEqual("Song A", app.current_title)
        self.assertEqual("Song A", app.flow_title.options["text"])
        self.assertEqual(
            "Komponist: Uwe   Dauer: 3:11   Produktion: FM   Jahr: 2026",
            app.flow_meta.options["text"],
        )
        self.assertEqual("1 / 1", app.progress_label.options["text"])
        self.assertEqual(100.0, app.progress["value"])
        self.assertEqual("Dauer kopieren", app.copy_button.options["text"])
        self.assertTrue(app.batch_enabled)

    def test_open_loudness_tab_updates_ui_and_logs(self):
        app = self.make_app_stub()
        app.tabs = FakeTabs(["dash", "akm", "laut"])
        app.loudness_status_label = FakeLabel()
        app.loudness_hint_label = FakeLabel()

        with mock.patch("akm_app.loudness_tools", None):
            app.open_loudness_tab()

        self.assertEqual(2, app.tabs.selected)
        self.assertTrue(app.tabs.updated)
        self.assertTrue(app.tabs.focused)
        self.assertIn("konnte nicht geladen", app.loudness_status_label.options["text"])
        self.assertEqual(
            "Dateien laden oder direkt Werke aus der aktuellen Übersicht übernehmen.",
            app.loudness_hint_label.options["text"],
        )
        self.assertIn("Lautheit-Tab wurde geöffnet.", app.logs)

    def test_use_selected_title_transfers_title_and_focuses_assistant_tab(self):
        app = self.make_app_stub()
        app.tab_assistant = "assistant-tab"
        app._get_selected_overview_item = lambda: {"title": "Song A"}

        app.use_selected_title()

        self.assertEqual("Song A", app.entry.get())
        self.assertEqual("Song A", app.current_title)
        self.assertEqual("assistant-tab", app.tabs.selected)
        self.assertTrue(app.entry.focused)
        self.assertIn("In Eingabe übernommen: Song A", app.logs)

    def test_on_release_drop_files_normalizes_paths_before_import(self):
        app = self.make_app_stub()
        app.tk = type("FakeTk", (), {"splitlist": lambda _self, data: ("{/tmp/a.wav}", "/tmp/b.wav", "/tmp/a.wav")})()
        app.release_import_audio_paths = lambda paths: setattr(app, "dropped_paths", paths)

        app.on_release_drop_files(type("Event", (), {"data": "ignored"})())

        self.assertEqual(["/tmp/a.wav", "/tmp/b.wav"], app.dropped_paths)
        self.assertIn("Drag&Drop erkannt: 2 Datei(en)", app.logs)

    def test_release_import_filtered_works_skips_duplicates(self):
        app = self.make_app_stub()
        app.tab_release = "release-tab"
        app.refresh_release_track_list = lambda: setattr(app, "release_refreshed", True)
        app.release_tracks = [
            {"title": "Song A", "duration": "", "production": "", "year": "", "audio_path": "", "source": "Werk"}
        ]
        app.overview_records = [
            {"title": "Song A", "duration": "", "production": "", "year": "", "audio_path": ""},
            {"title": "Song B", "duration": "3:11", "production": "FM", "year": "2026", "audio_path": ""},
        ]

        app.release_import_filtered_works()

        self.assertEqual(2, len(app.release_tracks))
        self.assertEqual("Song B", app.release_tracks[-1]["title"])
        self.assertEqual("release-tab", app.tabs.selected)
        self.assertTrue(app.release_refreshed)
        self.assertIn("Ins Release übernommen: 1 Werke", app.logs)
        self.assertIn("Schon im Release übersprungen: 1 Werke", app.logs)

    def test_loudness_import_filtered_works_uses_helper_state_and_selects_tab(self):
        app = self.make_app_stub()
        app.tab_loudness = "loudness-tab"
        app.overview_records = [
            {"title": "Song A", "audio_path": "/tmp/a.wav"},
            {"title": "Song B", "audio_path": "/tmp/missing.wav"},
        ]
        app.loudness_hint_label = FakeLabel()
        app.loudness_status_label = FakeLabel()
        app.loudness_results = ["old"]
        app._clear_loudness_tree = lambda: setattr(app, "loudness_tree_cleared", True)
        app.append_loudness_log = lambda message: app.logs.append(message)

        with mock.patch("os.path.exists", side_effect=lambda path: path == "/tmp/a.wav"):
            app.loudness_import_filtered_works()

        self.assertEqual(["/tmp/a.wav"], app.loudness_files)
        self.assertEqual([], app.loudness_results)
        self.assertTrue(app.loudness_tree_cleared)
        self.assertEqual("1 Werke in Lautheit übernommen.", app.loudness_status_label.options["text"])
        self.assertEqual("loudness-tab", app.tabs.selected)
        self.assertIn("Aus Werken übernommen: 1 Dateien", app.logs)

    def test_save_details_updates_loaded_record_even_if_other_items_exist(self):
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
        app.current_title = "Song A"
        app.current_detail_status = "ready"
        app.detail_vars = {
            "title": FakeVar("Song A"),
            "duration": FakeVar(""),
            "composer": FakeVar(""),
            "production": FakeVar(""),
            "year": FakeVar(""),
            "audio_path": FakeVar(""),
        }
        app.detail_tags = FakeText("")
        app.detail_notes = FakeText("updated A")
        app.detail_instrumental_var = FakeVar(False)

        app.save_details()

        entries = {item["title"]: item for item in self.load_entries()}
        self.assertEqual("updated A", entries["Song A"]["notes"])
        self.assertEqual("old B", entries["Song B"]["notes"])
        self.assertEqual("Song A", app.reloaded_title)
        self.assertIn("Werkdetails gespeichert: Song A", app.logs)

    def test_release_title_matching_requires_exact_normalized_match(self):
        app = self.make_app_stub()
        app._get_all_entries_cached = lambda _context: [
            {
                "title": "Intro Remix",
                "duration": "",
                "production": "",
                "year": "",
                "audio_path": "",
            }
        ]

        source_path = os.path.join(self.tempdir.name, "Intro.wav")
        with open(source_path, "wb") as handle:
            handle.write(b"audio")

        track = app._release_track_from_audio_path(source_path)

        self.assertEqual("Datei", track["source"])
        self.assertEqual("Intro", track["title"])

    def test_release_title_matching_keeps_exact_normalized_matches(self):
        app = self.make_app_stub()
        app._get_all_entries_cached = lambda _context: [
            {
                "title": "Intro",
                "duration": "1:11",
                "production": "Prod",
                "year": "2026",
                "audio_path": "",
            }
        ]

        source_path = os.path.join(self.tempdir.name, "01 - Intro_matched.wav")
        with open(source_path, "wb") as handle:
            handle.write(b"audio")

        track = app._release_track_from_audio_path(source_path)

        self.assertEqual("Datei→Werk", track["source"])
        self.assertEqual("Intro", track["title"])
        self.assertEqual("1:11", track["duration"])

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

    def test_build_distro_export_removes_old_release_artifacts_only(self):
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

        app = self.make_app_stub()
        app.release_vars = {
            "title": FakeVar("My Release"),
            "artist": FakeVar("Artist"),
            "export_dir": FakeVar(export_root),
            "cover_path": FakeVar(cover_path),
            "type": FakeVar("Album"),
            "release_date": FakeVar("2026-04-05"),
            "genre": FakeVar("Pop"),
            "subgenre": FakeVar("Indie"),
            "label": FakeVar("Label"),
            "copyright_line": FakeVar("C 2026"),
        }
        app.release_tracks = [
            {
                "title": "Fresh Track",
                "duration": "3:45",
                "production": "Prod",
                "year": "2026",
                "audio_path": audio_path,
            }
        ]
        app.release_status_label = FakeLabel()

        app.build_distro_export()

        self.assertFalse(os.path.exists(obsolete_audio))
        self.assertFalse(os.path.exists(obsolete_cover))
        self.assertTrue(os.path.exists(keep_file))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "01 - Fresh Track.wav")))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "cover.jpg")))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "tracklist.csv")))
        self.assertTrue(os.path.exists(os.path.join(release_dir, "checklist.txt")))


if __name__ == "__main__":
    unittest.main()
