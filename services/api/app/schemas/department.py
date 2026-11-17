from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    status: str = Field(default="active", max_length=20)


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    slug: str | None = Field(default=None, min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    status: str | None = Field(default=None, max_length=20)


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
