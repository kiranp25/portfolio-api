from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_featured: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_featured: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ProjectResponse]


class SkillBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    category: Optional[str] = Field(default=None, max_length=120)
    level: Optional[str] = Field(default=None, max_length=50)


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    category: Optional[str] = Field(default=None, max_length=120)
    level: Optional[str] = Field(default=None, max_length=50)


class SkillResponse(SkillBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SkillListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[SkillResponse]


class ExperienceBase(BaseModel):
    company: str = Field(..., min_length=2, max_length=200)
    role_title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company: Optional[str] = Field(default=None, min_length=2, max_length=200)
    role_title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None


class ExperienceResponse(ExperienceBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ExperienceListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ExperienceResponse]


class ResumeFileResponse(BaseModel):
    id: int
    user_id: int
    original_name: str
    stored_name: str
    content_type: Optional[str]
    size_bytes: int
    uploaded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeFileListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ResumeFileResponse]
