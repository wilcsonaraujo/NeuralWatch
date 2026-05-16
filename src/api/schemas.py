from datetime import datetime
from pydantic import BaseModel, Field


class HealthService(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime

class MetricsOutput(BaseModel):
    total_requests: int = Field(..., description="Total batch requests.")
    error_rate: float = Field(..., ge=0, le=1, description="Error rate (0-1)")
    avg_bytes_kb: float = Field(..., ge=0, description="Average bytes in KB")
    std_bytes_kb: float = Field(..., ge=0, description="Standard deviation in KB")
    empty_response_rate: float = Field(..., ge=0, le=1, description="Empty response rate")
    unique_endpoints: int = Field(..., ge=0, description="Number of unique endpoints")