from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, CompanySettings
from ..security import hash_password, verify_password, create_token
from ..deps import get_current_user

router = APIRouter()

class SetupIn(BaseModel):
    company_name: str
    admin_name: str
    admin_email: EmailStr
    admin_password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.get("/setup/status")
def setup_status(db: Session = Depends(get_db)):
    s = db.query(CompanySettings).first()
    return {"setup_done": bool(s and s.setup_done)}

@router.post("/setup")
def setup(data: SetupIn, db: Session = Depends(get_db)):
    if db.query(CompanySettings).first():
        raise HTTPException(409, "Setup already done")
    db.add(CompanySettings(company_name=data.company_name, setup_done=True))
    db.add(User(name=data.admin_name, email=data.admin_email,
                password_hash=hash_password(data.admin_password), role="admin"))
    db.commit()
    return {"message": "Setup complete"}

@router.post("/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == data.email).first()
    if not u or not verify_password(data.password, u.password_hash) or not u.is_active:
        raise HTTPException(401, "Wrong email or password")
    return {"token": create_token(u.id, u.role), "role": u.role,
            "name": u.name, "must_change_password": u.must_change_password}

@router.get("/auth/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

class ChangePwdIn(BaseModel):
    old_password: str
    new_password: str

@router.post("/auth/change-password")
def change_password(data: ChangePwdIn, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(401, "Old password is wrong")
    if len(data.new_password) < 6:
        raise HTTPException(422, "Password must be at least 6 characters")
    user.password_hash = hash_password(data.new_password)
    user.must_change_password = False
    db.commit()
    return {"message": "Password changed"}