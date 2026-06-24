from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import cv2
import torch
import numpy as np
from av import VideoFrame
import threading

from utils.common_logger import get_logger

app = FastAPI()
pcs = set()

logger = get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MiDaS
model_type = "MiDaS_small"
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas.eval()
transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform

class DepthTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()
        self.track = track
        
        self.latest_frame = None
        self.prev_img = None
        
        self.counter = 0
        self.lock = threading.lock()
        
        threading.Thread(target=self.worker, demon=True).start()
    
    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        if self.counter % 3 == 0:
            # --- 深度推定 ---
            input_batch = transform(img)
            
            with torch.no_grad():
                prediction = midas(input_batch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
                
            depth = prediction.cpu().numpy()
            depth = (depth - depth.min()) / (depth.max() - depth.min())
            
            depth_img = (depth * 255).astype(np.uint8)
            depth_img = cv2.cvtColor(depth_img, cv2.COLOR_GRAY2BGR)
            self.prev_img = depth_img
            # logger.info(f'{depth_img.shape}')
        else:
            depth_img = self.prev_img
        new_frame = VideoFrame.from_ndarray(depth_img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        
        self.counter += 1
        return new_frame

@app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    @pc.on("track")
    def on_track(track):
        logger.info("on_track")
        if track.kind == "video":
            pc.addTrack(DepthTrack(track))
    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    )
    
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    }