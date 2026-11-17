
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.db.database import get_db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.activity_log import ActivityLogResponse

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


def _sanitize_metadata(action: str, metadata: dict | None) -> dict | None:
    """
    Only expose explicitly approved metadata fields.
    Internal security metadata must never reach the API response.
    """
    if not isinstance(metadata, dict):
        return None

    if action in {"login_failed", "login_success"}:
        return None

    allowed_fields = {"resource_type", "resource_id"}
    sanitized = {
        key: value
        for key, value in metadata.items()
        if key in allowed_fields and isinstance(value, (str, int, float, bool))
    }

    return sanitized or None


@router.get("", response_model=list[ActivityLogResponse])
def list_audit_logs(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("owner", "admin")),
):
    statement = select(ActivityLog)

    if action:
        statement = statement.where(ActivityLog.action == action)

    statement = (
        statement
        .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
        .offset(offset)
        .limit(limit)
    )

    entries = db.scalars(statement).all()

    response = []

    for entry in entries:
        item = ActivityLogResponse.model_validate(entry)
        item.activity_metadata = _sanitize_metadata(
            entry.action,
            entry.activity_metadata,
        )
        response.append(item)

    return response
