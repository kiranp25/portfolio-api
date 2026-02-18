from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import cache_delete, cache_get_json, cache_set_json
from app.models.portfolio import Experience, Project, Skill
from app.models.users import User


def public_profile_cache_key(username: str) -> str:
    return f"public_profile:{username.lower()}"


def invalidate_public_profile_cache(username: str) -> None:
    cache_delete(public_profile_cache_key(username))


def get_public_profile(db: Session, username: str):
    cache_key = public_profile_cache_key(username)
    cached = cache_get_json(cache_key)
    if cached:
        return cached

    user = db.query(User).filter(
        User.username == username,
        User.is_active == True,
        User.is_deleted == False,
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    projects = db.query(Project).filter(
        Project.user_id == user.id,
        Project.is_deleted == False,
        Project.is_active == True,
    ).order_by(Project.is_featured.desc(), Project.id.desc()).all()

    skills = db.query(Skill).filter(
        Skill.user_id == user.id,
        Skill.is_deleted == False,
        Skill.is_active == True,
    ).order_by(Skill.name.asc()).all()

    experiences = db.query(Experience).filter(
        Experience.user_id == user.id,
        Experience.is_deleted == False,
        Experience.is_active == True,
    ).order_by(Experience.start_date.desc(), Experience.id.desc()).all()

    response = {
        "name": user.name,
        "username": user.username,
        "projects": [
            {
                "title": item.title,
                "description": item.description,
                "repo_url": item.repo_url,
                "live_url": item.live_url,
                "start_date": item.start_date,
                "end_date": item.end_date,
                "is_featured": item.is_featured,
            }
            for item in projects
        ],
        "skills": [
            {
                "name": item.name,
                "category": item.category,
                "level": item.level,
            }
            for item in skills
        ],
        "experiences": [
            {
                "company": item.company,
                "role_title": item.role_title,
                "description": item.description,
                "start_date": item.start_date,
                "end_date": item.end_date,
                "is_current": item.is_current,
            }
            for item in experiences
        ],
    }

    cache_set_json(cache_key, response, settings.PUBLIC_PROFILE_CACHE_TTL_SECONDS)
    return response
