from dataclasses import dataclass
import datetime as dt
from datetime import datetime

@dataclass
class WSResponseEvent(slot=True):
    session_id: str
    frame_id: int
    created_at: datetime
    payload: dict | str