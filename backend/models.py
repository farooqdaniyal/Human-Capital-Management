from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)          # admin | hr | employee
    employee_id = Column(Integer, nullable=True)   # employee ke liye
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CompanySettings(Base):
    __tablename__ = "company_settings"
    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    office_start = Column(String, default="09:00")
    grace_minutes = Column(Integer, default=15)
    half_day_hours = Column(Float, default=5)
    weekend_days = Column(String, default="SAT,SUN")
    office_lat = Column(Float, nullable=True)
    office_lng = Column(Float, nullable=True)
    radius_m = Column(Integer, default=150)
    setup_done = Column(Boolean, default=False)

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_code = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation = Column(String, nullable=True)
    joining_date = Column(Date, nullable=False)
    basic_salary = Column(Float, nullable=False)
    status = Column(String, default="active")   # active | probation | exited
    created_at = Column(DateTime, default=datetime.utcnow)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String, nullable=False)   # annual | sick | casual | unpaid
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days_count = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="pending")    # pending | approved | rejected | cancelled
    hr_comment = Column(String, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AiLog(Base):
    __tablename__ = "ai_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)