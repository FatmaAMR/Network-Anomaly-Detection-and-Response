#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$ROOT_DIR/ndr/bin/python"
VENV_UVICORN="$ROOT_DIR/ndr/bin/uvicorn"

fuser -k 8000/tcp 2>/dev/null || true
fuser -k 8001/tcp 2>/dev/null || true

echo "=== 1. Starting Kafka ==="
sudo docker compose up -d
sleep 3

echo "=== 2. Starting Ingestion Service (Port 8000) ==="
cd "$ROOT_DIR/ingestion_service"
$VENV_UVICORN app.main:app --host 0.0.0.0 --port 8000 &
INGESTION_PID=$!

echo "=== 3. Starting Detection Service (Port 8001) ==="
cd "$ROOT_DIR/detection_service"
$VENV_UVICORN app.main:app --host 0.0.0.0 --port 8001 &
DETECTION_PID=$!

cleanup() {
    echo ""
    echo "=== Shutting down services... ==="
    kill -TERM "$INGESTION_PID" "$DETECTION_PID" 2>/dev/null || true
    wait "$INGESTION_PID" "$DETECTION_PID" 2>/dev/null || true
    echo "Done."
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "Waiting for APIs to warm up..."
until curl -s http://localhost:8000/docs > /dev/null; do
    sleep 0.5
done
until curl -s http://localhost:8001/docs > /dev/null; do
    sleep 0.5
done
echo "APIs are UP!"

echo "=== 4. Starting Traffic Generator ==="
cd "$ROOT_DIR/traffic_generator"
$VENV_PYTHON producer_script.py

wait "$INGESTION_PID" "$DETECTION_PID"