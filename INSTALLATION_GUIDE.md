# SpecSentinel Installation Guide

Complete installation guide for SpecSentinel with multi-LLM support.

## Quick Start (Recommended)

Install everything in one command:

```bash
# Install all dependencies including all LLM SDKs
pip install -r requirements.txt
```

This installs:
- ✅ Core backend dependencies (FastAPI, ChromaDB, etc.)
- ✅ All LLM SDKs (OpenAI, Anthropic, WatsonX, Google)
- ✅ Frontend dependencies (Flask)

## Installation Options

### Option 1: Install Everything (Recommended)

```bash
pip install -r requirements.txt
```

**Includes:**
- Core dependencies
- OpenAI SDK
- Anthropic SDK
- IBM WatsonX.ai SDK
- Google Generative AI SDK

### Option 2: Install with setup.py

```bash
# Install core only
pip install -e .

# Install with all AI providers
pip install -e ".[ai]"

# Install with specific providers
pip install -e ".[ai-openai]"      # OpenAI only
pip install -e ".[ai-anthropic]"   # Anthropic only
pip install -e ".[ai-watsonx]"     # WatsonX only
pip install -e ".[ai-google]"      # Google only

# Install with development tools
pip install -e ".[dev]"

# Install everything
pip install -e ".[ai,dev]"
```

### Option 3: Manual Installation

Install core dependencies:
```bash
pip install chromadb>=0.5.0
pip install fastapi>=0.110.0
pip install uvicorn[standard]>=0.29.0
pip install pyyaml>=6.0
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.0
```

Then install your preferred LLM SDK(s):

```bash
# OpenAI
pip install openai>=1.12.0

# Anthropic Claude
pip install anthropic>=0.18.0

# IBM WatsonX.ai
pip install ibm-watsonx-ai>=1.0.0

# Google Gemini
pip install google-generativeai>=0.3.0
```

## Verify Installation

Run the setup verification script:

```bash
python setup_ai_agent.py
```

**Expected Output:**
```
======================================================================
  SpecSentinel Multi-LLM Setup Verification
======================================================================

1. Checking LLM packages...
✅ OpenAI package installed
✅ Anthropic package installed
✅ IBM WatsonX.ai package installed
✅ Google Generative AI package installed

2. Checking API keys...
✅ OpenAI API key configured: sk-proj...xyz
✅ Anthropic API key configured: sk-ant-...xyz
✅ WatsonX API key configured: your-ke...xyz
✅ WatsonX Project ID configured: 12345678...
✅ Google API key configured: AIzaSy...xyz

3. Testing AI Agent...
✅ Available providers: openai, anthropic, watsonx, google
✅ AI Agent initialized with openai (gpt-4o-mini)

======================================================================
  ✅ AI Agent Setup Complete!
======================================================================
```

## Configuration

### 1. Create .env File

Copy the example configuration:

```bash
cp .env.example .env
```

### 2. Add API Keys

Edit `.env` and add your API keys:

```bash
# OpenAI (Optional)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Anthropic (Optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# IBM WatsonX.ai (Optional)
WATSONX_API_KEY=your-ibm-cloud-api-key
WATSONX_PROJECT_ID=your-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL=ibm/granite-13b-chat-v2

# Google Gemini (Optional)
GOOGLE_API_KEY=your-key-here
GOOGLE_MODEL=gemini-1.5-flash
```

**Note:** You only need to configure ONE provider to use AI features.

### 3. Get API Keys

#### OpenAI
1. Visit https://platform.openai.com/api-keys
2. Create new API key
3. Copy and add to `.env`

#### Anthropic
1. Visit https://console.anthropic.com/
2. Create API key
3. Copy and add to `.env`

#### IBM WatsonX.ai
1. Visit https://cloud.ibm.com/
2. Create WatsonX.ai project
3. Get API key and Project ID
4. See `docs/WATSONX_SETUP.md` for detailed instructions

#### Google Gemini
1. Visit https://makersuite.google.com/app/apikey
2. Create API key
3. Copy and add to `.env`

## Start the Application

### Backend API

```bash
# Development mode
uvicorn src.api.app:app --reload

# Production mode
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

### Frontend (Optional)

```bash
cd frontend
python app.py
```

## Troubleshooting

### Issue: "No module named 'openai'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No LLM providers available"

**Solution:** Set at least one API key in `.env` file.

### Issue: "WatsonX initialization failed"

**Solution:** Ensure both `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set.

### Issue: Package conflicts

**Solution:** Use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## System Requirements

- **Python**: 3.11 or higher
- **OS**: Windows, Linux, macOS
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space

## Dependencies Overview

### Core Dependencies
- `chromadb>=0.5.0` - Vector database
- `fastapi>=0.110.0` - API framework
- `uvicorn>=0.29.0` - ASGI server
- `pyyaml>=6.0` - YAML parsing
- `requests>=2.31.0` - HTTP client
- `beautifulsoup4>=4.12.0` - Web scraping

### LLM SDKs (Optional)
- `openai>=1.12.0` - OpenAI GPT models
- `anthropic>=0.18.0` - Anthropic Claude models
- `ibm-watsonx-ai>=1.0.0` - IBM WatsonX.ai models
- `google-generativeai>=0.3.0` - Google Gemini models

### Frontend Dependencies
- `Flask==3.0.0` - Web framework
- `gunicorn==21.2.0` - WSGI server

## Installation Methods Comparison

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| `pip install -r requirements.txt` | ✅ Simple<br>✅ All-in-one<br>✅ Recommended | ❌ Installs all LLMs | Most users |
| `pip install -e ".[ai]"` | ✅ Flexible<br>✅ Editable install | ❌ Requires setup.py | Developers |
| Manual installation | ✅ Full control<br>✅ Minimal install | ❌ More steps | Advanced users |

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure API keys in `.env`
3. ✅ Verify setup: `python setup_ai_agent.py`
4. ✅ Start backend: `uvicorn src.api.app:app --reload`
5. ✅ Test with sample API spec

## Documentation

- **Multi-LLM Setup**: `docs/MULTI_LLM_SETUP.md`
- **WatsonX Setup**: `docs/WATSONX_SETUP.md`
- **AI Agent Guide**: `docs/AI_AGENT_GUIDE.md`
- **Architecture**: `docs/ARCHITECTURE.md`

## Support

For issues or questions:
1. Check documentation in `docs/` folder
2. Run `python setup_ai_agent.py` for diagnostics
3. Review logs in `logs/` folder
4. Open GitHub issue with error details

---

**Installation Complete!** 🎉

You can now analyze API specifications with AI-powered insights from multiple LLM providers.