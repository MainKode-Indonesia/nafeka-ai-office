from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    agent_id: UUID | None
    task_id: UUID | None
    action: str
    description: str | None
    activity_metadata: dict | None
    created_at: datetime
