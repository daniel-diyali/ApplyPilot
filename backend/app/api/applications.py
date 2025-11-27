# backend/app/api/applications.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
import logging
from app.core.database import save_application, get_applications, get_application, save_generated_content
from app.core.validators import validate_url, validate_text_length, sanitize_text

logger = logging.getLogger(__name__)
router = APIRouter()

class ApplicationIn(BaseModel):
    company: str
    position: str
    job_url: str = ""
    job_text: str = ""
    notes: str = ""
    
    @validator('company')
    def validate_company(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Company name is required and must be at least 2 characters')
        return sanitize_text(v)
    
    @validator('position')
    def validate_position(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Position title is required and must be at least 2 characters')
        return sanitize_text(v)
    
    @validator('job_url')
    def validate_job_url(cls, v):
        if v and not validate_url(v):
            raise ValueError('Invalid URL format')
        return v
    
    @validator('job_text')
    def validate_job_text(cls, v):
        if v and not validate_text_length(v, min_length=20):
            raise ValueError('Job text must be at least 20 characters')
        return sanitize_text(v)
    
    @validator('notes')
    def validate_notes(cls, v):
        return sanitize_text(v)

class ApplicationOut(BaseModel):
    id: int
    company: str
    position: str
    job_url: str
    job_text: str
    status: str
    applied_date: str
    notes: str

@router.post("/applications", response_model=dict)
def create_application(app_data: ApplicationIn):
    try:
        logger.info(f"Creating application for {app_data.company} - {app_data.position}")
        app_id = save_application(
            app_data.company,
            app_data.position,
            app_data.job_url,
            app_data.job_text,
            app_data.notes
        )
        return {"id": app_id, "message": "Application saved"}
    except Exception as e:
        logger.error(f"Failed to save application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications", response_model=List[ApplicationOut])
def list_applications():
    try:
        apps = get_applications()
        return apps
    except Exception as e:
        logger.error(f"Failed to get applications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications/{app_id}")
def get_application_detail(app_id: int):
    try:
        app = get_application(app_id)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        return app
    except Exception as e:
        logger.error(f"Failed to get application {app_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))