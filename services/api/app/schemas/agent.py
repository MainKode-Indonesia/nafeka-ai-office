from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    department_id: UUID
    manager_id: UUID | None = None
    name: str = Field(min_length=2, max_length=100)
    role: str = Field(min_length=2, max_length=100)
    instructions: str | None = None
    status: str = Field(default="active", max_length=20)


class AgentUpdate(BaseModel):
    department_id: UUID | None = None
    manager_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=100)
    role: str | None = Field(default=None, min_length=2, max_length=100)
    instructions: str | None = None
    status: str | None = Field(default=None, max_length=20)


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    department_id: UUID
    manager_id: UUID | None
    name: str
    role: str
    instructions: str | None
    status: str
    created_at: datetime
    updated_at: datetime
