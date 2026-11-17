from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.agent import Agent
from app.models.department import Department
from app.models.task import Task
from app.repositories.base import BaseRepository
from app.services.audit_service import record_activity


class ResourceService:
    def __init__(self, db: Session, actor=None):
        self.db = db
        self.actor = actor

    def repository(self, model):
        return BaseRepository(self.db, model)

    def _persist(self, operation, action, model, item_id=None):
        try:
            item = operation()
            resource_id = getattr(item, "id", item_id)

            record_activity(
                self.db,
                action=action,
                description=f"{action.replace('_', ' ').title()} {model.__name__}",
                user_id=getattr(self.actor, "id", None),
                metadata={
                    "resource_type": model.__name__,
                    "resource_id": str(resource_id) if resource_id else None,
                },
            )

            self.db.commit()

            if item is not None:
                self.db.refresh(item)

            return item

        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Database constraint conflict. Check duplicate values and related records.",
            ) from exc

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def list_items(self, model, offset=0, limit=50):
        return self.repository(model).list(offset, limit)

    def get_item(self, model, item_id: UUID):
        item = self.repository(model).get(item_id)

        if item is None:
            raise HTTPException(404, "Resource not found")

        return item

    def _validate_department(self, department_id):
        if self.db.get(Department, department_id) is None:
            raise HTTPException(404, "Department not found")

    def _validate_agent_reference(self, agent_id):
        if agent_id is not None and self.db.get(Agent, agent_id) is None:
            raise HTTPException(404, "Agent not found")

    def _validate_manager(self, manager_id, item_id=None):
        if manager_id is None:
            return

        visited = set()
        current_id = manager_id

        while current_id is not None:
            if item_id is not None and current_id == item_id:
                raise HTTPException(
                    400,
                    "Agent hierarchy cannot contain a management cycle",
                )

            if current_id in visited:
                raise HTTPException(
                    409,
                    "Existing agent hierarchy contains a cycle",
                )

            visited.add(current_id)
            manager = self.db.get(Agent, current_id)

            if manager is None:
                raise HTTPException(404, "Manager agent not found")

            current_id = manager.manager_id

    def create_item(self, model, data: dict):
        if model is Agent:
            self._validate_department(data["department_id"])
            self._validate_manager(data.get("manager_id"))

        if model is Task:
            self._validate_agent_reference(data.get("created_by_agent_id"))

        return self._persist(
            lambda: self.repository(model).create(data),
            f"{model.__name__.lower()}_created",
            model,
        )

    def update_item(self, model, item_id: UUID, data: dict):
        item = self.get_item(model, item_id)

        if model is Agent:
            if data.get("department_id") is not None:
                self._validate_department(data["department_id"])

            if "manager_id" in data:
                self._validate_manager(data["manager_id"], item_id)

        if model is Task and "created_by_agent_id" in data:
            self._validate_agent_reference(data["created_by_agent_id"])

        return self._persist(
            lambda: self.repository(model).update(item, data),
            f"{model.__name__.lower()}_updated",
            model,
            item_id,
        )

    def delete_item(self, model, item_id: UUID):
        item = self.get_item(model, item_id)

        def delete_operation():
            self.repository(model).delete(item)
            return None

        self._persist(
            delete_operation,
            f"{model.__name__.lower()}_deleted",
            model,
            item_id,
        )

        return {"message": "Resource deleted successfully"}
