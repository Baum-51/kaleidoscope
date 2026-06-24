from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import settings
from utils import get_logger
from routes import router

logger = get_logger(name=__name__)

app = FastAPI()
app.include_router(router=router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}