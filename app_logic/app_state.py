import copy
import os
from . import akm_core

class AppState:
    def __init__(self):
        # Current Catalog & Results
        self.all_records = []
        self.filtered_records = []
        self.current_mtime = None
        
        # Batch Context
        self.batch_queue = []
        self.batch_index = 0
        
        # Release Context
        self.release_tracks = []
        
        # Loudness Context
        self.loudness_files = []
        self.loudness_results = []
        
        # Current UI State (Common)
        self.last_selected_title = None

    def invalidate_cache(self):
        self.all_records = []
        self.current_mtime = None

    def get_all_records(self, force=False):
        mtime = self._get_data_mtime()
        if not force and self.all_records and self.current_mtime == mtime:
            return copy.deepcopy(self.all_records)
            
        try:
            records = akm_core.get_all_entries()
            self.all_records = records
            self.current_mtime = mtime
            return copy.deepcopy(self.all_records)
        except Exception:
            return []

    def _get_data_mtime(self):
        try:
            return os.path.getmtime(akm_core.DATA_FILE)
        except OSError:
            return None

    def get_record(self, title):
        for r in self.all_records:
            if r.get("title") == title:
                return copy.deepcopy(r)
        return None

    def set_release_tracks(self, tracks):
        self.release_tracks = list(tracks)
