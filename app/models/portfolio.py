from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base, BaseTable


class Project(Base, BaseTable):
    __tablename__ = "projects"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    repo_url = Column(String(500), nullable=True)
    live_url = Column(String(500), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    is_featured = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="projects")


class Skill(Base, BaseTable):
    __tablename__ = "skills"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False, index=True)
    category = Column(String(120), nullable=True)
    level = Column(String(50), nullable=True)

    user = relationship("User", back_populates="skills")


class Experience(Base, BaseTable):
    __tablename__ = "experiences"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(String(200), nullable=False, index=True)
    role_title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, nullable=False, default=False)

    user = relationship("User", back_populates="experiences")


class ResumeFile(Base, BaseTable):
    __tablename__ = "resume_files"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False, unique=True)
    storage_path = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="resume_files")
