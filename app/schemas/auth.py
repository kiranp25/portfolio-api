from datetime import datetime
from pydantic import Field, EmailStr, BaseModel

from typing import Optional


class RegisterRequest(BaseModel):
    name: str = Field(...,min_length=2,max_length=100)
    email_id: EmailStr
    password: str = Field(...,min_length=8, max_length=72)


class OTPVerifyRequest(BaseModel):
    email_id: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)



class LoginRequest(BaseModel):
    email_id: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AuthUserResponse(BaseModel):
    id: int
    name: Optional[str]
    username: str
    email_id: EmailStr
    role: str
    is_verify: bool
    last_login: Optional[datetime]

    class Config:
        from_attributes = True
