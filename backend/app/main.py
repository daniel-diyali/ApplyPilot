# backend/app/main.py
from fastapi import FastAPI
from app.api import jobs, resume, tracker, health, applications, files
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="ApplyPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative dev port
        "https://applypilot.com", # Production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(files.router, prefix="/api/v1", tags=["files"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/api/v1", tags=["applications"])
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(tracker.router, prefix="/tracker", tags=["tracker"])

@app.get("/")
def root():
    return {"status": "ApplyPilot API running"}
