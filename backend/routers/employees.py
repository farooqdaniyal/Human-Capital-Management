from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Employee, Department
from ..security import hash_password
from ..deps import require_role
from ..utils import temp_password

router = APIRouter(prefix="/employees", tags=["employees"])

class EmployeeIn(BaseModel):
    employee_code: str
    full_name: str
    email: EmailStr
    department_id: int
    designation: str | None = None
    joining_date: date
    basic_salary: float = Field(gt=0)
    phone: str | None = None
    address: str | None = None

@router.post("")
def register_employee(data: EmployeeIn, db: Session = Depends(get_db),
                      hr=Depends(require_role("hr"))):
    if not db.get(Department, data.department_id):
        raise HTTPException(422, "Unknown department")
    if db.query(Employee).filter(Employee.employee_code == data.employee_code).first():
        raise HTTPException(409, "Employee code already exists")
    if db.query(User).filter(User.email == data.email).first() or \
       db.query(Employee).filter(Employee.email == data.email).first():
        raise HTTPException(409, "Email already exists")

    emp = Employee(**data.model_dump())
    db.add(emp); db.flush()                      # emp.id mil jaye
    pwd = temp_password()
    db.add(User(name=data.full_name, email=data.email, role="employee",
                employee_id=emp.id, password_hash=hash_password(pwd),
                must_change_password=True))
    db.commit()
    return {"employee_id": emp.id, "email": data.email, "temporary_password": pwd}

@router.get("")
def list_employees(search: str = "", page: int = 1, size: int = 20,
                   db: Session = Depends(get_db),
                   user=Depends(require_role("admin", "hr"))):
    q = db.query(Employee)
    if search:
        q = q.filter(Employee.full_name.ilike(f"%{search}%"))
    rows = q.offset((page - 1) * size).limit(size).all()
    return [
    {
        "id": e.id,
        "code": e.employee_code,
        "name": e.full_name,
        "email": e.email,
        "department_id": e.department_id,
        "designation": e.designation,
        "status": e.status,
        "joining_date": str(e.joining_date) if e.joining_date else None,
        "basic_salary": e.basic_salary,
    }
    for e in rows
]