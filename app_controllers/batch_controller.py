from .base_controller import BaseController
from app_logic import akm_core, flow_tools


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

    def flow_copy(self):
        if not self.state.batch_queue:
            return
        it = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
        res = flow_tools.resolve_copy_action(it, self._get_batch_copy_stage())
        self.app.clipboard_clear()
        self.app.clipboard_append(res["value"])
        self._set_batch_copy_stage(res["next_stage"])
        batch_view = self._get_batch_view()
        if batch_view and hasattr(batch_view, "set_copy_button_label"):
            batch_view.set_copy_button_label(f"{res['copied_label']} ✓")

    def flow_submit(self):
        if not self.state.batch_queue:
            return
        it = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
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
