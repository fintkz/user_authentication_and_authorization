from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    role_name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleInDBBase(RoleBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


class Role(RoleInDBBase):
    pass


class RoleInDB(RoleInDBBase):
    pass
