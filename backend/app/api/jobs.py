# backend/app/api/jobs.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from app.core.scraper import scrape_job_text
from app.core.llm_client import generate_resume_bullets, generate_short_answer, generate_cover_letter
from app.core.database import save_application, save_generated_content

logger = logging.getLogger(__name__)
router = APIRouter()

class ScrapeIn(BaseModel):
    url: str

class ScrapeOut(BaseModel):
    job_text: str
    title: str = ""
    company: str = ""

class TailorIn(BaseModel):
    job_text: str
    resume_text: str

class TailorOut(BaseModel):
    bullets: List[str]
    answer: str

class CoverLetterIn(BaseModel):
    job_text: str
    resume_text: str
    company_name: str = ""
    position_title: str = ""

class CoverLetterOut(BaseModel):
    cover_letter: str

@router.post("/scrape", response_model=ScrapeOut)
def scrape(in_data: ScrapeIn):
    try:
        logger.info(f"Scraping job from URL: {in_data.url}")
        out = scrape_job_text(in_data.url)
        return out
    except Exception as e:
        logger.error(f"Scraping failed for {in_data.url}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tailor", response_model=TailorOut)
def tailor(in_data: TailorIn):
    try:
        logger.info("Generating tailored resume content")
        bullets = generate_resume_bullets(in_data.job_text, in_data.resume_text)
        answer = generate_short_answer(in_data.job_text, "Why are you a good fit?", in_data.resume_text)
        return {"bullets": bullets, "answer": answer}
    except Exception as e:
        logger.error(f"Tailoring failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cover-letter", response_model=CoverLetterOut)
def cover_letter(in_data: CoverLetterIn):
    try:
        logger.info("Generating cover letter")
        letter = generate_cover_letter(
            in_data.job_text, 
            in_data.resume_text, 
            in_data.company_name, 
            in_data.position_title
        )
        
        # Save application if company/position provided
        if in_data.company_name and in_data.position_title:
            app_id = save_application(
                in_data.company_name,
                in_data.position_title,
                job_text=in_data.job_text
            )
            save_generated_content(app_id, "cover_letter", letter)
        
        return {"cover_letter": letter}
    except Exception as e:
        logger.error(f"Cover letter generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
