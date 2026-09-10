from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.workers.tasks.process_video import process_video_task

router = APIRouter()

UPLOAD_DIR = Path("/app/storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    target_language: str = Form("original")
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
        raise HTTPException(status_code=400, detail="Unsupported video format")

    safe_name = file.filename.replace(" ", "_")
    stored_filename = f"{uuid4()}_{safe_name}"
    saved_path = UPLOAD_DIR / stored_filename

    try:
        with open(saved_path, "wb") as buffer:
            buffer.write(await file.read())

        task = process_video_task.delay(
            saved_path.as_posix(),
            stored_filename,
            target_language
        )

        return {
            "message": "Video uploaded successfully",
            "task_id": task.id,
            "stored_filename": stored_filename,
            "target_language": target_language,
            "file_path": saved_path.as_posix(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))