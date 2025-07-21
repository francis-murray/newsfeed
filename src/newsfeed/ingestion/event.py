from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Event:
    id: str # unique
    source: str # e.g. “reddit” or “ars-technica”
    title: str
    published_at: datetime # ISO-8601/RFC 3339 timestamp, UTC
    body: Optional[str] = None # Optional text body

 