# Logging Quick Start Guide

## Current Status: What Happens Now?

### ✅ YES - Basic Logs Are Generated

When you start the application using the README instructions, **logs ARE being generated**, but they use the **old basic logging system**:

```python
# Current logging in src/api/app.py (line 33-34)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
```

**What you get now:**
- ✅ Console output with timestamps and log levels
- ✅ Basic INFO, WARNING, ERROR messages
- ❌ NO file logging (logs only to console)
- ❌ NO structured logging with context
- ❌ NO performance tracking
- ❌ NO request/response logging
- ❌ NO log rotation
- ❌ NO separate log files per component

### 🎯 After Integration: What You'll Get

After integrating the new logging system, you'll get:

- ✅ Console output (colored and formatted)
- ✅ **File logging** to `logs/` directory
- ✅ **Structured logging** with rich context
- ✅ **Performance tracking** (execution times)
- ✅ **Request/response logging** (HTTP details)
- ✅ **Automatic log rotation** (10MB max per file)
- ✅ **Separate log files** per component
- ✅ **JSON format option** for production
- ✅ **Pipeline stage tracking**
- ✅ **Agent operation logging**

## Quick Integration (5 Minutes)

### Option 1: Minimal Integration (Just Add Middleware)

This gives you request/response logging with **zero code changes** to your existing logic:

**Step 1:** Update `src/api/app.py` - Add these 2 lines:

```python
# Add after line 31 (after other imports)
from src.utils.logging_middleware import FastAPILoggingMiddleware

# Add after line 48 (after CORS middleware)
app.add_middleware(FastAPILoggingMiddleware)
```

**Step 2:** Update `frontend/app.py` - Add these 2 lines:

```python
# Add after line 8 (after imports)
from src.utils.logging_middleware import FlaskLoggingMiddleware

# Add after line 10 (after app = Flask(__name__))
FlaskLoggingMiddleware(app)
```

**That's it!** Now you get:
- ✅ HTTP request/response logging to files
- ✅ Automatic log files in `logs/` directory
- ✅ Duration tracking for all requests
- ✅ Error logging with context

### Option 2: Full Integration (Replace Basic Logging)

For complete benefits, replace the basic logging setup:

**In `src/api/app.py`:**

```python
# REPLACE lines 33-34:
# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
# logger = logging.getLogger(__name__)

# WITH:
from src.utils.logging_config import get_logger
from src.utils.logging_middleware import FastAPILoggingMiddleware

logger = get_logger(__name__)

# Then add middleware after CORS:
app.add_middleware(FastAPILoggingMiddleware)
```

**In `frontend/app.py`:**

```python
# ADD at the top (after imports):
from src.utils.logging_config import get_logger
from src.utils.logging_middleware import FlaskLoggingMiddleware

logger = get_logger(__name__)

# ADD after app creation:
FlaskLoggingMiddleware(app)
```

## Testing the Integration

### 1. Start Your Application

```bash
# Using the README instructions
python run_app.py
```

### 2. Check Logs Are Being Created

```powershell
# List log files
Get-ChildItem logs\*.log

# Watch API logs in real-time
Get-Content logs\specsentinel.api.log -Wait

# Watch frontend logs
Get-Content logs\specsentinel.frontend.log -Wait
```

### 3. Make a Request

```bash
# Upload a spec file or use the web interface
# Then check the logs
```

### 4. View Request Logs

```powershell
# See all requests
Get-Content logs\specsentinel.requests.log

# Filter for errors
Select-String -Path "logs\*.log" -Pattern "ERROR"
```

## What Logs Will You See?

### Before Integration (Current):
```
2026-03-13 16:57:48 [INFO] Initializing SpecSentinel Vector Store...
2026-03-13 16:57:48 [INFO] Vector DB ready: {'security': 50, 'design': 30}
2026-03-13 16:57:48 [INFO] SpecSentinel ready.
```

### After Integration (With Middleware):
```
2026-03-13 16:57:48 [INFO] [specsentinel.api] Initializing SpecSentinel Vector Store...
2026-03-13 16:57:48 [INFO] [specsentinel.api] Vector DB ready
2026-03-13 16:57:48 [INFO] [specsentinel.api] SpecSentinel ready
2026-03-13 16:57:50 [INFO] [specsentinel.requests] Request: POST /analyze
2026-03-13 16:58:00 [INFO] [specsentinel.requests] Response: POST /analyze -> 200 (10250ms)
```

### After Full Integration (With Pipeline Logger):
```
2026-03-13 16:57:48 [INFO] [specsentinel.api] Initializing SpecSentinel Vector Store...
2026-03-13 16:57:50 [INFO] [specsentinel.requests] Request: POST /analyze
2026-03-13 16:57:50 [INFO] [specsentinel.pipeline] [PLAN] Starting...
2026-03-13 16:57:50 [INFO] [specsentinel.pipeline] [PLAN] Completed in 0.123s
2026-03-13 16:57:50 [INFO] [specsentinel.pipeline] [ANALYZE] Starting...
2026-03-13 16:57:51 [INFO] [specsentinel.pipeline] [ANALYZE] Completed in 1.234s
2026-03-13 16:57:51 [INFO] [specsentinel.pipeline] [MATCH] Starting...
2026-03-13 16:57:52 [INFO] [specsentinel.pipeline] [MATCH] Completed in 0.567s
2026-03-13 16:57:52 [INFO] [specsentinel.pipeline] [SCORE] Starting...
2026-03-13 16:57:52 [INFO] [specsentinel.pipeline] [SCORE] Completed in 0.089s
2026-03-13 16:58:00 [INFO] [specsentinel.requests] Response: POST /analyze -> 200 (10250ms)
```

## Configuration (Optional)

Create a `.env` file to customize logging:

```bash
# Copy the example
cp .env.example .env

# Edit .env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
FILE_LOGGING=true       # Enable file logging
JSON_LOGGING=false      # Use JSON format (for production)
```

## Summary

### Right Now (Without Integration):
- ✅ Application runs normally
- ✅ Console logs are displayed
- ❌ No log files created
- ❌ No request/response tracking
- ❌ No performance metrics

### After Minimal Integration (2 lines of code):
- ✅ Application runs normally
- ✅ Console logs are displayed
- ✅ **Log files created in `logs/` directory**
- ✅ **Request/response tracking**
- ✅ **Duration metrics**
- ✅ **Automatic log rotation**

### After Full Integration (Complete guide in docs/LOGGING_INTEGRATION.md):
- ✅ Everything from minimal integration
- ✅ **Pipeline stage tracking**
- ✅ **Performance logging**
- ✅ **Agent operation logging**
- ✅ **Structured logging with context**
- ✅ **JSON format option**

## Next Steps

1. **Try it now:** Start your app and check console logs (they work!)
2. **Quick win:** Add the 2-line middleware integration for file logging
3. **Full power:** Follow [LOGGING_INTEGRATION.md](./LOGGING_INTEGRATION.md) for complete integration

## Questions?

- **"Will my app break?"** No! The new logging is backward compatible
- **"Do I need to change my code?"** No for basic file logging, yes for advanced features
- **"Where are logs stored?"** `C:\Users\DebapriyoDasgupta\IBM_Hackathon_26\SpecSentinal_IBM_Hackathon\logs\`
- **"Can I use both?"** Yes! Old logging works, new logging adds features

---

**TL;DR:** Your app logs to console now. Add 2 lines of code to also log to files with request tracking. See [LOGGING_INTEGRATION.md](./LOGGING_INTEGRATION.md) for full integration.