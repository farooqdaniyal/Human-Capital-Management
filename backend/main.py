from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, org, users, employees, leave, ai

Base.metadata.create_all(bind=engine)
app = FastAPI(title="HCM Lite")

app.include_router(auth.router)
app.include_router(org.router)
app.include_router(users.router)
app.include_router(employees.router)
app.include_router(leave.router)
app.include_router(ai.router)

@app.get("/")
def home():
    return {"message": "HCM Lite API chal raha hai. /docs kholo."}