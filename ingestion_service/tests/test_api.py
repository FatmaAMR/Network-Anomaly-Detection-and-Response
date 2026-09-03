from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ingest_dynamic_payload():
    mock_payload = [
        {"sensor_id": "Zeek-01", "srcip": "10.0.0.1", "custom_field": "test_1"},
        {"sensor_id": "Suricata", "dstip": "192.168.1.5", "alert_type": "Exploit"}
    ]
    response = client.post("/api/v1/ingest", json=mock_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["events_processed"] == 2

def test_ingest_empty_payload():
    response = client.post("/api/v1/ingest", json=[])
    assert response.status_code == 400