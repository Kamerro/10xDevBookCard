from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str | None = None


class UserOut(BaseModel):
    id: UUID
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str
