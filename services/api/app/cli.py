import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User


def create_owner():
    db = SessionLocal()

    try:
        existing = db.scalar(
            select(User).where(User.role == "owner").limit(1)
        )

        if existing:
            print("An owner account already exists. Aborting.")
            return

        name = input("Owner name: ").strip()
        email = input("Owner email: ").strip().lower()
        password = getpass.getpass("Password (minimum 12 characters): ")
        confirmation = getpass.getpass("Confirm password: ")

        if not name or not email:
            raise ValueError("Name and email are required.")

        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters.")

        if password != confirmation:
            raise ValueError("Passwords do not match.")

        if db.scalar(select(User).where(User.email == email)):
            raise ValueError("Email is already registered.")

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="owner",
            is_active=True,
        )

        db.add(user)
        db.commit()

        print("Owner account created successfully.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_owner()
