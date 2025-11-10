# Screenshot Guide for QueueCTL Demo

## 🎬 Recommended Screenshot Order

### 1. **Project Structure** (File Explorer)
- Show the project folder structure
- Highlight: `queuectl/`, `README.md`, `test_queuectl.py`, `requirements.txt`

### 2. **Installation** (Terminal)
```powershell
python --version
pip install -r requirements.txt
pip install -e .
python -m queuectl --version
```

### 3. **Help Commands** (Terminal)
```powershell
python -m queuectl --help
python -m queuectl worker --help
python -m queuectl dlq --help
python -m queuectl config --help
```

### 4. **Empty Queue Status** (Terminal)
```powershell
python -m queuectl status
```

### 5. **Enqueue Jobs** (Terminal)
```powershell
python -m queuectl enqueue --id job1 --command "echo Hello World"
python -m queuectl enqueue --id job2 --command "sleep 2"
python -m queuectl enqueue --id job3 --command "echo Test"
```

### 6. **Status with Jobs** (Terminal)
```powershell
python -m queuectl status
python -m queuectl list
```

### 7. **Start Workers** (Terminal)
```powershell
python -m queuectl worker start --count 2
python -m queuectl status
```

### 8. **Jobs Processing** (Terminal - wait 3 seconds)
```powershell
python -m queuectl status
python -m queuectl list --state completed
```

### 9. **Failed Job & Retry** (Terminal)
```powershell
python -m queuectl enqueue --id fail1 --command "invalid-command" --max-retries 2
python -m queuectl worker start
# Wait 8-10 seconds
python -m queuectl status
python -m queuectl dlq list
```

### 10. **DLQ Retry** (Terminal)
```powershell
python -m queuectl dlq retry fail1
python -m queuectl status
python -m queuectl list --state pending
```

### 11. **Configuration** (Terminal)
```powershell
python -m queuectl config get
python -m queuectl config set max-retries 5
python -m queuectl config get max-retries
```

### 12. **Multiple Workers** (Terminal)
```powershell
python -m queuectl worker stop
python -m queuectl enqueue --id m1 --command "echo 1"
python -m queuectl enqueue --id m2 --command "echo 2"
python -m queuectl enqueue --id m3 --command "echo 3"
python -m queuectl worker start --count 3
python -m queuectl status
# Wait 2 seconds
python -m queuectl list
```

### 13. **Test Script** (Terminal)
```powershell
python test_queuectl.py
```

### 14. **Data Persistence** (Terminal + File Explorer)
```powershell
python -m queuectl enqueue --id persist --command "echo Test"
python -m queuectl list
# Show: C:\Users\prade\.queuectl\data\jobs.db exists
# Close terminal, reopen, then:
python -m queuectl list
```

### 15. **Final Status** (Terminal)
```powershell
python -m queuectl worker stop
python -m queuectl status
python -m queuectl list
```

---

## 📋 Quick Command Reference

### Essential Commands to Screenshot:

1. **Setup**
   - `pip install -r requirements.txt`
   - `pip install -e .`
   - `python -m queuectl --version`

2. **Core Operations**
   - `python -m queuectl enqueue --id X --command "Y"`
   - `python -m queuectl status`
   - `python -m queuectl list`
   - `python -m queuectl list --state completed`

3. **Workers**
   - `python -m queuectl worker start`
   - `python -m queuectl worker start --count 3`
   - `python -m queuectl worker stop`

4. **DLQ**
   - `python -m queuectl dlq list`
   - `python -m queuectl dlq retry <job-id>`

5. **Config**
   - `python -m queuectl config get`
   - `python -m queuectl config set max-retries 5`

6. **Testing**
   - `python test_queuectl.py`

---

## 💡 Tips for Better Screenshots

1. **Clear terminal** before each major section: `cls` (Windows) or `clear` (Linux/Mac)
2. **Use larger font** in terminal for readability
3. **Full-screen terminal** for better visibility
4. **Wait 2-3 seconds** between worker commands and status checks
5. **Show file structure** in a separate file explorer window
6. **Highlight important outputs** (completed jobs, DLQ, etc.)

---

## 🎥 For Video Demo

If recording a video, follow this script:

1. **Introduction** (5 sec): Show project folder
2. **Installation** (30 sec): Install and verify
3. **Basic Usage** (60 sec): Enqueue, status, list, workers
4. **Advanced Features** (60 sec): Failed jobs, DLQ, retry
5. **Configuration** (30 sec): Config get/set
6. **Testing** (30 sec): Run test script
7. **Conclusion** (10 sec): Final status

**Total: ~4-5 minutes**

