#!/usr/bin/env python3
"""Example usage of QueueCTL."""

import json
import subprocess
import time

def run_cmd(cmd):
    """Run a command and print output."""
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, end="")
    return result.returncode == 0

def main():
    print("="*60)
    print("QueueCTL Example Usage")
    print("="*60)
    
    # 1. Enqueue some jobs
    print("\n1. Enqueuing jobs...")
    jobs = [
        {"id": "example-1", "command": "echo 'Hello from job 1'", "max_retries": 3},
        {"id": "example-2", "command": "sleep 1", "max_retries": 3},
        {"id": "example-3", "command": "echo 'Job 3 completed'", "max_retries": 3},
    ]
    
    for job in jobs:
        job_json = json.dumps(job)
        run_cmd(["python", "-m", "queuectl", "enqueue", job_json])
    
    # 2. Check status
    print("\n2. Checking status...")
    run_cmd(["python", "-m", "queuectl", "status"])
    
    # 3. Start workers
    print("\n3. Starting workers...")
    run_cmd(["python", "-m", "queuectl", "worker", "start", "--count", "2"])
    
    # 4. Wait a bit
    print("\n4. Waiting for jobs to process...")
    time.sleep(3)
    
    # 5. Check status again
    print("\n5. Checking status after processing...")
    run_cmd(["python", "-m", "queuectl", "status"])
    
    # 6. List completed jobs
    print("\n6. Listing completed jobs...")
    run_cmd(["python", "-m", "queuectl", "list", "--state", "completed"])
    
    # 7. Stop workers
    print("\n7. Stopping workers...")
    run_cmd(["python", "-m", "queuectl", "worker", "stop"])
    
    print("\n" + "="*60)
    print("Example completed!")
    print("="*60)

if __name__ == "__main__":
    main()

