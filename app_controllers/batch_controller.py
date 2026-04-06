
import tkinter as tk
from .base_controller import BaseController
from app_logic import akm_core, flow_tools

class BatchController(BaseController):
    """Manages batch processing queue and flow sequence."""
    
    def reload_flow_data(self, preferred_index=None):
        """Re-synchronizes the Batch/Batch Queue with current state."""
        self.state.batch_queue = flow_tools.filter_batch_entries(self.state.get_all_records(True))
        if preferred_index is not None: self.state.batch_index = preferred_index
        self.update_flow()

    def update_flow(self):
        """Updates the visual state of the Batch Tab."""
        if self.state.batch_queue:
            item = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
            if hasattr(self.app, 'flow_title'): self.app.flow_title.config(text=item['title'])
            if hasattr(self.app, 'flow_meta'): self.app.flow_meta.config(text=flow_tools.build_flow_meta_text(item))
            if hasattr(self.app, 'progress'): 
                self.app.progress["value"] = ((self.state.batch_index + 1) / len(self.state.batch_queue)) * 100

    def flow_copy(self):
        it = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
        res = flow_tools.resolve_copy_action(it, self.app.copy_stage)
        self.app.clipboard_clear()
        self.app.clipboard_append(res["value"])
        self.app.copy_stage = res["next_stage"]
        if self.app.copy_button: self.app.copy_button.config(text=f"{res['copied_label']} kopiert")

    def flow_submit(self):
        it = self.state.batch_queue[self.state.batch_index % len(self.state.batch_queue)]
        self.tasks.run(lambda: akm_core.update_entry(it['title'], {"status": "submitted"}), 
                       lambda r: self.reload_flow_data(), 
                       busy_text="Melde...")

    def flow_next(self): 
        self.state.batch_index += 1
        self.update_flow()

    def open_track_in_batch(self, it):
        self.reload_flow_data()
        for i, f in enumerate(self.state.batch_queue):
            if f['title'] == it['title']: 
                self.state.batch_index = i
                self.app.select_tab_by_id("batch")
                self.update_flow()
                return
