import asyncio
import random
from datetime import datetime
from app.kafka_client import kafka_producer

class StreamSimulator:
    def __init__(self):
        self.is_streaming = False

    async def generate_traffic(self):
        while self.is_streaming:
            event = {
                "timestamp": datetime.now().timestamp(),
                "srcip": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "dstip": f"10.0.{random.randint(1, 5)}.{random.randint(1, 255)}",
                "sbytes": random.randint(64, 15000),
                "dbytes": random.randint(64, 5000),
                "sttl": random.choice([64, 128, 255]),
                "proto": random.choice(["tcp", "udp", "icmp"])
            }
            kafka_producer.send_event(event)
            await asyncio.sleep(0.5)

simulator = StreamSimulator()
