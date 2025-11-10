"""Job model and state management."""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional
import uuid


class JobState(Enum):
    """Job state enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD = "dead"


class Job:
    """Represents a background job."""
    
    def __init__(
        self,
        id: str = None,
        command: str = "",
        state: str = "pending",
        attempts: int = 0,
        max_retries: int = 3,
        created_at: str = None,
        updated_at: str = None,
        error_message: str = None,
        next_retry_at: str = None,
    ):
        """Initialize a job.
        
        Args:
            id: Unique job identifier. Generated if not provided.
            command: Command to execute.
            state: Current job state.
            attempts: Number of execution attempts.
            max_retries: Maximum retry attempts.
            created_at: Creation timestamp (ISO format).
            updated_at: Last update timestamp (ISO format).
            error_message: Last error message if any.
            next_retry_at: Next retry timestamp (ISO format).
        """
        self.id = id or str(uuid.uuid4())
        self.command = command
        self.state = JobState(state) if isinstance(state, str) else state
        self.attempts = attempts
        self.max_retries = max_retries
        self.error_message = error_message
        self.next_retry_at = next_retry_at
        
        now = datetime.utcnow().isoformat() + "Z"
        self.created_at = created_at or now
        self.updated_at = updated_at or now
    
    def to_dict(self) -> Dict:
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "command": self.command,
            "state": self.state.value,
            "attempts": self.attempts,
            "max_retries": self.max_retries,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error_message": self.error_message,
            "next_retry_at": self.next_retry_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Job":
        """Create job from dictionary."""
        return cls(
            id=data.get("id"),
            command=data.get("command", ""),
            state=data.get("state", "pending"),
            attempts=data.get("attempts", 0),
            max_retries=data.get("max_retries", 3),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            error_message=data.get("error_message"),
            next_retry_at=data.get("next_retry_at"),
        )
    
    def mark_processing(self):
        """Mark job as being processed."""
        self.state = JobState.PROCESSING
        self.updated_at = datetime.utcnow().isoformat() + "Z"
    
    def mark_completed(self):
        """Mark job as completed."""
        self.state = JobState.COMPLETED
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        self.error_message = None
    
    def mark_failed(self, error_message: str = None):
        """Mark job as failed."""
        self.attempts += 1
        self.state = JobState.FAILED
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        self.error_message = error_message
    
    def mark_dead(self, error_message: str = None):
        """Mark job as dead (moved to DLQ)."""
        self.state = JobState.DEAD
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        self.error_message = error_message
    
    def should_retry(self, backoff_base: int = 2) -> bool:
        """Check if job should be retried.
        
        Args:
            backoff_base: Base for exponential backoff calculation.
            
        Returns:
            True if job should be retried, False otherwise.
        """
        if self.state == JobState.COMPLETED:
            return False
        
        if self.attempts >= self.max_retries:
            return False
        
        return True
    
    def calculate_retry_delay(self, backoff_base: int = 2) -> int:
        """Calculate retry delay in seconds using exponential backoff.
        
        Args:
            backoff_base: Base for exponential backoff.
            
        Returns:
            Delay in seconds.
        """
        return backoff_base ** self.attempts
    
    def set_next_retry_time(self, backoff_base: int = 2):
        """Set the next retry timestamp."""
        delay = self.calculate_retry_delay(backoff_base)
        next_retry = datetime.utcnow()
        from datetime import timedelta
        next_retry += timedelta(seconds=delay)
        self.next_retry_at = next_retry.isoformat() + "Z"

