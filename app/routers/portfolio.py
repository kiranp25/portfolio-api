from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.deps import get_db
from app.models.users import User
from app.schemas.portfolio import (
    ExperienceCreate,
    ExperienceListResponse,
    ExperienceResponse,
    ExperienceUpdate,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
    ResumeFileListResponse,
    ResumeFileResponse,
    SkillCreate,
    SkillListResponse,
    SkillResponse,
    SkillUpdate,
)
from app.services.portfolio_service import (
    create_experience,
    create_project,
    create_skill,
    delete_experience,
    delete_project,
    delete_resume_file,
    delete_skill,
    get_experience,
    get_project,
    get_resume_file,
    get_skill,
    list_experiences,
    list_projects,
    list_resume_files,
    list_skills,
    update_experience,
    update_project,
    update_skill,
    upload_resume_file,
)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def post_project(
    payload: ProjectCreate,
    user_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_project(db, current_user, payload, user_id)


@router.get("/projects", response_model=ProjectListResponse, status_code=status.HTTP_200_OK)
def get_projects(
    user_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_projects(db, current_user, user_id, search, limit, offset)


@router.get("/projects/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_project(db, current_user, project_id)


@router.put("/projects/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def put_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_project(db, current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=status.HTTP_200_OK)
def remove_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_project(db, current_user, project_id)


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def post_skill(
    payload: SkillCreate,
    user_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_skill(db, current_user, payload, user_id)


@router.get("/skills", response_model=SkillListResponse, status_code=status.HTTP_200_OK)
def get_skills(
    user_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_skills(db, current_user, user_id, search, limit, offset)


@router.get("/skills/{skill_id}", response_model=SkillResponse, status_code=status.HTTP_200_OK)
def get_skill_by_id(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_skill(db, current_user, skill_id)


@router.put("/skills/{skill_id}", response_model=SkillResponse, status_code=status.HTTP_200_OK)
def put_skill(
    skill_id: int,
    payload: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_skill(db, current_user, skill_id, payload)


@router.delete("/skills/{skill_id}", status_code=status.HTTP_200_OK)
def remove_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_skill(db, current_user, skill_id)


@router.post("/experiences", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
def post_experience(
    payload: ExperienceCreate,
    user_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_experience(db, current_user, payload, user_id)


@router.get("/experiences", response_model=ExperienceListResponse, status_code=status.HTTP_200_OK)
def get_all_experiences(
    user_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_experiences(db, current_user, user_id, search, limit, offset)


@router.get("/experiences/{experience_id}", response_model=ExperienceResponse, status_code=status.HTTP_200_OK)
def get_experience_by_id(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_experience(db, current_user, experience_id)


@router.put("/experiences/{experience_id}", response_model=ExperienceResponse, status_code=status.HTTP_200_OK)
def put_experience(
    experience_id: int,
    payload: ExperienceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_experience(db, current_user, experience_id, payload)


@router.delete("/experiences/{experience_id}", status_code=status.HTTP_200_OK)
def remove_experience(
    experience_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_experience(db, current_user, experience_id)


@router.post("/files/upload", response_model=ResumeFileResponse, status_code=status.HTTP_201_CREATED)
def post_resume_file(
    file: UploadFile = File(...),
    user_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return upload_resume_file(db, current_user, file, user_id)


@router.get("/files", response_model=ResumeFileListResponse, status_code=status.HTTP_200_OK)
def get_resume_files(
    user_id: Optional[int] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_resume_files(db, current_user, user_id, limit, offset)


@router.get("/files/{file_id}", response_model=ResumeFileResponse, status_code=status.HTTP_200_OK)
def get_resume_file_by_id(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_resume_file(db, current_user, file_id)


@router.delete("/files/{file_id}", status_code=status.HTTP_200_OK)
def remove_resume_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_resume_file(db, current_user, file_id)
