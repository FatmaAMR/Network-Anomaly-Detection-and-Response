import json
import threading
from kafka import KafkaConsumer
from app.config import settings
from app.model_handler import model_handler

recent_alerts = []

class EventConsumer:
    def __init__(self):
        self.consumer = None
        self.is_running = False

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._consume_loop)
        self.thread.daemon = True
        self.thread.start()

    def _consume_loop(self):
        self.consumer = KafkaConsumer(
            settings.CONSUME_TOPIC,
            bootstrap_servers=[settings.KAFKA_BROKER],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest'
        )
        print(f"Started consuming from {settings.CONSUME_TOPIC}")
        
        for message in self.consumer:
            if not self.is_running:
                break
            
            event = message.value
            result = model_handler.predict(event)
            
            print(f"Processed event from {result.get('srcip')} -> Status: {result.get('label')} | Risk: {result.get('risk_score')}")
            
            if result.get("label") == "Attack":
                recent_alerts.append(result)
                if len(recent_alerts) > 100:
                    recent_alerts.pop(0)

    def stop(self):
        self.is_running = False
        if self.consumer:
            self.consumer.close()

kafka_consumer = EventConsumer()