# SpecSentinel - Complete Getting Started Guide 🚀

**Agentic AI API Health, Compliance & Governance Bot**  
IBM Hackathon 2026 | Version 1.0.0

---

## 📋 Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [Using the Web Interface](#using-the-web-interface)
5. [Viewing Logs](#viewing-logs)
6. [Multi-Agent System](#multi-agent-system)
7. [AI-Powered Analysis (Optional)](#ai-powered-analysis-optional)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)
10. [Advanced Features](#advanced-features)

---

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Windows PowerShell, Command Prompt, or Linux/Mac terminal

### Installation & Running

```bash
# 1. Clone and navigate to project
cd SpecSentinal_IBM_Hackathon

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application (starts both backend and frontend)
python run_app.py
```

**That's it!** Open your browser to:
- 🌐 **Frontend UI**: http://localhost:5000
- 🔧 **Backend API**: http://localhost:8000

---

## Installation

### Step 1: Virtual Environment Setup

```bash
# Navigate to project directory
cd c:\Users\YourUsername\SpecSentinal_IBM_Hackathon

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1  # PowerShell
# OR
.\venv\Scripts\activate.bat  # CMD
# OR
source venv/bin/activate     # Linux/Mac
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import chromadb, fastapi, yaml; print('✅ All packages installed!')"
```

### Step 3: Verify Setup

```bash
# Test the pipeline (no server needed)
python test_pipeline.py
```

Expected output:
```
============================================================
  SpecSentinel — Pipeline Integration Test
============================================================

[1/5] Initializing Vector Store...
  Rule counts: {'security': 10, 'design': 8, ...}

[2/5] Loading test spec...
  Paths: 3

[3/5] Extracting signals...
  24 signals extracted

[4/5] Matching rules from Vector DB...
  18 findings matched

[5/5] Computing health score and generating report...

  OVERALL HEALTH SCORE: 42.5/100  🟡 Moderate
```

---

## Running the Application

### Option 1: Single Command (Recommended)

```bash
# Starts both backend and frontend
python run_app.py
```

This starts:
- 🔧 Backend API on http://localhost:8000
- 🌐 Frontend UI on http://localhost:5000

Press `Ctrl+C` to stop both servers.

### Option 2: Separate Terminals

**Terminal 1 - Backend:**
```bash
cd src/api
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python app.py
```

### Option 3: Backend Only (API Testing)

```bash
cd src/api
python app.py
# OR
uvicorn src.api.app:app --reload --port 8000
```

---

## Using the Web Interface

### 1. Open the Frontend

Navigate to: http://localhost:5000

### 2. Upload Your API Specification

**Method A: Upload File**
1. Click "Upload File" tab (default)
2. Drag & drop or click "Choose File"
3. Select your OpenAPI YAML/JSON file
4. Click "Analyze Specification"

**Method B: Paste Spec**
1. Click "Paste Spec" tab
2. Paste your OpenAPI specification
3. Click "Analyze Specification"

### 3. Review Results

You'll see:
- **Health Score** (0-100) with color-coded band
- **Category Breakdown** (Security, Design, Error Handling, Documentation, Governance)
- **Detailed Findings** with severity badges
- **Priority Recommendations**
- **Export Options** (JSON/Text)

### 4. Test with Sample File

Use the included test file:
```
tests/sample_bad_spec.yaml
```

This file intentionally has issues to demonstrate the analysis capabilities.

---

## Viewing Logs

### Log Files Location

All logs are stored in: `logs/` directory

```
logs/
├── specsentinel.log                    # Main application log
├── specsentinel.api.log                # Backend API logs
├── specsentinel.frontend.log           # Frontend logs
├── specsentinel.pipeline.log           # Analysis pipeline logs
├── specsentinel.requests.log           # HTTP request/response logs
└── specsentinel.agent.*.log            # Individual agent logs
```

### Real-Time Log Monitoring

**PowerShell:**
```powershell
# Watch all logs
Get-Content logs\specsentinel.log -Wait

# Watch API logs only
Get-Content logs\specsentinel.api.log -Wait

# Watch with error filtering
Get-Content logs\specsentinel.log -Wait | Select-String "ERROR"
```

**Linux/Mac:**
```bash
# Watch all logs
tail -f logs/specsentinel.log

# Watch API logs
tail -f logs/specsentinel.api.log

# Watch with filtering
tail -f logs/specsentinel.log | grep ERROR
```

### Search Logs

**PowerShell:**
```powershell
# Find all errors
Select-String -Path "logs\*.log" -Pattern "ERROR"

# Find specific text
Select-String -Path "logs\*.log" -Pattern "analyze_spec"

# Count log entries by level
(Get-Content logs\specsentinel.log | Select-String "INFO").Count
(Get-Content logs\specsentinel.log | Select-String "ERROR").Count
```

**Linux/Mac:**
```bash
# Find all errors
grep -r "ERROR" logs/

# Find specific text
grep -r "analyze_spec" logs/

# Count log entries
grep -c "INFO" logs/specsentinel.log
grep -c "ERROR" logs/specsentinel.log
```

### Log Configuration

Create a `.env` file to customize logging:

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable file logging
FILE_LOGGING=true

# Use JSON format (for production)
JSON_LOGGING=false
```

### Log Rotation

Logs automatically rotate when they reach 10MB:
- Maximum file size: 10MB
- Backup count: 5 files
- Old logs: `.log.1`, `.log.2`, etc.
- Oldest logs are automatically deleted

---

## Multi-Agent System

SpecSentinel uses **5 specialized AI agents** for comprehensive analysis:

### The Agents

1. **Security Agent** 🔒
   - Authentication & authorization
   - Data protection
   - OWASP API Security Top 10

2. **Design Agent** 🎨
   - RESTful principles
   - API usability
   - Versioning & pagination

3. **Error Handling Agent** ⚠️
   - Error response schemas
   - HTTP status codes
   - RFC 7807 compliance

4. **Documentation Agent** 📚
   - Developer experience
   - API clarity
   - Examples & descriptions

5. **Governance Agent** 📋
   - Metadata & compliance
   - Change management
   - License & contact info

### Enable Multi-Agent Analysis

```bash
# Set environment variable
export USE_MULTI_AGENT=true  # Linux/Mac
$env:USE_MULTI_AGENT = "true"  # PowerShell

# Run the application
python run_app.py
```

### Performance

| Mode | Execution Time | Speedup |
|------|----------------|---------|
| Sequential | ~5-8 seconds | 1x |
| **Parallel** | ~2-3 seconds | **2-3x faster** |

### Multi-Agent Report Example

```json
{
  "multi_agent_analysis": {
    "summary": "Multi-Agent Analysis Complete (HIGH Risk)\nTotal Findings: 18",
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
      "[Design] Add API versioning (e.g., /v1/resource)",
      "[ErrorHandling] Define standardized error response schema"
    ]
  }
}
```

---

## AI-Powered Analysis (Optional)

Enhance reports with LLM-powered insights using OpenAI.

### Setup (3 Steps)

**Step 1: Install OpenAI Package**
```bash
pip install openai>=1.12.0
```

**Step 2: Get API Key**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Create an API key
4. Copy the key (starts with `sk-`)

**Step 3: Set Environment Variable**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="sk-your-api-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
```

### Verify Setup

```bash
python -c "from src.engine.ai_agent import is_ai_agent_available; print('AI Available:', is_ai_agent_available())"
```

Expected: `AI Available: True`

### What You Get

With AI enabled, reports include:
- **AI-Generated Explanations** - Plain-language issue descriptions
- **Auto-Generated Fix Code** - YAML snippets ready to use
- **Risk Assessment** - Business impact analysis
- **Priority Recommendations** - Intelligent action prioritization
- **Estimated Fix Time** - Effort estimation

### Cost

Typical costs with `gpt-4o-mini` (default):
- Small API (5-10 endpoints): ~$0.01-0.02 per analysis
- Medium API (20-50 endpoints): ~$0.03-0.05 per analysis
- Large API (100+ endpoints): ~$0.10-0.20 per analysis

### Disable AI

```bash
# Temporarily disable
unset OPENAI_API_KEY  # Linux/Mac
Remove-Item Env:\OPENAI_API_KEY  # PowerShell

# The system works perfectly without AI
```

---

## Troubleshooting

### Issue: ModuleNotFoundError

```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port Already in Use

```bash
# Backend (port 8000)
# Kill process using port 8000
netstat -ano | findstr :8000  # Find PID
taskkill /PID <PID> /F        # Kill process

# Or use different port
uvicorn src.api.app:app --port 8080

# Frontend (port 5000)
# Use different port
cd frontend
python app.py --port 5001
```

### Issue: ChromaDB Not Initializing

```bash
# Delete and recreate ChromaDB
Remove-Item -Recurse -Force .chromadb  # PowerShell
rm -rf .chromadb                       # Linux/Mac

# Reinitialize
python -c "from src.vectordb.store.chroma_client import SpecSentinelVectorStore; store = SpecSentinelVectorStore(); store.initialize()"
```

### Issue: No Logs Generated

```bash
# Check if FILE_LOGGING is enabled
echo $env:FILE_LOGGING  # Should be "true"

# Check directory exists
Test-Path logs  # PowerShell
ls -la logs     # Linux/Mac

# Set environment variable
$env:FILE_LOGGING = "true"  # PowerShell
export FILE_LOGGING=true    # Linux/Mac
```

### Issue: Frontend Can't Connect to Backend

1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check CORS settings in `src/api/app.py`

3. Check browser console (F12) for errors

### Issue: AI Agent Not Working

```bash
# Verify API key is set
echo $env:OPENAI_API_KEY  # PowerShell
echo $OPENAI_API_KEY      # Linux/Mac

# Test AI availability
python -c "from src.engine.ai_agent import is_ai_agent_available; print(is_ai_agent_available())"

# Check logs for AI errors
Select-String -Path "logs\*.log" -Pattern "AI-AGENT"
```

---

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check + rule counts |
| GET | `/stats` | Vector DB statistics |
| POST | `/analyze` | Upload spec file (multipart/form-data) |
| POST | `/analyze/text` | Send spec as JSON body |
| POST | `/refresh` | Trigger manual rule refresh |

### Example: Analyze Spec

```bash
# Upload file
curl -X POST http://localhost:8000/analyze \
  -F "file=@myapi.yaml" \
  -H "accept: application/json"

# Get text report
curl -X POST "http://localhost:8000/analyze?format=text" \
  -F "file=@myapi.yaml"

# Send as JSON
curl -X POST http://localhost:8000/analyze/text \
  -H "Content-Type: application/json" \
  -d @myapi.json
```

### Response Format

```json
{
  "meta": {
    "spec_name": "myapi.yaml",
    "generated_at": "2026-03-13T13:00:00Z",
    "tool": "SpecSentinel v1.0"
  },
  "health_score": {
    "total": 68.5,
    "band": "Moderate",
    "band_emoji": "🟡",
    "finding_counts": {
      "total": 15,
      "critical": 2,
      "high": 5,
      "medium": 6,
      "low": 2
    },
    "category_scores": {
      "Security": 45.0,
      "Design": 70.0,
      "ErrorHandling": 60.0,
      "Documentation": 80.0,
      "Governance": 75.0
    }
  },
  "findings": [...],
  "recommendations": [...]
}
```

---

## Advanced Features

### Auto Rule Refresh

Rules automatically update from external sources weekly:

```bash
# Manual refresh via API
curl -X POST http://localhost:8000/refresh

# Manual refresh via CLI
python src/vectordb/ingest/scheduler.py --schedule startup_only --run-now
```

### Custom Rules

Add your own rules to:
- `data/rules/owasp_rules.json` - Security rules
- `data/rules/openapi_rules.json` - Design rules
- `data/rules/governance_rules.json` - Error/Doc/Governance rules

Then reinitialize:
```bash
python -c "from src.vectordb.store.chroma_client import SpecSentinelVectorStore; store = SpecSentinelVectorStore(); store.initialize(force_reseed=True)"
```

### Scoring Customization

Edit `src/engine/scorer.py`:

```python
# Category weights (must sum to 100)
CATEGORY_WEIGHTS = {
    "Security":      35,  # Adjust these
    "Design":        20,
    "ErrorHandling": 15,
    "Documentation": 15,
    "Governance":    15,
}

# Severity deductions
SEVERITY_DEDUCTIONS = {
    "Critical": 20,  # Adjust these
    "High":     12,
    "Medium":    6,
    "Low":       2,
}
```

### CI/CD Integration

```yaml
# .github/workflows/api-review.yml
name: API Spec Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Analyze API Spec
        run: |
          python run_app.py &
          sleep 10
          curl -X POST http://localhost:8000/analyze \
            -F "file=@api-spec.yaml" > report.json
```

---

## Quick Reference

### Start Application
```bash
python run_app.py
```

### View Logs
```bash
Get-Content logs\specsentinel.log -Wait  # PowerShell
tail -f logs/specsentinel.log            # Linux/Mac
```

### Test Pipeline
```bash
python test_pipeline.py
```

### Enable Multi-Agent
```bash
$env:USE_MULTI_AGENT = "true"  # PowerShell
export USE_MULTI_AGENT=true    # Linux/Mac
```

### Enable AI
```bash
$env:OPENAI_API_KEY = "sk-..."  # PowerShell
export OPENAI_API_KEY="sk-..."  # Linux/Mac
```

### Check Health
```bash
curl http://localhost:8000/health
```

---

## Documentation

For more details, see:
- **[README.md](README.md)** - Project overview
- **[docs/SETUP.md](docs/SETUP.md)** - Detailed setup guide
- **[docs/MULTI_AGENT_SYSTEM.md](docs/MULTI_AGENT_SYSTEM.md)** - Multi-agent documentation
- **[docs/AI_AGENT_GUIDE.md](docs/AI_AGENT_GUIDE.md)** - AI agent guide
- **[docs/LOGGING.md](docs/LOGGING.md)** - Complete logging guide
- **[frontend/README.md](frontend/README.md)** - Frontend documentation

---

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review logs in `logs/` directory
3. Check the detailed documentation in `docs/`
4. Verify all dependencies are installed

---

**SpecSentinel v1.0** - IBM Hackathon 2026  
Agentic AI API Health, Compliance & Governance Bot

**Ready to analyze your APIs!** 🚀