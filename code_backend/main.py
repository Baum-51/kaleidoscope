from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import cv2
import torch
import numpy as np
from av import VideoFrame


from multiprocessing import Process, Value, Array
import ctypes
import time

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

frame_size = 192

class DepthTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()
        self.track = track
        
        # フレーム共有（固定サイズ）
        self.frame_array = Array(ctypes.c_uint8, frame_size*frame_size*3)
        self.result_array = Array(ctypes.c_int8, frame_size*frame_size*3)
        
        self.has_new_frame = Value("b", False)
        
        # worker起動
        self.process = Process (
            target=self.worker,
            daemon=True
        )
        
        self.process.start()
    
    async def recv(self):
        frame = await self.track.recv()
        
        img = frame.to_ndarray(format="bgr24")
        img = cv2.resize(img, (frame_size, frame_size))
        
        # 共有メモリにコピー
        np_array = np.frombuffer(self.frame_array.get_obj(), dtype=np.uint8)
        np_array[:] = img.flatten()
        
        self.has_new_frame.value = True
        
        # 結果取得
        result_np = np.frombuffer(self.result_array.get_obj(), dtype=np.uint8)
        result_img = result_np.reshape((frame_size, frame_size, 3))
        
        new_frame = VideoFrame.from_ndarray(result_img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        
        return new_frame
    
    def worker(self):
        while True:
            if not self.has_new_frame.value:
                continue
            
            self.has_new_frame.value = False
            
            img = np.frombuffer(self.frame_array.get_obj(), dtype=np.uint8)
            img = img.reshape((frame_size, frame_size, 3))
            
            # --- 推論 ---
            result = self.depth_process(img)
            
            result_np = np.frombuffer(self.result_array.get_obj(), dtype=np.uint8)
            result_np[:] = result.flatten()
            time.sleep(0.03)  # 約30FPS制限
    
    def depth_process(self, img):
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
        return depth_img
    
    def stop(self):
        if self.process.is_alive():
            self.process.terminate()
            self.process.join()
    

@app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    @pc.on("track")
    def on_track(track):
        logger.info("on_track")
        if track.kind == "video":
            depth_track = DepthTrack(track)
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