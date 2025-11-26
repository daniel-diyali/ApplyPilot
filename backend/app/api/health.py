# backend/app/api/health.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthOut(BaseModel):
    status: str
    message: str

@router.get("/health", response_model=HealthOut)
def health_check():
    return {"status": "healthy", "message": "ApplyPilot backend is running"}