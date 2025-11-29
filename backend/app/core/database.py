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
    
    # User profile table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            resume_text TEXT,
            preferences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
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

def save_user_profile(name: str = "", email: str = "", phone: str = "", resume_text: str = "", preferences: str = "") -> int:
    """Save or update user profile"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if profile exists
    cursor.execute("SELECT id FROM user_profile LIMIT 1")
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE user_profile 
            SET name=?, email=?, phone=?, resume_text=?, preferences=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (name, email, phone, resume_text, preferences, existing[0]))
        profile_id = existing[0]
    else:
        cursor.execute("""
            INSERT INTO user_profile (name, email, phone, resume_text, preferences)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, phone, resume_text, preferences))
        profile_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return profile_id

def get_user_profile() -> Optional[Dict]:
    """Get user profile"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_profile LIMIT 1")
    profile = cursor.fetchone()
    
    conn.close()
    return dict(profile) if profile else None

def update_application_status(app_id: int, status: str, notes: str = "") -> bool:
    """Update application status"""
    valid_statuses = ['applied', 'reviewing', 'phone_screen', 'interview', 'final_round', 'offer', 'rejected', 'withdrawn']
    
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE applications SET status = ?, notes = ? WHERE id = ?",
        (status, notes, app_id)
    )
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_applications_by_status(status: str = None) -> List[Dict]:
    """Get applications filtered by status"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status:
        cursor.execute("SELECT * FROM applications WHERE status = ? ORDER BY applied_date DESC", (status,))
    else:
        cursor.execute("SELECT * FROM applications ORDER BY applied_date DESC")
    
    apps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return apps

def get_application_stats() -> Dict:
    """Get application statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    status_counts = dict(cursor.fetchall())
    
    cursor.execute("SELECT COUNT(*) FROM applications WHERE applied_date >= date('now', '-30 days')")
    recent = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_applications": total,
        "status_breakdown": status_counts,
        "recent_applications": recent
    }

# Initialize database on import
init_db()