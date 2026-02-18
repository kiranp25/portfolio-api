from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class PublicProjectResponse(BaseModel):
    title: str
    description: Optional[str]
    repo_url: Optional[str]
    live_url: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    is_featured: bool

    class Config:
        from_attributes = True


class PublicSkillResponse(BaseModel):
    name: str
    category: Optional[str]
    level: Optional[str]

    class Config:
        from_attributes = True


class PublicExperienceResponse(BaseModel):
    company: str
    role_title: str
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    is_current: bool

    class Config:
        from_attributes = True


class PublicProfileResponse(BaseModel):
    name: Optional[str]
    username: str
    projects: List[PublicProjectResponse]
    skills: List[PublicSkillResponse]
    experiences: List[PublicExperienceResponse]
