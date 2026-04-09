import asyncio
import json
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRecorder

from utils.common_logger import get_logger

app = FastAPI()

logger = get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pcs = set()

@app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    recorder = MediaRecorder("./media/output.mp4")
    
    @pc.on("track")
    async def on_track(track):
        logger.info(f"Track received: {track.kind}")
        
        if track.kind=="video":
            recorder.addTrack(track)
            await recorder.start()
        
        @track.on("ended")
        async def on_ended():
            logger.info("Track ended")
            await recorder.stop()
    
    await pc.setRemoteDescription(offer)
    
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }