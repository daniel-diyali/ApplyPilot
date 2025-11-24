# backend/app/core/scraper.py
import requests
from bs4 import BeautifulSoup
from typing import Dict

def scrape_job_text(url: str) -> Dict[str,str]:
    """
    Basic scraper: fetch HTML and try to extract the job title, company, and description text.
    For JS-heavy sites, extend with Playwright/selenium.
    """
    r = requests.get(url, timeout=15, headers={"User-Agent": "ApplyPilotBot/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Heuristics:
    title = (soup.find("h1") or soup.find("h2") or soup.title)
    title_text = title.get_text(strip=True) if title else ""

    # company heuristics
    company = ""
    for sel in ['.company', '.topcard__org-name', '.posting-company', '.job-company']:
        el = soup.select_one(sel)
        if el:
            company = el.get_text(strip=True)
            break

    # job description: most sites use .description, .job-description etc.
    desc_candidates = soup.select(".description, .job-description, #jobDescriptionText")
    if desc_candidates:
        desc_text = "\n".join([c.get_text(separator="\n", strip=True) for c in desc_candidates])
    else:
        # fallback: take the largest <div> by text length
        divs = soup.find_all("div")
        candidate = max(divs, key=lambda d: len(d.get_text(strip=True) or ""))
        desc_text = candidate.get_text(separator="\n", strip=True)

    return {"title": title_text, "company": company, "description": desc_text, "url": url}
