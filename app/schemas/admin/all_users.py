from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr



# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    created_at: Optional[datetime] = None


class UserInDBBase(UserBase):
    id: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class AdminUser(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class AllUsers(BaseModel):
    users: List[AdminUser]
