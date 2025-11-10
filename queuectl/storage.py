"""Job storage using SQLite database."""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from queuectl.job import Job, JobState


class JobStorage:
    """Thread-safe job storage using SQLite."""
    
    def __init__(self, db_path: Path):
        """Initialize storage.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with self._lock:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    state TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_retries INTEGER NOT NULL DEFAULT 3,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error_message TEXT,
                    next_retry_at TEXT,
                    locked_by TEXT,
                    locked_at TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_state ON jobs(state)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_next_retry ON jobs(next_retry_at)
            """)
            conn.commit()
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_job(self, job: Job) -> Job:
        """Add a new job to storage.
        
        Args:
            job: Job to add.
            
        Returns:
            The added job.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO jobs (
                        id, command, state, attempts, max_retries,
                        created_at, updated_at, error_message, next_retry_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.id, job.command, job.state.value, job.attempts,
                    job.max_retries, job.created_at, job.updated_at,
                    job.error_message, job.next_retry_at
                ))
                conn.commit()
            finally:
                conn.close()
        
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID.
        
        Args:
            job_id: Job identifier.
            
        Returns:
            Job if found, None otherwise.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                row = conn.execute(
                    "SELECT * FROM jobs WHERE id = ?", (job_id,)
                ).fetchone()
                
                if row:
                    return self._row_to_job(row)
                return None
            finally:
                conn.close()
    
    def update_job(self, job: Job):
        """Update a job in storage.
        
        Args:
            job: Job to update.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    UPDATE jobs SET
                        command = ?, state = ?, attempts = ?, max_retries = ?,
                        updated_at = ?, error_message = ?, next_retry_at = ?,
                        locked_by = ?, locked_at = ?
                    WHERE id = ?
                """, (
                    job.command, job.state.value, job.attempts, job.max_retries,
                    job.updated_at, job.error_message, job.next_retry_at,
                    getattr(job, 'locked_by', None), getattr(job, 'locked_at', None),
                    job.id
                ))
                conn.commit()
            finally:
                conn.close()
    
    def lock_job(self, job_id: str, worker_id: str) -> bool:
        """Lock a job for processing by a worker.
        
        Args:
            job_id: Job identifier.
            worker_id: Worker identifier.
            
        Returns:
            True if job was successfully locked, False if already locked.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                # Check if job is already locked
                row = conn.execute(
                    "SELECT locked_by, locked_at FROM jobs WHERE id = ?", (job_id,)
                ).fetchone()
                
                if row and row['locked_by']:
                    # Check if lock is stale (older than 5 minutes)
                    if row['locked_at']:
                        try:
                            # Parse ISO format timestamp
                            locked_at_str = row['locked_at']
                            if locked_at_str.endswith('Z'):
                                locked_at_str = locked_at_str[:-1] + '+00:00'
                            locked_at = datetime.fromisoformat(locked_at_str)
                            # Convert to UTC naive datetime for comparison
                            if locked_at.tzinfo:
                                locked_at = locked_at.replace(tzinfo=None)
                            age = (datetime.utcnow() - locked_at).total_seconds()
                            if age < 300:  # 5 minutes
                                return False
                        except (ValueError, AttributeError):
                            # If parsing fails, consider lock stale
                            pass
                
                # Lock the job
                now = datetime.utcnow().isoformat() + "Z"
                conn.execute("""
                    UPDATE jobs SET
                        locked_by = ?, locked_at = ?, state = ?
                    WHERE id = ?
                """, (worker_id, now, JobState.PROCESSING.value, job_id))
                
                conn.commit()
                return conn.total_changes > 0
            finally:
                conn.close()
    
    def unlock_job(self, job_id: str):
        """Unlock a job after processing.
        
        Args:
            job_id: Job identifier.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    UPDATE jobs SET locked_by = NULL, locked_at = NULL
                    WHERE id = ?
                """, (job_id,))
                conn.commit()
            finally:
                conn.close()
    
    def get_next_job(self, worker_id: str, backoff_base: int = 2) -> Optional[Job]:
        """Get the next available job for processing.
        
        Args:
            worker_id: Worker identifier.
            backoff_base: Base for exponential backoff.
            
        Returns:
            Next available job or None.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.utcnow().isoformat() + "Z"
                
                # Try to get a pending job first
                row = conn.execute("""
                    SELECT * FROM jobs
                    WHERE state = ? AND (locked_by IS NULL OR locked_at IS NULL)
                    ORDER BY created_at ASC
                    LIMIT 1
                """, (JobState.PENDING.value,)).fetchone()
                
                if row:
                    job = self._row_to_job(row)
                    if self.lock_job(job.id, worker_id):
                        return self.get_job(job.id)
                
                # Try to get a failed job that's ready for retry
                row = conn.execute("""
                    SELECT * FROM jobs
                    WHERE state = ? AND attempts < max_retries
                      AND (next_retry_at IS NULL OR next_retry_at <= ?)
                      AND (locked_by IS NULL OR locked_at IS NULL)
                    ORDER BY next_retry_at ASC, created_at ASC
                    LIMIT 1
                """, (JobState.FAILED.value, now)).fetchone()
                
                if row:
                    job = self._row_to_job(row)
                    if self.lock_job(job.id, worker_id):
                        return self.get_job(job.id)
                
                return None
            finally:
                conn.close()
    
    def list_jobs(self, state: Optional[str] = None) -> List[Job]:
        """List jobs, optionally filtered by state.
        
        Args:
            state: Optional state filter.
            
        Returns:
            List of jobs.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                if state:
                    rows = conn.execute(
                        "SELECT * FROM jobs WHERE state = ? ORDER BY created_at DESC",
                        (state,)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM jobs ORDER BY created_at DESC"
                    ).fetchall()
                
                return [self._row_to_job(row) for row in rows]
            finally:
                conn.close()
    
    def get_dlq_jobs(self) -> List[Job]:
        """Get all jobs in the Dead Letter Queue.
        
        Returns:
            List of dead jobs.
        """
        return self.list_jobs(JobState.DEAD.value)
    
    def get_stats(self) -> dict:
        """Get statistics about jobs.
        
        Returns:
            Dictionary with job counts by state.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                stats = {}
                for state in JobState:
                    count = conn.execute(
                        "SELECT COUNT(*) as count FROM jobs WHERE state = ?",
                        (state.value,)
                    ).fetchone()['count']
                    stats[state.value] = count
                
                # Get active workers count
                active_workers = conn.execute("""
                    SELECT COUNT(DISTINCT locked_by) as count
                    FROM jobs
                    WHERE locked_by IS NOT NULL
                """).fetchone()['count']
                
                stats['active_workers'] = active_workers
                return stats
            finally:
                conn.close()
    
    def _row_to_job(self, row: sqlite3.Row) -> Job:
        """Convert database row to Job object."""
        job = Job(
            id=row['id'],
            command=row['command'],
            state=row['state'],
            attempts=row['attempts'],
            max_retries=row['max_retries'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            error_message=row['error_message'],
            next_retry_at=row['next_retry_at'],
        )
        # sqlite3.Row doesn't have .get(), use try/except or check keys
        job.locked_by = row['locked_by'] if 'locked_by' in row.keys() else None
        job.locked_at = row['locked_at'] if 'locked_at' in row.keys() else None
        return job

