import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Path, HTTPException, Depends
from redis.asyncio import Redis

from app.redis_client import add_event, get_redis, update_status, redis_pool
from app.schemas import Event, EventState

events: dict[str, Event] = {
    '1': Event(event_id='1', coefficient=1.2, deadline=int(time.time()) + 600, state=EventState.NEW),
    '2': Event(event_id='2', coefficient=1.15, deadline=int(time.time()) + 60, state=EventState.NEW),
    '3': Event(event_id='3', coefficient=1.67, deadline=int(time.time()) + 90, state=EventState.NEW)
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_pool(connection_pool=redis_pool)
    for _, event in events.items():
        await add_event(event=event, _redis=redis)
    await redis.aclose()

    yield


app = FastAPI(lifespan=lifespan)


@app.put('/event')
async def create_event(event: Event, _redis: Redis = Depends(get_redis)):
    if event.event_id not in events:
        events[event.event_id] = event
        await add_event(event=event, _redis=_redis)
        return {}

    need_update = False
    for p_name, p_value in event.dict(exclude_unset=True).items():
        setattr(events[event.event_id], p_name, p_value)
        if p_name == "state":
            need_update = True
    if need_update:
        await update_status(event=event, _redis=_redis)
    return {}


@app.get('/event/{event_id}')
async def get_event(event_id: str = Path()):
    if event_id in events:
        return events[event_id]

    raise HTTPException(status_code=404, detail="Event not found")


@app.get('/events')
async def get_events():
    return list(e for e in events.values() if time.time() < e.deadline)
