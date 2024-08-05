from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import EmailError, validate_email
from sqlalchemy.orm import Session, joinedload

from app.core.security import (
    get_password_hash,
    get_temporary_password,
    verify_password,
)
from app.crud.base import CRUDBase
from app.models.join_tables import UsersRole
from app.models.role import Role
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(
        self,
        db: Session,
        *,
        obj_in: UserCreate,
    ) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:
            if update_data["password"]:
                hashed_password = get_password_hash(update_data["password"])
                update_data["hashed_password"] = hashed_password
            del update_data["password"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[User]:
        try:
            validate_email(email)
            user = self.get_by_email(db, email=email)
        except EmailError:
            user = self.get_by_username(db, username=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def add_role(
        self, db: Session, *, user: User, role: Role, target_user: User = None
    ) -> Optional[UsersRole]:
        users_role = (
            db.query(UsersRole)
            .filter_by(
                user_id=user.id, role_id=role.id, target_user_id=target_user.id
            )
            .first()
        )
        if users_role:
            return users_role

        db_obj = UsersRole(user_id=user.id, role_id=role.id)
        if target_user:
            db_obj.target_user_id = target_user.id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_role(
        self, db: Session, *, user: User, role: Role, target_user: User = None
    ) -> bool:
        users_role = (
            db.query(UsersRole)
            .filter_by(
                user_id=user.id, role_id=role.id, target_user_id=target_user.id
            )
            .first()
        )
        if users_role:
            db.delete(users_role)
            db.commit()
        return True

    def get_all_users(
        self, db: Session, *, created_after: datetime, created_before: datetime
    ) -> Optional[List[User]]:
        return (
            db.query(User)
            .filter(
                User.created_at < created_before,
                User.created_at > created_after,
            )
            .order_by(User.created_at)
            .all()
        )

    def delete_user(self, db: Session, *, user: User) -> bool:
        user_obj = (
            db.query(User)
            .filter(User.id == user.id)
            .first()
        )
        if user_obj:
            db.flush()
            db.delete(user_obj)
            db.commit()
            return True
        return False

    def get_by_email_or_username(
        self, db: Session, *, email_or_username: str
    ) -> Optional[User]:
        try:
            validate_email(email_or_username)
            user = self.get_by_email(db, email=email_or_username)
        except EmailError:
            user = self.get_by_username(db, username=email_or_username)
        if not user:
            return None
        return user

    def get_multiple(
        self, db: Session, *, user_ids: List[int]
    ) -> Optional[List[User]]:
        return db.query(User).filter(User.id.in_(user_ids)).all()


user = CRUDUser(User)
