# backend/app/api/profile.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import logging
from app.core.database import save_user_profile, get_user_profile
from app.core.validators import validate_email, validate_phone, validate_text_length, sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter()

class ProfileIn(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    resume_text: str = ""
    preferences: str = ""
    
    @validator('name')
    def validate_name(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return sanitize_text(v)
    
    @validator('email')
    def validate_email_format(cls, v):
        if v and not validate_email(v):
            raise ValueError('Invalid email format')
        return v.strip().lower()
    
    @validator('phone')
    def validate_phone_format(cls, v):
        if v and not validate_phone(v):
            raise ValueError('Invalid phone number format')
        return v.strip()
    
    @validator('resume_text')
    def validate_resume_text(cls, v):
        if v and not validate_text_length(v, min_length=50):
            raise ValueError('Resume text must be at least 50 characters')
        return sanitize_text(v)
    
    @validator('preferences')
    def validate_preferences(cls, v):
        return sanitize_text(v)

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