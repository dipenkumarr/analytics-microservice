from fastapi import APIRouter
from .schema import EventSchema
from api.db.config import DATABASE_URL


router = APIRouter()


@router.get("/")
def read_events():
    print(DATABASE_URL)
    return {"items": [1, 2, 3]}


@router.get("/{event_id}")
def get_event(event_id: int) -> EventSchema:
    return {"id": event_id}
