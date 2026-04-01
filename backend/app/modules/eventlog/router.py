import uuid
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_active  # ✅ виправлено
from app.modules.eventlog.schemas import EventLogResponse
from app.modules.eventlog.service import EventLogService
from app.modules.users.models import User

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventLogResponse])
async def list_events(
    event_type: str | None = None,
    generator_id: uuid.UUID | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    current_user: User = Depends(require_active),  # ✅ виправлено
    db: AsyncSession = Depends(get_db),
):
    service = EventLogService(db)
    return await service.get_all(
        event_type=event_type,
        generator_id=generator_id,
        from_date=from_date,
        to_date=to_date,
    )  # ✅ додано закриваючу дужку


@router.get("/{event_id}", response_model=EventLogResponse)
async def get_event(
    event_id: uuid.UUID,
    current_user: User = Depends(require_active),  # ✅ виправлено
    db: AsyncSession = Depends(get_db),
):
    service = EventLogService(db)
    return await service.get_by_id(event_id)