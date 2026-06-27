import asyncio
from datetime import datetime

from core.event import PipelineInputEvent, WSResponseEvent
from core.types import PipelineEventType
from core.session import SessionRegistryManager

class PipelineOrchestrator:
    def __init__(self, input_queue: asyncio.Queue, session_registry: SessionRegistryManager):
        self.orchestrator_input_queue: asyncio.Queue[PipelineInputEvent] = input_queue
        self.session_registry = session_registry
    
    async def run(self):
        input_event = await self.orchestrator_input_queue.get()
        session_id = input_event.session_id
        session = self.session_registry.get_session(session_id=session_id)
        
        if input_event.event_type == PipelineEventType.INPUT_NEW_FRAME:
            pass
        
        if input_event.event_type == PipelineEventType.ALL_FINISHED_DATA:
            response_event = WSResponseEvent(
                session_id=session_id,
                frame_id=input_event.frame_id,
                created_at=datetime.now(),
                payload=input_event.payload
            )
            await session.ws_response_queue.put(response_event)