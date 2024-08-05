from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base
from .join_tables.all import UsersRole
import uuid
from setup import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID, primary_key=True, default=uuid.uuid4,
    )
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    password_expires_at = Column(DateTime(True))


    roles = relationship("UsersRole", foreign_keys=[UsersRole.user_id])