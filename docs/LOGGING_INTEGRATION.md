# Logging Integration Guide

How to integrate the new centralized logging system into existing SpecSentinel modules.

## Quick Migration Steps

### 1. Replace Basic Logging Setup

**Before:**
```python
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
```

**After:**
```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)
```

### 2. Add Middleware to FastAPI (src/api/app.py)

**Add at the top:**
```python
from src.utils.logging_middleware import FastAPILoggingMiddleware
```

**Add after app creation:**
```python
app = FastAPI(...)

# Add logging middleware
app.add_middleware(FastAPILoggingMiddleware)
```

### 3. Add Middleware to Flask (frontend/app.py)

**Add at the top:**
```python
from src.utils.logging_middleware import FlaskLoggingMiddleware
```

**Add after app creation:**
```python
app = Flask(__name__)

# Add logging middleware
FlaskLoggingMiddleware(app)
```

### 4. Use Pipeline Logger in Analysis Pipeline

**Before:**
```python
logger.info(f"[PLAN] Analyzing spec: {spec_name}")
logger.info(f"[ANALYZE] Extracted {len(signals)} signals")
logger.info(f"[MATCH] Matched {len(findings)} finding groups")
```

**After:**
```python
from src.utils.logging_config import PipelineLogger

pipeline = PipelineLogger()

pipeline.start_stage("PLAN", spec_name=spec_name)
# ... work ...
pipeline.end_stage("PLAN", paths=len(spec.get('paths', {})))

pipeline.start_stage("ANALYZE", spec_name=spec_name)
# ... work ...
pipeline.end_stage("ANALYZE", signals_count=len(signals))

pipeline.start_stage("MATCH", signals_count=len(signals))
# ... work ...
pipeline.end_stage("MATCH", findings_count=len(findings))
```

### 5. Add Performance Logging to Key Functions

**Before:**
```python
def compute_health_score(findings):
    # ... computation ...
    return health
```

**After:**
```python
from src.utils.logging_config import log_performance

@log_performance()
def compute_health_score(findings):
    # ... computation ...
    return health
```

### 6. Use Agent Logger in Agent Classes

**Before:**
```python
class SecurityAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, spec, signals, findings):
        self.logger.info("Starting analysis")
        # ... work ...
        self.logger.info(f"Found {len(results)} issues")
```

**After:**
```python
from src.utils.logging_config import AgentLogger

class SecurityAgent:
    def __init__(self):
        self.logger = AgentLogger("SecurityAgent")
    
    def analyze(self, spec, signals, findings):
        spec_name = spec.get("info", {}).get("title", "unknown")
        self.logger.log_analysis_start(spec_name)
        
        start_time = time.time()
        # ... work ...
        duration = time.time() - start_time
        
        self.logger.log_analysis_complete(
            findings_count=len(results),
            duration=duration,
            risk_level=results.risk_level
        )
```

### 7. Use Structured Logging for Context-Rich Logs

**Before:**
```python
logger.info(f"User {user_id} uploaded {filename} ({size} bytes)")
```

**After:**
```python
from src.utils.logging_config import StructuredLogger

logger = StructuredLogger(__name__)
logger.info(
    "File uploaded",
    user_id=user_id,
    filename=filename,
    size_bytes=size,
    content_type=content_type
)
```

## Complete Example: Updating src/api/app.py

Here's how to update the main API file:

```python
"""
specsentinel/api/app.py
FastAPI application for SpecSentinel.
"""

import json
import os
import sys
from pathlib import Path

import yaml

# Path setup for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

# NEW: Import logging utilities
from src.utils.logging_config import get_logger, PipelineLogger, log_performance
from src.utils.logging_middleware import FastAPILoggingMiddleware

from src.vectordb.store.chroma_client import SpecSentinelVectorStore
from src.vectordb.ingest.scheduler import start_scheduler
from src.engine.signal_extractor import OpenAPISignalExtractor
from src.engine.rule_matcher import RuleMatcher
from src.engine.scorer import compute_health_score
from src.engine.reporter import build_report, render_text_report
from src.engine.ai_agent_universal import UniversalAIAgent, is_any_llm_available
from src.engine.agents.orchestrator import AgentOrchestrator

# NEW: Use centralized logger
logger = get_logger(__name__)

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SpecSentinel",
    description="Agentic AI API Health, Compliance & Governance Bot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# NEW: Add logging middleware
app.add_middleware(FastAPILoggingMiddleware)

# ── Shared state ──────────────────────────────────────────────────────────────
store: SpecSentinelVectorStore = None


@app.on_event("startup")
async def startup_event():
    global store
    logger.info("Initializing SpecSentinel Vector Store...")
    store = SpecSentinelVectorStore()
    store.initialize()

    stats = store.get_collection_stats()
    logger.info("Vector DB ready", extra={"extra_data": stats})

    start_scheduler(
        store,
        run_now=False,
        schedule="weekly",
        background=True,
    )
    logger.info("SpecSentinel ready")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "SpecSentinel",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "POST /analyze  (upload YAML/JSON spec)",
            "analyze_text": "POST /analyze/text  (send spec as JSON body)",
            "stats": "GET  /stats",
            "health": "GET  /health",
            "refresh": "POST /refresh  (trigger rule ingestion)",
        },
    }


@app.get("/health")
async def health_check():
    stats = store.get_collection_stats() if store else {}
    return {"status": "ok", "rule_counts": stats}


@app.get("/stats")
async def stats():
    """Return current vector DB rule counts per category."""
    if not store:
        raise HTTPException(503, "Store not initialized")
    return store.get_collection_stats()


@app.post("/analyze")
async def analyze_spec(file: UploadFile = File(...), format: str = "json"):
    """Upload an OpenAPI spec file and receive a Health Report."""
    if not store:
        raise HTTPException(503, "Vector store not initialized")

    content = await file.read()
    spec_name = file.filename or "uploaded_spec"

    try:
        spec = _parse_spec(content, spec_name)
    except ValueError as e:
        raise HTTPException(400, f"Could not parse spec: {e}")

    report = _run_pipeline(spec, spec_name)

    if format == "text":
        return PlainTextResponse(render_text_report(report))
    return JSONResponse(report)


# ── Pipeline ──────────────────────────────────────────────────────────────────

# NEW: Add performance logging decorator
@log_performance()
def _run_pipeline(spec: dict, spec_name: str) -> dict:
    """Core agentic pipeline with enhanced logging."""
    
    # NEW: Use pipeline logger
    pipeline = PipelineLogger()
    
    try:
        # PLAN stage
        pipeline.start_stage("PLAN", spec_name=spec_name)
        paths_count = len(spec.get('paths', {}))
        schemas_count = len(spec.get('components', {}).get('schemas', {}) or {})
        pipeline.end_stage("PLAN", paths=paths_count, schemas=schemas_count)

        # ANALYZE stage
        pipeline.start_stage("ANALYZE", spec_name=spec_name)
        extractor = OpenAPISignalExtractor(spec)
        signals = extractor.extract_all()
        pipeline.end_stage("ANALYZE", signals_count=len(signals))

        # MATCH stage
        pipeline.start_stage("MATCH", signals_count=len(signals))
        matcher = RuleMatcher(store, n_results_per_signal=3)
        findings = matcher.match_signals(signals)
        pipeline.end_stage("MATCH", findings_count=len(findings))

        # SCORE stage
        pipeline.start_stage("SCORE", findings_count=len(findings))
        health = compute_health_score(findings)
        pipeline.end_stage("SCORE", health_score=health.total, band=health.band)

        # REPORT stage
        pipeline.start_stage("REPORT", spec_name=spec_name)
        report = build_report(spec_name, health, findings)
        pipeline.end_stage("REPORT", findings_count=len(report['findings']))

        # MULTI-AGENT stage (if enabled)
        use_multi_agent = os.getenv("USE_MULTI_AGENT", "false").lower() == "true"
        
        if use_multi_agent:
            try:
                pipeline.start_stage("MULTI-AGENT", spec_name=spec_name)
                llm_client = UniversalAIAgent() if is_any_llm_available() else None
                orchestrator = AgentOrchestrator(llm_client=llm_client, max_workers=5)
                agent_result = orchestrator.analyze(spec, signals, findings, parallel=True)
                report['multi_agent_analysis'] = orchestrator.to_dict(agent_result)
                pipeline.end_stage(
                    "MULTI-AGENT",
                    agents_count=len(agent_result.agents_used),
                    risk=agent_result.overall_risk
                )
            except Exception as e:
                pipeline.stage_error("MULTI-AGENT", e)
                report['multi_agent_analysis'] = {
                    'error': 'Multi-agent analysis unavailable',
                    'message': str(e)
                }

        # AI-ENHANCE stage (if available)
        if is_any_llm_available():
            try:
                pipeline.start_stage("AI-ENHANCE", spec_name=spec_name)
                ai_agent = UniversalAIAgent()
                
                if ai_agent.is_available():
                    provider_info = ai_agent.get_provider_info()
                    ai_insights = ai_agent.analyze_findings(spec, report['findings'], report['health_score'])
                    report['ai_insights'] = {
                        'summary': ai_insights.summary,
                        'risk_assessment': {
                            'level': ai_insights.risk_level,
                            'score': ai_insights.risk_score,
                            'business_impact': ai_insights.business_impact
                        },
                        'priority_actions': ai_insights.priority_actions,
                        'estimated_fix_time': ai_insights.estimated_fix_time,
                        'provider': ai_insights.provider
                    }
                    
                    enhanced_count = 0
                    for finding in report['findings']:
                        if finding['severity'] in ['Critical', 'High'] and enhanced_count < 5:
                            finding['ai_explanation'] = ai_agent.explain_finding(finding)
                            finding['ai_suggested_fix'] = ai_agent.generate_fix_code(finding, spec)
                            enhanced_count += 1
                    
                    pipeline.end_stage(
                        "AI-ENHANCE",
                        provider=provider_info['provider'],
                        enhanced_count=enhanced_count
                    )
                else:
                    pipeline.end_stage("AI-ENHANCE", available=False)
                    report['ai_insights'] = {
                        'available': False,
                        'message': 'No LLM provider available'
                    }
                
            except Exception as e:
                pipeline.stage_error("AI-ENHANCE", e)
                report['ai_insights'] = {
                    'error': 'AI enhancement unavailable',
                    'message': str(e)
                }
        else:
            logger.info("AI-ENHANCE skipped (no API keys configured)")
            report['ai_insights'] = {
                'available': False,
                'message': 'Set API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY'
            }

        return report
        
    except Exception as e:
        logger.exception("Pipeline failed", extra={"extra_data": {"spec_name": spec_name}})
        raise


def _parse_spec(content: bytes, filename: str) -> dict:
    """Parse YAML or JSON spec content into a dict."""
    text = content.decode("utf-8", errors="replace")
    try:
        if filename.endswith(".json") or text.strip().startswith("{"):
            return json.loads(text)
        else:
            return yaml.safe_load(text)
    except Exception as e:
        raise ValueError(f"Invalid YAML/JSON: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

## Testing the Integration

### 1. Test Basic Logging

```python
from src.utils.logging_config import get_logger

logger = get_logger("test")
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 2. Test Structured Logging

```python
from src.utils.logging_config import StructuredLogger

logger = StructuredLogger("test")
logger.info("Test event", user_id=123, action="test", status="success")
```

### 3. Test Performance Logging

```python
from src.utils.logging_config import log_performance
import time

@log_performance()
def slow_function():
    time.sleep(1)
    return "done"

result = slow_function()
# Should log: [PERF] slow_function completed in 1.000s
```

### 4. Test JSON Logging

```bash
export JSON_LOGGING=true
python -c "from src.utils.logging_config import get_logger; logger = get_logger('test'); logger.info('Test')"
```

## Environment Configuration

Create a `.env` file in the project root:

```bash
# Logging Configuration
LOG_LEVEL=INFO
JSON_LOGGING=false
FILE_LOGGING=true

# Feature Flags
USE_MULTI_AGENT=true
```

## Rollout Strategy

1. **Phase 1**: Add middleware to API and frontend
2. **Phase 2**: Update core pipeline with PipelineLogger
3. **Phase 3**: Add performance logging to key functions
4. **Phase 4**: Update agents with AgentLogger
5. **Phase 5**: Enable JSON logging in production

## Monitoring

After integration, monitor logs:

```bash
# Watch all logs
tail -f logs/*.log

# Watch specific module
tail -f logs/specsentinel.api.log

# Search for errors
grep ERROR logs/specsentinel.log

# Count log levels
grep -c INFO logs/specsentinel.log
grep -c ERROR logs/specsentinel.log
```

## Summary

The new logging system provides:

✅ **Centralized configuration** - One place to configure all logging  
✅ **Structured logging** - Rich context with every log message  
✅ **Performance tracking** - Automatic timing of operations  
✅ **Request logging** - Complete HTTP request/response tracking  
✅ **Agent logging** - Specialized logging for AI agents  
✅ **Pipeline logging** - Stage-by-stage execution tracking  
✅ **Production ready** - JSON format for log aggregation  

For detailed usage, see [LOGGING.md](./LOGGING.md).