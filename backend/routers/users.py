from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..security import hash_password
from ..deps import require_role
from ..utils import temp_password

router = APIRouter(prefix="/users", tags=["users"])

class HRIn(BaseModel):
    name: str
    email: EmailStr

@router.post("/hr")
def create_hr(data: HRIn, db: Session = Depends(get_db),
              admin=Depends(require_role("admin"))):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(409, "Email already exists")
    pwd = temp_password()
    db.add(User(name=data.name, email=data.email, role="hr",
                password_hash=hash_password(pwd), must_change_password=True))
    db.commit()
    return {"email": data.email, "temporary_password": pwd}