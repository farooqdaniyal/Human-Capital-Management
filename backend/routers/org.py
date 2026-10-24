from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Department
from ..deps import require_role, get_current_user

router = APIRouter(prefix="/org", tags=["org"])

class DeptIn(BaseModel):
    name: str

@router.post("/departments")
def create_department(data: DeptIn, db: Session = Depends(get_db),
                      user=Depends(require_role("admin"))):
    if db.query(Department).filter(Department.name == data.name).first():
        raise HTTPException(409, "Department already exists")
    d = Department(name=data.name)
    db.add(d); db.commit()
    return {"id": d.id, "name": d.name}

@router.get("/departments")
def list_departments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [{"id": d.id, "name": d.name} for d in db.query(Department).all()]