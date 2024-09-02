import enum
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class Event(BaseModel):
    event_id: str
    coefficient: Optional[Decimal] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None