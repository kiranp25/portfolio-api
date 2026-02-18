from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.users import User
from app.models.users import UserRole
from app.models.refresh_tokens import RefreshToken
from app.core.config import settings
from app.core.security import (
    password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from app.services.username_service import generate_unique_username


# -----------------------------
# Register User
# -----------------------------

def register_user(db: Session, data):

    existing_user = db.query(User).filter(
        User.email_id == data.email_id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        username=generate_unique_username(db, data.name),
        email_id=data.email_id,
        password_hash=password_hash(data.password),
        is_verify=True,   # skip OTP for now
        role=UserRole.USER
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}


# -----------------------------
# Login User
# -----------------------------

def login_user(db: Session, data):

    user = db.query(User).filter(
        User.email_id == data.email_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    return _issue_tokens(db, user)


# -----------------------------
# Dummy OTP (for now)
# -----------------------------

def verify_otp(db: Session, data):
    return {"message": "OTP verification skipped for now"}


def refresh_user_token(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("user_id")
    jti = payload.get("jti")
    if user_id is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload"
        )

    stored_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.jti == jti
    ).first()
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not recognized"
        )

    if stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked"
        )

    if stored_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    if stored_token.token_hash != hash_token(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token mismatch"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return _issue_tokens(db, user, rotate_from=stored_token)


def logout_user(db: Session, refresh_token: str):
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("user_id")
    jti = payload.get("jti")
    if user_id is None or jti is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload"
        )

    stored_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.jti == jti
    ).first()

    if stored_token and stored_token.revoked_at is None:
        stored_token.revoked_at = datetime.utcnow()
        db.commit()

    return {"message": "Logged out successfully"}


def _issue_tokens(db: Session, user: User, rotate_from: RefreshToken | None = None):
    access_token = create_access_token({"user_id": user.id, "role": user.role})
    refresh_token, jti, refresh_exp = create_refresh_token({"user_id": user.id})

    token_row = RefreshToken(
        user_id=user.id,
        jti=jti,
        token_hash=hash_token(refresh_token),
        expires_at=refresh_exp,
    )
    db.add(token_row)

    if rotate_from is not None:
        rotate_from.revoked_at = datetime.utcnow()
        rotate_from.replaced_by_jti = jti

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_expires_in": getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", settings.REFREH_TOKEN_EXPIRE_DAYS) * 86400
    }
