# backend/app/api/profile.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from app.core.database import save_user_profile, get_user_profile

logger = logging.getLogger(__name__)
router = APIRouter()

class ProfileIn(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    resume_text: str = ""
    preferences: str = ""

class ProfileOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    resume_text: str
    preferences: str
    created_at: str
    updated_at: str

@router.post("/profile")
def create_or_update_profile(profile_data: ProfileIn):
    try:
        logger.info("Saving user profile")
        profile_id = save_user_profile(
            profile_data.name,
            profile_data.email,
            profile_data.phone,
            profile_data.resume_text,
            profile_data.preferences
        )
        return {"id": profile_id, "message": "Profile saved successfully"}
    except Exception as e:
        logger.error(f"Failed to save profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile", response_model=Optional[ProfileOut])
def get_profile():
    try:
        profile = get_user_profile()
        return profile
    except Exception as e:
        logger.error(f"Failed to get profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))