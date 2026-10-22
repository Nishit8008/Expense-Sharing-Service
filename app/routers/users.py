from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    return user_service.create_user(db, user_in)


@router.get("", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return all users in the system."""
    return user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID."""
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user
