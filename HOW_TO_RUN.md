# How to Run QueueCTL

## Quick Start (3 Steps)

### Step 1: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

**OR** install as a package (recommended):

```bash
pip install -e .
```

### Step 2: Verify Installation

Check if the command is available:

```bash
# If installed as package:
queuectl --version

# OR if running directly:
python -m queuectl --version
```

### Step 3: Run Your First Job

```bash
# 1. Enqueue a job
queuectl enqueue '{"id":"my-first-job","command":"echo Hello World"}'

# 2. Start a worker to process it
queuectl worker start

# 3. Wait a moment, then check status
queuectl status

# 4. List completed jobs
queuectl list --state completed

# 5. Stop the worker when done
queuectl worker stop
```

---

## Detailed Step-by-Step Guide

### Method 1: Using the Installed Command (Recommended)

#### 1. Install the package:
```bash
pip install -e .
```

#### 2. Now you can use `queuectl` directly:
```bash
queuectl --help
queuectl status
queuectl enqueue '{"id":"job1","command":"echo test"}'
```

### Method 2: Running as Python Module

#### 1. Install dependencies only:
```bash
pip install -r requirements.txt
```

#### 2. Run using Python module:
```bash
python -m queuectl --help
python -m queuectl status
python -m queuectl enqueue '{"id":"job1","command":"echo test"}'
```

---

## Complete Example Workflow

### Terminal 1: Enqueue Jobs and Monitor

```bash
# Navigate to project directory
cd FLAM

# Install (if not done already)
pip install -r requirements.txt

# Enqueue some jobs
queuectl enqueue '{"id":"job1","command":"echo Hello","max_retries":3}'
queuectl enqueue '{"id":"job2","command":"sleep 2","max_retries":3}'
queuectl enqueue '{"id":"job3","command":"echo World","max_retries":3}'

# Check status
queuectl status

# Start workers (this will run in background)
queuectl worker start --count 2

# Wait a few seconds, then check status again
queuectl status

# List all jobs
queuectl list

# List only completed jobs
queuectl list --state completed

# Stop workers when done
queuectl worker stop
```

### Terminal 2: Monitor Workers (Optional)

You can open a second terminal to monitor while workers are running:

```bash
# Watch status in real-time
watch -n 1 queuectl status  # Linux/Mac
# OR on Windows PowerShell:
while ($true) { queuectl status; Start-Sleep -Seconds 2 }
```

---

## Testing the System

Run the comprehensive test suite:

```bash
python test_queuectl.py
```

This will test:
- ✅ Basic job completion
- ✅ Failed job retry and DLQ
- ✅ Multiple workers
- ✅ Data persistence
- ✅ Configuration

---

## Common Commands Reference

```bash
# Enqueue jobs
queuectl enqueue '{"id":"job1","command":"echo hello"}'
queuectl enqueue --id job2 --command "sleep 1"

# Worker management
queuectl worker start
queuectl worker start --count 3
queuectl worker stop

# Status and listing
queuectl status
queuectl list
queuectl list --state pending
queuectl list --state completed
queuectl list --state failed
queuectl list --state dead

# Dead Letter Queue
queuectl dlq list
queuectl dlq retry job-id

# Configuration
queuectl config get
queuectl config get max-retries
queuectl config set max-retries 5
queuectl config set backoff-base 3

# Help
queuectl --help
queuectl enqueue --help
queuectl worker --help
```

---

## Troubleshooting

### Issue: `queuectl: command not found`

**Solution:**
- Make sure you ran `pip install -e .`
- OR use `python -m queuectl` instead of `queuectl`

### Issue: `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Workers not processing jobs

**Solution:**
1. Check if workers are running: `queuectl status`
2. Make sure jobs are enqueued: `queuectl list --state pending`
3. Restart workers: `queuectl worker stop && queuectl worker start`

### Issue: Permission errors (Windows)

**Solution:**
- Run PowerShell/Command Prompt as Administrator
- OR use `python -m queuectl` instead

---

## Example Scripts

### Run the example script:
```bash
python example_usage.py
```

### Run the test suite:
```bash
python test_queuectl.py
```

---

## Where is Data Stored?

All data is stored in your home directory:
- **Windows**: `C:\Users\YourUsername\.queuectl\`
- **Linux/Mac**: `~/.queuectl/`

Files:
- `config.json` - Configuration
- `data/jobs.db` - SQLite database with all jobs
- `data/workers.pid` - Worker process IDs

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run a test job
3. ✅ Try the test suite: `python test_queuectl.py`
4. ✅ Read the full README.md for detailed documentation
5. ✅ Explore the CLI commands with `--help`

Happy queuing! 🚀

