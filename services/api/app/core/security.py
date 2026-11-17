from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(password, hashed_password)
    except Exception:
        # Invalid or unsupported stored password hash.
        return False


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": ["sub", "iat", "exp", "type"],
        },
    )

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type")

    try:
        return UUID(payload["sub"])
    except (ValueError, TypeError, AttributeError) as exc:
        raise InvalidTokenError("Invalid token subject") from exc
