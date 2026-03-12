# SpecSentinel 🛡️

**Agentic AI API Health, Compliance & Governance Bot**

IBM Hackathon 2026 MVP — Vector DB Rule Engine for OpenAPI Specification Analysis

---

## 📋 Overview

SpecSentinel is an intelligent API governance tool that automatically analyzes OpenAPI specifications to identify security vulnerabilities, design flaws, error handling gaps, documentation issues, and governance problems using AI-powered semantic matching with a vector database.

### Key Features

- ✅ **Automated API Spec Analysis** - Upload YAML/JSON OpenAPI specs
- ✅ **Vector DB Rule Engine** - ChromaDB with 29+ curated rules
- ✅ **Semantic Matching** - AI-powered rule matching using embeddings
- ✅ **Weighted Scoring** - 0-100 health score with category breakdown
- ✅ **Auto Rule Refresh** - Weekly updates from OWASP, OpenAPI, RFC sources
- ✅ **REST API** - FastAPI server with multiple endpoints
- ✅ **Web Frontend** - Modern, responsive UI for easy analysis
- ✅ **Detailed Reports** - JSON and text format outputs

---

## 🏗️ Project Structure

```
SpecSentinel_IBM_Hackathon/
├── src/                          # Source code
│   ├── engine/                   # Core analysis engine
│   │   ├── signal_extractor.py  # OpenAPI spec parser
│   │   ├── rule_matcher.py      # Vector DB semantic search
│   │   ├── scorer.py            # Health score calculator
│   │   └── reporter.py          # Report generator
│   │
│   ├── vectordb/                 # Vector database layer
│   │   ├── store/
│   │   │   └── chroma_client.py # ChromaDB wrapper
│   │   └── ingest/
│   │       ├── scraper.py       # Web scraper for rules
│   │       └── scheduler.py     # Auto-refresh scheduler
│   │
│   └── api/                      # REST API
│       └── app.py               # FastAPI application
│
├── frontend/                     # Web Frontend
│   ├── index.html               # Main HTML page
│   ├── css/
│   │   └── styles.css           # Styles and animations
│   ├── js/
│   │   └── app.js               # Frontend logic & API integration
│   ├── README.md                # Frontend documentation
│   └── QUICKSTART.md            # Quick start guide
│
├── data/                         # Data files
│   └── rules/                   # Seed rule files
│       ├── owasp_rules.json     # OWASP API Security rules
│       ├── openapi_rules.json   # OpenAPI best practices
│       └── governance_rules.json # Error/doc/governance rules
│
├── tests/                        # Test files
│   ├── test_pipeline.py         # Integration test
│   └── sample_bad_spec.yaml     # Test OpenAPI spec
│
├── docs/                         # Documentation
│   ├── README.md                # Detailed project docs
│   ├── SETUP.md                 # Setup instructions
│   └── PROJECT_SUMMARY.md       # Technical summary
│
├── config/                       # Configuration
│   └── setup.ps1                # Automated setup script
│
├── requirements.txt              # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SpecSentinel_IBM_Hackathon
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the package in development mode**
   ```bash
   pip install -e .
   ```

### Running the Application

#### Option 1: Run Integration Test (No Server)

```bash
python tests/test_pipeline.py
```

This will:
- Initialize ChromaDB with seed rules
- Analyze the sample bad spec
- Print the health report to console
- Save `tests/report_output.json`

#### Option 2: Start the API Server

```bash

---

## 🌐 Web Frontend

SpecSentinel includes a modern web-based frontend for easy API specification analysis.

### Quick Start

**Terminal 1 - Start Backend:**
```bash
cd src/api
python app.py
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
python -m http.server 8080
```

**Open Browser:**
```
http://localhost:8080
```

### Features

- 📁 **File Upload** - Drag & drop or browse for YAML/JSON files
- 📝 **Direct Paste** - Paste your OpenAPI spec directly
- 📊 **Visual Reports** - Interactive health score with animated charts
- 🔍 **Filterable Findings** - Filter by severity (Critical/High/Medium/Low)
- 💾 **Export Options** - Download JSON or text reports
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

### Documentation

- [Frontend README](frontend/README.md) - Complete documentation
- [Quick Start Guide](frontend/QUICKSTART.md) - Get started in 5 minutes

cd src/api
python app.py
```

Or using uvicorn directly:
```bash
uvicorn src.api.app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

---

## 📊 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check + rule counts |
| GET | `/stats` | Vector DB collection statistics |
| POST | `/analyze` | Upload spec file (multipart/form-data) |
| POST | `/analyze/text` | Send spec as JSON body |
| POST | `/refresh` | Trigger manual rule refresh |

### Example Usage

**Analyze a spec file:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@myapi.yaml" \
  -H "accept: application/json"
```

**Get text report:**
```bash
curl -X POST "http://localhost:8000/analyze?format=text" \
  -F "file=@myapi.yaml"
```

**Check rule counts:**
```bash
curl http://localhost:8000/stats
```

---

## 🎯 Analysis Categories

### 1. Security (35% weight)
- Missing authentication schemes
- No global security requirements
- Missing 401/403/429 responses
- Sensitive data exposure
- Broken authorization patterns

### 2. Design (20% weight)
- Missing API versioning
- No operationId on endpoints
- Verbs in paths (non-RESTful)
- GET with request body
- Missing pagination

### 3. Error Handling (15% weight)
- No standardized error schema
- Missing RFC 7807 fields
- Inconsistent error responses

### 4. Documentation (15% weight)
- Missing endpoint summaries
- No operation descriptions
- Missing request body examples

### 5. Governance (15% weight)
- Missing API version in info
- No contact information
- Missing license
- Deprecated endpoints without flag

---

## 📈 Scoring Model

### Formula
```
Total Score = Σ(Category Raw Score × Category Weight)

Category Raw Score = 100 - Σ(Severity Deductions)

Severity Deductions:
- Critical: -20 points
- High: -12 points
- Medium: -6 points
- Low: -2 points
```

### Maturity Bands

| Score | Band | Emoji | Description |
|-------|------|-------|-------------|
| 86-100 | Excellent | ✅ | Best practices followed |
| 71-85 | Good | 🟢 | Minor issues, mostly compliant |
| 41-70 | Moderate | 🟡 | Some issues, needs improvement |
| 0-40 | Poor | 🔴 | Critical issues, major gaps |

---

## 🛠️ Technology Stack

- **Python 3.13** - Core language
- **FastAPI** - Web framework
- **ChromaDB** - Vector database
- **APScheduler** - Task scheduling
- **PyYAML** - YAML parsing
- **BeautifulSoup4** - HTML parsing
- **Uvicorn** - ASGI server

---

## 📚 Documentation

For detailed documentation, see:
- [docs/README.md](docs/README.md) - Comprehensive project documentation
- [docs/SETUP.md](docs/SETUP.md) - Detailed setup instructions
- [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) - Technical architecture

---

## 🧪 Testing

Run the integration test:
```bash
python tests/test_pipeline.py
```

This tests the complete pipeline:
1. Vector store initialization
2. Signal extraction from OpenAPI spec
3. Rule matching via semantic search
4. Health score computation
5. Report generation

---

## 🔄 Auto Rule Refresh

Rules are automatically updated from external sources weekly:

| Source | Category | URL |
|--------|----------|-----|
| OWASP API Security Top 10 2023 | Security | owasp.org |
| OpenAPI 3.x Best Practices | Design | learn.openapis.org |
| RFC 7807 Problem Details | ErrorHandling | datatracker.ietf.org |

Manual refresh:
```bash
curl -X POST http://localhost:8000/refresh
```

Or run the scheduler directly:
```bash
python src/vectordb/ingest/scheduler.py --schedule startup_only
```

---

## 🤝 Contributing

This is an IBM Hackathon 2026 project. For questions or contributions, please refer to the project documentation.

---

## 📄 License

See project documentation for license information.

---

## 🏆 IBM Hackathon 2026

**Category**: Agentic AI / API Governance  
**Tech Stack**: Python, FastAPI, ChromaDB  
**Status**: MVP Complete ✅

---

**Last Updated**: 2026-03-11  
**Version**: 1.0.0