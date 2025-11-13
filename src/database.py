"""Database models and management for storing analysis history."""
import os
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'resume_analyzer.db')

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize the database schema."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                resume_filename TEXT NOT NULL,
                job_desc_filename TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                analysis_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes separately
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id ON analyses(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at ON analyses(created_at)
        ''')
        
        # Create stored_files table (optional file storage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stored_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()

def save_analysis(
    session_id: str,
    resume_filename: str,
    job_desc_filename: str,
    similarity_score: float,
    analysis_data: Dict[str, Any]
) -> int:
    """
    Save an analysis to the database.
    
    Args:
        session_id: Unique session identifier
        resume_filename: Name of the resume file
        job_desc_filename: Name of the job description file
        similarity_score: Overall similarity score
        analysis_data: Complete analysis results dictionary
    
    Returns:
        The ID of the saved analysis
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses 
            (session_id, resume_filename, job_desc_filename, similarity_score, analysis_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            resume_filename,
            job_desc_filename,
            similarity_score,
            json.dumps(analysis_data)
        ))
        return cursor.lastrowid

def get_session_history(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get analysis history for a session.
    
    Args:
        session_id: Session identifier
        limit: Maximum number of results to return
    
    Returns:
        List of analysis records
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, resume_filename, job_desc_filename, 
                   similarity_score, analysis_data, created_at
            FROM analyses
            WHERE session_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (session_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'resume_filename': row['resume_filename'],
                'job_desc_filename': row['job_desc_filename'],
                'similarity_score': row['similarity_score'],
                'analysis_data': json.loads(row['analysis_data']),
                'created_at': row['created_at']
            })
        return results

def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific analysis by ID.
    
    Args:
        analysis_id: Analysis ID
    
    Returns:
        Analysis record or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, session_id, resume_filename, job_desc_filename,
                   similarity_score, analysis_data, created_at
            FROM analyses
            WHERE id = ?
        ''', (analysis_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row['id'],
                'session_id': row['session_id'],
                'resume_filename': row['resume_filename'],
                'job_desc_filename': row['job_desc_filename'],
                'similarity_score': row['similarity_score'],
                'analysis_data': json.loads(row['analysis_data']),
                'created_at': row['created_at']
            }
        return None

def cleanup_old_analyses(days_old: int = 30):
    """
    Delete analyses older than specified days.
    
    Args:
        days_old: Number of days to keep
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM analyses
            WHERE created_at < datetime('now', '-' || ? || ' days')
        ''', (days_old,))
        deleted_count = cursor.rowcount
        conn.commit()
        return deleted_count

# Initialize database on module import
init_db()
