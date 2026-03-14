# 🚀 Restart Guide - Multi-Agent Now Enabled by Default!

## What Changed?

✅ **Multi-agent system is now ENABLED BY DEFAULT**
✅ **Pipeline logs now appear in console**
✅ **All 5 specialized agents run automatically**

## Quick Restart

Just restart your backend server:

```powershell
# Stop current backend (Ctrl+C)

# Start backend
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

## What You'll See Now

When you upload an OpenAPI spec, you'll see these logs in your console:

### 1. Standard Pipeline Stages
```
[INFO] [specsentinel.pipeline] [PLAN] Starting...
[INFO] [specsentinel.pipeline] [PLAN] Completed in 0.000s
[INFO] [specsentinel.pipeline] [ANALYZE] Starting...
[INFO] [specsentinel.pipeline] [ANALYZE] Completed in 0.001s
[INFO] [specsentinel.pipeline] [MATCH] Starting...
[INFO] [specsentinel.pipeline] [MATCH] Completed in 8.315s
[INFO] [specsentinel.pipeline] [SCORE] Starting...
[INFO] [specsentinel.pipeline] [SCORE] Completed in 0.000s
[INFO] [specsentinel.pipeline] [REPORT] Starting...
[INFO] [specsentinel.pipeline] [REPORT] Completed in 0.000s
```

### 2. 🤖 Multi-Agent Stage (NEW - Now Automatic!)
```
[INFO] [specsentinel.pipeline] [MULTI-AGENT] Starting...
[INFO] [src.engine.agents.orchestrator] Starting parallel agent analysis...
[INFO] [src.engine.agents.orchestrator] SecurityAgent completed: 3 findings
[INFO] [src.engine.agents.orchestrator] DesignAgent completed: 5 findings
[INFO] [src.engine.agents.orchestrator] ErrorHandlingAgent completed: 2 findings
[INFO] [src.engine.agents.orchestrator] DocumentationAgent completed: 1 findings
[INFO] [src.engine.agents.orchestrator] GovernanceAgent completed: 0 findings
[INFO] [src.engine.agents.orchestrator] Orchestration complete: 5 agents, 2.34s, risk=HIGH
[INFO] [specsentinel.pipeline] [MULTI-AGENT] Completed in 2.340s
```

### 3. AI Enhancement (if API keys configured)
```
[INFO] [specsentinel.pipeline] [AI-ENHANCE] Starting...
[INFO] [specsentinel.pipeline] [AI-ENHANCE] Completed in 3.120s
```

## The 5 Specialized Agents

Your API specs are now analyzed by:

1. **SecurityAgent** - Authentication, authorization, encryption
2. **DesignAgent** - REST best practices, resource design
3. **ErrorHandlingAgent** - Error responses, status codes
4. **DocumentationAgent** - API documentation quality
5. **GovernanceAgent** - Compliance, standards adherence

All running **in parallel** for maximum speed!

## API Response Enhancement

Your API responses now include a new `multi_agent_analysis` section:

```json
{
  "health_score": {...},
  "findings": [...],
  "multi_agent_analysis": {
    "summary": "Multi-Agent Analysis Complete (HIGH Risk)...",
    "overall_risk": "HIGH",
    "execution_time": 2.34,
    "agents_used": ["SecurityAgent", "DesignAgent", ...],
    "top_recommendations": [...],
    "agent_analyses": [...]
  },
  "ai_insights": {...}
}
```

## Performance

- **Standard pipeline**: ~8-10 seconds
- **With multi-agent**: ~10-15 seconds (only +2-5 seconds!)
- Agents run in **parallel**, so minimal overhead

## To Disable (if needed)

If you want faster analysis without multi-agent:

```powershell
$env:USE_MULTI_AGENT="false"
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

## Verify It's Working

1. **Console logs**: Look for `[MULTI-AGENT]` stage
2. **Log files**: Check `logs\src.engine.agents.orchestrator.log`
3. **API response**: Should include `multi_agent_analysis` section

## Files Modified

- `src/api/app.py` - Changed default from `false` to `true`
- `src/engine/agents/orchestrator.py` - Added centralized logging
- `src/engine/agents/base_agent.py` - Added centralized logging

## Documentation

- `PIPELINE_LOGS_FIXED.md` - General pipeline logging guide
- `MULTI_AGENT_LOGGING_GUIDE.md` - Complete multi-agent guide
- `RESTART_WITH_MULTI_AGENT.md` - This file!

---

**Ready to test?** Just restart your backend and upload a file! 🚀

**Made with Bob** 🤖