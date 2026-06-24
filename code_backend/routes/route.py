from fastapi import APIRouter, WebSocket

router = APIRouter

@router.websocket('/ws')
async def websocket_access(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()