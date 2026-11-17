from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.db.database import get_db
from app.models.agent import Agent
from app.models.department import Department
from app.models.task import Task
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.schemas.auth import UserResponse
from app.services.resource_service import ResourceService

router = APIRouter(tags=["Resources"])

READ = Depends(get_current_user)
ADMIN = Depends(require_roles("owner", "admin"))
MANAGER = Depends(require_roles("owner", "admin", "manager"))


# Departments
@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = READ,
):
    return ResourceService(db, current_user).list_items(Department, offset, limit)


@router.get("/departments/{item_id}", response_model=DepartmentResponse)
def get_department(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = READ,
):
    return ResourceService(db, current_user).get_item(Department, item_id)


@router.post("/departments", response_model=DepartmentResponse, status_code=201)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    return ResourceService(db, current_user).create_item(
        Department, payload.model_dump()
    )


@router.patch("/departments/{item_id}", response_model=DepartmentResponse)
def update_department(
    item_id: UUID,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    return ResourceService(db, current_user).update_item(
        Department, item_id, payload.model_dump(exclude_unset=True)
    )


@router.delete("/departments/{item_id}")
def delete_department(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    return ResourceService(db, current_user).delete_item(Department, item_id)


# Agents
@router.get("/agents", response_model=list[AgentResponse])
def list_agents(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = READ,
):
    return ResourceService(db, current_user).list_items(Agent, offset, limit)


@router.get("/agents/{item_id}", response_model=AgentResponse)
def get_agent(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = READ,
):
    return ResourceService(db, current_user).get_item(Agent, item_id)


@router.post("/agents", response_model=AgentResponse, status_code=201)
def create_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    return ResourceService(db, current_user).create_item(Agent, payload.model_dump())


@router.patch("/agents/{item_id}", response_model=AgentResponse)
def update_agent(
    item_id: UUID,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    return ResourceService(db, current_user).update_item(
        Agent, item_id, payload.model_dump(exclude_unset=True)
    )


@router.delete("/agents/{item_id}")
def delete_agent(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    return ResourceService(db, current_user).delete_item(Agent, item_id)


# Tasks
@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = READ,
):
    return ResourceService(db, current_user).list_items(Task, offset, limit)


@router.get("/tasks/{item_id}", response_model=TaskResponse)
def get_task(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = READ,
):
    return ResourceService(db, current_user).get_item(Task, item_id)


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = MANAGER,
):
    return ResourceService(db, current_user).create_item(Task, payload.model_dump())


@router.patch("/tasks/{item_id}", response_model=TaskResponse)
def update_task(
    item_id: UUID,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = MANAGER,
):
    return ResourceService(db, current_user).update_item(
        Task, item_id, payload.model_dump(exclude_unset=True)
    )


@router.delete("/tasks/{item_id}")
def delete_task(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    return ResourceService(db, current_user).delete_item(Task, item_id)


# Users: only administrative users may list user accounts.
@router.get("/users", response_model=list[UserResponse])
def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = ADMIN,
):
    from sqlalchemy import select
    return list(
        db.scalars(
            select(User).offset(offset).limit(limit)
        ).all()
    )
