"""CLI interface for QueueCTL."""

import json
import sys
from datetime import datetime
from typing import Optional

import click
from tabulate import tabulate

from queuectl.config import Config
from queuectl.job import Job, JobState
from queuectl.storage import JobStorage
from queuectl.worker import WorkerManager


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """QueueCTL - A CLI-based background job queue system."""
    pass


@cli.command()
@click.argument('job_data', required=False)
@click.option('--id', help='Job ID (auto-generated if not provided)')
@click.option('--command', help='Command to execute')
@click.option('--max-retries', type=int, help='Maximum retry attempts')
def enqueue(job_data: Optional[str], id: Optional[str], command: Optional[str], max_retries: Optional[int]):
    """Enqueue a new job.
    
    Job data can be provided as JSON string or via options.
    
    Examples:
        queuectl enqueue '{"id":"job1","command":"sleep 2"}'
        queuectl enqueue --id job1 --command "echo hello"
    """
    config = Config()
    storage = JobStorage(config.get_db_path())
    
    try:
        if job_data:
            # Parse JSON input
            data = json.loads(job_data)
            job = Job.from_dict(data)
        else:
            # Use command-line options
            if not command:
                click.echo("Error: Either provide job_data JSON or --command option", err=True)
                sys.exit(1)
            
            job = Job(
                id=id,
                command=command,
                max_retries=max_retries or config.get("max_retries", 3)
            )
        
        storage.add_job(job)
        click.echo(f"Job enqueued: {job.id}")
        click.echo(f"  Command: {job.command}")
        click.echo(f"  Max retries: {job.max_retries}")
    
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def worker():
    """Manage worker processes."""
    pass


@worker.command()
@click.option('--count', type=int, default=1, help='Number of workers to start')
def start(count: int):
    """Start worker processes."""
    config = Config()
    manager = WorkerManager(config)
    
    try:
        manager.start_workers(count)
    except Exception as e:
        click.echo(f"Error starting workers: {e}", err=True)
        sys.exit(1)


@worker.command()
def stop():
    """Stop all running workers gracefully."""
    config = Config()
    manager = WorkerManager(config)
    
    try:
        manager.stop_workers()
    except Exception as e:
        click.echo(f"Error stopping workers: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Show summary of all job states and active workers."""
    config = Config()
    storage = JobStorage(config.get_db_path())
    manager = WorkerManager(config)
    
    try:
        stats = storage.get_stats()
        active_workers = manager.get_active_worker_count()
        
        click.echo("Queue Status")
        click.echo("=" * 50)
        
        table = [
            ["Pending", stats.get("pending", 0)],
            ["Processing", stats.get("processing", 0)],
            ["Completed", stats.get("completed", 0)],
            ["Failed", stats.get("failed", 0)],
            ["Dead (DLQ)", stats.get("dead", 0)],
            ["Active Workers", active_workers],
        ]
        
        click.echo(tabulate(table, headers=["State", "Count"], tablefmt="simple"))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--state', type=click.Choice(['pending', 'processing', 'completed', 'failed', 'dead']),
              help='Filter jobs by state')
def list(state: Optional[str]):
    """List jobs, optionally filtered by state."""
    config = Config()
    storage = JobStorage(config.get_db_path())
    
    try:
        jobs = storage.list_jobs(state)
        
        if not jobs:
            click.echo("No jobs found")
            return
        
        table_data = []
        for job in jobs:
            table_data.append([
                job.id,
                job.command[:50] + "..." if len(job.command) > 50 else job.command,
                job.state.value,
                job.attempts,
                job.max_retries,
                job.created_at[:19] if job.created_at else "N/A",
            ])
        
        headers = ["ID", "Command", "State", "Attempts", "Max Retries", "Created At"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def dlq():
    """Manage Dead Letter Queue."""
    pass


@dlq.command()
def list():
    """List all jobs in the Dead Letter Queue."""
    config = Config()
    storage = JobStorage(config.get_db_path())
    
    try:
        jobs = storage.get_dlq_jobs()
        
        if not jobs:
            click.echo("No jobs in Dead Letter Queue")
            return
        
        table_data = []
        for job in jobs:
            table_data.append([
                job.id,
                job.command[:50] + "..." if len(job.command) > 50 else job.command,
                job.attempts,
                job.max_retries,
                job.error_message[:50] + "..." if job.error_message and len(job.error_message) > 50 else (job.error_message or "N/A"),
                job.created_at[:19] if job.created_at else "N/A",
            ])
        
        headers = ["ID", "Command", "Attempts", "Max Retries", "Error", "Created At"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@dlq.command()
@click.argument('job_id')
def retry(job_id: str):
    """Retry a job from the Dead Letter Queue.
    
    This resets the job to pending state and clears attempts.
    """
    config = Config()
    storage = JobStorage(config.get_db_path())
    
    try:
        job = storage.get_job(job_id)
        
        if not job:
            click.echo(f"Error: Job {job_id} not found", err=True)
            sys.exit(1)
        
        if job.state != JobState.DEAD:
            click.echo(f"Error: Job {job_id} is not in Dead Letter Queue", err=True)
            sys.exit(1)
        
        # Reset job to pending
        job.state = JobState.PENDING
        job.attempts = 0
        job.error_message = None
        job.next_retry_at = None
        job.updated_at = datetime.utcnow().isoformat() + "Z"
        
        storage.update_job(job)
        click.echo(f"Job {job_id} moved back to pending queue")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def config():
    """Manage configuration."""
    pass


@config.command('set')
@click.argument('key')
@click.argument('value')
def set_config(key: str, value: str):
    """Set a configuration value.
    
    Examples:
        queuectl config set max-retries 5
        queuectl config set backoff-base 3
    """
    config = Config()
    
    try:
        # Try to convert value to appropriate type
        if value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit():
            value = float(value)
        elif value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        
        config.set(key, value)
        click.echo(f"Configuration updated: {key} = {value}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@config.command('get')
@click.argument('key', required=False)
def get_config(key: Optional[str]):
    """Get configuration value(s).
    
    If key is not provided, shows all configuration.
    """
    config = Config()
    
    try:
        if key:
            value = config.get(key)
            if value is not None:
                click.echo(f"{key} = {value}")
            else:
                click.echo(f"Configuration key '{key}' not found", err=True)
                sys.exit(1)
        else:
            # Show all config
            click.echo("Configuration:")
            for k, v in config._config.items():
                click.echo(f"  {k} = {v}")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()

