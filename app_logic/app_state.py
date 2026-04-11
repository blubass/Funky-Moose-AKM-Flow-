import copy
import os
from typing import List, Dict, Optional, Any, Callable
from . import akm_core
from .models import TrackRecord

class AppState:
    def __init__(self):
        # Observer System
        self._observers: Dict[str, List[Callable]] = {}

        # Current Catalog & Results
        self.all_records: List[TrackRecord] = []
        self.filtered_records: List[TrackRecord] = []
        self.current_mtime: Optional[float] = None
        
        # Batch Context
        self.batch_queue: List[TrackRecord] = []
        self.batch_index: int = 0
        
        # Release Context
        self.release_tracks: List[TrackRecord] = []
        
        # Loudness Context
        self.loudness_files: List[str] = []
        self.loudness_results: List[Dict[str, Any]] = []
        
        # Current UI State (Common)
        self.last_selected_title: Optional[str] = None

    # --- OBSERVER SYSTEM ---

    def subscribe(self, event_name: str, callback: Callable):
        """Register a callback for a specific event."""
        if event_name not in self._observers:
            self._observers[event_name] = []
        self._observers[event_name].append(callback)

    def unsubscribe(self, event_name: str, callback: Callable):
        """Remove a callback from an event."""
        if event_name in self._observers:
            try:
                self._observers[event_name].remove(callback)
            except ValueError:
                pass

    def emit(self, event_name: str, payload: Any = None):
        """Notify all subscribers of an event."""
        for callback in self._observers.get(event_name, []):
            try:
                callback(payload)
            except Exception as e:
                import logging
                logging.error(f"Error in AppState observer '{event_name}': {e}")

    # --- DATA ACCESS ---

    def invalidate_cache(self) -> None:
        """Clears in-memory cache to force a reload from disk on next access."""
        self.all_records = []
        self.current_mtime = None
        self.emit("cache_invalidated")

    def get_all_records(self, force: bool = False, copy_data: bool = False) -> List[TrackRecord]:
        """Retrieves all catalogue records, utilizing the repository-backed cache."""
        mtime = self._get_data_mtime()
        if not force and self.all_records and self.current_mtime == mtime:
            return copy.deepcopy(self.all_records) if copy_data else self.all_records
            
        try:
            # Use Repository directly
            records = akm_core._get_repo().load_all(strict=True)
            self.all_records = records
            self.current_mtime = mtime
            return copy.deepcopy(self.all_records) if copy_data else self.all_records
        except Exception:
            return []

    def _get_data_mtime(self) -> Optional[float]:
        try:
            # Use Repository path property
            return os.path.getmtime(akm_core._get_repo().data_file)
        except OSError:
            return None

    def get_record(self, title: str) -> Optional[TrackRecord]:
        if not self.all_records:
            self.get_all_records()
        for r in self.all_records:
            if r.title == title:
                return copy.deepcopy(r)
        return None

    def set_release_tracks(self, tracks: List[TrackRecord]) -> None:
        self.release_tracks = list(tracks)
        self.emit("release_tracks_changed", self.release_tracks)
