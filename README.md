# Network Detection & Response (NDR) MVP

An ML-powered cybersecurity platform designed to assist SOC analysts in detecting, classifying, and prioritizing anomalous network activity using an event-driven microservices architecture.

## Architecture
- **Ingestion Service (FastAPI):** Simulates or ingests real-time network traffic streams.
- **Detection Service (FastAPI):** The core ML engine processing payloads. Orchestrates One-Class SVM (Anomaly Detection) and Supervised Classifiers (Attack Classification).
- **SOC Dashboard (Streamlit):** Real-time monitoring UI tailored for security teams.

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd ndr-ml-pipeline
   ```

2. **Start the microservices:**
   ```bash
   docker-compose up --build -d
   ```

3. **Trigger the Network Stream:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/stream -H "Content-Type: application/json" -d '{"action": "start"}'
   ```

4. **Access the Dashboard:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/stream -H "Content-Type: application/json" -d '{"action": "start"}'
   ```

