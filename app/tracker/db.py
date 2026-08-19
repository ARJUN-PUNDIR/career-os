import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.config.settings import settings
from app.schemas.models import UnifiedJobListing

def get_db_connection():
    """Returns a connection to the local SQLite database."""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite tables for jobs, application tracking, and usage rate-limiting."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table for storing discovered jobs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        source_platform TEXT NOT NULL,
        location TEXT,
        date_posted TEXT,
        raw_jd TEXT,
        apply_url TEXT,
        salary_range TEXT,
        ats_score REAL DEFAULT 0.0,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Table for storing user application status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE,
        status TEXT NOT NULL,
        compiled_pdf_path TEXT,
        cover_letter_path TEXT,
        applied_at TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs (job_id)
    )
    """)
    
    # Table for caching parsed candidate resume profiles by PDF MD5 hash
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_cache (
        pdf_hash TEXT PRIMARY KEY,
        candidate_profile_json TEXT NOT NULL,
        parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table for daily rate-limiting tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_usage_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_session TEXT DEFAULT 'default_user',
        run_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"💾 [Database] SQLite initialized at: {settings.DB_PATH}")

def get_today_usage_count(user_session: str = "default_user") -> int:
    """Returns total search runs triggered today by the user."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM daily_usage_log WHERE user_session = ? AND run_date = ?", (user_session, today_str))
    row = cursor.fetchone()
    conn.close()
    return row["count"] if row else 0

def increment_daily_usage(user_session: str = "default_user"):
    """Logs a new pipeline execution for today."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO daily_usage_log (user_session, run_date) VALUES (?, ?)", (user_session, today_str))
    conn.commit()
    conn.close()

def check_daily_limit_exceeded(max_limit: int = 2, user_session: str = "default_user") -> bool:
    """Returns True if today's usage exceeds max_limit."""
    return get_today_usage_count(user_session) >= max_limit

def get_cached_resume_profile(pdf_hash: str) -> Optional[Dict[str, Any]]:
    """Returns cached CandidateProfile dict if pdf_hash exists in SQLite DB."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT candidate_profile_json FROM resume_cache WHERE pdf_hash = ?", (pdf_hash,))
    row = cursor.fetchone()
    conn.close()
    if row:
        import json
        return json.loads(row["candidate_profile_json"])
    return None

def save_resume_profile_cache(pdf_hash: str, profile_dict: Dict[str, Any]):
    """Caches parsed CandidateProfile dict in SQLite DB by pdf_hash."""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO resume_cache (pdf_hash, candidate_profile_json)
    VALUES (?, ?)
    """, (pdf_hash, json.dumps(profile_dict)))
    conn.commit()
    conn.close()

def is_job_existing(job_id: str) -> bool:
    """Checks if a job_id hash already exists in SQLite DB."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_job(job: UnifiedJobListing):
    """Saves a unified job listing to SQLite DB if not already present."""
    if is_job_existing(job.job_id):
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO jobs (job_id, title, company, source_platform, location, date_posted, raw_jd, apply_url, salary_range, ats_score)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job.job_id,
        job.title,
        job.company,
        job.source_platform,
        job.location,
        job.date_posted,
        job.raw_jd,
        job.apply_url,
        job.salary_range,
        job.ats_score
    ))
    conn.commit()
    conn.close()

def get_saved_jobs() -> List[Dict[str, Any]]:
    """Fetches all stored jobs from SQLite DB."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY discovered_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Initialize DB on module import
init_db()
