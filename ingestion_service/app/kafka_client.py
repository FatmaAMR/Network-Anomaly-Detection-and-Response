import json
from kafka import KafkaProducer
from app.config import settings

class EventProducer:
    def __init__(self):
        self.producer = None

    def connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=[settings.KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3
            )
            print(f"Connected to Kafka at {settings.KAFKA_BROKER}")
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")

    def send_event(self, event: dict):
        if self.producer:
            self.producer.send(settings.TOPIC_NAME, event)

    def close(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()

kafka_producer = EventProducer()