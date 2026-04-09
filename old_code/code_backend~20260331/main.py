from fastapi import FastAPI, Response, UploadFile
import cv2
import numpy as np

from services.transform_magic_world import process

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/transform")
async def transform(file: UploadFile):
    image = await file.read()
    
    img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
    result = process(img)
    
    _, buffer = cv2.imencode(".png", result)
    
    return Response(content=buffer.tobytes(), media_type="image/png")