import asyncio
import httpx
import random
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(title="NDR Ingestion Service")

DETECTION_SERVICE_URL = "http://detection_service:8001/api/v1/detect"
is_streaming = False

class StreamControl(BaseModel):
    action: str 

async def generate_mock_stream():
    global is_streaming
    async with httpx.AsyncClient() as client:
        while is_streaming:
            event = {
                "srcip": f"192.168.1.{random.randint(1, 255)}",
                "sport": random.randint(1024, 65535),
                "dstip": f"10.0.0.{random.randint(1, 255)}",
                "dsport": random.choice([80, 443, 22, 21, 3389]),
                "proto": random.choice(["tcp", "udp"]),
                "state": "CON",
                "dur": random.uniform(0.0, 5.0),
                "sbytes": random.randint(64, 1500),
                "dbytes": random.randint(64, 5000)
            }
            
            try:
                await client.post(DETECTION_SERVICE_URL, json=event)
            except Exception as e:
                print(f"Connection failed: {e}")
                
            await asyncio.sleep(1.5)

@app.post("/api/v1/stream")
async def control_stream(control: StreamControl, background_tasks: BackgroundTasks):
    global is_streaming
    if control.action == "start" and not is_streaming:
        is_streaming = True
        background_tasks.add_task(generate_mock_stream)
        return {"status": "Streaming started"}
    elif control.action == "stop":
        is_streaming = False
        return {"status": "Streaming stopped"}
    return {"status": "No action taken"}