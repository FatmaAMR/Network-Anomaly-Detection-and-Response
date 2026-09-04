from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.routes import router
from app.model_handler import model_handler
from app.kafka_consumer import kafka_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_handler.load_models()
    kafka_consumer.start()
    yield
    kafka_consumer.stop()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(router)