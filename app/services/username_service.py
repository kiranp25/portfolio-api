import re

from sqlalchemy.orm import Session

from app.models.users import User


def normalize_username_seed(seed: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_]", "", seed.lower().replace(" ", "_"))
    return cleaned or "user"


def generate_unique_username(db: Session, seed: str) -> str:
    base = normalize_username_seed(seed)
    candidate = base
    counter = 1

    while db.query(User).filter(User.username == candidate).first() is not None:
        counter += 1
        candidate = f"{base}{counter}"

    return candidate
