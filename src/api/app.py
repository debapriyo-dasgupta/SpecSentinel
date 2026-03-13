"""
specsentinel/api/app.py

FastAPI application for SpecSentinel.
Accepts an OpenAPI spec (YAML or JSON), runs the agentic analysis pipeline,
and returns a structured API Health Report.
"""

import json
import logging
import sys
import os
from pathlib import Path

import yaml

# Path setup for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from src.vectordb.store.chroma_client import SpecSentinelVectorStore
from src.vectordb.ingest.scheduler import start_scheduler
from src.engine.signal_extractor import OpenAPISignalExtractor
from src.engine.rule_matcher import RuleMatcher
from src.engine.scorer import compute_health_score
from src.engine.reporter import build_report, render_text_report
from src.engine.ai_agent_universal import UniversalAIAgent, is_any_llm_available, get_available_providers
from src.engine.agents.orchestrator import AgentOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

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

# ── Shared state ──────────────────────────────────────────────────────────────
store: SpecSentinelVectorStore = None


@app.on_event("startup")
async def startup_event():
    global store
    logger.info("Initializing SpecSentinel Vector Store...")
    store = SpecSentinelVectorStore()
    store.initialize()   # Seeds from local JSON if collections are empty

    stats = store.get_collection_stats()
    logger.info(f"Vector DB ready: {stats}")

    # Start background ingestion scheduler (weekly refresh from external sources)
    start_scheduler(
        store,
        run_now=False,     # Set True to ingest from web on startup
        schedule="weekly",
        background=True,
    )
    logger.info("SpecSentinel ready.")


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

    report = _run_pipeline(spec, spec_name)

    if format == "text":
        return PlainTextResponse(render_text_report(report))
    return JSONResponse(report)


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

    report = _run_pipeline(spec, spec_name)

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

def _run_pipeline(spec: dict, spec_name: str) -> dict:
    """
    Core agentic pipeline:
    PLAN → ANALYZE (extract signals) → MATCH (vector DB) → SCORE → REPORT → AI-ENHANCE
    """
    try:
        logger.info(f"[PLAN] Analyzing spec: {spec_name}")
        logger.info(f"[PLAN] Paths: {len(spec.get('paths', {}))}, "
                    f"Schemas: {len(spec.get('components', {}).get('schemas', {}) or {})}")

        # ANALYZE: extract signals
        extractor = OpenAPISignalExtractor(spec)
        signals   = extractor.extract_all()
        logger.info(f"[ANALYZE] Extracted {len(signals)} signals")

        # MATCH: query vector DB
        matcher  = RuleMatcher(store, n_results_per_signal=3)
        findings = matcher.match_signals(signals)
        logger.info(f"[MATCH] Matched {len(findings)} finding groups")

        # SCORE: compute health score
        health = compute_health_score(findings)
        logger.info(f"[SCORE] Health: {health.total}/100 ({health.band})")

        # REPORT
        report = build_report(spec_name, health, findings)
        logger.info(f"[REPORT] Generated report with {len(report['findings'])} findings")

        # MULTI-AGENT: Run specialized agents in parallel (optional)
        use_multi_agent = os.getenv("USE_MULTI_AGENT", "false").lower() == "true"
        
        if use_multi_agent:
            try:
                logger.info("[MULTI-AGENT] Running specialized agents in parallel...")
                
                # Initialize LLM client if available
                llm_client = UniversalAIAgent() if is_any_llm_available() else None
                
                # Run orchestrated multi-agent analysis
                orchestrator = AgentOrchestrator(llm_client=llm_client, max_workers=5)
                agent_result = orchestrator.analyze(spec, signals, findings, parallel=True)
                
                # Add multi-agent insights to report
                report['multi_agent_analysis'] = orchestrator.to_dict(agent_result)
                
                logger.info(
                    f"[MULTI-AGENT] Complete: {len(agent_result.agents_used)} agents, "
                    f"{agent_result.execution_time:.2f}s, risk={agent_result.overall_risk}"
                )
                
            except Exception as e:
                logger.warning(f"[MULTI-AGENT] Failed: {e}")
                report['multi_agent_analysis'] = {
                    'error': 'Multi-agent analysis unavailable',
                    'message': str(e)
                }
        
        # AI-ENHANCE: Add AI-powered insights (if available)
        if is_any_llm_available():
            try:
                logger.info("[AI-AGENT] Enhancing report with AI insights...")
                ai_agent = UniversalAIAgent()
                
                if ai_agent.is_available():
                    provider_info = ai_agent.get_provider_info()
                    logger.info(f"[AI-AGENT] Using {provider_info['provider']} ({provider_info['model']})")
                    
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
                    
                    # Add AI explanations and fix code to top 5 critical/high findings
                    enhanced_count = 0
                    for finding in report['findings']:
                        if finding['severity'] in ['Critical', 'High'] and enhanced_count < 5:
                            finding['ai_explanation'] = ai_agent.explain_finding(finding)
                            finding['ai_suggested_fix'] = ai_agent.generate_fix_code(finding, spec)
                            enhanced_count += 1
                    
                    logger.info(f"[AI-AGENT] Enhanced {enhanced_count} findings with {provider_info['provider']}")
                else:
                    logger.info("[AI-AGENT] No LLM provider available")
                    report['ai_insights'] = {
                        'available': False,
                        'message': 'No LLM API keys configured'
                    }
                
            except Exception as e:
                logger.warning(f"[AI-AGENT] Failed to enhance report: {e}")
                report['ai_insights'] = {
                    'error': 'AI enhancement unavailable',
                    'message': str(e)
                }
        else:
            available_providers = get_available_providers()
            logger.info(f"[AI-AGENT] Skipped (no API keys configured)")
            report['ai_insights'] = {
                'available': False,
                'message': 'Set one of these API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY',
                'supported_providers': ['openai', 'anthropic', 'google'],
                'available_providers': available_providers
            }

        return report
    except Exception as e:
        logger.error(f"[ERROR] Pipeline failed: {str(e)}", exc_info=True)
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
