from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NetworkEvent(BaseModel):
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    srcip: str
    sport: int
    dstip: str
    dsport: int
    proto: str
    state: str
    dur: float
    sbytes: int
    dbytes: int
    
class DetectionResult(BaseModel):
    event_id: str
    timestamp: float
    srcip: str
    dstip: str
    is_anomaly: bool
    anomaly_score: float
    attack_category: str
    severity: str