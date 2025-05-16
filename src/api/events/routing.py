from fastapi import APIRouter, Depends, HTTPException, Query
from .model import (
    EventModel,
    EventCreateSchema,
    EventBucketSchema,
    EventUpdateSchema,
    get_utc_now,
)
from api.db.config import DATABASE_URL
from api.db.session import get_session
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from timescaledb.hyperfunctions import time_bucket
from typing import List


router = APIRouter()

DEFAULT_LOOKUP_PAGES = ["/about", "/contact", "/pages", "/pricing", "pricing"]


@router.get("/", response_model=List[EventBucketSchema])
def read_events(
    duration: str = Query(default="1 day"),
    pages: List = Query(default=None),
    session: Session = Depends(get_session),
):
    bucket = time_bucket(duration, EventModel.time)
    lookup_pages = (
        pages
        if isinstance(pages, List) and len(pages) > 0
        else ["/about", "/contact", "/pages", "/pricing", "pricing"]
    )

    query = (
        select(
            bucket.label("bucket"),
            EventModel.page.label("page"),
            func.count().label("count"),
        )
        .where(
            EventModel.page.in_(lookup_pages),
        )
        .group_by(bucket, EventModel.page)
        .order_by(bucket, EventModel.page)
    )
    results = session.exec(query).fetchall()

    return results


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
