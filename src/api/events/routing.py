from fastapi import APIRouter, Depends, HTTPException
from .model import (
    EventModel,
    EventCreateSchema,
    EventListSchema,
    EventUpdateSchema,
    get_utc_now,
)
from api.db.config import DATABASE_URL
from api.db.session import get_session
from sqlmodel import Session, select


router = APIRouter()


@router.get("/", response_model=EventListSchema)
def read_events(session: Session = Depends(get_session)):
    query = select(EventModel).order_by(EventModel.updated_at.desc()).limit(10)
    results = session.exec(query).all()

    return {"results": results, "count": len(results)}


@router.get("/{event_id}", response_model=EventModel)
def get_event(event_id: int, session: Session = Depends(get_session)) -> EventModel:
    query = select(EventModel).where(EventModel.id == event_id)
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Event not found")

    return result


@router.post("/", response_model=EventModel)
def create_event(payload: EventCreateSchema, session: Session = Depends(get_session)):
    data = payload.model_dump()
    obj = EventModel.model_validate(data)
    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj


@router.put("/{event_id}", response_model=EventModel)
def update_event(
    event_id: int, payload: EventUpdateSchema, session: Session = Depends(get_session)
) -> EventModel:

    query = select(EventModel).where(EventModel.id == event_id)
    obj = session.exec(query).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Event not found")

    data = payload.model_dump()
    for k, v in data.items():
        setattr(obj, k, v)

    obj.updated_at = get_utc_now()
    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj
