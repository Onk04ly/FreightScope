import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import risk, shipments, upload, ws
from app.config import settings

app = FastAPI(title="FreightScope API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(shipments.router, prefix="/api")
app.include_router(risk.router, prefix="/api")
app.include_router(ws.router)


@app.on_event("startup")
async def startup():
    os.makedirs(settings.upload_dir, exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}
