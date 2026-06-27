from dataclasses import dataclass
import datetime as dt
from datetime import datetime
from core.types.pipeline_event_type import PipelineEventType

@dataclass
class PipelineInputEvent(slot=True):
    session_id: str
    frame_id: int
    timestamp: datetime
    event_type: PipelineEventType
    payload: str | bytes