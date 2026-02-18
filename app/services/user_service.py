from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import re
from typing import Optional

from app.models.users import User, UserRole
from app.core.security import password_hash, verify_password
from app.services.username_service import generate_unique_username, normalize_username_seed


def list_users(
    db: Session,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    include_deleted: bool = False,
    limit: int = 20,
    offset: int = 0,
):
    query = db.query(User)

    if not include_deleted:
        query = query.filter(User.is_deleted == False)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (User.name.ilike(search_term)) |
            (User.username.ilike(search_term)) |
            (User.email_id.ilike(search_term))
        )

    total = query.count()
    items = query.order_by(User.id.asc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def update_user_role(db: Session, user_id: int, role: str) -> User:
    if role not in UserRole.ALL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    user = get_user_by_id(db, user_id)
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def create_user_by_admin(
    db: Session,
    name: Optional[str],
    username: Optional[str],
    email_id: str,
    password: str,
    role: str = UserRole.USER,
    is_verify: bool = True,
) -> User:
    if role not in UserRole.ALL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )

    if not _is_strong_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be 8-72 chars and include upper, lower, number, and special character"
        )

    existing_user = db.query(User).filter(User.email_id == email_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    resolved_username = username or generate_unique_username(db, name or email_id.split("@")[0])
    resolved_username = normalize_username_seed(resolved_username)

    if db.query(User).filter(User.username == resolved_username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    user = User(
        name=name,
        username=resolved_username,
        email_id=email_id,
        password_hash=password_hash(password),
        is_verify=is_verify,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def disable_user(db: Session, user_id: int, admin_user_id: int) -> User:
    user = get_user_by_id(db, user_id)

    if user.id == admin_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot disable self"
        )

    user.is_active = False
    user.modify_by = admin_user_id
    db.commit()
    db.refresh(user)
    return user


def enable_user(db: Session, user_id: int, admin_user_id: int) -> User:
    user = get_user_by_id(db, user_id)

    user.is_active = True
    user.modify_by = admin_user_id
    db.commit()
    db.refresh(user)
    return user


def _is_strong_password(password: str) -> bool:
    if len(password) < 8 or len(password) > 72:
        return False
    checks = [
        r"[a-z]",
        r"[A-Z]",
        r"[0-9]",
        r"[^A-Za-z0-9]",
    ]
    return all(re.search(pattern, password) for pattern in checks)


def change_password(db: Session, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )

    if old_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from old password"
        )

    if not _is_strong_password(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be 8-72 chars and include upper, lower, number, and special character"
        )

    user.password_hash = password_hash(new_password)
    db.commit()
