from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas.auth import LoginRequest, RegisterRequest, TokenOut, UserOut
from app.services.auth_service import authenticate_user, create_access_token, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    if payload.password_confirm is not None and payload.password != payload.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        user = create_user(db, email=str(payload.email), password=payload.password)
    except ValueError as e:
        if str(e) == "email_taken":
            raise HTTPException(status_code=400, detail="Email already registered") from e
        if str(e) == "password_invalid_length":
            raise HTTPException(status_code=400, detail="Password must be 8-19 characters") from e
        if str(e) == "password_missing_uppercase":
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter") from e
        if str(e) == "password_missing_digit":
            raise HTTPException(status_code=400, detail="Password must contain at least one digit") from e
        if str(e) == "password_missing_special":
            raise HTTPException(status_code=400, detail="Password must contain at least one special character") from e
        raise

    return UserOut(id=user.id, email=user.email)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    user = authenticate_user(db, email=str(payload.email), password=payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user_id=str(user.id))
    return TokenOut(access_token=token, token_type="bearer")
