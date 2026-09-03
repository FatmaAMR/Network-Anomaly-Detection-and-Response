import asyncio
import json
import random
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from kafka import KafkaProducer

app = FastAPI(title="Ingestion Service")

KAFKA_BROKER = "kafka:29092"
TOPIC_NAME = "network-events"

def get_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        print(f"Kafka not ready: {e}")
        return None

is_streaming = False

async def generate_traffic():
    global is_streaming
    producer = get_producer()
    
    while is_streaming and producer:
        event = {
            "timestamp": datetime.now().timestamp(),
            "srcip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "dstip": f"10.0.{random.randint(1, 5)}.{random.randint(1, 255)}",
            "sbytes": random.randint(64, 15000),
            "dbytes": random.randint(64, 5000),
            "sttl": random.choice([64, 128, 255]),
            "proto": random.choice(["tcp", "udp", "icmp"])
        }
        producer.send(TOPIC_NAME, event)
        await asyncio.sleep(0.5)

@app.post("/api/v1/stream/start")
async def start_stream(background_tasks: BackgroundTasks):
    global is_streaming
    if not is_streaming:
        is_streaming = True
        background_tasks.add_task(generate_traffic)
    return {"status": "Streaming started"}

@app.post("/api/v1/stream/stop")
async def stop_stream():
    global is_streaming
    is_streaming = False
    return {"status": "Streaming stopped"}