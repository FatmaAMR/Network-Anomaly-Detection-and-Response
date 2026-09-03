from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.schemas import IngestionResponse, StreamControlResponse
from app.kafka_client import kafka_producer
from app.simulator import simulator

router = APIRouter(prefix="", tags=["Ingestion"])

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_events(payload: List[Dict[str, Any]]):
    if not payload:
        raise HTTPException(status_code=400, detail="Empty payload")
    
    for event in payload:
        kafka_producer.send_event(event)
        
    return IngestionResponse(
        status="success", 
        message="Events queued to Kafka", 
        events_processed=len(payload)
    )

@router.post("/stream/start", response_model=StreamControlResponse)
async def start_stream(background_tasks: BackgroundTasks):
    if not simulator.is_streaming:
        simulator.is_streaming = True
        background_tasks.add_task(simulator.generate_traffic)
    return StreamControlResponse(status="Streaming Started", is_active=True)

@router.post("/stream/stop", response_model=StreamControlResponse)
async def stop_stream():
    simulator.is_streaming = False
    return StreamControlResponse(status="Streaming Stopped", is_active=False)
