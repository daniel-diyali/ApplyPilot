# backend/app/api/jobs.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from app.core.scraper import scrape_job_text
from app.core.llm_client import generate_resume_bullets, generate_short_answer

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
