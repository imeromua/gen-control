import uuid
from datetime import datetime

from pydantic import BaseModel


class EventLogResponse(BaseModel):
    id: uuid.UUID
    event_type: str
    generator_id: uuid.UUID | None
    performed_by: uuid.UUID | None
    meta: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
