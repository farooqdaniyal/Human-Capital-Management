from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LeaveRequest, Employee, User
from ..deps import require_role, get_current_user

router = APIRouter(prefix="/leave", tags=["leave"])


class LeaveApplyIn(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveDecisionIn(BaseModel):
    comment: str | None = None


def count_days(start: date, end: date) -> int:
    return (end - start).days + 1


@router.post("/apply")
def apply_leave(
    data: LeaveApplyIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("employee")),
):
    if not user.employee_id:
        raise HTTPException(422, "Employee profile not linked")

    if data.end_date < data.start_date:
        raise HTTPException(422, "End date cannot be before start date")

    # simple overlap check
    existing = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == user.employee_id,
        LeaveRequest.status.in_(["pending", "approved"]),
        LeaveRequest.start_date <= data.end_date,
        LeaveRequest.end_date >= data.start_date,
    ).first()

    if existing:
        raise HTTPException(422, "Leave overlaps with existing request")

    days = count_days(data.start_date, data.end_date)

    leave = LeaveRequest(
        employee_id=user.employee_id,
        leave_type=data.leave_type,
        start_date=data.start_date,
        end_date=data.end_date,
        days_count=days,
        reason=data.reason,
        status="pending",
    )

    db.add(leave)
    db.commit()
    db.refresh(leave)

    return {"message": "Leave request submitted", "id": leave.id}


@router.get("/my")
def my_leaves(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("employee")),
):
    rows = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == user.employee_id
    ).order_by(LeaveRequest.created_at.desc()).all()

    return [
        {
            "id": r.id,
            "leave_type": r.leave_type,
            "start_date": str(r.start_date),
            "end_date": str(r.end_date),
            "days_count": r.days_count,
            "reason": r.reason,
            "status": r.status,
            "hr_comment": r.hr_comment,
        }
        for r in rows
    ]


@router.get("/pending")
def pending_leaves(
    db: Session = Depends(get_db),
    hr: User = Depends(require_role("hr")),
):
    rows = db.query(LeaveRequest).filter(
        LeaveRequest.status == "pending"
    ).order_by(LeaveRequest.created_at.desc()).all()

    result = []
    for r in rows:
        emp = db.get(Employee, r.employee_id)
        result.append(
            {
                "id": r.id,
                "employee_id": r.employee_id,
                "employee_name": emp.full_name if emp else "Unknown",
                "employee_code": emp.employee_code if emp else "—",
                "leave_type": r.leave_type,
                "start_date": str(r.start_date),
                "end_date": str(r.end_date),
                "days_count": r.days_count,
                "reason": r.reason,
                "status": r.status,
            }
        )

    return result


@router.post("/{leave_id}/approve")
def approve_leave(
    leave_id: int,
    data: LeaveDecisionIn,
    db: Session = Depends(get_db),
    hr: User = Depends(require_role("hr")),
):
    leave = db.get(LeaveRequest, leave_id)

    if not leave:
        raise HTTPException(404, "Leave request not found")

    if leave.status != "pending":
        raise HTTPException(409, "Leave already decided")

    leave.status = "approved"
    leave.hr_comment = data.comment
    leave.approved_by = hr.id

    db.commit()

    return {"message": "Leave approved"}


@router.post("/{leave_id}/reject")
def reject_leave(
    leave_id: int,
    data: LeaveDecisionIn,
    db: Session = Depends(get_db),
    hr: User = Depends(require_role("hr")),
):
    leave = db.get(LeaveRequest, leave_id)

    if not leave:
        raise HTTPException(404, "Leave request not found")

    if leave.status != "pending":
        raise HTTPException(409, "Leave already decided")

    leave.status = "rejected"
    leave.hr_comment = data.comment
    leave.approved_by = hr.id

    db.commit()

    return {"message": "Leave rejected"}