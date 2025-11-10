# QueueCTL - CLI Background Job Queue System

A production-grade CLI-based background job queue system built with Python. QueueCTL manages background jobs with worker processes, implements automatic retries with exponential backoff, and maintains a Dead Letter Queue (DLQ) for permanently failed jobs.

## 🚀 Features

- ✅ **Job Management**: Enqueue, list, and monitor background jobs
- ✅ **Worker Processes**: Run multiple workers in parallel for concurrent job processing
- ✅ **Automatic Retries**: Exponential backoff retry mechanism for failed jobs
- ✅ **Dead Letter Queue**: Permanent storage for jobs that exceed max retries
- ✅ **Persistent Storage**: SQLite-based storage that survives restarts
- ✅ **Job Locking**: Prevents duplicate job execution across workers
- ✅ **Graceful Shutdown**: Workers finish current jobs before exiting
- ✅ **Configuration Management**: CLI-based configuration for retry and backoff settings
- ✅ **Clean CLI Interface**: Intuitive commands with helpful output

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)

## 🔧 Installation

### Option 1: Install as Package (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd FLAM

# Install the package
pip install -e .

# Verify installation
queuectl --version
```

### Option 2: Run Directly

```bash
# Clone the repository
git clone <repository-url>
cd FLAM

# Install dependencies
pip install -r requirements.txt

# Run using Python module
python -m queuectl --version
```

## 📖 Usage

### Basic Commands

#### Enqueue a Job

```bash
# Using JSON format
queuectl enqueue '{"id":"job1","command":"echo Hello World","max_retries":3}'

# Using command-line options
queuectl enqueue --id job2 --command "sleep 2" --max-retries 3
```

#### Start Workers

```bash
# Start a single worker
queuectl worker start

# Start multiple workers
queuectl worker start --count 3
```

#### Stop Workers

```bash
queuectl worker stop
```

#### Check Status

```bash
queuectl status
```

Output example:
```
Queue Status
==================================================
State            Count
----------------  -----
Pending          2
Processing       1
Completed        15
Failed           0
Dead (DLQ)       1
Active Workers   3
```

#### List Jobs

```bash
# List all jobs
queuectl list

# List jobs by state
queuectl list --state pending
queuectl list --state completed
queuectl list --state failed
queuectl list --state dead
```

#### Dead Letter Queue

```bash
# List all DLQ jobs
queuectl dlq list

# Retry a job from DLQ (resets to pending)
queuectl dlq retry job1
```

#### Configuration

```bash
# Get all configuration
queuectl config get

# Get specific configuration value
queuectl config get max-retries

# Set configuration value
queuectl config set max-retries 5
queuectl config set backoff-base 3
```

### Complete Example Workflow

```bash
# 1. Enqueue some jobs
queuectl enqueue '{"id":"job1","command":"echo Hello","max_retries":3}'
queuectl enqueue '{"id":"job2","command":"sleep 1","max_retries":3}'
queuectl enqueue '{"id":"job3","command":"nonexistent-command","max_retries":2}'

# 2. Check status
queuectl status

# 3. Start workers
queuectl worker start --count 2

# 4. Monitor jobs
queuectl list

# 5. Wait a bit, then check status again
queuectl status

# 6. Check DLQ for failed jobs
queuectl dlq list

# 7. Stop workers
queuectl worker stop
```

## 🏗️ Architecture

### Job Lifecycle

```
pending → processing → completed
              ↓
           failed → (retry with backoff) → failed → ... → dead (DLQ)
```

### Components

1. **Job Model** (`queuectl/job.py`)
   - Represents a job with state, attempts, and metadata
   - Manages job state transitions
   - Calculates retry delays using exponential backoff

2. **Storage** (`queuectl/storage.py`)
   - SQLite-based persistent storage
   - Thread-safe job operations
   - Job locking mechanism to prevent duplicate processing

3. **Worker** (`queuectl/worker.py`)
   - Executes jobs in separate processes
   - Handles retries and error cases
   - Graceful shutdown support

4. **Configuration** (`queuectl/config.py`)
   - Manages system configuration
   - Stores settings in `~/.queuectl/config.json`
   - Database stored in `~/.queuectl/data/jobs.db`

5. **CLI** (`queuectl/cli.py`)
   - Command-line interface using Click
   - All operations accessible via CLI

### Data Persistence

- **Configuration**: `~/.queuectl/config.json`
- **Database**: `~/.queuectl/data/jobs.db`
- **Worker PIDs**: `~/.queuectl/data/workers.pid`

All data persists across restarts. Jobs remain in the queue even after system restarts.

### Retry Mechanism

Failed jobs are automatically retried with exponential backoff:

```
delay = base ^ attempts seconds
```

Example with `backoff_base = 2`:
- Attempt 1: 2^0 = 1 second
- Attempt 2: 2^1 = 2 seconds
- Attempt 3: 2^2 = 4 seconds
- Attempt 4: 2^3 = 8 seconds

After `max_retries` attempts, jobs are moved to the Dead Letter Queue.

### Worker Management

- Multiple workers can run concurrently
- Each worker processes one job at a time
- Jobs are locked during processing to prevent duplicates
- Workers gracefully shut down (finish current job before exit)
- Worker PIDs are tracked for management

## 🧪 Testing

Run the test script to validate core functionality:

```bash
python test_queuectl.py
```

The test script validates:
1. ✅ Basic job completion
2. ✅ Failed job retry and DLQ
3. ✅ Multiple workers processing jobs
4. ✅ Data persistence across restarts
5. ✅ Configuration management

## 📊 Job Specification

Each job contains the following fields:

```json
{
  "id": "unique-job-id",
  "command": "echo 'Hello World'",
  "state": "pending",
  "attempts": 0,
  "max_retries": 3,
  "created_at": "2025-01-04T10:30:00Z",
  "updated_at": "2025-01-04T10:30:00Z",
  "error_message": null,
  "next_retry_at": null
}
```

### Job States

| State | Description |
|-------|-------------|
| `pending` | Waiting to be picked up by a worker |
| `processing` | Currently being executed |
| `completed` | Successfully executed |
| `failed` | Failed, but retryable |
| `dead` | Permanently failed (moved to DLQ) |

## ⚙️ Configuration

Default configuration:

```json
{
  "max_retries": 3,
  "backoff_base": 2,
  "worker_count": 1,
  "data_dir": "~/.queuectl/data"
}
```

Configuration can be modified via CLI:

```bash
queuectl config set max-retries 5
queuectl config set backoff-base 3
```

## 🔍 Troubleshooting

### Workers not processing jobs

1. Check if workers are running: `queuectl status`
2. Verify jobs are enqueued: `queuectl list --state pending`
3. Check for locked jobs: Jobs may be stuck if a worker crashed. The lock expires after 5 minutes.

### Jobs stuck in processing

If a worker crashes, jobs may remain in "processing" state. The lock mechanism automatically expires after 5 minutes, allowing other workers to pick up the job.

### Database issues

If you encounter database corruption, you can reset the database:

```bash
# Backup first (optional)
cp ~/.queuectl/data/jobs.db ~/.queuectl/data/jobs.db.backup

# Remove database (will be recreated)
rm ~/.queuectl/data/jobs.db
```

## 🎯 Assumptions & Trade-offs

### Assumptions

1. **Command Execution**: Jobs execute shell commands. Commands that return exit code 0 are considered successful.
2. **Timeout**: Jobs have a 5-minute execution timeout to prevent hanging processes.
3. **Lock Expiration**: Job locks expire after 5 minutes to handle crashed workers.
4. **Storage**: SQLite is sufficient for single-machine deployments. For distributed systems, consider PostgreSQL or similar.

### Trade-offs

1. **SQLite vs. Other DBs**: SQLite chosen for simplicity and zero-configuration. Suitable for single-machine use.
2. **File-based PID tracking**: Worker PIDs stored in file. More robust solutions (e.g., systemd) could be used in production.
3. **No job priorities**: All jobs are processed FIFO. Priority queues could be added as an enhancement.
4. **No job scheduling**: Jobs execute immediately. Scheduled/delayed jobs could be added as a bonus feature.

## 🚀 Future Enhancements (Bonus Features)

Potential improvements:

- [ ] Job timeout handling (configurable per job)
- [ ] Job priority queues
- [ ] Scheduled/delayed jobs (`run_at` field)
- [ ] Job output logging
- [ ] Metrics and execution statistics
- [ ] Web dashboard for monitoring
- [ ] Flask API for programmatic access

## 📝 License

This project is part of a backend developer internship assignment.

## 👤 Author

Developed as part of QueueCTL Backend Developer Internship Assignment.

---

## 📸 Demo

For a working CLI demo, please refer to the demo video link (to be added).

## ✅ Checklist

- [x] Working CLI application (`queuectl`)
- [x] Persistent job storage (SQLite)
- [x] Multiple worker support
- [x] Retry mechanism with exponential backoff
- [x] Dead Letter Queue
- [x] Configuration management
- [x] Clean CLI interface with help texts
- [x] Comprehensive README.md
- [x] Code structured with clear separation of concerns
- [x] Test script to validate core flows

