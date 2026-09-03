import os

class Settings:
    PROJECT_NAME = "Aegis Ingestion Service"
    VERSION = "1.0.0"
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    TOPIC_NAME = os.getenv("KAFKA_TOPIC", "network-events")

settings = Settings()