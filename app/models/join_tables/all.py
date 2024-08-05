# coding: utf-8
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base
import uuid
from setup import UUID
metadata = Base.metadata


class UsersRole(Base):
    __tablename__ = "users_roles"
    __table_args__ = (
        Index(
            "users_roles_user_id_role_id_uindex",
            "user_id",
            "role_id",
            unique=True,
        ),
    )

    id = Column(
        UUID, primary_key=True, default=uuid.uuid4,
    )
    user_id = Column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    role_id = Column(
        ForeignKey("roles.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    target_user_id = Column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )

    target_user = relationship("User", foreign_keys=[target_user_id])
    role = relationship("Role")


class RolesPermission(Base):
    __tablename__ = "roles_permissions"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    role_id = Column(ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    permission_id = Column(
        ForeignKey("permissions.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    permission = relationship("Permission")
    role = relationship("Role")