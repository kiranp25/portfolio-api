from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.rate_limit import limit_public
from app.schemas.public import PublicProfileResponse
from app.services.public_service import get_public_profile

router = APIRouter(prefix="/public", tags=["Public"])


@router.get(
    "/{username}",
    response_model=PublicProfileResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(limit_public)],
)
def get_profile(username: str, db: Session = Depends(get_db)):
    return get_public_profile(db, username)
