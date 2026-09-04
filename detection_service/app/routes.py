from fastapi import APIRouter, HTTPException
from app.kafka_consumer import recent_alerts

router = APIRouter(prefix="/api/v1", tags=["Detection"])

@router.get("/alerts")
def get_alerts():
    formatted_alerts = []
    for idx, alert in enumerate(reversed(recent_alerts)):
        formatted_alerts.append({
            "event_id": f"INC-{8942 + idx}",
            "timestamp": alert.get("timestamp", 1710000000),
            "severity": alert.get("priority", "High"),
            "attack_category": alert.get("attack_type", "Normal"),
            "srcip": alert.get("srcip", "192.168.1.50"),
            "dstip": alert.get("dstip", "10.0.0.5"),
            "anomaly_score": alert.get("risk_score", 0.5),
            "raw_features": alert.get("raw_features", {"sbytes": 500, "dbytes": 0, "sttl": 254, "proto": "tcp"})
        })
    return formatted_alerts

@router.get("/stats")
def get_stats():
    total_events = len(recent_alerts)
    critical_threats = sum(1 for a in recent_alerts if a.get("priority") in ["Critical", "High"])
    unique_suspicious_ips = len(set(a.get("srcip") for a in recent_alerts if a.get("srcip")))
    
    categories = {}
    total_attacks = len(recent_alerts)
    
    if total_attacks > 0:
        for a in recent_alerts:
            cat = a.get("attack_type", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1
                
        for key in categories:
            categories[key] = round((categories[key] / total_attacks) * 100)
    else:
        categories = {"No Active Threats": 0}

    return {
        "total_events": total_events * 10 + 100,
        "critical_threats": critical_threats,
        "suspicious_ips": unique_suspicious_ips,
        "throughput_gbps": round(1.8 + (len(recent_alerts) * 0.05), 2),
        "classifications": categories
    }

@router.get("/alerts/{event_id}")
def get_alert_detail(event_id: str):
    if not recent_alerts:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    latest = recent_alerts[-1]
    return {
        "event_id": event_id,
        "timestamp": latest.get("timestamp", 1710000000),
        "severity": latest.get("priority", "High"),
        "attack_category": latest.get("attack_type", "Exploits"),
        "srcip": latest.get("srcip", "175.45.176.99"),
        "dstip": latest.get("dstip", "192.168.10.42"),
        "anomaly_score": latest.get("risk_score", 0.95),
        "raw_features": {
            "sbytes": 1420,
            "dbytes": 320,
            "sttl": 64,
            "proto": "tcp"
        }
    }