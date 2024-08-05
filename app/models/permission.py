import uuid
from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base
from setup import UUID

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(
        UUID, primary_key=True, default=uuid.uuid4,
    )
    permission_name = Column(
        ForeignKey(
            "enums_permission_names.title",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    description = Column(Text)

    permission_name1 = relationship("EnumsPermissionName")
    roles = relationship(
        "Role",
        secondary="roles_permissions",
        back_populates="permissions",
        viewonly=True,
    )