from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import cv2
import torch
import numpy as np
from av import VideoFrame


import asyncio

from utils.common_logger import get_logger
from core.load_model_lifespan import lifespan

app = FastAPI(lifespan=lifespan)
pcs = set()

logger = get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frame_size = 192

class DepthTrack(VideoStreamTrack):
    def __init__(self, track, app: FastAPI):
        super().__init__()
        self.track = track
        self.app = app
        
        # フレーム共有（固定サイズ）
        self.latest_frame = np.zeros((frame_size, frame_size, 3), dtype=np.uint8)
        self.current_task: asyncio.Task | None = None
        self.latest_result = None
        
    async def recv(self):
        frame = await self.track.recv()
        
        img = frame.to_ndarray(format="bgr24")
        img = cv2.resize(img, (frame_size, frame_size))
        self.latest_frame = img
        
        # 深度推定実行
        if self.current_task is None or self.current_task.done():
            self.current_task = asyncio.create_task(self.process_worker())
        
        result_img = self.latest_result if self.latest_result is not None else img
        
        new_frame = VideoFrame.from_ndarray(result_img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame
        
    async def process_worker(self):
        while True:
            if self.latest_frame is None:
                await asyncio.sleep(0.01)
                continue
            img = self.latest_frame
            # result = await asyncio.to_thread(self.depth_process, img)
            # self.latest_result = result
            depth, seg = await asyncio.to_thread(self.process_frame, img)
            self.latest_result = depth
    
    def depth_process(self, img):
        # --- 深度推定 ---
        midas = self.app.state.midas
        transform = self.app.state.transform
        
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
        return depth_img
    
    def process_frame(self, img):
        # depth
        midas_model = self.app.state.midas
        transform = self.app.state.transform
        
        input_batch = transform(img)
        
        with torch.no_grad():
            depth_pred = midas_model(input_batch)
        
        depth = depth_pred.squeeze().cpu().numpy()
        depth = (depth - depth.min()) / (depth.max() - depth.min())
        
        depth_img = (depth * 255).astype(np.uint8)
        depth_img = cv2.cvtColor(depth_img, cv2.COLOR_GRAY2BGR)
        
        # segmentation
        seg_processor = self.app.state.seg_processor
        seg_model = self.app.state.seg_model
        
        inputs = seg_processor(images=img, return_tensors="pt")
        with torch.no_grad():
            outputs = seg_model(**inputs)
        
        logits = outputs.logits
        seg = logits.argmax(dim=1)[0].cpu().numpy()
        seg_img = self.colorize(seg)
        
        return depth_img, seg_img

    def colorize(self, seg):
        palette = {
            0: [0, 0, 0],       # background
            3: [0, 255, 0],     # tree
            2: [255, 0, 0],     # building
            1: [0, 0, 255],     # road
        }

        color = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)

        for k, v in palette.items():
            color[seg == k] = v

        return color
    

@app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    @pc.on("track")
    def on_track(track):
        logger.info("on_track")
        if track.kind == "video":
            depth_track = DepthTrack(track, app=app)
            pc.addTrack(depth_track)
        @track.on("ended")
        async def on_ended():
            logger.info("ended track")
            depth_track.stop()
    
    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    )
    
    @pc.on("connectionstatechange")
    async def on_state_change():
        logger.info(pc.connectionState)
        if pc.connectionState in ["failed", "closed", "disconnected"]:
            await pc.close()
            pcs.discard(pc)
    
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    }