import tkinter as tk
from .base_controller import BaseController
from app_logic import akm_core, flow_tools


class BatchController(BaseController):
    """Manages batch processing queue and flow sequence."""

    def reload_flow_data(self, preferred_index=None):
        """Re-synchronizes the Batch Queue with current state."""
        self.state.batch_queue = flow_tools.filter_batch_entries(self.state.get_all_records(True))
        if preferred_index is not None:
            self.state.batch_index = min(preferred_index, max(0, len(self.state.batch_queue) - 1))
        self.update_flow()

    def update_flow(self):
        """Updates the visual state of the Batch Tab."""
        q = self.state.batch_queue
        if not q:
            self._set_empty_state()
            return

        idx = self.state.batch_index % len(q)
        item = q[idx]

        if hasattr(self.app, 'flow_title'):
            self.app.flow_title.config(text=item.get('title', '—'))
        if hasattr(self.app, 'flow_meta'):
            self.app.flow_meta.config(text=flow_tools.build_flow_meta_text(item))
        if hasattr(self.app, 'progress'):
            self.app.progress["value"] = ((idx + 1) / len(q)) * 100
        if hasattr(self.app, 'progress_label'):
            self.app.progress_label.config(text=f"{idx + 1} / {len(q)}")
        if hasattr(self.app, 'copy_button') and self.app.copy_button:
            self.app.copy_button.config(text="Titel kopieren")
        self.app.copy_stage = flow_tools.DEFAULT_COPY_STAGE

    def _set_empty_state(self):
        """Shows an empty/done state when the batch queue is exhausted."""
        if hasattr(self.app, 'flow_title'):
            self.app.flow_title.config(text="Alle Werke erledigt ✓")
        if hasattr(self.app, 'flow_meta'):
            self.app.flow_meta.config(text="Keine offenen Einträge in der Queue.")
        if hasattr(self.app, 'progress'):
            self.app.progress["value"] = 100
        if hasattr(self.app, 'progress_label'):
            self.app.progress_label.config(text="0 / 0")

    def flow_copy(self):
        if not self.state.batch_queue:
            return
        it = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
        res = flow_tools.resolve_copy_action(it, self.app.copy_stage)
        self.app.clipboard_clear()
        self.app.clipboard_append(res["value"])
        self.app.copy_stage = res["next_stage"]
        if hasattr(self.app, 'copy_button') and self.app.copy_button:
            self.app.copy_button.config(text=f"{res['copied_label']} ✓")

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
                self.update_flow()
                return
