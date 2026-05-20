import datetime
import os
from fastapi import APIRouter, HTTPException
from src.api.schemas import HealthService, MetricsOutput
from src.db.database import get_all_metrics
from src.etl.pipeline import run_pipeline
from src.ml.autoencoder_model import (
    load_threshold,
    predict_anomaly_autoencoder,
    run_autoencoder_model,
)
from src.ml.model import get_prediction, run_scaler_model

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


@router.post("/train-scaler-model", summary="Run Train Scaler Model")
def run_scaler_training_model():
    try:
        run_scaler_model()
        return {"message": "Scalar model retrained successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/train-autoencoder-model", summary="Run Train Autoencoder Model")
def run_autoencoder_training_model():
    try:
        run_autoencoder_model()
        return {"message": "Autoencoder model retrained successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/predict-autoencoder", summary="Predict Autoencoder Model")
def run_predict_autoencoder_training_model(metrics: dict):
    try:
        current_threshold = load_threshold()
        is_anomaly = predict_anomaly_autoencoder(metrics, current_threshold)
        return {"anomaly_detected": is_anomaly, "threshold_used": current_threshold}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/predict", summary="Predict Model")
def run_predic_model(metrics: dict):
    try:
        get_predis_anomaly = get_prediction(metrics)
        model_used = os.getenv("MODEL_TYPE", "ISOLATION_FOREST")
        
        return {
            "anomaly_detected": get_predis_anomaly,
            "model_version": model_used,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
