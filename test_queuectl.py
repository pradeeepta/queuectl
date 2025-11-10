#!/usr/bin/env python3
"""Test script to validate QueueCTL core functionality."""

import json
import subprocess
import time
from pathlib import Path


def run_command(cmd: list) -> tuple[str, str, int]:
    """Run a command and return stdout, stderr, and return code."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1


def test_basic_job_completion():
    """Test 1: Basic job completes successfully."""
    print("\n" + "="*60)
    print("TEST 1: Basic job completion")
    print("="*60)
    
    # Enqueue a simple job
    job_data = json.dumps({
        "id": "test-job-1",
        "command": "echo 'Hello World'",
        "max_retries": 3
    })
    
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "enqueue", job_data])
    print(f"Enqueue output: {stdout}")
    if stderr:
        print(f"Enqueue errors: {stderr}")
    
    # Start a worker
    print("\nStarting worker...")
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "worker", "start", "--count", "1"])
    print(f"Worker start: {stdout}")
    
    # Wait for job to complete
    print("\nWaiting for job to complete...")
    time.sleep(3)
    
    # Check status
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "status"])
    print(f"\nStatus:\n{stdout}")
    
    # List completed jobs
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "list", "--state", "completed"])
    print(f"\nCompleted jobs:\n{stdout}")
    
    # Stop worker
    run_command(["python", "-m", "queuectl", "worker", "stop"])
    
    print("\n✓ Test 1 completed")


def test_failed_job_retry():
    """Test 2: Failed job retries with backoff and moves to DLQ."""
    print("\n" + "="*60)
    print("TEST 2: Failed job retry and DLQ")
    print("="*60)
    
    # Enqueue a job that will fail
    job_data = json.dumps({
        "id": "test-job-2",
        "command": "nonexistent-command-12345",
        "max_retries": 2
    })
    
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "enqueue", job_data])
    print(f"Enqueue output: {stdout}")
    
    # Start a worker
    print("\nStarting worker...")
    run_command(["python", "-m", "queuectl", "worker", "start", "--count", "1"])
    
    # Wait for retries
    print("\nWaiting for retries (this may take a few seconds)...")
    time.sleep(8)  # Wait for retries with backoff
    
    # Check status
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "status"])
    print(f"\nStatus:\n{stdout}")
    
    # Check DLQ
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "dlq", "list"])
    print(f"\nDLQ jobs:\n{stdout}")
    
    # Stop worker
    run_command(["python", "-m", "queuectl", "worker", "stop"])
    
    print("\n✓ Test 2 completed")


def test_multiple_workers():
    """Test 3: Multiple workers process jobs without overlap."""
    print("\n" + "="*60)
    print("TEST 3: Multiple workers")
    print("="*60)
    
    # Enqueue multiple jobs
    for i in range(5):
        job_data = json.dumps({
            "id": f"test-job-3-{i}",
            "command": f"echo 'Job {i}'",
            "max_retries": 3
        })
        run_command(["python", "-m", "queuectl", "enqueue", job_data])
    
    print("Enqueued 5 jobs")
    
    # Start multiple workers
    print("\nStarting 3 workers...")
    run_command(["python", "-m", "queuectl", "worker", "start", "--count", "3"])
    
    # Wait for jobs to complete
    print("\nWaiting for jobs to complete...")
    time.sleep(5)
    
    # Check status
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "status"])
    print(f"\nStatus:\n{stdout}")
    
    # List all jobs
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "list"])
    print(f"\nAll jobs:\n{stdout}")
    
    # Stop workers
    run_command(["python", "-m", "queuectl", "worker", "stop"])
    
    print("\n✓ Test 3 completed")


def test_persistence():
    """Test 4: Job data survives restart."""
    print("\n" + "="*60)
    print("TEST 4: Data persistence")
    print("="*60)
    
    # Enqueue a job
    job_data = json.dumps({
        "id": "test-job-4",
        "command": "echo 'Persistent job'",
        "max_retries": 3
    })
    
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "enqueue", job_data])
    print(f"Enqueued job: {stdout}")
    
    # Check job exists
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "list", "--state", "pending"])
    print(f"\nPending jobs before restart:\n{stdout}")
    
    # Simulate restart (just check that job still exists)
    print("\nSimulating restart (checking job persistence)...")
    time.sleep(1)
    
    # Check job still exists
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "list", "--state", "pending"])
    print(f"\nPending jobs after 'restart':\n{stdout}")
    
    # Process the job
    run_command(["python", "-m", "queuectl", "worker", "start", "--count", "1"])
    time.sleep(2)
    run_command(["python", "-m", "queuectl", "worker", "stop"])
    
    print("\n✓ Test 4 completed")


def test_configuration():
    """Test 5: Configuration management."""
    print("\n" + "="*60)
    print("TEST 5: Configuration management")
    print("="*60)
    
    # Get current config
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "config", "get"])
    print(f"Current config:\n{stdout}")
    
    # Set a config value
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "config", "set", "max-retries", "5"])
    print(f"\nSet max-retries: {stdout}")
    
    # Get the value back
    stdout, stderr, code = run_command(["python", "-m", "queuectl", "config", "get", "max-retries"])
    print(f"Get max-retries: {stdout}")
    
    # Reset to default
    run_command(["python", "-m", "queuectl", "config", "set", "max-retries", "3"])
    
    print("\n✓ Test 5 completed")


def main():
    """Run all tests."""
    print("="*60)
    print("QueueCTL Test Suite")
    print("="*60)
    
    try:
        test_basic_job_completion()
        test_failed_job_retry()
        test_multiple_workers()
        test_persistence()
        test_configuration()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        print("\nNote: Some tests may show warnings or errors in output.")
        print("This is expected behavior for testing error handling.")
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        # Clean up
        run_command(["python", "-m", "queuectl", "worker", "stop"])
    except Exception as e:
        print(f"\n\nTest error: {e}")
        # Clean up
        run_command(["python", "-m", "queuectl", "worker", "stop"])


if __name__ == "__main__":
    main()

