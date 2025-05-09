# from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional, List


class EventSchema(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = ""
