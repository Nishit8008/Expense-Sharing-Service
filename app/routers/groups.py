import csv
import io
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.group import GroupCreate, GroupResponse, GroupMemberAdd, GroupMemberResponse, GroupDetailResponse
from app.schemas.user import UserResponse
from app.schemas.expense import ExpenseSimpleResponse, ExpenseResponse
from app.schemas.analytics import GroupAnalyticsResponse
from app.services import group_service, expense_service, balance_service, analytics_service

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
def create_group(group_in: GroupCreate, db: Session = Depends(get_db)):
    """Create a new group."""
    return group_service.create_group(db, group_in)


@router.get("", response_model=List[GroupResponse])
def list_groups(db: Session = Depends(get_db)):
    """List all groups."""
    return db.query(group_service.Group).all()


@router.get("/{group_id}", response_model=GroupDetailResponse)
def get_group_details(group_id: int, db: Session = Depends(get_db)):
    """Get group details including its members."""
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    members = group_service.get_group_members(db, group_id)
    member_responses = [
        GroupMemberResponse(id=m.id, user_id=m.id, name=m.name, joined_at=None)
        for m in members
    ]
    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        created_at=group.created_at,
        members=member_responses
    )


@router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
def add_user_to_group(
    group_id: int,
    member_in: GroupMemberAdd,
    db: Session = Depends(get_db)
):
    """Add a user to a group."""
    target_group_id = group_id or member_in.group_id
    member = group_service.add_member(db, group_id=target_group_id, user_id=member_in.user_id)
    return {
        "message": "User added to group successfully",
        "group_id": member.group_id,
        "user_id": member.user_id
    }


@router.get("/{group_id}/members", response_model=List[UserResponse])
def list_group_members(group_id: int, db: Session = Depends(get_db)):
    """Return all members belonging to a group."""
    return group_service.get_group_members(db, group_id)


@router.get("/{group_id}/expenses")
def list_group_expenses(
    group_id: int,
    detailed: bool = Query(False, description="Set to true for full detailed expense breakdown"),
    db: Session = Depends(get_db)
):
    """
    Return all expenses for a particular group.
    By default returns format specified in assignment page 7:
    [
      {
        "description": "Dinner",
        "amount": 1200,
        "paid_by": "Mohit"
      }
    ]
    """
    expenses = expense_service.get_group_expenses(db, group_id)

    if detailed:
        results = []
        for e in expenses:
            splits_data = [
                {"user_id": s.user_id, "user_name": s.user.name, "amount": s.amount}
                for s in e.splits
            ]
            results.append({
                "id": e.id,
                "description": e.description,
                "amount": e.amount,
                "paid_by": e.payer.name,
                "paid_by_id": e.paid_by,
                "category": e.category,
                "split_type": e.split_type,
                "created_at": e.created_at,
                "splits": splits_data
            })
        return results

    # Strict assignment format
    return [
        {
            "description": e.description,
            "amount": int(e.amount) if e.amount == int(e.amount) else e.amount,
            "paid_by": e.payer.name
        }
        for e in expenses
    ]


@router.get("/{group_id}/balances")
def get_group_balances(group_id: int, db: Session = Depends(get_db)):
    """Return balances between members of a specific group."""
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    return balance_service.calculate_balances(db, group_id=group_id)


@router.get("/{group_id}/analytics", response_model=GroupAnalyticsResponse)
def get_group_analytics(group_id: int, db: Session = Depends(get_db)):
    """
    Product Enhancement: Detailed group spending analytics,
    category breakdown, member fair share vs paid, and top spender.
    """
    return analytics_service.get_group_analytics(db, group_id)


@router.get("/{group_id}/export/csv")
def export_group_expenses_csv(group_id: int, db: Session = Depends(get_db)):
    """
    Product Enhancement: Export group expenses as a CSV file.
    """
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    expenses = expense_service.get_group_expenses(db, group_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Expense ID", "Description", "Amount", "Category", "Paid By", "Split Type", "Date"])

    for e in expenses:
        writer.writerow([
            e.id,
            e.description,
            e.amount,
            e.category,
            e.payer.name,
            e.split_type,
            e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else ""
        ])

    csv_data = output.getvalue()
    output.close()

    filename = f"group_{group_id}_expenses.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
