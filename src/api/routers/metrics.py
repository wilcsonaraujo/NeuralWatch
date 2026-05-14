from fastapi import APIRouter
import datetime
from ..schemas import HealthMetricsOutput

router = APIRouter()

@router.get("/health", response_model=HealthMetricsOutput)
async def health_metrics_get_response():
    return {"status": "ativo",
            "service": "local host",
            "version": "v1",
            "environment": "dev",
            "timestamp": datetime.datetime.now()
            }
