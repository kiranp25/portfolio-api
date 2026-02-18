from datetime import datetime
from typing import Literal, Optional, List


from pydantic import BaseModel, EmailStr, Field

from app.models.users import UserRole


class UserBase(BaseModel):
    name: Optional[str]
    username: str
    email_id: EmailStr


class UserResponse(UserBase):
    id: int
    is_verify: bool
    last_login: Optional[datetime]
    role: str
    is_active: bool
    is_deleted: bool
    created_at: datetime
    modify_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    username: Optional[str] = None
    email_id: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role: Literal[UserRole.ADMIN, UserRole.USER]


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class AdminCreateUserRequest(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email_id: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    role: Literal[UserRole.ADMIN, UserRole.USER] = UserRole.USER
    is_verify: bool = True


class UserListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[UserResponse]
