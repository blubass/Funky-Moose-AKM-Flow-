from .base_controller import BaseController
from app_logic import akm_core, flow_tools
from app_logic.text_utils import clean_text as _clean_text


class BatchController(BaseController):
    """Manages batch processing queue and flow sequence."""

    def _get_batch_view(self):
        return self.get_built_tab("batch")

    def _get_batch_copy_stage(self):
        batch_view = self._get_batch_view()
        if batch_view and hasattr(batch_view, "get_copy_stage"):
            return batch_view.get_copy_stage()
        return getattr(self, "_copy_stage", flow_tools.DEFAULT_COPY_STAGE)

    def _set_batch_copy_stage(self, stage):
        batch_view = self._get_batch_view()
        if batch_view and hasattr(batch_view, "set_copy_stage"):
            batch_view.set_copy_stage(stage)
            return
        self._copy_stage = stage or flow_tools.DEFAULT_COPY_STAGE

    def _get_current_batch_item(self):
        if not self.state.batch_queue:
            return None
        return self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]

    def reload_flow_data(self, preferred_index=None):
        """Re-synchronizes the Batch Queue with current state."""
        previous_title = getattr(self.app, "current_title", None)
        queue = flow_tools.filter_batch_entries(self.state.get_all_records(True))
        self.state.batch_queue = queue
        self.state.batch_index = flow_tools.resolve_flow_index(
            queue,
            current_index=self.state.batch_index,
            previous_title=previous_title,
            preferred_index=preferred_index,
        )
        self.update_flow()

    def update_flow(self):
        """Updates the visual state of the Batch Tab."""
        flow_state = flow_tools.build_flow_state(
            self.state.batch_queue,
            self.state.batch_index,
            self._get_batch_copy_stage(),
        )
        self.state.batch_index = flow_state["resolved_index"]
        self.app.current_title = flow_state["current_title"]
        batch_view = self._get_batch_view()
        if batch_view and hasattr(batch_view, "render_flow_state"):
            batch_view.render_flow_state(
                title_text=flow_state["title_text"],
                meta_text=flow_state["meta_text"],
                progress_value=flow_state["progress_value"],
                progress_text=flow_state["progress_text"],
                copy_button_label=flow_state["copy_button_label"],
                has_duration=flow_state["has_duration"],
                status_text=flow_tools.build_flow_status_text(self.state.batch_queue, flow_state),
                hint_text=flow_tools.build_flow_hint_text(
                    self.state.batch_queue,
                    flow_state,
                    self._get_batch_copy_stage(),
                ),
                meta_summary=flow_tools.build_flow_meta_summary(self.state.batch_queue),
                enabled=flow_state["has_item"],
            )

    def _set_empty_state(self):
        """Shows an empty/done state when the batch queue is exhausted."""
        batch_view = self._get_batch_view()
        if batch_view and hasattr(batch_view, "render_empty_state"):
            batch_view.render_empty_state()

    def flow_copy_title(self):
        self.flow_copy(stage="title")

    def flow_copy_duration(self):
        self.flow_copy(stage="duration")

    def flow_copy(self, stage=None):
        it = self._get_current_batch_item()
        if not it:
            return
        copy_stage = stage or self._get_batch_copy_stage()
        if copy_stage == "duration" and not _clean_text(it.get("duration")):
            return
        res = flow_tools.resolve_copy_action(it, copy_stage)
        self.app.clipboard_clear()
        self.app.clipboard_append(res["value"])
        self._set_batch_copy_stage(res["next_stage"])
        if res["advance_after_copy"]:
            self.state.batch_index = flow_tools.next_flow_index(
                self.state.batch_index,
                len(self.state.batch_queue),
            )
            self.update_flow()
            return
        batch_view = self._get_batch_view()
        if batch_view and hasattr(batch_view, "set_copy_button_label"):
            batch_view.set_copy_button_label(f"{res['copied_label']} ✓")

    def flow_submit(self):
        it = self._get_current_batch_item()
        if not it:
            return
        self.tasks.run(
            lambda: akm_core.update_entry(it['title'], {"status": "submitted"}),
            lambda r: self.reload_flow_data(),
            busy_text="Melde als submitted..."
        )

    def flow_next(self):
        if not self.state.batch_queue:
            return
        self.state.batch_index = (self.state.batch_index + 1) % len(self.state.batch_queue)
        self.update_flow()

    def open_track_in_batch(self, it):
        self.reload_flow_data()
        for i, f in enumerate(self.state.batch_queue):
            if f['title'] == it.get('title'):
                self.state.batch_index = i
                self.app.select_tab_by_id("batch")
                if hasattr(self.app, "batch_tab"):
                    _ = self.app.batch_tab
                self.update_flow()
                return
