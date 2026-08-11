from fastapi import APIRouter
from celery.result import AsyncResult
from app.core.celery_app import celery_app

router = APIRouter()


@router.get("/{task_id}")
async def get_job_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None,
    }

    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["result"] = {
            "error": str(task_result.result),
            "traceback": task_result.traceback,
        }

    return response