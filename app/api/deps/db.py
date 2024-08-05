from typing import Generator

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        print("Rolling back from db error")
        print(e)
    finally:
        db.close()