from sqlalchemy import Column, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from setup import UUID
from .base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(
        UUID,
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
    )
    role_name = Column(String, nullable=False, unique=True)
    description = Column(Text)

    permissions = relationship(
        "Permission",
        secondary="roles_permissions",
        back_populates="roles",
        viewonly=True,
    )
