from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def record_activity(
    db: Session,
    action: str,
    description: str,
    user_id=None,
    agent_id=None,
    task_id=None,
    metadata: dict | None = None,
):
    entry = ActivityLog(
        user_id=user_id,
        agent_id=agent_id,
        task_id=task_id,
        action=action,
        description=description,
        activity_metadata=metadata,
    )
    db.add(entry)
    return entry
