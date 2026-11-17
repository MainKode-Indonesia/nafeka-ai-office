from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository:
    def __init__(self, db: Session, model: Any):
        self.db = db
        self.model = model

    def get(self, item_id: UUID):
        return self.db.get(self.model, item_id)

    def list(self, offset: int = 0, limit: int = 50):
        statement = (
            select(self.model)
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())

    def create(self, data: dict):
        item = self.model(**data)
        self.db.add(item)
        self.db.flush()
        return item

    def update(self, item, data: dict):
        for key, value in data.items():
            setattr(item, key, value)
        self.db.flush()
        return item

    def delete(self, item):
        self.db.delete(item)
        self.db.flush()
