# QueueCTL Quick Start Guide

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Basic Usage

### 1. Enqueue a Job

```bash
queuectl enqueue '{"id":"job1","command":"echo Hello World"}'
```

### 2. Start Workers

```bash
queuectl worker start --count 2
```

### 3. Check Status

```bash
queuectl status
```

### 4. List Jobs

```bash
queuectl list
queuectl list --state completed
```

### 5. Stop Workers

```bash
queuectl worker stop
```

## Testing

Run the test suite:

```bash
python test_queuectl.py
```

## Configuration

```bash
# View configuration
queuectl config get

# Set max retries
queuectl config set max-retries 5

# Set backoff base
queuectl config set backoff-base 3
```

## Dead Letter Queue

```bash
# List DLQ jobs
queuectl dlq list

# Retry a DLQ job
queuectl dlq retry job-id
```

