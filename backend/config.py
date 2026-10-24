import os
from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"
JWT_EXPIRE_MIN = 480
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hcm.db")
AI_API_KEY = os.getenv("AI_API_KEY", "")