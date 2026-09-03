# Network Detection & Response (NDR) MVP

An ML-powered cybersecurity platform designed to assist SOC analysts in detecting, classifying, and prioritizing anomalous network activity using an event-driven microservices architecture.

##  System Architecture
1. **Ingestion Service**: Simulates raw network traffic and streams packets into Kafka (Producer).
2. **Message Broker**: Apache Kafka & Zookeeper handling high-throughput telemetry data.
3. **Detection Service**: Consumes Kafka events, processes them through the UNSW-NB15 ML classification pipeline, and serves the REST APIs.
4. **Dashboard UI**: A custom, dark-themed vanilla HTML/JS interface for real-time monitoring and SOC analyst actions.
## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FatmaAMR/Network-Anomaly-Detection-and-Response.git
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



```sudo docker exec -it ndr-mvp-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic network-events --from-beginning
```