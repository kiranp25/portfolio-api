from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    OTPVerifyRequest,
    RefreshTokenRequest,
    TokenResponse,
    AuthUserResponse,
)
from app.services.auth_service import (
    register_user,
    verify_otp,
    login_user,
    refresh_user_token,
    logout_user,
)
from app.core.deps import get_current_user
from app.core.rate_limit import limit_login
from app.models.users import User


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)



@router.post("/register",status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, data)

@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify(data: OTPVerifyRequest, db: Session = Depends(get_db)):
    return verify_otp(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(limit_login)],
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, data)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_user_token(db, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return logout_user(db, data.refresh_token)

@router.get("/me", response_model=AuthUserResponse, status_code=status.HTTP_200_OK)
def current_user(current_user: User= Depends(get_current_user)):
    return current_user
