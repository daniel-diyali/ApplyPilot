# backend/app/api/applications.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
from app.core.database import save_application, get_applications, get_application, save_generated_content

logger = logging.getLogger(__name__)
router = APIRouter()

class ApplicationIn(BaseModel):
    company: str
    position: str
    job_url: str = ""
    job_text: str = ""
    notes: str = ""

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