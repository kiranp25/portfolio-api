from datetime import datetime
from pathlib import Path
from typing import Optional, Type
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.portfolio import Experience, Project, ResumeFile, Skill
from app.models.users import User, UserRole
from app.services.public_service import invalidate_public_profile_cache


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "resumes"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _resolve_owner_id(current_user: User, user_id: Optional[int] = None) -> int:
    if user_id is None:
        return current_user.id
    if current_user.role != UserRole.ADMIN and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's records"
        )
    return user_id


def _get_owned_record(
    db: Session,
    model: Type[Project | Skill | Experience | ResumeFile],
    record_id: int,
    current_user: User,
):
    record = db.query(model).filter(model.id == record_id, model.is_deleted == False).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    if current_user.role != UserRole.ADMIN and record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not permitted")
    return record


def create_project(db: Session, current_user: User, payload, user_id: Optional[int] = None) -> Project:
    owner_id = _resolve_owner_id(current_user, user_id)
    project = Project(user_id=owner_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    _invalidate_public_cache_by_user_id(db, owner_id)
    return project


def list_projects(
    db: Session,
    current_user: User,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    owner_id = _resolve_owner_id(current_user, user_id)
    query = db.query(Project).filter(Project.user_id == owner_id, Project.is_deleted == False)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Project.title.ilike(term)) | (Project.description.ilike(term)))
    total = query.count()
    items = query.order_by(Project.id.desc()).offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def get_project(db: Session, current_user: User, project_id: int) -> Project:
    return _get_owned_record(db, Project, project_id, current_user)


def update_project(db: Session, current_user: User, project_id: int, payload) -> Project:
    project = _get_owned_record(db, Project, project_id, current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    project.modify_by = current_user.id
    db.commit()
    db.refresh(project)
    _invalidate_public_cache_by_user_id(db, project.user_id)
    return project


def delete_project(db: Session, current_user: User, project_id: int):
    project = _get_owned_record(db, Project, project_id, current_user)
    project.is_deleted = True
    project.deleted_by = current_user.id
    project.deleted_at = datetime.utcnow()
    db.commit()
    _invalidate_public_cache_by_user_id(db, project.user_id)
    return {"message": "Project deleted successfully"}


def create_skill(db: Session, current_user: User, payload, user_id: Optional[int] = None) -> Skill:
    owner_id = _resolve_owner_id(current_user, user_id)
    skill = Skill(user_id=owner_id, **payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    _invalidate_public_cache_by_user_id(db, owner_id)
    return skill


def list_skills(
    db: Session,
    current_user: User,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    owner_id = _resolve_owner_id(current_user, user_id)
    query = db.query(Skill).filter(Skill.user_id == owner_id, Skill.is_deleted == False)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Skill.name.ilike(term)) | (Skill.category.ilike(term)))
    total = query.count()
    items = query.order_by(Skill.id.desc()).offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def get_skill(db: Session, current_user: User, skill_id: int) -> Skill:
    return _get_owned_record(db, Skill, skill_id, current_user)


def update_skill(db: Session, current_user: User, skill_id: int, payload) -> Skill:
    skill = _get_owned_record(db, Skill, skill_id, current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(skill, key, value)
    skill.modify_by = current_user.id
    db.commit()
    db.refresh(skill)
    _invalidate_public_cache_by_user_id(db, skill.user_id)
    return skill


def delete_skill(db: Session, current_user: User, skill_id: int):
    skill = _get_owned_record(db, Skill, skill_id, current_user)
    skill.is_deleted = True
    skill.deleted_by = current_user.id
    skill.deleted_at = datetime.utcnow()
    db.commit()
    _invalidate_public_cache_by_user_id(db, skill.user_id)
    return {"message": "Skill deleted successfully"}


def create_experience(db: Session, current_user: User, payload, user_id: Optional[int] = None) -> Experience:
    owner_id = _resolve_owner_id(current_user, user_id)
    experience = Experience(user_id=owner_id, **payload.model_dump())
    db.add(experience)
    db.commit()
    db.refresh(experience)
    _invalidate_public_cache_by_user_id(db, owner_id)
    return experience


def list_experiences(
    db: Session,
    current_user: User,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    owner_id = _resolve_owner_id(current_user, user_id)
    query = db.query(Experience).filter(Experience.user_id == owner_id, Experience.is_deleted == False)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((Experience.company.ilike(term)) | (Experience.role_title.ilike(term)))
    total = query.count()
    items = query.order_by(Experience.id.desc()).offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def get_experience(db: Session, current_user: User, experience_id: int) -> Experience:
    return _get_owned_record(db, Experience, experience_id, current_user)


def update_experience(db: Session, current_user: User, experience_id: int, payload) -> Experience:
    experience = _get_owned_record(db, Experience, experience_id, current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(experience, key, value)
    experience.modify_by = current_user.id
    db.commit()
    db.refresh(experience)
    _invalidate_public_cache_by_user_id(db, experience.user_id)
    return experience


def delete_experience(db: Session, current_user: User, experience_id: int):
    experience = _get_owned_record(db, Experience, experience_id, current_user)
    experience.is_deleted = True
    experience.deleted_by = current_user.id
    experience.deleted_at = datetime.utcnow()
    db.commit()
    _invalidate_public_cache_by_user_id(db, experience.user_id)
    return {"message": "Experience deleted successfully"}


def upload_resume_file(
    db: Session,
    current_user: User,
    file: UploadFile,
    user_id: Optional[int] = None,
) -> ResumeFile:
    owner_id = _resolve_owner_id(current_user, user_id)

    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC, DOCX files are supported"
        )

    file_bytes = file.file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10 MB"
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    extension = Path(file.filename or "resume").suffix
    stored_name = f"{uuid4().hex}{extension}"
    disk_path = UPLOAD_DIR / stored_name
    disk_path.write_bytes(file_bytes)

    record = ResumeFile(
        user_id=owner_id,
        original_name=file.filename or "resume",
        stored_name=stored_name,
        storage_path=str(disk_path),
        content_type=content_type or None,
        size_bytes=len(file_bytes),
        uploaded_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    _invalidate_public_cache_by_user_id(db, owner_id)
    return record


def list_resume_files(
    db: Session,
    current_user: User,
    user_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
):
    owner_id = _resolve_owner_id(current_user, user_id)
    query = db.query(ResumeFile).filter(ResumeFile.user_id == owner_id, ResumeFile.is_deleted == False)
    total = query.count()
    items = query.order_by(ResumeFile.id.desc()).offset(offset).limit(limit).all()
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def get_resume_file(db: Session, current_user: User, file_id: int) -> ResumeFile:
    return _get_owned_record(db, ResumeFile, file_id, current_user)


def delete_resume_file(db: Session, current_user: User, file_id: int):
    record = _get_owned_record(db, ResumeFile, file_id, current_user)
    record.is_deleted = True
    record.deleted_by = current_user.id
    record.deleted_at = datetime.utcnow()

    path = Path(record.storage_path)
    if path.exists():
        path.unlink()

    db.commit()
    _invalidate_public_cache_by_user_id(db, record.user_id)
    return {"message": "Resume file deleted successfully"}


def _invalidate_public_cache_by_user_id(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.username:
        invalidate_public_profile_cache(user.username)
