import datetime
import string

from pydantic import BaseModel
from typing import Optional

class healthMetricsResponse(BaseModel):
    status: string
    service: string
    version: string
    environment: string
    timestamp: datetime