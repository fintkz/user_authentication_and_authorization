from sqlalchemy import Column, String, Text

from ..base import Base


class EnumsPermissionName(Base):
    __tablename__ = "enums_permission_names"

    title = Column(String, primary_key=True)
    description = Column(Text)
