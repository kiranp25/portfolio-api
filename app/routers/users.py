from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.db.deps import get_db
from app.models.users import User, UserRole
from app.schemas.user import (
    AdminCreateUserRequest,
    ChangePasswordRequest,
    UserListResponse,
    UserResponse,
    UserRoleUpdate,
)
from app.services.user_service import (
    change_password,
    create_user_by_admin,
    enable_user,
    disable_user,
    get_user_by_id,
    list_users,
    update_user_role,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=UserListResponse, status_code=status.HTTP_200_OK)
def all_users(
    role: Optional[Literal[UserRole.ADMIN, UserRole.USER]] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None),
    include_deleted: bool = Query(default=False),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin),
):
    return list_users(
        db,
        role=role,
        is_active=is_active,
        search=search,
        include_deleted=include_deleted,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminCreateUserRequest,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin),
):
    return create_user_by_admin(
        db,
        name=payload.name,
        username=payload.username,
        email_id=payload.email_id,
        password=payload.password,
        role=payload.role,
        is_verify=payload.is_verify,
    )


@router.put("/change-password", status_code=status.HTTP_200_OK)
def put_change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_password(db, current_user, payload.old_password, payload.new_password)
    return {"message": "Password changed successfully"}


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin),
):
    return get_user_by_id(db, user_id)


@router.patch("/{user_id}/role", response_model=UserResponse, status_code=status.HTTP_200_OK)
def patch_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    _admin_user: User = Depends(require_admin),
):
    return update_user_role(db, user_id, payload.role)


@router.patch("/{user_id}/disable", response_model=UserResponse, status_code=status.HTTP_200_OK)
def patch_disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return disable_user(db, user_id, admin_user.id)


@router.patch("/{user_id}/enable", response_model=UserResponse, status_code=status.HTTP_200_OK)
def patch_enable_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    return enable_user(db, user_id, admin_user.id)
