from contextlib import asynccontextmanager
from fastapi import FastAPI
import torch
from transformers import AutoImageProcessor, SegformerForSemanticSegmentation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時
    # 深度推定追加
    app.state.midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
    app.state.midas.eval()
    
    app.state.transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
    
    # segmentation追加
    app.state.seg_processor = AutoImageProcessor.from_pretrained(
        "nvidia/segformer-b0-finetuned-ade-512-512"
    )
    app.state.seg_model = SegformerForSemanticSegmentation.from_pretrained(
        "nvidia/segformer-b0-finetuned-ade-512-512"
    )
    app.state.seg_model.eval()
    
    yield
    
    # shutdown時
    app.state.midas = None
    app.state.seg_model = None
    