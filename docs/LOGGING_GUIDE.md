# SpecSentinel Logging Guide

## Overview

SpecSentinel uses a centralized logging system that outputs to both terminal (console) and log files. This guide explains how to view and configure logs.

## Quick Start

### Start with Full Logging

Use the provided PowerShell script to start both servers with verbose logging:

```powershell
.\start_with_logs.ps1
```

This will:
- Set `LOG_LEVEL=DEBUG` for verbose output
- Open separate terminal windows for backend and frontend
- Display all logs in real-time
- Save logs to `./logs/` directory

### Manual Start with Logging

**Backend:**
```powershell
$env:LOG_LEVEL='DEBUG'
$env:USE_MULTI_AGENT='true'
python src/api/app.py
```

**Frontend:**
```powershell
$env:LOG_LEVEL='DEBUG'
cd frontend
python app.py
```

## Log Levels

Configure log verbosity with the `LOG_LEVEL` environment variable:

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Very detailed logs | Development, troubleshooting |
| `INFO` | General information | Normal operation (default) |
| `WARNING` | Warning messages | Production monitoring |
| `ERROR` | Error messages | Production |
| `CRITICAL` | Critical failures | Production |

**Example:**
```powershell
$env:LOG_LEVEL='DEBUG'  # Verbose
$env:LOG_LEVEL='INFO'   # Normal (default)
$env:LOG_LEVEL='ERROR'  # Minimal
```

## Log Output Locations

### 1. Terminal/Console Output

All logs are displayed in the terminal with:
- Colored output (INFO=green, ERROR=red, etc.)
- Timestamp
- Log level
- Logger name (module)
- Message

**Example:**
```
2026-03-15 10:30:45 [INFO    ] [src.api.app              ] SpecSentinel Backend Ready!
2026-03-15 10:30:46 [DEBUG   ] [src.engine.rule_matcher  ] Batch querying 10 signals for category 'security'
```

### 2. Log Files

Logs are automatically saved to `./logs/` directory:

| File | Content |
|------|---------|
| `__main__.log` | Backend server logs |
| `specsentinel.log` | General application logs |
| `src.api.app.log` | API endpoint logs |
| `src.engine.*.log` | Pipeline component logs |
| `src.vectordb.*.log` | Vector database logs |

**Log Rotation:**
- Max file size: 10MB
- Backup count: 5 files
- Old logs automatically archived

## What Gets Logged

### Backend Startup
```
======================================================================
SpecSentinel Backend Starting...
======================================================================
Multi-Agent Mode: ENABLED
Available LLM Providers: openai, anthropic
Initializing SpecSentinel Vector Store...
Vector DB Collections Ready:
  - security: 150 rules
  - design: 120 rules
  - error_handling: 80 rules
  - documentation: 90 rules
  - governance: 60 rules
Starting background ingestion scheduler...
======================================================================
SpecSentinel Backend Ready!
API Documentation: http://localhost:8000/docs
======================================================================
```

### Frontend Startup
```
======================================================================
SpecSentinel Frontend Starting...
======================================================================
Backend API URL: http://localhost:8000
Flask Environment: development
Log Level: DEBUG
======================================================================
SpecSentinel Frontend Ready!
Server: http://localhost:5000
======================================================================
```

### Request Processing
```
2026-03-15 10:31:00 [INFO    ] Request: POST /analyze/stream
2026-03-15 10:31:00 [INFO    ] Pipeline stage: PLAN started
2026-03-15 10:31:00 [INFO    ] Pipeline stage: ANALYZE started
2026-03-15 10:31:01 [DEBUG   ] Batch querying 25 signals for category 'security'
2026-03-15 10:31:02 [INFO    ] Matched 23/25 signals to rules using batch queries
2026-03-15 10:31:02 [INFO    ] Response: POST /analyze/stream -> 200 (2.5s)
```

### Multi-Agent Analysis (when enabled)
```
2026-03-15 10:31:03 [INFO    ] Starting multi-agent analysis
2026-03-15 10:31:03 [INFO    ] [SecurityAgent] Analyzing 10 security findings
2026-03-15 10:31:05 [INFO    ] [DesignAgent] Analyzing 8 design findings
2026-03-15 10:31:07 [INFO    ] [Orchestrator] Consolidating 5 agent reports
```

## Environment Variables

Configure logging behavior:

```powershell
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
$env:LOG_LEVEL='DEBUG'

# Enable/disable file logging
$env:FILE_LOGGING='true'

# Enable JSON format (for log aggregation tools)
$env:JSON_LOGGING='false'

# Enable multi-agent mode
$env:USE_MULTI_AGENT='true'
```

## Viewing Logs

### Real-time Terminal Logs

Watch logs as they happen:
```powershell
# Backend
python src/api/app.py

# Frontend (separate terminal)
cd frontend
python app.py
```

### View Log Files

```powershell
# View latest backend logs
Get-Content logs/__main__.log -Tail 50 -Wait

# View all logs
Get-ChildItem logs/*.log | ForEach-Object { Get-Content $_.FullName }

# Search logs
Select-String -Path logs/*.log -Pattern "ERROR"
```

### Filter Logs by Level

```powershell
# Show only errors
Select-String -Path logs/*.log -Pattern "\[ERROR"

# Show warnings and errors
Select-String -Path logs/*.log -Pattern "\[(ERROR|WARNING)"
```

## Troubleshooting

### No Logs Appearing

1. Check log level:
   ```powershell
   $env:LOG_LEVEL='DEBUG'
   ```

2. Verify file logging is enabled:
   ```powershell
   $env:FILE_LOGGING='true'
   ```

3. Check logs directory exists:
   ```powershell
   Test-Path logs
   ```

### Log Files Too Large

Logs automatically rotate at 10MB. To manually clear:
```powershell
Get-ChildItem logs/*.log | ForEach-Object { Clear-Content $_.FullName }
```

### Logging Errors

If you see "I/O operation on closed file" errors:
- Restart the servers
- Logs will be recreated automatically

## Performance Impact

- **Console logging**: Minimal impact (~1-2% overhead)
- **File logging**: Low impact (~2-5% overhead)
- **DEBUG level**: Higher overhead due to volume
- **Recommendation**: Use INFO level in production

## Best Practices

1. **Development**: Use `DEBUG` level with console output
2. **Production**: Use `INFO` or `WARNING` level with file output
3. **Troubleshooting**: Enable `DEBUG` temporarily
4. **Monitoring**: Parse log files for ERROR/WARNING patterns
5. **Archival**: Backup old log files periodically

## Log Format

### Console Format
```
TIMESTAMP [LEVEL   ] [LOGGER_NAME              ] MESSAGE
```

### File Format
```
TIMESTAMP [LEVEL   ] [LOGGER_NAME              ] [FILE:LINE] MESSAGE
```

### JSON Format (when enabled)
```json
{
  "timestamp": "2026-03-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "src.api.app",
  "message": "Request processed",
  "module": "app",
  "function": "analyze",
  "line": 123
}
```

## Integration with Monitoring Tools

### Splunk/ELK Stack

Enable JSON logging:
```powershell
$env:JSON_LOGGING='true'
```

Configure log shipper to read from `./logs/*.log`

### CloudWatch/Azure Monitor

Use the log files as input for cloud monitoring services.

## Support

For logging issues:
1. Check this guide
2. Review `src/utils/logging_config.py`
3. Verify environment variables
4. Check file permissions on `./logs/` directory

## Related Documentation

- [Multi-Agent System](MULTI_AGENT_SYSTEM.md)
- [Batch Querying Optimization](BATCH_QUERYING_OPTIMIZATION.md)
- [Architecture](ARCHITECTURE.md)