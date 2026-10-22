from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user_in: UserCreate) -> User:
    db_user = User(name=user_in.name, email=user_in.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()
