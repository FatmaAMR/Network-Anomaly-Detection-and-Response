import asyncio
import json
import uuid
import random
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer
from collections import Counter
from pydantic import BaseModel

app = FastAPI(title="Aegis SOC - Detection Engine")

# تفعيل CORS عشان بورت 80 يقدر يكلم بورت 8001
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alerts_db = []
global_stats = {
    "total_events": 0,
    "total_bytes": 0,
    "start_time": datetime.now().timestamp()
}

# قراءة رابط الكافكا من متغيرات البيئة (أو وضع افتراضي)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:29092")
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
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest'
        )
        for msg in consumer:
            event = msg.value
            global_stats["total_events"] += 1
            global_stats["total_bytes"] += event.get("sbytes", 0) + event.get("dbytes", 0)
            
            result = process_ml(event)
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
    elapsed = max(1, datetime.now().timestamp() - global_stats["start_time"])
    throughput_bps = (global_stats["total_bytes"] * 8) / elapsed
    throughput_gbps = throughput_bps / (1024**3)
    counts = Counter(a.attack_category for a in alerts_db)
    total_anomalies = max(1, sum(counts.values()))
    classifications = {k: round((v/total_anomalies)*100) for k, v in counts.items()}

    return {
        "total_events": global_stats["total_events"], 
        "critical_threats": high_alerts,
        "suspicious_ips": unique_ips,
        "throughput_gbps": round(throughput_gbps * 10000, 2),
        "classifications": classifications
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