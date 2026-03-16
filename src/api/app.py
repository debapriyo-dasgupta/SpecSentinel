"""
specsentinel/api/app.py

FastAPI application for SpecSentinel.
Accepts an OpenAPI spec (YAML or JSON), runs the agentic analysis pipeline,
and returns a structured API Health Report.
"""

import json
import sys
import os
from pathlib import Path

import yaml

# Path setup for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

# NEW: Import centralized logging
from src.utils.logging_config import get_logger, PipelineLogger, log_performance
from src.utils.logging_middleware import FastAPILoggingMiddleware

from src.vectordb.store.chroma_client import SpecSentinelVectorStore
from src.vectordb.ingest.scheduler import start_scheduler
from src.engine.signal_extractor import OpenAPISignalExtractor
from src.engine.rule_matcher import RuleMatcher
from src.engine.scorer import compute_health_score
from src.engine.reporter import build_report, render_text_report
from src.engine.ai_agent_universal import UniversalAIAgent, is_any_llm_available, get_available_providers
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
from typing import Optional
store: Optional[SpecSentinelVectorStore] = None

# Constants
MAX_AI_ENHANCED_FINDINGS = 5


@app.on_event("startup")
async def startup_event():
    global store
    logger.info("=" * 70)
    logger.info("SpecSentinel Backend Starting...")
    logger.info("=" * 70)
    
    # Check multi-agent mode
    use_multi_agent = os.getenv("USE_MULTI_AGENT", "false").lower() == "true"
    logger.info(f"Multi-Agent Mode: {'ENABLED' if use_multi_agent else 'DISABLED'}")
    
    # Check LLM availability
    available_providers = get_available_providers()
    if available_providers:
        logger.info(f"Available LLM Providers: {', '.join(available_providers)}")
    else:
        logger.warning("No LLM providers configured - AI analysis will be limited")
    
    logger.info("Initializing SpecSentinel Vector Store...")
    store = SpecSentinelVectorStore()
    store.initialize()   # Seeds from local JSON if collections are empty

    stats = store.get_collection_stats()
    logger.info(f"Vector DB Collections Ready:")
    for category, count in stats.items():
        logger.info(f"  - {category}: {count} rules")

    # Start background ingestion scheduler (weekly refresh from external sources)
    logger.info("Starting background ingestion scheduler...")
    start_scheduler(
        store,
        run_now=False,     # Set True to ingest from web on startup
        schedule="weekly",
        background=True,
    )
    
    logger.info("=" * 70)
    logger.info("SpecSentinel Backend Ready!")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("=" * 70)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service": "SpecSentinel",
        "version": "1.0.0",
        "status":  "running",
        "endpoints": {
            "analyze":     "POST /analyze  (upload YAML/JSON spec)",
            "analyze_text":"POST /analyze/text  (send spec as JSON body)",
            "stats":       "GET  /stats",
            "health":      "GET  /health",
            "refresh":     "POST /refresh  (trigger rule ingestion)",
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
    """
    Upload an OpenAPI spec file (YAML or JSON) and receive a Health Report.

    Query params:
        format: 'json' (default) or 'text'
    """
    if not store:
        raise HTTPException(503, "Vector store not initialized")

    content = await file.read()
    spec_name = file.filename or "uploaded_spec"

    try:
        spec = _parse_spec(content, spec_name)
    except ValueError as e:
        raise HTTPException(400, f"Could not parse spec: {e}")

    # Run pipeline in thread pool to avoid blocking event loop
    report = await run_in_threadpool(_run_pipeline, spec, spec_name)

    if format == "text":
        return PlainTextResponse(render_text_report(report))
    return JSONResponse(report)


@app.post("/analyze/stream")
async def analyze_spec_stream(file: UploadFile = File(...)):
    """
    Upload an OpenAPI spec file and receive real-time pipeline progress via Server-Sent Events.
    
    Returns:
        StreamingResponse with text/event-stream content type
        Each event contains JSON data about pipeline stage progress
    """
    if not store:
        raise HTTPException(503, "Vector store not initialized")

    content = await file.read()
    spec_name = file.filename or "uploaded_spec"

    try:
        spec = _parse_spec(content, spec_name)
    except ValueError as e:
        raise HTTPException(400, f"Could not parse spec: {e}")

    async def event_generator():
        """Generate Server-Sent Events for pipeline progress"""
        import json
        import time
        
        # NEW: Create pipeline logger for streaming endpoint
        pipeline = PipelineLogger()
        
        try:
            # PLAN stage
            pipeline.start_stage("PLAN", spec_name=spec_name)
            yield f"data: {json.dumps({'stage': 'PLAN', 'status': 'started', 'message': 'Planning analysis...'})}\n\n"
            
            start_time = time.time()
            paths_count = len(spec.get('paths', {}))
            schemas_count = len(spec.get('components', {}).get('schemas', {}) or {})
            duration = time.time() - start_time
            
            pipeline.end_stage("PLAN", paths=paths_count, schemas=schemas_count)
            yield f"data: {json.dumps({'stage': 'PLAN', 'status': 'completed', 'duration': round(duration, 3), 'paths': paths_count, 'schemas': schemas_count})}\n\n"
            
            # ANALYZE stage
            pipeline.start_stage("ANALYZE", spec_name=spec_name)
            yield f"data: {json.dumps({'stage': 'ANALYZE', 'status': 'started', 'message': 'Extracting signals from spec...'})}\n\n"
            
            start_time = time.time()
            extractor = OpenAPISignalExtractor(spec)
            signals = extractor.extract_all()
            duration = time.time() - start_time
            
            pipeline.end_stage("ANALYZE", signals_count=len(signals))
            yield f"data: {json.dumps({'stage': 'ANALYZE', 'status': 'completed', 'duration': round(duration, 3), 'signals_count': len(signals)})}\n\n"
            
            # MATCH stage
            pipeline.start_stage("MATCH", signals_count=len(signals))
            yield f"data: {json.dumps({'stage': 'MATCH', 'status': 'started', 'message': 'Matching rules from vector database...'})}\n\n"
            
            start_time = time.time()
            matcher = RuleMatcher(store, n_results_per_signal=3)
            findings = matcher.match_signals(signals)
            duration = time.time() - start_time
            
            pipeline.end_stage("MATCH", findings_count=len(findings))
            yield f"data: {json.dumps({'stage': 'MATCH', 'status': 'completed', 'duration': round(duration, 3), 'findings_count': len(findings)})}\n\n"
            
            # SCORE stage
            pipeline.start_stage("SCORE", findings_count=len(findings))
            yield f"data: {json.dumps({'stage': 'SCORE', 'status': 'started', 'message': 'Computing health score...'})}\n\n"
            
            start_time = time.time()
            health = compute_health_score(findings)
            duration = time.time() - start_time
            
            pipeline.end_stage("SCORE", health_score=health.total, band=health.band)
            yield f"data: {json.dumps({'stage': 'SCORE', 'status': 'completed', 'duration': round(duration, 3), 'health_score': health.total, 'band': health.band})}\n\n"
            
            # REPORT stage
            pipeline.start_stage("REPORT", spec_name=spec_name)
            yield f"data: {json.dumps({'stage': 'REPORT', 'status': 'started', 'message': 'Generating report...'})}\n\n"
            
            start_time = time.time()
            report = build_report(spec_name, health, findings)
            duration = time.time() - start_time
            
            pipeline.end_stage("REPORT", findings_count=len(report['findings']))
            yield f"data: {json.dumps({'stage': 'REPORT', 'status': 'completed', 'duration': round(duration, 3)})}\n\n"
            
            # MULTI-AGENT: Run specialized agents in parallel (enabled by default)
            use_multi_agent = os.getenv("USE_MULTI_AGENT", "true").lower() == "true"
            
            if use_multi_agent:
                try:
                    pipeline.start_stage("MULTI-AGENT", spec_name=spec_name)
                    yield f"data: {json.dumps({'stage': 'MULTI-AGENT', 'status': 'started', 'message': 'Running specialized agents...'})}\n\n"
                    
                    start_time = time.time()
                    
                    # Initialize LLM client if available
                    llm_client = UniversalAIAgent() if is_any_llm_available() else None
                    
                    # Run orchestrated multi-agent analysis
                    orchestrator = AgentOrchestrator(llm_client=llm_client, max_workers=5)
                    agent_result = orchestrator.analyze(spec, signals, findings, parallel=True)
                    
                    # Add multi-agent insights to report
                    report['multi_agent_analysis'] = orchestrator.to_dict(agent_result)
                    
                    duration = time.time() - start_time
                    pipeline.end_stage(
                        "MULTI-AGENT",
                        agents_count=len(agent_result.agents_used),
                        execution_time=agent_result.execution_time,
                        risk=agent_result.overall_risk
                    )
                    yield f"data: {json.dumps({'stage': 'MULTI-AGENT', 'status': 'completed', 'duration': round(duration, 3), 'agents': len(agent_result.agents_used), 'risk': agent_result.overall_risk})}\n\n"
                    
                except Exception as e:
                    pipeline.stage_error("MULTI-AGENT", e)
                    logger.exception("Multi-agent analysis failed in streaming endpoint")
                    report['multi_agent_analysis'] = {
                        'error': 'Multi-agent analysis unavailable',
                        'message': str(e)
                    }
                    yield f"data: {json.dumps({'stage': 'MULTI-AGENT', 'status': 'error', 'message': str(e)})}\n\n"
            
            # AI Enhancement (if available)
            if is_any_llm_available():
                pipeline.start_stage("AI-ENHANCE", spec_name=spec_name)
                yield f"data: {json.dumps({'stage': 'AI-ENHANCE', 'status': 'started', 'message': 'Enhancing with AI insights...'})}\n\n"
                
                try:
                    start_time = time.time()
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
                        
                        # Add AI explanations and fix code to top findings in parallel
                        from concurrent.futures import ThreadPoolExecutor, as_completed
                        
                        critical_high_findings = [
                            f for f in report['findings']
                            if f['severity'] in ['Critical', 'High']
                        ][:MAX_AI_ENHANCED_FINDINGS]
                        
                        enhanced_count = 0
                        if critical_high_findings:
                            with ThreadPoolExecutor(max_workers=3) as executor:
                                # Submit all enhancement tasks
                                future_to_finding = {
                                    executor.submit(
                                        lambda f: (
                                            ai_agent.explain_finding(f),
                                            ai_agent.generate_fix_code(f, spec)
                                        ),
                                        finding
                                    ): finding
                                    for finding in critical_high_findings
                                }
                                
                                # Collect results as they complete
                                for future in as_completed(future_to_finding):
                                    finding = future_to_finding[future]
                                    try:
                                        explanation, fix_code = future.result()
                                        finding['ai_explanation'] = explanation
                                        finding['ai_suggested_fix'] = fix_code
                                        enhanced_count += 1
                                    except Exception as e:
                                        logger.warning(f"Failed to enhance finding: {e}")
                        
                        duration = time.time() - start_time
                        pipeline.end_stage("AI-ENHANCE", provider=provider_info['provider'], model=provider_info['model'], enhanced_count=enhanced_count)
                        yield f"data: {json.dumps({'stage': 'AI-ENHANCE', 'status': 'completed', 'duration': round(duration, 3), 'provider': provider_info['provider']})}\n\n"
                    else:
                        pipeline.end_stage("AI-ENHANCE", available=False)
                        report['ai_insights'] = {'available': False, 'message': 'No LLM provider available'}
                        yield f"data: {json.dumps({'stage': 'AI-ENHANCE', 'status': 'skipped', 'message': 'No LLM provider available'})}\n\n"
                        
                except Exception as e:
                    pipeline.stage_error("AI-ENHANCE", e)
                    logger.warning(f"AI enhancement failed: {e}")
                    report['ai_insights'] = {'error': 'AI enhancement unavailable', 'message': str(e)}
                    yield f"data: {json.dumps({'stage': 'AI-ENHANCE', 'status': 'error', 'message': str(e)})}\n\n"
            
            # Final result
            yield f"data: {json.dumps({'stage': 'COMPLETE', 'status': 'completed', 'result': report})}\n\n"
            
        except Exception as e:
            logger.exception("Pipeline streaming failed")
            yield f"data: {json.dumps({'stage': 'ERROR', 'status': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/analyze/text")
async def analyze_spec_text(body: dict, format: str = "json"):
    """
    Send an OpenAPI spec as a JSON body: {"spec": {...}, "name": "myapi"}
    """
    if not store:
        raise HTTPException(503, "Vector store not initialized")

    spec = body.get("spec")
    if not spec:
        raise HTTPException(400, "Request body must include 'spec' key with OpenAPI dict")

    spec_name = body.get("name", "inline_spec")

    if isinstance(spec, str):
        try:
            spec = _parse_spec(spec.encode(), spec_name)
        except ValueError as e:
            raise HTTPException(400, str(e))

    # Run pipeline in thread pool to avoid blocking event loop
    report = await run_in_threadpool(_run_pipeline, spec, spec_name)

    if format == "text":
        return PlainTextResponse(render_text_report(report))
    return JSONResponse(report)


@app.post("/refresh")
async def trigger_refresh(background_tasks: BackgroundTasks):
    """Manually trigger a rule ingestion refresh from external sources."""
    if not store:
        raise HTTPException(503, "Store not initialized")

    from src.vectordb.ingest.scheduler import run_ingestion_job
    background_tasks.add_task(run_ingestion_job, store)
    return {"status": "ingestion_started", "message": "Rule refresh running in background"}


# ── Pipeline ──────────────────────────────────────────────────────────────────

@log_performance()
def _run_pipeline(spec: dict, spec_name: str) -> dict:
    """
    Core agentic pipeline with enhanced logging:
    PLAN → ANALYZE (extract signals) → MATCH (vector DB) → SCORE → REPORT → AI-ENHANCE
    """
    # NEW: Use pipeline logger for stage tracking
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

        # MULTI-AGENT: Run specialized agents in parallel (enabled by default)
        use_multi_agent = os.getenv("USE_MULTI_AGENT", "true").lower() == "true"
        
        if use_multi_agent:
            try:
                pipeline.start_stage("MULTI-AGENT", spec_name=spec_name)
                
                # Initialize LLM client if available
                llm_client = UniversalAIAgent() if is_any_llm_available() else None
                
                # Run orchestrated multi-agent analysis
                orchestrator = AgentOrchestrator(llm_client=llm_client, max_workers=5)
                agent_result = orchestrator.analyze(spec, signals, findings, parallel=True)
                
                # Add multi-agent insights to report
                report['multi_agent_analysis'] = orchestrator.to_dict(agent_result)
                
                pipeline.end_stage(
                    "MULTI-AGENT",
                    agents_count=len(agent_result.agents_used),
                    execution_time=agent_result.execution_time,
                    risk=agent_result.overall_risk
                )
                
            except Exception as e:
                pipeline.stage_error("MULTI-AGENT", e)
                report['multi_agent_analysis'] = {
                    'error': 'Multi-agent analysis unavailable',
                    'message': str(e)
                }
        
        # AI-ENHANCE: Add AI-powered insights (if available)
        if is_any_llm_available():
            try:
                pipeline.start_stage("AI-ENHANCE", spec_name=spec_name)
                ai_agent = UniversalAIAgent()
                
                if ai_agent.is_available():
                    provider_info = ai_agent.get_provider_info()
                    
                    # Generate overall AI insights
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
                    
                    # Add AI explanations and fix code to top findings in parallel
                    from concurrent.futures import ThreadPoolExecutor, as_completed
                    
                    critical_high_findings = [
                        f for f in report['findings']
                        if f['severity'] in ['Critical', 'High']
                    ][:MAX_AI_ENHANCED_FINDINGS]
                    
                    enhanced_count = 0
                    if critical_high_findings:
                        with ThreadPoolExecutor(max_workers=3) as executor:
                            # Submit all enhancement tasks
                            future_to_finding = {
                                executor.submit(
                                    lambda f: (
                                        ai_agent.explain_finding(f),
                                        ai_agent.generate_fix_code(f, spec)
                                    ),
                                    finding
                                ): finding
                                for finding in critical_high_findings
                            }
                            
                            # Collect results as they complete
                            for future in as_completed(future_to_finding):
                                finding = future_to_finding[future]
                                try:
                                    explanation, fix_code = future.result()
                                    finding['ai_explanation'] = explanation
                                    finding['ai_suggested_fix'] = fix_code
                                    enhanced_count += 1
                                except Exception as e:
                                    logger.warning(f"Failed to enhance finding: {e}")
                    
                    pipeline.end_stage(
                        "AI-ENHANCE",
                        provider=provider_info['provider'],
                        model=provider_info['model'],
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
                'message': 'Set one of these API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY',
                'supported_providers': ['openai', 'anthropic', 'google'],
                'available_providers': get_available_providers()
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


# ── CLI runner ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
