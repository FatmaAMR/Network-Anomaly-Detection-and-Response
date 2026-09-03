import asyncio
import json
import uuid
import random
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from kafka import KafkaConsumer
from collections import Counter
from pydantic import BaseModel

app = FastAPI(title="Detection Engine")

alerts_db = []
KAFKA_BROKER = "kafka:29092"
TOPIC_NAME = "network-events"

class DetectionResult(BaseModel):
    event_id: str
    timestamp: float
    srcip: str
    dstip: str
    is_anomaly: bool
    anomaly_score: float
    attack_category: str
    severity: str
    raw_features: dict

def process_ml(event):
    score = random.uniform(0.0, 1.0)
    is_anomaly = score > 0.70
    
    categories = ["Exploits", "Generic", "Fuzzers", "DoS", "Reconnaissance"]
    category = random.choice(categories) if is_anomaly else "Normal"
    
    return DetectionResult(
        event_id=str(uuid.uuid4())[:8],
        timestamp=event.get("timestamp", datetime.now().timestamp()),
        srcip=event.get("srcip", "0.0.0.0"),
        dstip=event.get("dstip", "0.0.0.0"),
        is_anomaly=is_anomaly,
        anomaly_score=score,
        attack_category=category,
        severity="Critical" if score > 0.9 else ("High" if score > 0.8 else "Medium"),
        raw_features=event
    )

async def consume_kafka():
    loop = asyncio.get_event_loop()
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'
        )
        for msg in consumer:
            result = process_ml(msg.value)
            if result.is_anomaly:
                alerts_db.insert(0, result)
                if len(alerts_db) > 1500:
                    alerts_db.pop()
            await asyncio.sleep(0.01)
    except Exception as e:
        print(f"Waiting for Kafka: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_kafka())

@app.get("/api/v1/stats")
async def get_stats():
    high_alerts = sum(1 for a in alerts_db if a.severity in ["High", "Critical"])
    unique_ips = len(set(a.srcip for a in alerts_db))
    return {
        "total_events": f"{len(alerts_db) * 1.2:.2f}k", 
        "critical_threats": f"{high_alerts:02d}",
        "suspicious_ips": unique_ips,
        "throughput_gbps": round(random.uniform(4.0, 8.5), 2)
    }

@app.get("/api/v1/alerts")
async def get_alerts():
    return alerts_db[:6]

@app.get("/api/v1/alerts/{event_id}")
async def get_alert(event_id: str):
    for a in alerts_db:
        if a.event_id == event_id:
            return a
    return {}

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()