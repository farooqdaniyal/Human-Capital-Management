from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from groq import Groq
import os

from ..database import get_db
from ..deps import get_current_user
from ..models import User, Employee, Department, LeaveRequest, AiLog

router = APIRouter(prefix="/ai", tags=["ai"])


class ChatIn(BaseModel):
    question: str


def get_groq_client():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise HTTPException(500, "GROQ_API_KEY is not set")
    return Groq(api_key=key)


def get_employee_scope(user: User):
    if user.role == "employee":
        return user.employee_id
    return None


def tool_headcount(db: Session, user: User):
    if user.role == "employee":
        return "You are not allowed to view company headcount."

    count = db.query(Employee).filter(Employee.status.in_(["active", "probation"])).count()
    return f"Active/probation employee headcount is {count}."


def tool_employees_by_department(db: Session, user: User, dept_name: str | None = None):
    if user.role == "employee":
        return "You are not allowed to view department employee lists."

    q = db.query(Employee, Department).join(Department, Employee.department_id == Department.id)

    if dept_name:
        q = q.filter(Department.name.ilike(f"%{dept_name}%"))

    rows = q.all()

    if not rows:
        return "No employees found for that department."

    names = [f"{emp.full_name} ({dept.name})" for emp, dept in rows]
    return "Employees found: " + ", ".join(names[:20])


def tool_my_leave_balance(db: Session, user: User):
    if user.role != "employee":
        return "This question is for employees. HR/Admin can use leave summaries."

    if not user.employee_id:
        return "Your employee profile is not linked."

    approved = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == user.employee_id,
        LeaveRequest.status == "approved",
    ).all()

    used = sum([float(x.days_count or 0) for x in approved])

    # simple quota for MVP
    annual_quota = 14
    remaining = max(0, annual_quota - used)

    return f"You have used {used} approved leave days. Your approximate annual leave balance is {remaining} days."


def tool_leave_today(db: Session, user: User):
    today = date.today()

    if user.role == "employee":
        rows = db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == user.employee_id,
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
        ).all()
    else:
        rows = db.query(LeaveRequest).filter(
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
        ).all()

    if not rows:
        return "No approved leave found for today."

    result = []
    for r in rows:
        emp = db.get(Employee, r.employee_id)
        result.append(f"{emp.full_name if emp else 'Employee'} ({r.leave_type})")

    return "On leave today: " + ", ".join(result)


def tool_salary_question(db: Session, user: User, question: str):
    q = question.lower()

    if user.role == "employee":
        # Employee can only ask own salary
        if "my" in q or "meri" in q or "mera" in q:
            emp = db.get(Employee, user.employee_id)
            if not emp:
                return "Your employee profile is not linked."
            return f"Your basic salary is {emp.basic_salary:,.0f}. Gross salary is approximately {emp.basic_salary * 1.5:,.0f}."

        return "Sorry, you are not allowed to view another employee's salary."

    return "Admin/HR can view salary from the employee/payroll pages. For privacy, I will not expose salary details in chat."


def build_context_answer(db: Session, user: User, question: str):
    q = question.lower()

    if "headcount" in q or "how many employees" in q or "kitne employees" in q:
        return tool_headcount(db, user)

    if "department" in q or "it" in q or "hr" in q or "sales" in q:
        dept_name = None
        for name in ["IT", "HR", "Sales", "Finance"]:
            if name.lower() in q:
                dept_name = name
        return tool_employees_by_department(db, user, dept_name)

    if "leave today" in q or "on leave" in q or "chutti" in q:
        return tool_leave_today(db, user)

    if "leave balance" in q or "sick leaves" in q or "leaves left" in q:
        return tool_my_leave_balance(db, user)

    if "salary" in q or "pay" in q or "tankhwa" in q:
        return tool_salary_question(db, user, question)

    return "No exact tool matched. Answer using available HR policy and general system guidance."


@router.post("/chat")
def ai_chat(
    data: ChatIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    question = data.question.strip()

    if not question:
        raise HTTPException(422, "Question is required")

    tool_result = build_context_answer(db, user, question)

    client = get_groq_client()

    system_prompt = f"""
You are HCM Lite AI Assistant.
Answer in simple English or Roman Urdu if user asks in Roman Urdu.
Use ONLY the given tool result and HR rules.
Respect role-based access.
If the tool result refuses access, repeat that refusal politely.

User role: {user.role}
Tool result: {tool_result}
"""

    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL", "openai/gpt-oss-120b"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
        max_tokens=350,
    )

    answer = response.choices[0].message.content

    db.add(AiLog(user_id=user.id, question=question, answer=answer))
    db.commit()

    return {
        "answer": answer,
        "ai_generated": True,
        "tool_result": tool_result,
    }