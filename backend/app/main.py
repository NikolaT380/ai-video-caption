import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.health import router as health_router
from app.api.routes.videos import router as videos_router
from app.api.routes.jobs import router as jobs_router

app = FastAPI(
    title="AI Video Captioning API",
    version="1.0.0",
    description="Upload video, process captions, and track background jobs."
)

OUTPUT_DIR = "/app/storage/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(videos_router, prefix="/api/videos", tags=["videos"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])

@app.get("/")
async def root():
    return {"message": "API is running"}