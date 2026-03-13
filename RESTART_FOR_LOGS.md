# 🔄 Restart Required to See Pipeline Logs

## Why Pipeline Logs Aren't Showing

The pipeline logging code was just integrated into `src/api/app.py`, but your application is still running the **old code** from before the integration.

## ✅ Solution: Restart the Application

### Step 1: Stop the Current Application

Press `Ctrl+C` in the terminal where `run_app.py` is running.

### Step 2: Restart the Application

```bash
python run_app.py
```

### Step 3: Upload a Spec File

Go to http://localhost:5000 and upload a spec file (or use the API directly).

### Step 4: Check the Logs

```powershell
# Watch for pipeline logs in real-time
Get-Content logs\specsentinel.pipeline.log -Wait

# Or view all logs
Get-ChildItem logs\*.log | ForEach-Object {
    Write-Host "`n=== $($_.Name) ===" -ForegroundColor Cyan
    Get-Content $_.FullName | Select-Object -Last 20
}
```

## 📊 What You'll See After Restart

### Console Output:
```
[Backend] 2026-03-13 17:20:00 [INFO] [specsentinel.pipeline] [PLAN] Starting...
[Backend] 2026-03-13 17:20:00 [INFO] [specsentinel.pipeline] [PLAN] Completed in 0.123s
[Backend] 2026-03-13 17:20:00 [INFO] [specsentinel.pipeline] [ANALYZE] Starting...
[Backend] 2026-03-13 17:20:01 [INFO] [specsentinel.pipeline] [ANALYZE] Completed in 1.234s
[Backend] 2026-03-13 17:20:01 [INFO] [specsentinel.pipeline] [MATCH] Starting...
[Backend] 2026-03-13 17:20:02 [INFO] [specsentinel.pipeline] [MATCH] Completed in 0.567s
[Backend] 2026-03-13 17:20:02 [INFO] [specsentinel.pipeline] [SCORE] Starting...
[Backend] 2026-03-13 17:20:02 [INFO] [specsentinel.pipeline] [SCORE] Completed in 0.089s
[Backend] 2026-03-13 17:20:02 [INFO] [specsentinel.pipeline] [REPORT] Starting...
[Backend] 2026-03-13 17:20:02 [INFO] [specsentinel.pipeline] [REPORT] Completed in 0.045s
[Backend] 2026-03-13 17:20:02 [INFO] [__main__] [PERF] _run_pipeline completed in 2.058s
```

### Log Files Created:
- `logs/specsentinel.pipeline.log` - Pipeline stage tracking ⭐ NEW!
- `logs/specsentinel.api.log` - API logs with performance metrics
- `logs/specsentinel.frontend.log` - Frontend request logs
- `logs/specsentinel.requests.log` - HTTP request/response logs

## 🎯 Quick Test

After restarting, run this to see pipeline logs:

```powershell
# Upload a test spec
curl -X POST http://localhost:8000/analyze `
  -F "file=@tests/petStoreSwagger.json"

# View the pipeline logs
Get-Content logs\specsentinel.pipeline.log
```

## 📝 Current Status

**Before Restart:**
- ❌ Pipeline logs not appearing (old code running)
- ✅ Frontend logs working
- ✅ Basic API logs working

**After Restart:**
- ✅ Pipeline stage tracking (PLAN → ANALYZE → MATCH → SCORE → REPORT)
- ✅ Performance metrics for each stage
- ✅ Execution time tracking
- ✅ All enhanced logging features

## 🔍 Verify Integration

After restart, check if the new code is loaded:

```powershell
# This should show pipeline logs after you analyze a spec
Get-Content logs\specsentinel.pipeline.log

# This should show performance metrics
Select-String -Path "logs\*.log" -Pattern "PERF"

# This should show stage tracking
Select-String -Path "logs\*.log" -Pattern "Starting\.\.\.|Completed in"
```

## ⚠️ Important

The pipeline logs will ONLY appear:
1. ✅ After you restart the application
2. ✅ After you upload/analyze a spec file
3. ✅ In the `logs/specsentinel.pipeline.log` file

They won't appear from your previous analysis (at 17:06:08 and 17:14:42) because that was using the old code.

---

**TL;DR:** Stop the app (Ctrl+C), restart it (`python run_app.py`), then upload a spec to see the new pipeline logs! 🚀