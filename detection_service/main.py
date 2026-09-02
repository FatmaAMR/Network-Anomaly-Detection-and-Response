from fastapi import FastAPI, HTTPException
from typing import List
import uuid
import random
from shared.schemas import NetworkEvent, DetectionResult

app = FastAPI(title="NDR Detection Engine")

alerts_db: List[DetectionResult] = []
MAX_ALERTS = 1000

@app.post("/api/v1/detect", response_model=DetectionResult)
async def process_event(event: NetworkEvent):
    mock_score = random.uniform(0.0, 1.0)
    is_anomaly = mock_score > 0.75
    
    attack_types = ["Normal", "Fuzzers", "DoS", "Exploits", "Reconnaissance"]
    category = "Normal"
    severity = "Low"
    
    if is_anomaly:
        category = random.choice(attack_types[1:])
        severity = "High" if mock_score > 0.9 else "Medium"
        
    result = DetectionResult(
        event_id=str(uuid.uuid4()),
        timestamp=event.timestamp,
        srcip=event.srcip,
        dstip=event.dstip,
        is_anomaly=is_anomaly,
        anomaly_score=mock_score,
        attack_category=category,
        severity=severity
    )
    
    if is_anomaly:
        alerts_db.insert(0, result)
        if len(alerts_db) > MAX_ALERTS:
            alerts_db.pop()
            
    return result

@app.get("/api/v1/alerts", response_model=List[DetectionResult])
async def get_recent_alerts(limit: int = 50):
    return alerts_db[:limit]