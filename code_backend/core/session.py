import asyncio
from dataclasses import dataclass
from pydantic import field
from datetime import datetime
import uuid

from utils import get_logger
from core.event import WSResponseEvent
    
@dataclass(slots=True)
class SessionRuntime:
    session_id: str
    ws_response_queue: asyncio.Queue[WSResponseEvent] = field( default_factory=asyncio.Queue )
    
    tasks: set[asyncio.Task] # 保険
    
    created_at: datetime
    logger = logger = get_logger
    
    def add_task(self, task: asyncio.Task):
        self.tasks.add(task)
        task.add_done_callback( lambda t: self.tasks.discard(t) )
    
    async def shutdown(self):
        for task in self.tasks: task.cancel()
        results = await asyncio.gather( *self.tasks, return_exceptions=True, )
        for result in results:
            if isinstance(result, Exception):
                self.logger.exception(result)
                

class SessionRegistryManager:
    def __init__(self):
        self.session_registry: dict[str, SessionRuntime] = {}
        
    def create_session(self):
        session_id = uuid.uuid4
        session = SessionRuntime(
            session_id=session_id,
            ws_response_queue=asyncio.Queue(),
            created_at=datetime.now(),
        )
        self.session_registry[session_id] = session
        
    def get_session(self, session_id):
        session = self.session_registry.get(session_id)
        return session

    
    def delete_session(self, session_id):
        session = self.session_registry.pop(session_id)
                