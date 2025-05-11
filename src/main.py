from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.events import router as event_router
from api.db.session import init_db

# Import the model to ensure it's registered with SQLModel.metadata before init_db is called
from api.events.model import EventModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan: Starting application...")
    print(f"Lifespan: EventModel table name expected: {EventModel.__tablename__}")
    print("Lifespan: Attempting to initialize DB...")
    init_db()
    print("Lifespan: DB initialization process finished.")
    yield
    print("Lifespan: Shutting down application...")


app = FastAPI(lifespan=lifespan)
app.include_router(event_router, prefix="/api/events")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/healthz")
def read_api_health():
    return {"status": "ok"}
