from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    priority: int = Field(default=3, ge=1, le=5)
    created_by_agent_id: UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    status: str | None = Field(default=None, max_length=30)
    priority: int | None = Field(default=None, ge=1, le=5)
    created_by_agent_id: UUID | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: str
    priority: int
    created_by_agent_id: UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
