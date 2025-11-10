"""Worker process implementation."""

import os
import platform
import signal
import subprocess
import sys
import time
from multiprocessing import Process
from pathlib import Path
from typing import Optional

from queuectl.config import Config
from queuectl.job import Job, JobState
from queuectl.storage import JobStorage


def _worker_process_entry(worker_id: str, db_path: Path):
    """Worker process entry point (module-level function for Windows multiprocessing).
    
    Args:
        worker_id: Unique worker identifier.
        db_path: Path to the database file.
    """
    config = Config()
    storage = JobStorage(db_path)
    worker = Worker(worker_id, config, storage)
    worker.run()


class Worker:
    """Worker process that executes jobs."""
    
    def __init__(self, worker_id: str, config: Config, storage: JobStorage = None):
        """Initialize worker.
        
        Args:
            worker_id: Unique worker identifier.
            config: Configuration instance.
            storage: Job storage instance (optional, will be created if None).
        """
        self.worker_id = worker_id
        self.config = config
        # Create storage in worker process to avoid pickling issues on Windows
        if storage is None:
            self.storage = JobStorage(config.get_db_path())
        else:
            self.storage = storage
        self.running = False
        self.current_job: Optional[Job] = None
    
    def run(self):
        """Main worker loop."""
        # Create storage in this process (needed for Windows multiprocessing)
        if not hasattr(self, '_storage_initialized'):
            self.storage = JobStorage(self.config.get_db_path())
            self._storage_initialized = True
        
        self.running = True
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            self.running = False
            if self.current_job:
                self.storage.unlock_job(self.current_job.id)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        backoff_base = self.config.get("backoff_base", 2)
        
        while self.running:
            try:
                job = self.storage.get_next_job(self.worker_id, backoff_base)
                
                if job is None:
                    # No jobs available, wait a bit
                    time.sleep(1)
                    continue
                
                self.current_job = job
                self._process_job(job, backoff_base)
                self.current_job = None
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}", file=sys.stderr)
                if self.current_job:
                    self.storage.unlock_job(self.current_job.id)
                    self.current_job = None
                time.sleep(1)
    
    def _process_job(self, job: Job, backoff_base: int):
        """Process a single job.
        
        Args:
            job: Job to process.
            backoff_base: Base for exponential backoff.
        """
        try:
            # Execute the command
            result = subprocess.run(
                job.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Success
                job.mark_completed()
                self.storage.update_job(job)
            else:
                # Failure
                error_msg = result.stderr or result.stdout or "Command failed"
                job.mark_failed(error_msg[:500])  # Limit error message length
                
                if job.should_retry(backoff_base):
                    job.set_next_retry_time(backoff_base)
                    self.storage.update_job(job)
                else:
                    # Move to DLQ
                    job.mark_dead(f"Exceeded max retries ({job.max_retries})")
                    self.storage.update_job(job)
        
        except subprocess.TimeoutExpired:
            error_msg = "Job execution timed out"
            job.mark_failed(error_msg)
            
            if job.should_retry(backoff_base):
                job.set_next_retry_time(backoff_base)
                self.storage.update_job(job)
            else:
                job.mark_dead(f"Exceeded max retries ({job.max_retries})")
                self.storage.update_job(job)
        
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            job.mark_failed(error_msg)
            
            if job.should_retry(backoff_base):
                job.set_next_retry_time(backoff_base)
                self.storage.update_job(job)
            else:
                job.mark_dead(f"Exceeded max retries ({job.max_retries})")
                self.storage.update_job(job)
        
        finally:
            # Always unlock the job
            self.storage.unlock_job(job.id)


class WorkerManager:
    """Manages multiple worker processes."""
    
    def __init__(self, config: Config):
        """Initialize worker manager.
        
        Args:
            config: Configuration instance.
        """
        self.config = config
        self.storage = JobStorage(config.get_db_path())
        self.workers: list[Process] = []
        self.pid_file = config.get_pid_file()
    
    def start_workers(self, count: int = 1):
        """Start worker processes.
        
        Args:
            count: Number of workers to start.
        """
        # Stop existing workers first
        self.stop_workers()
        
        worker_pids = []
        
        for i in range(count):
            worker_id = f"worker-{os.getpid()}-{i}"
            db_path = self.config.get_db_path()
            # Use module-level function for Windows multiprocessing compatibility
            process = Process(target=_worker_process_entry, args=(worker_id, db_path), daemon=False)
            process.start()
            self.workers.append(process)
            worker_pids.append(process.pid)
        
        # Save PIDs to file
        self._save_pids(worker_pids)
        
        print(f"Started {count} worker(s)")
        for i, pid in enumerate(worker_pids):
            print(f"  Worker {i+1}: PID {pid}")
    
    def stop_workers(self):
        """Stop all worker processes gracefully."""
        # Load PIDs from file
        pids = self._load_pids()
        
        if not pids and not self.workers:
            print("No workers running")
            return
        
        # Stop processes started in this session
        for process in self.workers:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
        
        # Stop processes from previous sessions
        for pid in pids:
            try:
                if platform.system() == 'Windows':
                    # On Windows, use taskkill or terminate the process directly
                    try:
                        # Try to terminate gracefully using taskkill
                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                     capture_output=True, timeout=2, check=False)
                    except Exception:
                        pass
                else:
                    # Unix-like systems
                    os.kill(pid, signal.SIGTERM)
                    # Wait a bit for graceful shutdown
                    time.sleep(1)
                    # Force kill if still running
                    try:
                        os.kill(pid, 0)  # Check if process exists
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # Process already terminated
            except ProcessLookupError:
                pass  # Process doesn't exist
            except PermissionError:
                print(f"Warning: Cannot stop process {pid} (permission denied)")
            except Exception:
                # Ignore other errors (process might not exist)
                pass
        
        self.workers.clear()
        self._clear_pids()
        print("All workers stopped")
    
    def get_active_worker_count(self) -> int:
        """Get the number of active workers.
        
        Returns:
            Number of active workers.
        """
        pids = self._load_pids()
        active = 0
        
        for pid in pids:
            try:
                if platform.system() == 'Windows':
                    # On Windows, check if process exists differently
                    try:
                        subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, timeout=1, check=False)
                        # If tasklist succeeds, process might exist (check output)
                        active += 1
                    except Exception:
                        pass
                else:
                    os.kill(pid, 0)  # Check if process exists
                    active += 1
            except ProcessLookupError:
                pass
            except Exception:
                pass
        
        return active
    
    def _save_pids(self, pids: list[int]):
        """Save worker PIDs to file."""
        try:
            with open(self.pid_file, 'w') as f:
                for pid in pids:
                    f.write(f"{pid}\n")
        except IOError:
            pass
    
    def _load_pids(self) -> list[int]:
        """Load worker PIDs from file.
        
        Returns:
            List of worker PIDs.
        """
        if not self.pid_file.exists():
            return []
        
        try:
            with open(self.pid_file, 'r') as f:
                return [int(line.strip()) for line in f if line.strip().isdigit()]
        except (IOError, ValueError):
            return []
    
    def _clear_pids(self):
        """Clear PID file."""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except IOError:
            pass

