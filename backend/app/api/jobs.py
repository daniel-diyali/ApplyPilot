# backend/app/api/jobs.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.scraper import scrape_job_text
from app.core.llm_client import generate_resume_bullets, generate_short_answer

router = APIRouter()

class ScrapeIn(BaseModel):
    url: str

class TailorIn(BaseModel):
    job_text: str
    resume_text: str

@router.post("/scrape")
def scrape(in_data: ScrapeIn):
    try:
        out = scrape_job_text(in_data.url)
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tailor")
def tailor(in_data: TailorIn):
    bullets = generate_resume_bullets(in_data.job_text, in_data.resume_text)
    answer = generate_short_answer(in_data.job_text, "Why are you a good fit?", in_data.resume_text)
    return {"bullets": bullets, "answer": answer}
