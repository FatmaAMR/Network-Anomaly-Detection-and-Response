import os

class Settings:
    PROJECT_NAME = "Aegis Detection Service"
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
    CONSUME_TOPIC = os.getenv("KAFKA_TOPIC", "network-events")
    MODEL_PATH = os.getenv("MODEL_PATH", "models/ndr_model.pkl")

settings = Settings()