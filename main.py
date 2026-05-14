from fastapi import FastAPI
from src.api.routers import metrics_router

app = FastAPI()
app.include_router(metrics_router)
