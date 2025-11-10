# QueueCTL - Demo Commands for Screenshots

This document lists all commands you need to run to demonstrate the complete functionality for your assignment submission.

---

## 📸 Screenshot Session 1: Installation & Setup

### 1. Show Python Version
```powershell
python --version
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Install Package
```powershell
pip install -e .
```

### 4. Verify Installation
```powershell
python -m queuectl --version
```

### 5. Show Help
```powershell
python -m queuectl --help
```

---

## 📸 Screenshot Session 2: Basic Job Operations

### 1. Check Initial Status (Empty Queue)
```powershell
python -m queuectl status
```

### 2. Enqueue First Job (Using Options)
```powershell
python -m queuectl enqueue --id job1 --command "echo Hello World"
```

### 3. Enqueue Second Job (Using Options)
```powershell
python -m queuectl enqueue --id job2 --command "sleep 2" --max-retries 3
```

### 4. Enqueue Third Job (Using JSON - if on Linux/Mac)
```bash
python -m queuectl enqueue '{"id":"job3","command":"echo Test Job","max_retries":3}'
```

**OR on Windows PowerShell, use options instead:**
```powershell
python -m queuectl enqueue --id job3 --command "echo Test Job" --max-retries 3
```

### 5. Check Status After Enqueuing
```powershell
python -m queuectl status
```

### 6. List All Jobs
```powershell
python -m queuectl list
```

### 7. List Pending Jobs Only
```powershell
python -m queuectl list --state pending
```

---

## 📸 Screenshot Session 3: Worker Management

### 1. Start Single Worker
```powershell
python -m queuectl worker start
```

### 2. Check Status (Should Show Active Worker)
```powershell
python -m queuectl status
```

### 3. Wait a few seconds, then check completed jobs
```powershell
python -m queuectl list --state completed
```

### 4. Stop Worker
```powershell
python -m queuectl worker stop
```

### 5. Start Multiple Workers
```powershell
python -m queuectl worker start --count 3
```

### 6. Check Status (Should Show 3 Active Workers)
```powershell
python -m queuectl status
```

### 7. Stop All Workers
```powershell
python -m queuectl worker stop
```

---

## 📸 Screenshot Session 4: Failed Jobs & Retry Mechanism

### 1. Enqueue a Job That Will Fail
```powershell
python -m queuectl enqueue --id fail-job --command "nonexistent-command-12345" --max-retries 2
```

### 2. Check Status
```powershell
python -m queuectl status
```

### 3. Start Worker
```powershell
python -m queuectl worker start
```

### 4. Wait 5-10 seconds (for retries with backoff), then check status
```powershell
python -m queuectl status
```

### 5. List Failed Jobs
```powershell
python -m queuectl list --state failed
```

### 6. Wait a bit more, then check DLQ (job should move to DLQ after max retries)
```powershell
python -m queuectl dlq list
```

### 7. Check Status (Should Show Job in DLQ)
```powershell
python -m queuectl status
```

### 8. Stop Worker
```powershell
python -m queuectl worker stop
```

---

## 📸 Screenshot Session 5: Dead Letter Queue (DLQ)

### 1. List DLQ Jobs
```powershell
python -m queuectl dlq list
```

### 2. Retry a Job from DLQ
```powershell
python -m queuectl dlq retry fail-job
```

### 3. Check Status (Job should be back to pending)
```powershell
python -m queuectl status
```

### 4. List Pending Jobs (Should show the retried job)
```powershell
python -m queuectl list --state pending
```

---

## 📸 Screenshot Session 6: Configuration Management

### 1. Get All Configuration
```powershell
python -m queuectl config get
```

### 2. Get Specific Config Value
```powershell
python -m queuectl config get max-retries
```

### 3. Set Max Retries
```powershell
python -m queuectl config set max-retries 5
```

### 4. Verify the Change
```powershell
python -m queuectl config get max-retries
```

### 5. Set Backoff Base
```powershell
python -m queuectl config set backoff-base 3
```

### 6. Verify Backoff Base
```powershell
python -m queuectl config get backoff-base
```

### 7. Get All Config Again (Show Updated Values)
```powershell
python -m queuectl config get
```

---

## 📸 Screenshot Session 7: Multiple Workers & Concurrency

### 1. Enqueue Multiple Jobs
```powershell
python -m queuectl enqueue --id multi1 --command "echo Job 1"
python -m queuectl enqueue --id multi2 --command "echo Job 2"
python -m queuectl enqueue --id multi3 --command "echo Job 3"
python -m queuectl enqueue --id multi4 --command "echo Job 4"
python -m queuectl enqueue --id multi5 --command "echo Job 5"
```

### 2. Check Status (Should Show 5 Pending)
```powershell
python -m queuectl status
```

### 3. Start 3 Workers
```powershell
python -m queuectl worker start --count 3
```

### 4. Wait 3-5 seconds, then check status
```powershell
python -m queuectl status
```

### 5. List All Jobs (Show processing/completed states)
```powershell
python -m queuectl list
```

### 6. Wait a bit more, check completed jobs
```powershell
python -m queuectl list --state completed
```

### 7. Stop Workers
```powershell
python -m queuectl worker stop
```

---

## 📸 Screenshot Session 8: Data Persistence

### 1. Enqueue a Job
```powershell
python -m queuectl enqueue --id persist-test --command "echo Persistence Test"
```

### 2. Check Status
```powershell
python -m queuectl status
```

### 3. List Jobs (Show job exists)
```powershell
python -m queuectl list
```

### 4. **Close terminal/restart** (Simulate system restart)

### 5. Check Status Again (Job should still be there)
```powershell
python -m queuectl status
```

### 6. List Jobs (Job should persist)
```powershell
python -m queuectl list
```

### 7. Process the Job
```powershell
python -m queuectl worker start
```

### 8. Wait, then check completed
```powershell
python -m queuectl list --state completed
```

### 9. Stop Worker
```powershell
python -m queuectl worker stop
```

---

## 📸 Screenshot Session 9: Test Script Execution

### 1. Run Test Script
```powershell
python test_queuectl.py
```

**This will demonstrate:**
- Basic job completion
- Failed job retry and DLQ
- Multiple workers
- Data persistence
- Configuration management

---

## 📸 Screenshot Session 10: Help Commands

### 1. Main Help
```powershell
python -m queuectl --help
```

### 2. Worker Help
```powershell
python -m queuectl worker --help
```

### 3. DLQ Help
```powershell
python -m queuectl dlq --help
```

### 4. Config Help
```powershell
python -m queuectl config --help
```

### 5. Enqueue Help
```powershell
python -m queuectl enqueue --help
```

---

## 📸 Quick Demo Flow (For Video Recording)

If you want to record a single continuous demo, use this flow:

```powershell
# 1. Show version
python -m queuectl --version

# 2. Show help
python -m queuectl --help

# 3. Check empty status
python -m queuectl status

# 4. Enqueue jobs
python -m queuectl enqueue --id demo1 --command "echo Hello"
python -m queuectl enqueue --id demo2 --command "sleep 1"
python -m queuectl enqueue --id demo3 --command "nonexistent-cmd" --max-retries 2

# 5. Show status
python -m queuectl status

# 6. List jobs
python -m queuectl list

# 7. Start workers
python -m queuectl worker start --count 2

# 8. Wait 5 seconds, then show status
python -m queuectl status

# 9. Show completed jobs
python -m queuectl list --state completed

# 10. Show DLQ
python -m queuectl dlq list

# 11. Show config
python -m queuectl config get

# 12. Stop workers
python -m queuectl worker stop

# 13. Final status
python -m queuectl status
```

---

## 📝 Notes for Screenshots

1. **Clear Terminal**: Clear terminal between sections for clean screenshots
   ```powershell
   cls  # Windows
   # or
   clear  # Linux/Mac
   ```

2. **Wait Times**: Some commands need a few seconds between them (especially when workers are processing)

3. **Error Handling**: The failed job command will show errors - this is expected and demonstrates error handling

4. **Multiple Terminals**: You can use multiple terminal windows:
   - Terminal 1: Run commands
   - Terminal 2: Monitor status continuously

5. **File Locations**: You can show where data is stored:
   ```powershell
   # Windows
   dir $env:USERPROFILE\.queuectl
   
   # Linux/Mac
   ls -la ~/.queuectl
   ```

---

## ✅ Checklist for Screenshots

Make sure you capture:

- [ ] Installation commands
- [ ] Help commands (main + subcommands)
- [ ] Enqueue jobs (both methods)
- [ ] Status command (empty, with jobs, with workers)
- [ ] List jobs (all states: pending, completed, failed, dead)
- [ ] Worker start (single and multiple)
- [ ] Worker stop
- [ ] Failed job → retry → DLQ flow
- [ ] DLQ list and retry
- [ ] Configuration get/set
- [ ] Test script execution
- [ ] Data persistence (before/after restart simulation)

---

**Good luck with your submission!** 🚀

