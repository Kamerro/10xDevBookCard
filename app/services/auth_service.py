from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.user import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_user(db: Session, email: str, password: str) -> User:
    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing is not None:
        raise ValueError("email_taken")

    if len(password) < 8:
        raise ValueError("password_too_short")

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_access_token(*, user_id: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.jwt_access_token_exp_minutes)

    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": exp,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
