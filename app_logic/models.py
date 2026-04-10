from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

def get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

@dataclass
class TrackRecord:
    title: str
    status: str = "in_progress"
    date: str = field(default_factory=get_today_str)
    last_change: str = field(default_factory=get_today_str)
    duration: str = ""
    composer: str = ""
    production: str = ""
    year: str = ""
    instrumental: bool = False
    notes: str = ""
    audio_path: str = ""
    tags: List[str] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        """Backward compatibility for dictionary-style access."""
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        """Backward compatibility for indexing (e.g. record['title'])."""
        if not hasattr(self, key):
            raise KeyError(key)
        return getattr(self, key)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackRecord':
        """
        Creates a TrackRecord from a dictionary, applying normalization logic.
        Ensures backward compatibility with older data formats.
        """
        if not data:
            return cls(title="Unknown")
            
        def clean(val):
            if val is None: return ""
            return str(val).strip()

        title = clean(data.get("title", ""))
        status = clean(data.get("status", "in_progress"))
        if status not in ["in_progress", "ready", "submitted", "confirmed"]:
            status = "in_progress"
            
        date = clean(data.get("date")) or get_today_str()
        last_change = clean(data.get("last_change")) or date
        
        tags = data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        elif not isinstance(tags, list):
            tags = []
            
        return cls(
            title=title,
            status=status,
            date=date,
            last_change=last_change,
            duration=clean(data.get("duration", "")),
            composer=clean(data.get("composer", "")),
            production=clean(data.get("production", "")),
            year=clean(data.get("year", "")),
            instrumental=bool(data.get("instrumental", False)),
            notes=clean(data.get("notes", "")),
            audio_path=clean(data.get("audio_path", "")),
            tags=[clean(t) for t in tags if clean(t)]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the record back to a dictionary for JSON serialization."""
        return asdict(self)
