from app.db.base import Base, BaseTable
from sqlalchemy import Column, Boolean, DateTime, String
from sqlalchemy.orm import relationship


class UserRole:
    ADMIN = "admin"
    USER = "user"
    ALL = {ADMIN, USER}



class User(Base, BaseTable):
    __tablename__ = "users"

    name = Column(String(80), nullable=True)
    username = Column(String(80), nullable=False, unique=True, index=True)
    email_id = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_verify = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    otp = Column(String(20), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    role = Column(String(20), default=UserRole.USER, nullable=False)
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    projects = relationship("Project", back_populates="user")
    skills = relationship("Skill", back_populates="user")
    experiences = relationship("Experience", back_populates="user")
    resume_files = relationship("ResumeFile", back_populates="user")
