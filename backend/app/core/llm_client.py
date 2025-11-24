# backend/app/core/llm_client.py
import os
import openai
from typing import Dict

openai.api_key = os.getenv("OPENAI_API_KEY", "")

def generate_resume_bullets(job_text: str, resume_text: str) -> str:
    prompt = f"""
You are ApplyPilot, an assistant that rewrites and tailors resume bullets for maximum relevance to a job.
Job posting:
{job_text}

Candidate resume (bullets and experience):
{resume_text}

Produce 5-8 improved resume bullets that are concise, metric-driven if possible, and tailored to the job posting. Return them as a JSON list.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # swap if needed
        messages=[{"role":"user","content":prompt}],
        max_tokens=400,
        temperature=0.2
    )
    text = resp.choices[0].message.content
    return text

def generate_short_answer(job_text: str, question: str, resume_text: str) -> str:
    prompt = f"""
Job posting:
{job_text}

Candidate resume:
{resume_text}

Question: {question}

Write a 120-200 word tailored answer demonstrating fit, highlight relevant experiences, and end with one sentence describing why you'd be excited to join.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=400,
        temperature=0.25
    )
    return resp.choices[0].message.content
