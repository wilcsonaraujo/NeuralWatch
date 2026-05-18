import datetime
from fastapi import APIRouter, HTTPException
from src.api.schemas import HealthService, MetricsOutput
from src.db.database import get_all_metrics
from src.etl.pipeline import run_pipeline
from src.ml.model import prepare_data_for_training, train_and_save_model_iso_forest, train_and_save_model_scaler

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


@router.get("/metrics", response_model=list[MetricsOutput], summary="Pipeline Metrics")
async def metrics_get_response():
    metrics = get_all_metrics()
    return metrics


@router.post("/run-pipeline", summary="Run Pipeline")
def run_pipeline_router():
    metrics = run_pipeline()
    return metrics


@router.post("/train-model", summary="Run Training Model")
def run_training_model():
    try:
        df = (df.pipe(prepare_data_for_training).pipe(train_and_save_model_scaler))
        train_and_save_model_scaler(df)
        return {"message": "Model retrained successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
