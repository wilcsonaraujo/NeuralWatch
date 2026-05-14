from datetime import datetime
from pydantic import BaseModel


class HealthMetricsOutput(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime