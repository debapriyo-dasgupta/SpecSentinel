# Multi-Agent System Logging Guide 🤖

## Overview

The multi-agent system is **ENABLED BY DEFAULT** ✅. It runs 5 specialized agents in parallel to provide comprehensive, deeper analysis of your OpenAPI specifications.

## Multi-Agent is Now Active!

🎉 **No configuration needed!** The multi-agent system runs automatically when you analyze specs.

### How to Disable (if needed)

If you want to disable multi-agent for faster analysis:

```powershell
# Disable multi-agent
$env:USE_MULTI_AGENT="false"

# Then restart backend
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

## Multi-Agent Logs You'll See

When multi-agent is **ENABLED**, you'll see these additional logs:

### 1. Orchestrator Initialization
```
[INFO] [src.engine.agents.orchestrator] Orchestrator initialized with 5 agents
```

### 2. Individual Agent Initialization
```
[INFO] [src.engine.agents.base_agent] Initialized SecurityAgent for security analysis
[INFO] [src.engine.agents.base_agent] Initialized DesignAgent for design analysis
[INFO] [src.engine.agents.base_agent] Initialized ErrorHandlingAgent for error_handling analysis
[INFO] [src.engine.agents.base_agent] Initialized DocumentationAgent for documentation analysis
[INFO] [src.engine.agents.base_agent] Initialized GovernanceAgent for governance analysis
```

### 3. Pipeline Stage: MULTI-AGENT
```
[INFO] [specsentinel.pipeline] [MULTI-AGENT] Starting...
```

### 4. Orchestration Start
```
[INFO] [src.engine.agents.orchestrator] Starting parallel agent analysis...
```

### 5. Individual Agent Completion (in parallel)
```
[INFO] [src.engine.agents.orchestrator] SecurityAgent completed: 3 findings
[INFO] [src.engine.agents.orchestrator] DesignAgent completed: 5 findings
[INFO] [src.engine.agents.orchestrator] ErrorHandlingAgent completed: 2 findings
[INFO] [src.engine.agents.orchestrator] DocumentationAgent completed: 1 findings
[INFO] [src.engine.agents.orchestrator] GovernanceAgent completed: 0 findings
```

### 6. Orchestration Complete
```
[INFO] [src.engine.agents.orchestrator] Orchestration complete: 5 agents, 2.34s, risk=HIGH
```

### 7. Pipeline Stage Complete
```
[INFO] [specsentinel.pipeline] [MULTI-AGENT] Completed in 2.340s
```

## Complete Pipeline Flow with Multi-Agent

When multi-agent is enabled, your complete pipeline logs will look like:

```
2026-03-14 11:53:32 [INFO] [specsentinel.pipeline] [PLAN] Starting...
2026-03-14 11:53:32 [INFO] [specsentinel.pipeline] [PLAN] Completed in 0.000s
2026-03-14 11:53:32 [INFO] [specsentinel.pipeline] [ANALYZE] Starting...
2026-03-14 11:53:32 [INFO] [specsentinel.pipeline] [ANALYZE] Completed in 0.001s
2026-03-14 11:53:32 [INFO] [specsentinel.pipeline] [MATCH] Starting...
2026-03-14 11:53:40 [INFO] [specsentinel.pipeline] [MATCH] Completed in 8.315s
2026-03-14 11:53:40 [INFO] [specsentinel.pipeline] [SCORE] Starting...
2026-03-14 11:53:40 [INFO] [specsentinel.pipeline] [SCORE] Completed in 0.000s
2026-03-14 11:53:40 [INFO] [specsentinel.pipeline] [REPORT] Starting...
2026-03-14 11:53:40 [INFO] [specsentinel.pipeline] [REPORT] Completed in 0.000s

🤖 MULTI-AGENT SECTION (only when USE_MULTI_AGENT=true):
2026-03-14 11:53:40 [INFO] [specsentinel.pipeline] [MULTI-AGENT] Starting...
2026-03-14 11:53:40 [INFO] [src.engine.agents.orchestrator] Starting parallel agent analysis...
2026-03-14 11:53:41 [INFO] [src.engine.agents.orchestrator] SecurityAgent completed: 3 findings
2026-03-14 11:53:41 [INFO] [src.engine.agents.orchestrator] DesignAgent completed: 5 findings
2026-03-14 11:53:42 [INFO] [src.engine.agents.orchestrator] ErrorHandlingAgent completed: 2 findings
2026-03-14 11:53:42 [INFO] [src.engine.agents.orchestrator] DocumentationAgent completed: 1 findings
2026-03-14 11:53:42 [INFO] [src.engine.agents.orchestrator] GovernanceAgent completed: 0 findings
2026-03-14 11:53:42 [INFO] [src.engine.agents.orchestrator] Orchestration complete: 5 agents, 2.34s, risk=HIGH
2026-03-14 11:53:42 [INFO] [specsentinel.pipeline] [MULTI-AGENT] Completed in 2.340s

2026-03-14 11:53:42 [INFO] [specsentinel.pipeline] [AI-ENHANCE] Starting...
2026-03-14 11:53:45 [INFO] [specsentinel.pipeline] [AI-ENHANCE] Completed in 3.120s
```

## Log Files

Multi-agent logs are written to:
- **Console**: Real-time output in terminal
- **Files**:
  - `logs/src.engine.agents.orchestrator.log` - Orchestrator logs
  - `logs/src.engine.agents.base_agent.log` - Individual agent logs
  - `logs/specsentinel.pipeline.log` - Pipeline stage logs

## Checking Multi-Agent Status

### Check if Multi-Agent is Enabled
```powershell
# Check environment variable
echo $env:USE_MULTI_AGENT
```

### View Multi-Agent Logs
```powershell
# View orchestrator logs
Get-Content logs\src.engine.agents.orchestrator.log -Tail 50

# View base agent logs
Get-Content logs\src.engine.agents.base_agent.log -Tail 50

# View pipeline logs (includes MULTI-AGENT stage)
Get-Content logs\specsentinel.pipeline.log -Tail 50
```

## Key Differences: With vs Without Multi-Agent

### WITHOUT Multi-Agent (Default)
```
[PLAN] → [ANALYZE] → [MATCH] → [SCORE] → [REPORT] → [AI-ENHANCE]
```

### WITH Multi-Agent (USE_MULTI_AGENT=true)
```
[PLAN] → [ANALYZE] → [MATCH] → [SCORE] → [REPORT] → [MULTI-AGENT] → [AI-ENHANCE]
                                                           ↓
                                        5 Specialized Agents in Parallel:
                                        • SecurityAgent
                                        • DesignAgent
                                        • ErrorHandlingAgent
                                        • DocumentationAgent
                                        • GovernanceAgent
```

## API Response Differences

When multi-agent is enabled, the API response includes an additional section:

```json
{
  "health_score": {...},
  "findings": [...],
  "multi_agent_analysis": {
    "summary": "Multi-Agent Analysis Complete (HIGH Risk)\nTotal Findings: 11\n...",
    "overall_risk": "HIGH",
    "execution_time": 2.34,
    "parallel_execution": true,
    "agents_used": ["SecurityAgent", "DesignAgent", "ErrorHandlingAgent", "DocumentationAgent", "GovernanceAgent"],
    "top_recommendations": [
      "[security] Implement OAuth 2.0 authentication",
      "[design] Add pagination to list endpoints",
      ...
    ],
    "agent_analyses": [
      {
        "category": "security",
        "agent": "SecurityAgent",
        "findings_count": 3,
        "risk_level": "HIGH",
        "confidence": 0.85,
        "summary": "...",
        "recommendations": [...]
      },
      ...
    ]
  },
  "ai_insights": {...}
}
```

## Testing Multi-Agent System

### Step 1: Restart Backend (Multi-Agent is Already Enabled!)
```powershell
python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Upload a File
Upload an OpenAPI spec via the frontend at http://localhost:5000

### Step 3: Watch Console Logs
Look for the **[MULTI-AGENT]** stage and individual agent completion logs - they should appear automatically!

### Step 4: Check Log Files
```powershell
# Should show orchestrator activity
Get-Content logs\src.engine.agents.orchestrator.log -Tail 20
```

## Troubleshooting

### Multi-Agent Not Running?

1. **Check environment variable** (should be empty or "true"):
   ```powershell
   echo $env:USE_MULTI_AGENT
   # Empty or "true" = ENABLED (default)
   # "false" = DISABLED
   ```

2. **Restart backend** to apply changes

3. **Check logs** for the [MULTI-AGENT] stage:
   ```powershell
   Get-Content logs\specsentinel.pipeline.log | Select-String "MULTI-AGENT"
   ```

4. **Verify in API response**: The response should include `multi_agent_analysis` section

### Performance Impact

Multi-agent analysis adds ~2-5 seconds to the pipeline:
- **Without multi-agent**: ~8-10 seconds total
- **With multi-agent**: ~10-15 seconds total

The agents run in **parallel**, so the overhead is minimal compared to running them sequentially.

---

**Made with Bob** 🤖