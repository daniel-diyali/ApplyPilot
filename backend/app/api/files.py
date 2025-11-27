# backend/app/api/files.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import logging
from app.core.file_parser import parse_resume_file

logger = logging.getLogger(__name__)
router = APIRouter()

class ResumeUploadOut(BaseModel):
    filename: str
    text: str
    message: str

@router.post("/upload-resume", response_model=ResumeUploadOut)
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF and DOCX files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Parse the file
        logger.info(f"Parsing resume file: {file.filename}")
        resume_text = parse_resume_file(file.filename, file_content)
        
        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file"
            )
        
        return {
            "filename": file.filename,
            "text": resume_text,
            "message": "Resume uploaded and parsed successfully"
        }
        
    except ValueError as e:
        logger.error(f"File parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resume upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))