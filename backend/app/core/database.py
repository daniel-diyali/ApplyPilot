# backend/app/core/database.py
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "applypilot.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            job_url TEXT,
            job_text TEXT,
            status TEXT DEFAULT 'applied',
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)
    
    # Generated content table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER,
            content_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications (id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_application(company: str, position: str, job_url: str = "", job_text: str = "", notes: str = "") -> int:
    """Save a job application and return the ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO applications (company, position, job_url, job_text, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (company, position, job_url, job_text, notes))
    
    app_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return app_id

def save_generated_content(application_id: int, content_type: str, content: str):
    """Save generated content (resume bullets, cover letter, etc.)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO generated_content (application_id, content_type, content)
        VALUES (?, ?, ?)
    """, (application_id, content_type, content))
    
    conn.commit()
    conn.close()

def get_applications() -> List[Dict]:
    """Get all applications"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM applications ORDER BY applied_date DESC")
    apps = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return apps

def get_application(app_id: int) -> Optional[Dict]:
    """Get a specific application with its generated content"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    app = cursor.fetchone()
    
    if app:
        app = dict(app)
        cursor.execute("SELECT * FROM generated_content WHERE application_id = ?", (app_id,))
        app['generated_content'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return app

# Initialize database on import
init_db()