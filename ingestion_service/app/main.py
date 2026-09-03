from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.routes import router
from app.kafka_client import kafka_producer

@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka_producer.connect()
    yield
    kafka_producer.close()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(router, prefix="/api")