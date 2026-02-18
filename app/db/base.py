from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,  Integer, Boolean, DateTime
from datetime import datetime
from sqlalchemy.sql import func

Base = declarative_base()
class BaseTable:
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)

    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    modify_by = Column(Integer, nullable=True)
    modify_at = Column(DateTime, onupdate=func.now())

    deleted_by = Column(Integer, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

