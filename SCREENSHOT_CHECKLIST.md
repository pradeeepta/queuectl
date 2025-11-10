# Screenshot Checklist - Take These One by One

## 📸 Screenshot 1: Project Structure
**What to capture:** File Explorer showing your project folder
- Show `queuectl/` folder
- Show `README.md`, `test_queuectl.py`, `requirements.txt`
- **File name:** `01-project-structure.png`

---

## 📸 Screenshot 2: Python Version Check
**Command to run:**
```powershell
python --version
```
**What to capture:** Terminal showing Python version
- **File name:** `02-python-version.png`

---

## 📸 Screenshot 3: Installation - Install Dependencies
**Command to run:**
```powershell
pip install -r requirements.txt
```
**What to capture:** Terminal showing successful installation
- **File name:** `03-install-dependencies.png`

---

## 📸 Screenshot 4: Installation - Install Package
**Command to run:**
```powershell
pip install -e .
```
**What to capture:** Terminal showing package installation
- **File name:** `04-install-package.png`

---

## 📸 Screenshot 5: Verify Installation
**Command to run:**
```powershell
python -m queuectl --version
```
**What to capture:** Terminal showing version output
- **File name:** `05-verify-installation.png`

---

## 📸 Screenshot 6: Main Help Command
**Command to run:**
```powershell
python -m queuectl --help
```
**What to capture:** Terminal showing all available commands
- **File name:** `06-main-help.png`

---

## 📸 Screenshot 7: Worker Help
**Command to run:**
```powershell
python -m queuectl worker --help
```
**What to capture:** Terminal showing worker subcommands
- **File name:** `07-worker-help.png`

---

## 📸 Screenshot 8: DLQ Help
**Command to run:**
```powershell
python -m queuectl dlq --help
```
**What to capture:** Terminal showing DLQ commands
- **File name:** `08-dlq-help.png`

---

## 📸 Screenshot 9: Empty Queue Status
**Command to run:**
```powershell
python -m queuectl status
```
**What to capture:** Terminal showing empty queue (all zeros)
- **File name:** `09-empty-status.png`

---

## 📸 Screenshot 10: Enqueue First Job
**Command to run:**
```powershell
python -m queuectl enqueue --id job1 --command "echo Hello World"
```
**What to capture:** Terminal showing "Job enqueued" message
- **File name:** `10-enqueue-job1.png`

---

## 📸 Screenshot 11: Enqueue Second Job
**Command to run:**
```powershell
python -m queuectl enqueue --id job2 --command "sleep 2" --max-retries 3
```
**What to capture:** Terminal showing second job enqueued
- **File name:** `11-enqueue-job2.png`

---

## 📸 Screenshot 12: Status After Enqueuing
**Command to run:**
```powershell
python -m queuectl status
```
**What to capture:** Terminal showing 2 pending jobs
- **File name:** `12-status-with-jobs.png`

---

## 📸 Screenshot 13: List All Jobs
**Command to run:**
```powershell
python -m queuectl list
```
**What to capture:** Terminal showing table with all jobs
- **File name:** `13-list-all-jobs.png`

---

## 📸 Screenshot 14: List Pending Jobs
**Command to run:**
```powershell
python -m queuectl list --state pending
```
**What to capture:** Terminal showing only pending jobs
- **File name:** `14-list-pending.png`

---

## 📸 Screenshot 15: Start Single Worker
**Command to run:**
```powershell
python -m queuectl worker start
```
**What to capture:** Terminal showing "Started 1 worker(s)"
- **File name:** `15-start-worker.png`

---

## 📸 Screenshot 16: Status with Active Worker
**Command to run:**
```powershell
python -m queuectl status
```
**What to capture:** Terminal showing "Active Workers: 1"
- **File name:** `16-status-with-worker.png`

---

## 📸 Screenshot 17: Wait 3 seconds, then Check Completed Jobs
**Command to run:**
```powershell
python -m queuectl list --state completed
```
**What to capture:** Terminal showing completed jobs
- **File name:** `17-completed-jobs.png`

---

## 📸 Screenshot 18: Stop Worker
**Command to run:**
```powershell
python -m queuectl worker stop
```
**What to capture:** Terminal showing "All workers stopped"
- **File name:** `18-stop-worker.png`

---

## 📸 Screenshot 19: Start Multiple Workers
**Command to run:**
```powershell
python -m queuectl worker start --count 3
```
**What to capture:** Terminal showing "Started 3 worker(s)" with PIDs
- **File name:** `19-start-multiple-workers.png`

---

## 📸 Screenshot 20: Status with Multiple Workers
**Command to run:**
```powershell
python -m queuectl status
```
**What to capture:** Terminal showing "Active Workers: 3"
- **File name:** `20-status-multiple-workers.png`

---

## 📸 Screenshot 21: Enqueue Failed Job
**Command to run:**
```powershell
python -m queuectl enqueue --id fail-job --command "nonexistent-command-12345" --max-retries 2
```
**What to capture:** Terminal showing failed job enqueued
- **File name:** `21-enqueue-failed-job.png`

---

## 📸 Screenshot 22: Start Worker for Failed Job
**Command to run:**
```powershell
python -m queuectl worker start
```
**What to capture:** Terminal showing worker started
- **File name:** `22-start-worker-for-fail.png`

---

## 📸 Screenshot 23: Wait 8-10 seconds, then Check Status (Job should be in DLQ)
**Command to run:**
```powershell
python -m queuectl status
```
**What to capture:** Terminal showing job in "Dead (DLQ)" state
- **File name:** `23-status-with-dlq.png`

---

## 📸 Screenshot 24: List DLQ Jobs
**Command to run:**
```powershell
python -m queuectl dlq list
```
**What to capture:** Terminal showing table with DLQ jobs
- **File name:** `24-dlq-list.png`

---

## 📸 Screenshot 25: Retry Job from DLQ
**Command to run:**
```powershell
python -m queuectl dlq retry fail-job
```
**What to capture:** Terminal showing "Job moved back to pending queue"
- **File name:** `25-dlq-retry.png`

---

## 📸 Screenshot 26: Status After Retry
**Command to run:**
```powershell
python -m queuectl status
```
**What to capture:** Terminal showing job back in pending state
- **File name:** `26-status-after-retry.png`

---

## 📸 Screenshot 27: Get All Configuration
**Command to run:**
```powershell
python -m queuectl config get
```
**What to capture:** Terminal showing all config values
- **File name:** `27-config-get-all.png`

---

## 📸 Screenshot 28: Get Specific Config
**Command to run:**
```powershell
python -m queuectl config get max-retries
```
**What to capture:** Terminal showing max-retries value
- **File name:** `28-config-get-specific.png`

---

## 📸 Screenshot 29: Set Configuration
**Command to run:**
```powershell
python -m queuectl config set max-retries 5
```
**What to capture:** Terminal showing "Configuration updated"
- **File name:** `29-config-set.png`

---

## 📸 Screenshot 30: Verify Config Change
**Command to run:**
```powershell
python -m queuectl config get max-retries
```
**What to capture:** Terminal showing updated value (5)
- **File name:** `30-config-verify.png`

---

## 📸 Screenshot 31: List Failed Jobs
**Command to run:**
```powershell
python -m queuectl list --state failed
```
**What to capture:** Terminal showing failed jobs (if any)
- **File name:** `31-list-failed.png`

---

## 📸 Screenshot 32: List Dead Jobs
**Command to run:**
```powershell
python -m queuectl list --state dead
```
**What to capture:** Terminal showing dead jobs
- **File name:** `32-list-dead.png`

---

## 📸 Screenshot 33: Test Script Execution - Start
**Command to run:**
```powershell
python test_queuectl.py
```
**What to capture:** Terminal showing test script starting
- **File name:** `33-test-script-start.png`

---

## 📸 Screenshot 34: Test Script - Results
**Command to run:** (Same command, wait for completion)
**What to capture:** Terminal showing "All tests completed!"
- **File name:** `34-test-script-results.png`

---

## 📸 Screenshot 35: Data Persistence - Before Restart
**Command to run:**
```powershell
python -m queuectl enqueue --id persist-test --command "echo Persistence"
python -m queuectl list
```
**What to capture:** Terminal showing job exists
- **File name:** `35-persistence-before.png`

---

## 📸 Screenshot 36: Data Persistence - After Restart Simulation
**Steps:**
1. Close terminal
2. Open new terminal
3. Run: `python -m queuectl list`

**What to capture:** Terminal showing job still exists (proves persistence)
- **File name:** `36-persistence-after.png`

---

## 📸 Screenshot 37: Final Status
**Command to run:**
```powershell
python -m queuectl worker stop
python -m queuectl status
```
**What to capture:** Terminal showing final queue status
- **File name:** `37-final-status.png`

---

## 📸 Screenshot 38: Database File Location (Optional but Good)
**What to capture:** File Explorer showing:
- `C:\Users\prade\.queuectl\data\jobs.db`
- Shows where data is stored
- **File name:** `38-database-location.png`

---

## 📋 Quick Summary - Minimum Required Screenshots

If you're short on time, take at least these **10 essential screenshots**:

1. ✅ Installation (`pip install -r requirements.txt`)
2. ✅ Help command (`queuectl --help`)
3. ✅ Enqueue job
4. ✅ Status command
5. ✅ Start worker
6. ✅ Completed jobs
7. ✅ DLQ list
8. ✅ Configuration get/set
9. ✅ Test script execution
10. ✅ Final status

---

## 💡 Tips for Taking Screenshots

1. **Clear terminal** before each screenshot: `cls` (Windows)
2. **Full-screen terminal** for better visibility
3. **Use larger font** in terminal (easier to read)
4. **Wait 2-3 seconds** after commands that need processing time
5. **Name files clearly** (01-installation.png, 02-help.png, etc.)
6. **Save in `screenshots/` folder**

---

## 📁 Folder Structure for Screenshots

Create this folder structure:
```
FLAM/
├── screenshots/
│   ├── 01-project-structure.png
│   ├── 02-python-version.png
│   ├── 03-install-dependencies.png
│   ├── ... (all other screenshots)
│   └── 38-database-location.png
```

---

## ✅ Screenshot Checklist

- [ ] Screenshot 1: Project Structure
- [ ] Screenshot 2: Python Version
- [ ] Screenshot 3: Install Dependencies
- [ ] Screenshot 4: Install Package
- [ ] Screenshot 5: Verify Installation
- [ ] Screenshot 6: Main Help
- [ ] Screenshot 7: Worker Help
- [ ] Screenshot 8: DLQ Help
- [ ] Screenshot 9: Empty Status
- [ ] Screenshot 10: Enqueue Job 1
- [ ] Screenshot 11: Enqueue Job 2
- [ ] Screenshot 12: Status with Jobs
- [ ] Screenshot 13: List All Jobs
- [ ] Screenshot 14: List Pending
- [ ] Screenshot 15: Start Worker
- [ ] Screenshot 16: Status with Worker
- [ ] Screenshot 17: Completed Jobs
- [ ] Screenshot 18: Stop Worker
- [ ] Screenshot 19: Start Multiple Workers
- [ ] Screenshot 20: Status Multiple Workers
- [ ] Screenshot 21: Enqueue Failed Job
- [ ] Screenshot 22: Start Worker for Fail
- [ ] Screenshot 23: Status with DLQ
- [ ] Screenshot 24: DLQ List
- [ ] Screenshot 25: DLQ Retry
- [ ] Screenshot 26: Status After Retry
- [ ] Screenshot 27: Config Get All
- [ ] Screenshot 28: Config Get Specific
- [ ] Screenshot 29: Config Set
- [ ] Screenshot 30: Config Verify
- [ ] Screenshot 31: List Failed
- [ ] Screenshot 32: List Dead
- [ ] Screenshot 33: Test Script Start
- [ ] Screenshot 34: Test Script Results
- [ ] Screenshot 35: Persistence Before
- [ ] Screenshot 36: Persistence After
- [ ] Screenshot 37: Final Status
- [ ] Screenshot 38: Database Location

**Total: 38 Screenshots**

---

**Follow this list one by one, and you'll have everything you need!** 📸

