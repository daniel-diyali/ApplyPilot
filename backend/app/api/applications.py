# backend/app/api/applications.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
import logging
from app.core.database import save_application, get_applications, get_application, save_generated_content, update_application_status, get_applications_by_status, get_application_stats
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

class StatusUpdateIn(BaseModel):
    status: str
    notes: str = ""
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['applied', 'reviewing', 'phone_screen', 'interview', 'final_round', 'offer', 'rejected', 'withdrawn']
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v
    
    @validator('notes')
    def validate_notes(cls, v):
        return sanitize_text(v)

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

@router.put("/applications/{app_id}/status")
def update_status(app_id: int, status_data: StatusUpdateIn):
    try:
        logger.info(f"Updating application {app_id} status to {status_data.status}")
        updated = update_application_status(app_id, status_data.status, status_data.notes)
        if not updated:
            raise HTTPException(status_code=404, detail="Application not found")
        return {"message": "Status updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update status for application {app_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications/status/{status}")
def get_applications_by_status_endpoint(status: str):
    try:
        apps = get_applications_by_status(status)
        return apps
    except Exception as e:
        logger.error(f"Failed to get applications by status {status}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/applications/stats")
def get_stats():
    try:
        stats = get_application_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get application stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))