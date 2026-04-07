import copy
import os
from typing import List, Dict, Optional, Any
from . import akm_core

class AppState:
    def __init__(self):
        # Current Catalog & Results
        self.all_records: List[Dict[str, Any]] = []
        self.filtered_records: List[Dict[str, Any]] = []
        self.current_mtime: Optional[float] = None
        
        # Batch Context
        self.batch_queue: List[Dict[str, Any]] = []
        self.batch_index: int = 0
        
        # Release Context
        self.release_tracks: List[Dict[str, Any]] = []
        
        # Loudness Context
        self.loudness_files: List[str] = []
        self.loudness_results: List[Dict[str, Any]] = []
        
        # Current UI State (Common)
        self.last_selected_title: Optional[str] = None

    def invalidate_cache(self) -> None:
        """Clears in-memory cache to force a reload from disk on next access."""
        self.all_records = []
        self.current_mtime = None

    def get_all_records(self, force: bool = False) -> List[Dict[str, Any]]:
        """Retrieves all catalogue records, utilizing an mtime-based cache."""
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

    def _get_data_mtime(self) -> Optional[float]:
        try:
            return os.path.getmtime(akm_core.DATA_FILE)
        except OSError:
            return None

    def get_record(self, title: str) -> Optional[Dict[str, Any]]:
        for r in self.all_records:
            if r.get("title") == title:
                return copy.deepcopy(r)
        return None

    def set_release_tracks(self, tracks: List[Dict[str, Any]]) -> None:
        self.release_tracks = list(tracks)
