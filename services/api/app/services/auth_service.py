import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.services.audit_service import record_activity


def _login_fingerprint(email: str, client_ip: str) -> str:
    identity = f"{client_ip.strip()}|{email.strip().lower()}"
    return hmac.new(
        settings.jwt_secret_key.encode(),
        identity.encode(),
        hashlib.sha256,
    ).hexdigest()


def _check_login_limit(db: Session, fingerprint: str):
    window = timedelta(minutes=settings.login_rate_limit_window_minutes)
    now = datetime.now(timezone.utc)
    cutoff = now - window

    # Serialize requests for the same IP/email fingerprint.
    db.execute(
        select(
            func.pg_advisory_xact_lock(
                func.hashtextextended(fingerprint, 0)
            )
        )
    )

    attempts = db.scalar(
        select(func.count(ActivityLog.id)).where(
            ActivityLog.action == "login_failed",
            ActivityLog.activity_metadata["fingerprint"].as_string()
            == fingerprint,
            ActivityLog.created_at >= cutoff,
        )
    ) or 0

    if attempts >= settings.login_rate_limit_attempts:
        oldest = db.scalar(
            select(func.min(ActivityLog.created_at)).where(
                ActivityLog.action == "login_failed",
                ActivityLog.activity_metadata["fingerprint"].as_string()
                == fingerprint,
                ActivityLog.created_at >= cutoff,
            )
        )

        retry_after = settings.login_rate_limit_window_minutes * 60

        if oldest is not None:
            if oldest.tzinfo is None:
                oldest = oldest.replace(tzinfo=timezone.utc)
            retry_after = max(
                1,
                int((oldest + window - now).total_seconds()),
            )

        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
    client_ip: str = "unknown",
):
    normalized_email = email.strip().lower()
    fingerprint = _login_fingerprint(normalized_email, client_ip)

    try:
        _check_login_limit(db, fingerprint)

        user = db.scalar(
            select(User).where(User.email == normalized_email)
        )

        if (
            user is None
            or not user.is_active
            or not verify_password(password, user.password_hash)
        ):
            record_activity(
                db,
                action="login_failed",
                description="Failed login attempt",
                metadata={"fingerprint": fingerprint},
            )
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password is incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user.last_login_at = datetime.now(timezone.utc)

        record_activity(
            db,
            action="login_success",
            description="User logged in successfully",
            user_id=user.id,
            metadata={"client_ip": client_ip},
        )

        db.commit()
        db.refresh(user)

        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
        }

    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise
