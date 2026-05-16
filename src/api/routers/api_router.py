import datetime
from fastapi import APIRouter
from src.api.schemas import HealthService, MetricsOutput
from src.etl.pipeline import run_pipeline

router = APIRouter()


@router.get("/health", response_model=HealthService, summary="Health Check")
async def health_get_response():
    return {
        "status": "healthy",
        "service": "NeuralWatch ETL",
        "version": "1.0.0",
        "environment": "dev",
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }


@router.get("/metrics", response_model=MetricsOutput, summary="Pipeline Metrics")
async def metrics_get_response():
    metrics = run_pipeline()
    return metrics
