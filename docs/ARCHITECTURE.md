# SpecSentinel Architecture Documentation

**Version**: 1.0.0  
**Last Updated**: 2026-03-13  
**Project**: SpecSentinel - Agentic AI API Health, Compliance & Governance Bot

---

## Table of Contents

1. [Overall System Architecture](#1-overall-system-architecture)
2. [Analysis Pipeline Flow](#2-analysis-pipeline-flow)
3. [Multi-Agent System Architecture](#3-multi-agent-system-architecture)
4. [LLM Provider Selection Flow](#4-llm-provider-selection-flow)
5. [Vector Database Structure](#5-vector-database-structure)
6. [Component Interaction Diagram](#6-component-interaction-diagram)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Data Flow Diagram](#8-data-flow-diagram)

---

## 1. Overall System Architecture

This diagram shows the complete system architecture including client layer, frontend, backend API, analysis pipeline, vector database, multi-agent system, and AI/LLM integration.

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser] --> B[Frontend Flask App]
        C[API Client/curl] --> D[Backend FastAPI]
    end
    
    subgraph "Frontend Layer"
        B --> D
    end
    
    subgraph "Backend API Layer"
        D[FastAPI Server<br/>Port 8000]
        D --> E[Pipeline Orchestrator]
    end
    
    subgraph "Analysis Pipeline"
        E --> F[Signal Extractor]
        F --> G[Rule Matcher]
        G --> H[Health Scorer]
        H --> I[Report Generator]
        I --> J{Multi-Agent<br/>Enabled?}
        J -->|Yes| K[Agent Orchestrator]
        J -->|No| L[Standard Report]
        K --> M[AI Enhancement]
        L --> M
        M --> N[Final Report]
    end
    
    subgraph "Vector Database"
        G <--> O[(ChromaDB)]
        O --> P[Security Rules]
        O --> Q[Design Rules]
        O --> R[Error Rules]
        O --> S[Doc Rules]
        O --> T[Gov Rules]
    end
    
    subgraph "Multi-Agent System"
        K --> U[Security Agent]
        K --> V[Design Agent]
        K --> W[Error Agent]
        K --> X[Doc Agent]
        K --> Y[Gov Agent]
    end
    
    subgraph "AI/LLM Layer"
        M <--> Z{LLM Provider}
        Z -->|API Key| AA[OpenAI GPT]
        Z -->|API Key| AB[Anthropic Claude]
        Z -->|API Key| AC[Google Gemini]
    end
    
    N --> D
    
    style D fill:#0f62fe,color:#fff
    style K fill:#24a148,color:#fff
    style Z fill:#f1c21b,color:#000
    style O fill:#8a3ffc,color:#fff
```

### Key Components

- **Client Layer**: Web browsers and API clients
- **Frontend**: Flask app serving the web UI (Port 5000)
- **Backend API**: FastAPI server handling analysis requests (Port 8000)
- **Analysis Pipeline**: Core analysis engine with 5 stages
- **Vector Database**: ChromaDB with 5 rule collections
- **Multi-Agent System**: 5 specialized agents for parallel analysis
- **AI/LLM Layer**: Support for OpenAI, Anthropic, and Google

---

## 2. Analysis Pipeline Flow

This sequence diagram illustrates the complete flow of an API specification analysis request through the system.

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Server
    participant Extractor as Signal Extractor
    participant Matcher as Rule Matcher
    participant VectorDB as ChromaDB
    participant Scorer as Health Scorer
    participant MultiAgent as Multi-Agent System
    participant LLM as LLM Provider
    participant Reporter as Report Generator
    
    User->>API: POST /analyze (OpenAPI Spec)
    API->>Extractor: Extract signals
    Extractor->>Extractor: Parse spec structure
    Extractor->>Extractor: Identify issues
    Extractor-->>API: 32 signals extracted
    
    API->>Matcher: Match signals to rules
    Matcher->>VectorDB: Query with embeddings
    VectorDB-->>Matcher: Similar rules (threshold 0.35)
    Matcher-->>API: 18 findings matched
    
    API->>Scorer: Calculate health score
    Scorer->>Scorer: Apply category weights
    Scorer->>Scorer: Deduct by severity
    Scorer-->>API: Score: 42.5/100
    
    alt Multi-Agent Enabled
        API->>MultiAgent: Run specialized agents
        par Parallel Execution
            MultiAgent->>MultiAgent: Security Agent
            MultiAgent->>MultiAgent: Design Agent
            MultiAgent->>MultiAgent: Error Agent
            MultiAgent->>MultiAgent: Doc Agent
            MultiAgent->>MultiAgent: Gov Agent
        end
        MultiAgent-->>API: Agent analyses
    end
    
    alt LLM Available
        API->>LLM: Generate AI insights
        LLM-->>API: Explanations + Fix code
    end
    
    API->>Reporter: Build final report
    Reporter-->>API: JSON/Text report
    API-->>User: Complete analysis
```

### Pipeline Stages

1. **Signal Extraction**: Parse OpenAPI spec and identify potential issues
2. **Rule Matching**: Use vector similarity to match signals with rules
3. **Health Scoring**: Calculate weighted score based on findings
4. **Multi-Agent Analysis** (Optional): Parallel specialized agent analysis
5. **AI Enhancement** (Optional): LLM-powered insights and recommendations
6. **Report Generation**: Create final JSON/text report

---

## 3. Multi-Agent System Architecture

This diagram shows how the multi-agent system coordinates 5 specialized agents running in parallel.

```mermaid
graph TB
    subgraph "Input"
        A[OpenAPI Spec] --> B[Signals]
        A --> C[Findings]
    end
    
    B --> D[Agent Orchestrator]
    C --> D
    
    subgraph "Parallel Agent Execution"
        D -->|Thread 1| E[Security Agent]
        D -->|Thread 2| F[Design Agent]
        D -->|Thread 3| G[Error Handling Agent]
        D -->|Thread 4| H[Documentation Agent]
        D -->|Thread 5| I[Governance Agent]
    end
    
    subgraph "Agent Analysis"
        E --> E1[Filter Security Findings]
        E1 --> E2[Assess Risk]
        E2 --> E3[Generate Recommendations]
        E3 --> E4[Calculate Confidence]
        
        F --> F1[Filter Design Findings]
        G --> G1[Filter Error Findings]
        H --> H1[Filter Doc Findings]
        I --> I1[Filter Gov Findings]
    end
    
    E4 --> J[Result Aggregation]
    F1 --> J
    G1 --> J
    H1 --> J
    I1 --> J
    
    J --> K[Conflict Resolution]
    K --> L[Priority Ranking]
    L --> M[Unified Report]
    
    subgraph "Output"
        M --> N[Overall Risk: HIGH]
        M --> O[Top 10 Recommendations]
        M --> P[Per-Agent Analysis]
        M --> Q[Execution Time: 2.3s]
    end
    
    style D fill:#24a148,color:#fff
    style E fill:#da1e28,color:#fff
    style F fill:#0f62fe,color:#fff
    style G fill:#f1c21b,color:#000
    style H fill:#8a3ffc,color:#fff
    style I fill:#33b1ff,color:#000
```

### Agent Responsibilities

| Agent | Category | Focus Areas |
|-------|----------|-------------|
| **Security Agent** | Security | Authentication, authorization, OWASP Top 10 |
| **Design Agent** | Design | RESTful principles, versioning, naming |
| **Error Handling Agent** | ErrorHandling | Status codes, RFC 7807, error schemas |
| **Documentation Agent** | Documentation | Descriptions, examples, developer experience |
| **Governance Agent** | Governance | Metadata, licensing, deprecation |

### Performance

- **Parallel Execution**: 5 agents run simultaneously using ThreadPoolExecutor
- **Speed Improvement**: 2-3x faster than sequential analysis
- **Typical Time**: 2-3 seconds for complete multi-agent analysis

---

## 4. LLM Provider Selection Flow

This flowchart shows how the Universal AI Agent automatically selects the best available LLM provider.

```mermaid
flowchart TD
    A[Universal AI Agent] --> B{Check OPENAI_API_KEY}
    B -->|Found| C[Initialize OpenAI Client]
    C --> D[Use GPT-4o-mini]
    
    B -->|Not Found| E{Check ANTHROPIC_API_KEY}
    E -->|Found| F[Initialize Anthropic Client]
    F --> G[Use Claude 3.5 Sonnet]
    
    E -->|Not Found| H{Check GOOGLE_API_KEY}
    H -->|Found| I[Initialize Google Client]
    I --> J[Use Gemini 1.5 Flash]
    
    H -->|Not Found| K[No LLM Available]
    K --> L[Graceful Degradation]
    
    D --> M[AI-Enhanced Analysis]
    G --> M
    J --> M
    L --> N[Standard Analysis Only]
    
    M --> O[Generate Explanations]
    M --> P[Generate Fix Code]
    M --> Q[Risk Assessment]
    
    style C fill:#0f62fe,color:#fff
    style F fill:#8a3ffc,color:#fff
    style I fill:#f1c21b,color:#000
    style K fill:#da1e28,color:#fff
```

### Provider Priority

1. **OpenAI** (First choice if API key available)
   - Model: GPT-4o-mini (default)
   - Cost: $0.15/$0.60 per 1M tokens

2. **Anthropic** (Second choice)
   - Model: Claude 3.5 Sonnet (default)
   - Cost: $3.00/$15.00 per 1M tokens

3. **Google** (Third choice)
   - Model: Gemini 1.5 Flash (default)
   - Cost: $0.075/$0.30 per 1M tokens

4. **None** (Graceful degradation)
   - System works without AI
   - Uses rule-based analysis only

---

## 5. Vector Database Structure

This entity-relationship diagram shows the structure of ChromaDB collections and their relationships.

```mermaid
erDiagram
    CHROMADB ||--o{ SECURITY_COLLECTION : contains
    CHROMADB ||--o{ DESIGN_COLLECTION : contains
    CHROMADB ||--o{ ERROR_COLLECTION : contains
    CHROMADB ||--o{ DOC_COLLECTION : contains
    CHROMADB ||--o{ GOV_COLLECTION : contains
    
    SECURITY_COLLECTION {
        string rule_id PK
        string title
        string severity
        string category
        string source
        string benchmark
        string fix_guidance
        string check_pattern
        array tags
        vector embedding
    }
    
    DESIGN_COLLECTION {
        string rule_id PK
        string title
        string severity
        vector embedding
    }
    
    ERROR_COLLECTION {
        string rule_id PK
        string title
        vector embedding
    }
    
    DOC_COLLECTION {
        string rule_id PK
        string title
        vector embedding
    }
    
    GOV_COLLECTION {
        string rule_id PK
        string title
        vector embedding
    }
```

### Collection Details

| Collection | Rules | Source | Purpose |
|------------|-------|--------|---------|
| **security** | 10 | OWASP API Security Top 10 | Authentication, authorization, data protection |
| **design** | 8 | OpenAPI Best Practices | RESTful design, versioning, naming |
| **error_handling** | 4 | RFC 7807 | Error responses, status codes |
| **documentation** | 3 | API Documentation Standards | Descriptions, examples |
| **governance** | 4 | API Governance | Metadata, licensing, deprecation |

### Embedding Model

- **Model**: all-MiniLM-L6-v2 (Sentence Transformers)
- **Dimensions**: 384
- **Similarity Metric**: Cosine similarity
- **Threshold**: 0.35 (minimum for match)

---

## 6. Component Interaction Diagram

This diagram shows how different components interact with each other across layers.

```mermaid
graph LR
    subgraph "Data Layer"
        A[(ChromaDB<br/>Vector Store)]
        B[JSON Rule Files]
    end
    
    subgraph "Engine Layer"
        C[Signal Extractor]
        D[Rule Matcher]
        E[Health Scorer]
        F[Report Generator]
    end
    
    subgraph "Agent Layer"
        G[Agent Orchestrator]
        H[5 Specialized Agents]
    end
    
    subgraph "AI Layer"
        I[Universal AI Agent]
        J[OpenAI]
        K[Anthropic]
        L[Google]
    end
    
    subgraph "API Layer"
        M[FastAPI Server]
        N[Flask Frontend]
    end
    
    B --> A
    A <--> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    I --> K
    I --> L
    F --> M
    G --> M
    N --> M
    
    style A fill:#8a3ffc,color:#fff
    style G fill:#24a148,color:#fff
    style I fill:#f1c21b,color:#000
    style M fill:#0f62fe,color:#fff
```

### Layer Responsibilities

1. **Data Layer**: Persistent storage of rules and embeddings
2. **Engine Layer**: Core analysis logic and algorithms
3. **Agent Layer**: Specialized domain experts for parallel analysis
4. **AI Layer**: LLM integration for enhanced insights
5. **API Layer**: HTTP interfaces for clients

---

## 7. Deployment Architecture

This diagram shows the deployment structure with ports, services, and external dependencies.

```mermaid
graph TB
    subgraph "Client"
        A[Web Browser]
        B[API Client]
    end
    
    subgraph "Frontend Server - Port 5000"
        C[Flask App]
        C --> D[Static Files]
        C --> E[Templates]
    end
    
    subgraph "Backend Server - Port 8000"
        F[FastAPI/Uvicorn]
        F --> G[Analysis Pipeline]
        F --> H[Multi-Agent System]
    end
    
    subgraph "Data Storage"
        I[(ChromaDB<br/>.chromadb/)]
        J[Rule Files<br/>data/rules/]
    end
    
    subgraph "External Services"
        K[OpenAI API]
        L[Anthropic API]
        M[Google AI API]
    end
    
    A --> C
    B --> F
    C --> F
    G --> I
    J --> I
    H --> K
    H --> L
    H --> M
    
    style C fill:#0f62fe,color:#fff
    style F fill:#24a148,color:#fff
    style I fill:#8a3ffc,color:#fff
```

### Deployment Configuration

| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| **Frontend** | Flask | 5000 | Web UI, static files |
| **Backend** | FastAPI/Uvicorn | 8000 | REST API, analysis engine |
| **Vector DB** | ChromaDB | - | Local file storage (.chromadb/) |
| **Rule Files** | JSON | - | Seed data (data/rules/) |

### External Dependencies

- **OpenAI API**: Optional, for GPT models
- **Anthropic API**: Optional, for Claude models
- **Google AI API**: Optional, for Gemini models

---

## 8. Data Flow Diagram

This flowchart shows the complete data flow from input to output.

```mermaid
flowchart LR
    A[OpenAPI Spec<br/>YAML/JSON] --> B[Parse & Validate]
    B --> C[Extract Signals<br/>32 signals]
    C --> D[Vector Embedding]
    D --> E[Semantic Search<br/>ChromaDB]
    E --> F[Match Rules<br/>threshold 0.35]
    F --> G[Filter Findings<br/>18 matches]
    G --> H[Calculate Score<br/>weighted]
    H --> I{Multi-Agent?}
    I -->|Yes| J[5 Agents Parallel]
    I -->|No| K[Standard Path]
    J --> L[Aggregate Results]
    K --> L
    L --> M{LLM Available?}
    M -->|Yes| N[AI Enhancement]
    M -->|No| O[Skip AI]
    N --> P[Final Report]
    O --> P
    P --> Q[JSON Response]
    
    style D fill:#8a3ffc,color:#fff
    style J fill:#24a148,color:#fff
    style N fill:#f1c21b,color:#000
```

### Data Transformations

1. **Input**: OpenAPI Spec (YAML/JSON) → Parsed Dict
2. **Extraction**: Spec Dict → 32 Signals (structured observations)
3. **Embedding**: Signals → 384-dim Vectors
4. **Matching**: Vectors → 18 Rule Matches (similarity > 0.35)
5. **Scoring**: Matches → Health Score (0-100)
6. **Multi-Agent**: Matches → Per-Category Analysis (parallel)
7. **AI Enhancement**: Findings → Explanations + Fix Code
8. **Output**: Aggregated Data → JSON Report

---

## Technology Stack

### Backend
- **Python 3.11+**: Core language
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **ChromaDB**: Vector database
- **Sentence Transformers**: Embeddings

### Frontend
- **Flask**: Web framework
- **HTML/CSS/JavaScript**: UI
- **Fetch API**: Backend communication

### AI/LLM
- **OpenAI SDK**: GPT models
- **Anthropic SDK**: Claude models
- **Google AI SDK**: Gemini models

### Multi-Agent
- **ThreadPoolExecutor**: Parallel execution
- **Concurrent.futures**: Thread management

---

## Performance Metrics

| Metric | Standard | Multi-Agent | With LLM |
|--------|----------|-------------|----------|
| **Analysis Time** | 3-5s | 2-3s | 5-8s |
| **Throughput** | 12-20/min | 20-30/min | 8-12/min |
| **Memory Usage** | 100MB | 200MB | 250MB |
| **CPU Usage** | 1 core | 5 cores | 1-5 cores |

---

## Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **Data Privacy**: API specs sent to LLM providers (opt-in)
3. **Vector DB**: Local storage, no external transmission
4. **CORS**: Configurable, restrictive in production
5. **Input Validation**: All inputs validated before processing

---

## Scalability

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Shared ChromaDB via network storage
- Stateless API design

### Vertical Scaling
- Increase worker threads for multi-agent
- Larger vector DB for more rules
- More powerful LLM models

---

## Monitoring & Observability

### Logging
- Structured logging with levels (INFO, WARNING, ERROR)
- Per-component logging (API, Engine, Agents, LLM)
- Execution time tracking

### Metrics
- Request count and latency
- Agent execution times
- LLM API usage and costs
- Vector DB query performance

---

## Future Architecture Enhancements

1. **Microservices**: Split into separate services
2. **Message Queue**: Async processing with RabbitMQ/Kafka
3. **Caching Layer**: Redis for frequent queries
4. **Database**: PostgreSQL for persistent storage
5. **Container Orchestration**: Kubernetes deployment
6. **API Gateway**: Kong or AWS API Gateway
7. **Monitoring**: Prometheus + Grafana
8. **Tracing**: OpenTelemetry integration

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic API Reference](https://docs.anthropic.com/)
- [Google AI Documentation](https://ai.google.dev/)

---

**SpecSentinel Architecture** - Agentic AI for API Governance  
Version 1.0.0 | IBM Hackathon 2026