import asyncio
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WebsocketSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        
    async def receive_worker(self):
        while True:
            message = await self.websocket.receive()

            if "text" in message and message["text"] is not None:
                pass

            elif "bytes" in message and message["bytes"] is not None:
                pass
    
    async def send_worker(self):
        while True:
            pass
    
    async def run(self):
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.receive_worker)
                tg.create_task(self.send_worker)
        except WebSocketDisconnect:
            await self.close()
    
    async def close(self):
        pass