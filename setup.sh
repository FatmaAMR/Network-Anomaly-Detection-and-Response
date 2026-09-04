#!/usr/bin/env bash
set -e

echo "=== 1. Initializing Virtual Environment ==="
if [ ! -d "ndr" ]; then
    uv venv ndr
    echo "Virtual environment 'ndr' created."
else
    echo "Virtual environment 'ndr' already exists."
fi

source ndr/bin/activate

echo "=== 2. Installing Ingestion Service Dependencies ==="
uv pip install -r ingestion_service/requirements.txt

echo "=== 3. Installing Detection Service Dependencies ==="
uv pip install -r detection_service/requirements.txt

echo "=== 4. Installing Traffic Generator Dependencies ==="
uv pip install -r traffic_generator/requirements.txt

echo "=== Setup Complete! ==="
echo "Run 'source ndr/bin/activate' to activate the environment."