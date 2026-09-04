from fastapi import APIRouter
from app.kafka_consumer import recent_alerts

router = APIRouter(prefix="/api/detection", tags=["Detection"])

@router.get("/alerts")
async def get_alerts():

    return {"status": "success", "alerts": recent_alerts}

@router.get("/stats")
async def get_stats():
    return {
        "total_alerts": len(recent_alerts),
        "active_threats": len([a for a in recent_alerts if a["risk_score"] > 0.8])
    }