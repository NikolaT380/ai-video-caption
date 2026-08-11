from fastapi import APIRouter
from app.core.celery_app import celery_app

router = APIRouter()


@router.get("/health")
async def health_check():
    status = {
        "api": "online",
        "redis_broker": "unknown",
        "celery_workers": "unknown"
    }

    try:
        inspector = celery_app.control.inspect(timeout=1.0)
        ping_result = inspector.ping()

        if ping_result:
            status["redis_broker"] = "online"
            status["celery_workers"] = f"online ({len(ping_result)} nodes found)"
        else:
            status["redis_broker"] = "online"
            status["celery_workers"] = "offline (no workers responding)"

    except Exception as e:
        status["redis_broker"] = "offline/error"
        status["celery_workers"] = "offline/error"
        status["error_details"] = str(e)

    return status