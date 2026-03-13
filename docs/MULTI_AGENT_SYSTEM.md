# Multi-Agent System Guide 🤖

## Overview

SpecSentinel's Multi-Agent System uses **5 specialized AI agents** that work in parallel to analyze different aspects of your API specification. Each agent is an expert in its domain, providing deep, focused analysis.

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenAPI Specification                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Orchestrator (Coordinator)                │
│  • Manages 5 specialized agents                              │
│  • Runs agents in parallel (ThreadPoolExecutor)              │
│  • Aggregates results                                         │
│  • Resolves conflicts                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Security   │  │   Design    │  │    Error    │
│   Agent     │  │   Agent     │  │  Handling   │
│             │  │             │  │   Agent     │
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐
│Documentation│  │ Governance  │
│   Agent     │  │   Agent     │
└─────────────┘  └─────────────┘
         │               │
         └───────┬───────┘
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Aggregated Multi-Agent Report                   │
│  • Per-agent analysis                                         │
│  • Overall risk assessment                                    │
│  • Unified recommendations                                    │
│  • Execution metrics                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🤖 Specialized Agents

### 1. Security Agent 🔒
**Focus**: Authentication, Authorization, Data Protection

**Analyzes**:
- Authentication schemes (OAuth2, JWT, API Keys)
- Authorization patterns
- Sensitive data exposure
- Security headers
- Rate limiting
- HTTPS enforcement
- OWASP API Security Top 10

**Example Findings**:
- Missing authentication on endpoints
- No global security requirements
- Missing 401/403 responses
- Hardcoded credentials

---

### 2. Design Agent 🎨
**Focus**: RESTful Principles, API Usability

**Analyzes**:
- RESTful naming conventions
- HTTP method usage
- Resource modeling
- API versioning
- Pagination patterns
- Filtering and sorting
- URL structure

**Example Findings**:
- Verbs in URL paths
- Missing API versioning
- Inconsistent naming
- Missing operationId

---

### 3. Error Handling Agent ⚠️
**Focus**: Error Responses, Status Codes

**Analyzes**:
- Error response schemas
- HTTP status codes
- RFC 7807 Problem Details compliance
- Consistent error format
- Error messages
- Exception handling

**Example Findings**:
- No standardized error schema
- Missing error responses (400, 404, 500)
- Inconsistent error format
- Missing RFC 7807 fields

---

### 4. Documentation Agent 📚
**Focus**: Developer Experience, API Clarity

**Analyzes**:
- Endpoint descriptions
- Parameter descriptions
- Request/response examples
- Schema descriptions
- API overview
- Code samples

**Example Findings**:
- Missing endpoint summaries
- No request examples
- Undocumented parameters
- Missing schema descriptions

---

### 5. Governance Agent 📋
**Focus**: Metadata, Compliance, Change Management

**Analyzes**:
- API metadata (title, version, contact)
- License information
- Terms of service
- Deprecation notices
- Change management
- Compliance requirements

**Example Findings**:
- Missing version information
- No contact details
- Missing license
- Undocumented deprecations

---

## 🚀 Usage

### Enable Multi-Agent System

```bash
# Set environment variable
export USE_MULTI_AGENT=true

# Run the application
python run_app.py
```

### API Request

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@myapi.yaml" \
  -H "accept: application/json"
```

### Response Format

```json
{
  "health_score": {...},
  "findings": [...],
  "multi_agent_analysis": {
    "summary": "Multi-Agent Analysis Complete (HIGH Risk)\nTotal Findings: 18\n\n• Security: 5 issues (HIGH risk, 85% confidence)\n• Design: 4 issues (MEDIUM risk, 78% confidence)\n• ErrorHandling: 3 issues (MEDIUM risk, 82% confidence)\n• Documentation: 4 issues (LOW risk, 90% confidence)\n• Governance: 2 issues (LOW risk, 95% confidence)",
    "overall_risk": "HIGH",
    "execution_time": 2.34,
    "parallel_execution": true,
    "agents_used": [
      "SecurityAgent",
      "DesignAgent",
      "ErrorHandlingAgent",
      "DocumentationAgent",
      "GovernanceAgent"
    ],
    "top_recommendations": [
      "[Security] Implement authentication (OAuth2, JWT, or API Key)",
      "[Security] Add global security requirements",
      "[Design] Add API versioning (e.g., /v1/resource)",
      "[ErrorHandling] Define standardized error response schema (RFC 7807)",
      "[Documentation] Add descriptions to 8 endpoint(s)"
    ],
    "agent_analyses": [
      {
        "category": "Security",
        "agent": "SecurityAgent",
        "findings_count": 5,
        "risk_level": "HIGH",
        "confidence": 0.85,
        "summary": "5 Security issue(s) found: 2 Critical 3 High",
        "recommendations": [
          "Implement authentication (OAuth2, JWT, or API Key)",
          "Add global security requirements",
          "Add 401 responses to authenticated endpoints"
        ]
      }
      // ... other agents
    ]
  }
}
```

---

## ⚡ Performance

### Parallel vs Sequential

| Mode | Execution Time | Speedup |
|------|----------------|---------|
| **Sequential** | ~5-8 seconds | 1x |
| **Parallel** | ~2-3 seconds | **2-3x faster** |

### Resource Usage

- **CPU**: 5 threads (one per agent)
- **Memory**: ~100-200MB additional
- **Network**: Only if LLM enabled

---

## 🔧 Configuration

### Environment Variables

```bash
# Enable/disable multi-agent system
USE_MULTI_AGENT=true  # or false

# Number of parallel workers (default: 5)
MULTI_AGENT_WORKERS=5

# Enable LLM for agents (requires API key)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
# or
GOOGLE_API_KEY=...
```

### Programmatic Usage

```python
from src.engine.agents.orchestrator import AgentOrchestrator
from src.engine.ai_agent_universal import UniversalAIAgent

# Initialize with LLM
llm_client = UniversalAIAgent()
orchestrator = AgentOrchestrator(llm_client=llm_client, max_workers=5)

# Run analysis
result = orchestrator.analyze(
    spec=openapi_spec,
    signals=extracted_signals,
    findings=matched_findings,
    parallel=True  # or False for sequential
)

# Access results
print(result.summary)
print(result.overall_risk)
print(result.top_recommendations)

for analysis in result.agent_analyses:
    print(f"{analysis.category}: {len(analysis.findings)} findings")
```

---

## 🎯 Benefits

### 1. **Specialized Expertise**
Each agent is an expert in its domain, providing deeper insights than a general-purpose analyzer.

### 2. **Parallel Execution**
Agents run simultaneously, reducing analysis time by 2-3x.

### 3. **Comprehensive Coverage**
5 agents ensure no aspect of your API is overlooked.

### 4. **Confidence Scoring**
Each agent provides a confidence score for its findings.

### 5. **Unified Recommendations**
Orchestrator aggregates and prioritizes recommendations across all agents.

### 6. **Scalable**
Easy to add new specialized agents for additional categories.

---

## 🆚 Comparison

### Standard Analysis vs Multi-Agent

| Feature | Standard | Multi-Agent |
|---------|----------|-------------|
| **Agents** | 1 (general) | 5 (specialized) |
| **Execution** | Sequential | Parallel |
| **Speed** | Baseline | 2-3x faster |
| **Depth** | General | Deep per category |
| **Confidence** | N/A | Per-agent scoring |
| **Recommendations** | Mixed | Prioritized by risk |

---

## 🔍 Agent Coordination

### How Agents Work Together

1. **Orchestrator** receives spec, signals, and findings
2. **Distributes** work to specialized agents
3. **Agents** analyze in parallel, each focusing on their category
4. **Orchestrator** collects results as they complete
5. **Aggregates** findings, resolves conflicts
6. **Prioritizes** recommendations by risk level
7. **Returns** unified report

### Conflict Resolution

When agents have overlapping findings:
- **Highest severity wins** for risk assessment
- **All recommendations kept** but deduplicated
- **Confidence scores** help prioritize

---

## 📊 Example Output

```
Multi-Agent Analysis Complete (HIGH Risk)
Total Findings: 18

• Security: 5 issues (HIGH risk, 85% confidence)
• Design: 4 issues (MEDIUM risk, 78% confidence)
• ErrorHandling: 3 issues (MEDIUM risk, 82% confidence)
• Documentation: 4 issues (LOW risk, 90% confidence)
• Governance: 2 issues (LOW risk, 95% confidence)

Top Recommendations:
1. [Security] Implement authentication (OAuth2, JWT, or API Key)
2. [Security] Add global security requirements
3. [Design] Add API versioning (e.g., /v1/resource)
4. [ErrorHandling] Define standardized error response schema
5. [Documentation] Add descriptions to 8 endpoint(s)

Execution: 2.34s (parallel)
```

---

## 🐛 Troubleshooting

### Issue: "Multi-agent analysis unavailable"

**Solution**: Check if `USE_MULTI_AGENT=true` is set

```bash
export USE_MULTI_AGENT=true
```

### Issue: Slow performance

**Solution**: Ensure parallel execution is enabled

```python
result = orchestrator.analyze(spec, signals, findings, parallel=True)
```

### Issue: Agent failures

**Solution**: Check logs for specific agent errors

```
[MULTI-AGENT] SecurityAgent completed: 5 findings
[MULTI-AGENT] DesignAgent failed: <error>
```

---

## 🚀 Future Enhancements

### Planned Features

- [ ] **Custom Agents**: Create your own specialized agents
- [ ] **Agent Learning**: Agents learn from feedback
- [ ] **Dynamic Prioritization**: Adjust agent focus based on API type
- [ ] **Agent Communication**: Agents share insights
- [ ] **Visualization**: Agent collaboration diagrams

---

## 📚 API Reference

### AgentOrchestrator

```python
class AgentOrchestrator:
    def __init__(self, llm_client=None, max_workers=5)
    def analyze(self, spec, signals, findings, parallel=True) -> OrchestrationResult
    def to_dict(self, result) -> dict
```

### AgentAnalysis

```python
@dataclass
class AgentAnalysis:
    category: str
    agent_name: str
    findings: List[Dict]
    summary: str
    risk_level: str
    recommendations: List[str]
    confidence: float
```

### OrchestrationResult

```python
@dataclass
class OrchestrationResult:
    agent_analyses: List[AgentAnalysis]
    execution_time: float
    agents_used: List[str]
    parallel_execution: bool
    summary: str
    overall_risk: str
    top_recommendations: List[str]
```

---

## ✅ Best Practices

1. **Enable for Production**: Use multi-agent for thorough analysis
2. **Disable for Development**: Use standard for faster iterations
3. **Monitor Performance**: Check execution times
4. **Review Agent Logs**: Understand what each agent found
5. **Combine with LLM**: Enable LLM for deeper insights

---

**Multi-Agent System** - Specialized expertise, parallel execution, comprehensive coverage!  
Version 1.0.0 | SpecSentinel Advanced Analysis