from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate


def create_group(db: Session, group_in: GroupCreate) -> Group:
    db_group = Group(name=group_in.name, description=group_in.description)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def get_group(db: Session, group_id: int) -> Optional[Group]:
    return db.query(Group).filter(Group.id == group_id).first()


def add_member(db: Session, group_id: int, user_id: int) -> GroupMember:
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user.name} is already a member of group {group.name}"
        )

    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_group_members(db: Session, group_id: int) -> List[User]:
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )

    members = (
        db.query(User)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )
    return members


def is_member(db: Session, group_id: int, user_id: int) -> bool:
    count = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).count()
    return count > 0
