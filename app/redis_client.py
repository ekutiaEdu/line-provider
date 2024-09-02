from decimal import Decimal
from enum import Enum
from time import time

import redis.asyncio as redis
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from app.config import settings
from app.schemas import EventState, Event


class EventStatus(str, Enum):
    pending = "PENDING"
    win = "WIN"
    lose = "LOSE"


class EventFull(BaseModel):
    id: int = Field(..., ge=0)
    odds: Decimal = Field(..., ge=0, decimal_places=2)
    status: EventStatus = ...
    deadline: int = Field(..., ge=0)


def convert_event_to_event_full(event: Event) -> EventFull:
    event_id = int(event.event_id)

    if not event.coefficient:
        raise ValueError()
    odds = event.coefficient

    status_map = {
        EventState.NEW: EventStatus.pending,
        EventState.FINISHED_WIN: EventStatus.win,
        EventState.FINISHED_LOSE: EventStatus.lose
    }
    status = status_map.get(event.state, EventStatus.pending)

    if not event.deadline:
        raise ValueError()
    deadline = event.deadline

    return EventFull(id=event_id, odds=odds, status=status, deadline=deadline)


redis_pool = redis.ConnectionPool.from_url(settings.redis_dsn)


async def get_redis() -> Redis:
    _redis = Redis.from_pool(connection_pool=redis_pool)
    yield _redis
    await _redis.aclose()


async def add_event(event: Event, _redis: Redis) -> None:
    try:
        event_to_redis = convert_event_to_event_full(event)
    except ValueError:
        print("Error: cannot convert.")
        return

    expire = event_to_redis.deadline - int(time())
    if expire < 1:
        return

    await _redis.set(name=f"event:{event_to_redis.id}", value=event_to_redis.model_dump_json(), ex=expire)


async def update_status(event: Event, _redis: Redis) -> None:
    try:
        event_to_redis = convert_event_to_event_full(event)
    except ValueError:
        print("Error: cannot convert.")
        return

    await _redis.xadd(
        name=settings.REDIS_EVENTS_STREAM,
        fields={"event_id": event_to_redis.id, "event_status": event_to_redis.status})
