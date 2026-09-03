from typing import Dict, Any, List
from pydantic import BaseModel, Field

class IngestionResponse(BaseModel):
    status: str
    message: str
    events_processed: int

class StreamControlResponse(BaseModel):
    status: str
    is_active: bool