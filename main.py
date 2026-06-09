from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin 
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, etc.
    allow_headers=["*"],
)

app.include_router(router)
