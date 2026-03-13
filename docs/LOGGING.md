# SpecSentinel Logging Guide

Comprehensive logging system for SpecSentinel with structured logging, performance tracking, and request/response monitoring.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Logger Types](#logger-types)
- [Middleware](#middleware)
- [Performance Logging](#performance-logging)
- [Structured Logging](#structured-logging)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

SpecSentinel uses a centralized logging system that provides:

- **Multiple output formats**: Console (colored), file, and JSON
- **Log rotation**: Automatic rotation with configurable size limits
- **Structured logging**: JSON format with extra context fields
- **Performance tracking**: Function execution time monitoring
- **Request/response logging**: HTTP request/response tracking
- **Agent logging**: Specialized logging for AI agents
- **Pipeline logging**: Stage-by-stage pipeline execution tracking

## Quick Start

### Basic Usage

```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### Structured Logging

```python
from src.utils.logging_config import StructuredLogger

logger = StructuredLogger(__name__)

logger.info("User logged in", user_id=123, ip="192.168.1.1")
logger.error("Database error", query="SELECT *", error_code=500)
```

### Performance Logging

```python
from src.utils.logging_config import log_performance

@log_performance()
def expensive_operation():
    # Your code here
    pass
```

## Configuration

### Environment Variables

Configure logging behavior using environment variables:

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export LOG_LEVEL=INFO

# Enable JSON logging (for production)
export JSON_LOGGING=true

# Enable file logging
export FILE_LOGGING=true
```

### Programmatic Configuration

```python
from src.utils.logging_config import setup_logging

# Custom logger with specific settings
logger = setup_logging(
    name="mymodule",
    level="DEBUG",
    enable_console=True,
    enable_file=True,
    enable_json=False
)
```

## Logger Types

### 1. Standard Logger

Basic logger for general application logging:

```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Standard log message")
```

### 2. Structured Logger

Logger with extra context fields:

```python
from src.utils.logging_config import StructuredLogger

logger = StructuredLogger(__name__)
logger.info(
    "API request processed",
    method="POST",
    path="/analyze",
    duration_ms=150,
    status_code=200
)
```

### 3. Request Logger

Specialized logger for HTTP requests:

```python
from src.utils.logging_config import RequestLogger

req_logger = RequestLogger()

# Log incoming request
req_logger.log_request(
    method="POST",
    path="/api/analyze",
    client_ip="192.168.1.1",
    user_agent="Mozilla/5.0"
)

# Log response
req_logger.log_response(
    method="POST",
    path="/api/analyze",
    status_code=200,
    duration_ms=250
)

# Log error
req_logger.log_error(
    method="POST",
    path="/api/analyze",
    error=exception_object
)
```

### 4. Pipeline Logger

Logger for analysis pipeline stages:

```python
from src.utils.logging_config import PipelineLogger

pipeline = PipelineLogger()

# Start stage
pipeline.start_stage("ANALYZE", spec_name="petstore.yaml")

# ... do work ...

# End stage
pipeline.end_stage("ANALYZE", signals_count=42)

# Log error
pipeline.stage_error("ANALYZE", error=exception_object)
```

### 5. Agent Logger

Logger for AI agent operations:

```python
from src.utils.logging_config import AgentLogger

agent_logger = AgentLogger("SecurityAgent")

# Log analysis start
agent_logger.log_analysis_start("petstore.yaml", category="security")

# Log completion
agent_logger.log_analysis_complete(
    findings_count=5,
    duration=2.5,
    risk_level="HIGH"
)

# Log LLM call
agent_logger.log_llm_call(
    model="gpt-4o-mini",
    tokens=1500,
    cost=0.002
)

# Log error
agent_logger.log_error(exception_object, context="analysis")
```

## Middleware

### FastAPI Middleware

Add request/response logging to FastAPI:

```python
from fastapi import FastAPI
from src.utils.logging_middleware import FastAPILoggingMiddleware

app = FastAPI()
app.add_middleware(FastAPILoggingMiddleware)
```

### Flask Middleware

Add request/response logging to Flask:

```python
from flask import Flask
from src.utils.logging_middleware import FlaskLoggingMiddleware

app = Flask(__name__)
FlaskLoggingMiddleware(app)
```

## Performance Logging

### Function Decorator

Log execution time of functions:

```python
from src.utils.logging_config import log_performance

@log_performance()
def analyze_spec(spec):
    # Your code here
    return result
```

### Context Manager

Log execution time of code blocks:

```python
from src.utils.logging_config import log_execution_time

with log_execution_time("database query"):
    # Your code here
    result = db.query()
```

### Function Call Logging

Log function calls with arguments:

```python
from src.utils.logging_middleware import log_function_call

@log_function_call()
def process_data(data, options=None):
    # Your code here
    return result
```

## Structured Logging

### JSON Format

Enable JSON logging for production:

```bash
export JSON_LOGGING=true
```

JSON output example:

```json
{
  "timestamp": "2024-03-13T11:00:00.000Z",
  "level": "INFO",
  "logger": "specsentinel.api",
  "message": "Request processed",
  "module": "app",
  "function": "analyze_spec",
  "line": 125,
  "method": "POST",
  "path": "/analyze",
  "status_code": 200,
  "duration_ms": 250
}
```

### Adding Context

Add extra fields to log messages:

```python
logger = StructuredLogger(__name__)

logger.info(
    "User action",
    user_id=123,
    action="upload",
    file_size=1024,
    file_type="yaml"
)
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

```python
logger.debug("Detailed variable state: %s", variable)
logger.info("Operation completed successfully")
logger.warning("Deprecated API usage detected")
logger.error("Failed to connect to database")
logger.critical("System out of memory")
```

### 2. Include Context

Always include relevant context in log messages:

```python
# Bad
logger.error("Failed")

# Good
logger.error(
    "Failed to analyze spec",
    spec_name="petstore.yaml",
    error_type="ValidationError",
    line_number=42
)
```

### 3. Use Structured Logging

Prefer structured logging over string formatting:

```python
# Bad
logger.info(f"User {user_id} performed {action}")

# Good
logger.info("User action", user_id=user_id, action=action)
```

### 4. Log Exceptions Properly

Use `exception()` method to include traceback:

```python
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed", operation="risky_operation")
```

### 5. Performance Logging

Use decorators for consistent performance tracking:

```python
@log_performance()
def expensive_function():
    # Your code
    pass
```

## Examples

### Complete API Endpoint Example

```python
from src.utils.logging_config import get_logger, log_performance
from src.utils.logging_config import PipelineLogger

logger = get_logger(__name__)
pipeline = PipelineLogger()

@log_performance()
async def analyze_spec(spec: dict, spec_name: str):
    logger.info(f"Starting analysis: {spec_name}")
    
    try:
        # Extract signals
        pipeline.start_stage("EXTRACT", spec_name=spec_name)
        signals = extract_signals(spec)
        pipeline.end_stage("EXTRACT", signals_count=len(signals))
        
        # Match rules
        pipeline.start_stage("MATCH", signals_count=len(signals))
        findings = match_rules(signals)
        pipeline.end_stage("MATCH", findings_count=len(findings))
        
        # Score
        pipeline.start_stage("SCORE", findings_count=len(findings))
        score = compute_score(findings)
        pipeline.end_stage("SCORE", health_score=score.total)
        
        logger.info(
            f"Analysis complete: {spec_name}",
            extra={
                "extra_data": {
                    "signals": len(signals),
                    "findings": len(findings),
                    "score": score.total
                }
            }
        )
        
        return {"score": score, "findings": findings}
        
    except Exception as e:
        logger.exception(f"Analysis failed: {spec_name}")
        raise
```

### Agent Analysis Example

```python
from src.utils.logging_config import AgentLogger

class SecurityAgent:
    def __init__(self):
        self.logger = AgentLogger("SecurityAgent")
    
    def analyze(self, spec, signals, findings):
        self.logger.log_analysis_start(
            spec.get("info", {}).get("title", "unknown"),
            signals_count=len(signals)
        )
        
        start_time = time.time()
        
        try:
            # Perform analysis
            results = self._analyze_security(spec, signals, findings)
            
            duration = time.time() - start_time
            self.logger.log_analysis_complete(
                findings_count=len(results),
                duration=duration,
                risk_level=results.risk_level
            )
            
            return results
            
        except Exception as e:
            self.logger.log_error(e, spec_name=spec.get("info", {}).get("title"))
            raise
```

### Request Logging Example

```python
from src.utils.logging_config import RequestLogger
import time

req_logger = RequestLogger()

async def handle_request(request):
    start_time = time.time()
    
    # Log request
    req_logger.log_request(
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    try:
        # Process request
        response = await process(request)
        
        # Log response
        duration_ms = (time.time() - start_time) * 1000
        req_logger.log_response(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        return response
        
    except Exception as e:
        # Log error
        req_logger.log_error(
            method=request.method,
            path=request.url.path,
            error=e
        )
        raise
```

## Log Files

Logs are stored in the `logs/` directory:

```
logs/
├── specsentinel.log          # Main application log
├── specsentinel.api.log      # API backend log
├── specsentinel.frontend.log # Frontend log
├── specsentinel.agent.*.log  # Agent-specific logs
└── specsentinel.pipeline.log # Pipeline execution log
```

### Log Rotation

Logs automatically rotate when they reach 10MB:

- Maximum file size: 10MB
- Backup count: 5 files
- Old logs: `specsentinel.log.1`, `specsentinel.log.2`, etc.

## Troubleshooting

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
```

### View Logs in Real-Time

```bash
# Linux/Mac
tail -f logs/specsentinel.log

# Windows PowerShell
Get-Content logs/specsentinel.log -Wait
```

### Parse JSON Logs

```bash
# Pretty print JSON logs
cat logs/specsentinel.log | jq '.'

# Filter by level
cat logs/specsentinel.log | jq 'select(.level == "ERROR")'

# Filter by module
cat logs/specsentinel.log | jq 'select(.module == "api")'
```

## Integration with Monitoring Tools

### Elasticsearch/Logstash

JSON logging format is compatible with ELK stack:

```bash
export JSON_LOGGING=true
```

### CloudWatch/DataDog

Use structured logging for better filtering:

```python
logger.info("Event", event_type="analysis", status="success")
```

### Prometheus Metrics

Combine with performance logging for metrics:

```python
@log_performance()
def operation():
    # Execution time is logged
    pass
```

## Summary

The SpecSentinel logging system provides:

✅ Centralized configuration  
✅ Multiple output formats  
✅ Structured logging with context  
✅ Performance tracking  
✅ Request/response logging  
✅ Agent-specific logging  
✅ Pipeline stage tracking  
✅ Automatic log rotation  
✅ Production-ready JSON format  

For questions or issues, refer to the main documentation or create an issue on GitHub.