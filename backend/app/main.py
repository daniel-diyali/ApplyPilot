# backend/app/main.py
from fastapi import FastAPI
from app.api import jobs, resume, tracker
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ApplyPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(tracker.router, prefix="/tracker", tags=["tracker"])

@app.get("/")
def root():
    return {"status": "ApplyPilot API running"}
