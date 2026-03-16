# Multi-LLM Provider Setup Guide

## Overview

SpecSentinel now supports **multiple LLM providers** with automatic fallback:

1. **OpenAI** (GPT-4o-mini, GPT-4o)
2. **Anthropic Claude** (Claude 3.5 Sonnet, Claude 3 Haiku)
3. **IBM WatsonX.ai** (Granite, Llama, Mixtral models)
4. **Google Gemini** (Gemini 1.5 Pro, Gemini 1.5 Flash)

The system automatically detects which API keys are available and uses the best provider.

---

## 🚀 Quick Setup

### Option 1: OpenAI (Default)

```bash
# Install
pip install openai>=1.12.0

# Set API key
export OPENAI_API_KEY="sk-your-key-here"

# Optional: Choose model
export OPENAI_MODEL="gpt-4o-mini"  # or "gpt-4o"
```

**Get API Key**: https://platform.openai.com/api-keys

---

### Option 2: Anthropic Claude (Recommended for Quality)

```bash
# Install
pip install anthropic>=0.18.0

# Set API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Optional: Choose model
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"  # or "claude-3-haiku-20240307"
```

**Get API Key**: https://console.anthropic.com/

---

### Option 3: IBM WatsonX.ai (Enterprise-Grade)

```bash
# Install
pip install ibm-watsonx-ai>=1.0.0

# Set credentials
export WATSONX_API_KEY="your-ibm-cloud-api-key"
export WATSONX_PROJECT_ID="your-project-id"
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"

# Optional: Choose model
export WATSONX_MODEL="ibm/granite-13b-chat-v2"
```

**Get API Key**: https://cloud.ibm.com/
**Detailed Setup**: See [WATSONX_SETUP.md](./WATSONX_SETUP.md)

---

### Option 4: Google Gemini (Best Cost/Performance)

```bash
# Install
pip install google-generativeai>=0.3.0

# Set API key
export GOOGLE_API_KEY="your-key-here"

# Optional: Choose model
export GOOGLE_MODEL="gemini-1.5-flash"  # or "gemini-1.5-pro"
```

**Get API Key**: https://makersuite.google.com/app/apikey

---

## 🔄 Automatic Provider Selection

The system automatically selects providers in this priority order:

1. **OpenAI** (if `OPENAI_API_KEY` is set)
2. **Anthropic** (if `ANTHROPIC_API_KEY` is set)
3. **IBM WatsonX** (if `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set)
4. **Google** (if `GOOGLE_API_KEY` is set)
5. **None** (gracefully degrades, no AI insights)

### Example: Multiple Keys

```bash
# Set multiple keys - OpenAI will be used first
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export WATSONX_API_KEY="..."
export WATSONX_PROJECT_ID="..."
export GOOGLE_API_KEY="..."

# Run the app
python run_app.py
```

**Log Output**:
```
[AI-AGENT] Using openai (gpt-4o-mini)
```

---

## 🎯 Provider Comparison

| Provider | Model | Cost (1M tokens) | Speed | Quality | Context |
|----------|-------|------------------|-------|---------|---------|
| **OpenAI** | gpt-4o-mini | $0.15 / $0.60 | Fast | High | 128K |
| **OpenAI** | gpt-4o | $2.50 / $10.00 | Moderate | Very High | 128K |
| **Anthropic** | claude-3-5-sonnet | $3.00 / $15.00 | Fast | Excellent | 200K |
| **Anthropic** | claude-3-haiku | $0.25 / $1.25 | Very Fast | Good | 200K |
| **WatsonX** | granite-13b-chat-v2 | Varies* | Fast | Good | 8K |
| **WatsonX** | llama-3-70b-instruct | Varies* | Moderate | Excellent | 8K |
| **Google** | gemini-1.5-flash | $0.075 / $0.30 | Very Fast | Good | 1M |
| **Google** | gemini-1.5-pro | $1.25 / $5.00 | Moderate | High | 2M |

*WatsonX pricing varies by IBM Cloud plan and region

---

## 💰 Cost Comparison (Typical API Analysis)

| Provider | Model | Cost per Analysis | Best For |
|----------|-------|-------------------|----------|
| Google | gemini-1.5-flash | **$0.005-0.01** | Budget |
| Anthropic | claude-3-haiku | $0.01-0.02 | Speed + Cost |
| OpenAI | gpt-4o-mini | $0.01-0.05 | Balanced |
| WatsonX | granite-13b-chat-v2 | $0.02-0.08* | Enterprise |
| Anthropic | claude-3-5-sonnet | $0.05-0.10 | Quality |
| OpenAI | gpt-4o | $0.10-0.20 | Premium |

*WatsonX costs depend on IBM Cloud plan

---

## 🔧 Configuration

### Environment Variables

```bash
# Provider API Keys (set at least one)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export WATSONX_API_KEY="..."
export WATSONX_PROJECT_ID="..."
export GOOGLE_API_KEY="..."

# Model Selection (optional)
export OPENAI_MODEL="gpt-4o-mini"
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
export WATSONX_MODEL="ibm/granite-13b-chat-v2"
export GOOGLE_MODEL="gemini-1.5-flash"
```

### Using .env File

Create `.env` in project root:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# IBM WatsonX.ai
WATSONX_API_KEY=your-ibm-cloud-api-key
WATSONX_PROJECT_ID=your-project-id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL=ibm/granite-13b-chat-v2

# Google
GOOGLE_API_KEY=your-key-here
GOOGLE_MODEL=gemini-1.5-flash
```

---

## 📊 Testing Providers

### Check Available Providers

```bash
python -c "from src.engine.ai_agent_universal import get_available_providers; print('Available:', get_available_providers())"
```

**Output**:
```
Available: ['openai', 'anthropic', 'watsonx', 'google']
```

### Test Specific Provider

```python
from src.engine.ai_agent_universal import UniversalAIAgent

# Auto-detect
agent = UniversalAIAgent()
print(agent.get_provider_info())

# Force specific provider
agent = UniversalAIAgent(preferred_provider="anthropic")
print(agent.get_provider_info())
```

---

## 🎨 Provider-Specific Features

### OpenAI
- ✅ Most widely used
- ✅ Excellent documentation
- ✅ Function calling support
- ✅ JSON mode

### Anthropic Claude
- ✅ Best reasoning quality
- ✅ Excellent code generation
- ✅ Longer context (200K)
- ✅ Better at following instructions

### IBM WatsonX.ai
- ✅ Enterprise-grade security
- ✅ On-premises deployment option
- ✅ IBM Granite models optimized for business
- ✅ Compliance-ready (GDPR, HIPAA)

### Google Gemini
- ✅ Cheapest option
- ✅ Fastest responses
- ✅ Massive context (1M-2M tokens)
- ✅ Multimodal support

---

## 🔒 Security & Privacy

### Data Handling

| Provider | Data Retention | Training | Region |
|----------|----------------|----------|--------|
| OpenAI | 30 days | Opt-out available | US |
| Anthropic | Not used for training | Never | US |
| WatsonX | Configurable | Never | Multi-region |
| Google | Not used for training | Never | Global |

### Best Practices

1. **Don't send sensitive data** to any LLM
2. **Use environment variables** for API keys
3. **Rotate keys regularly**
4. **Monitor usage** in provider dashboards
5. **Set spending limits** in provider accounts

---

## 🐛 Troubleshooting

### Issue: "No LLM provider available"

```bash
# Check which keys are set
env | grep -E "(OPENAI|ANTHROPIC|GOOGLE)_API_KEY"

# Set at least one key
export OPENAI_API_KEY="sk-..."
```

### Issue: "Import error: openai/anthropic/watsonx/google"

```bash
# Install missing package
pip install openai anthropic ibm-watsonx-ai google-generativeai

# Or install all at once
pip install -r requirements.txt
```

### Issue: "API key invalid"

1. Check key format:
   - OpenAI: starts with `sk-`
   - Anthropic: starts with `sk-ant-`
   - WatsonX: IBM Cloud API key format
   - Google: alphanumeric string

2. Verify key is active in provider dashboard

3. Check for typos or extra spaces

4. For WatsonX: Ensure both API key AND project ID are set

### Issue: "Rate limit exceeded"

- Wait a few minutes
- Upgrade your plan
- Switch to different provider
- Implement caching

---

## 📈 Performance Tips

### 1. Use Fastest Models

```bash
# Fastest options
export GOOGLE_MODEL="gemini-1.5-flash"      # Fastest
export ANTHROPIC_MODEL="claude-3-haiku-20240307"  # Very fast
export OPENAI_MODEL="gpt-4o-mini"           # Fast
```

### 2. Cache Results

The system automatically caches identical specs. For additional caching:

```python
# Implement in your code
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_analysis(spec_hash):
    return agent.analyze_findings(...)
```

### 3. Reduce Token Usage

- Only enhance top 5 findings (already implemented)
- Use shorter prompts
- Choose smaller models

---

## 🎯 Recommendations

### For Production
**Use Anthropic Claude 3.5 Sonnet**
- Best quality
- Excellent reasoning
- Worth the cost

### For Development
**Use Google Gemini 1.5 Flash**
- Very cheap
- Fast enough
- Good quality

### For Balance
**Use OpenAI GPT-4o-mini**
- Good quality
- Reasonable cost
- Widely supported

---

## 📚 API Response Format

All providers return the same format:

```json
{
  "ai_insights": {
    "summary": "Executive summary...",
    "risk_assessment": {
      "level": "HIGH",
      "score": 75,
      "business_impact": "Security issues detected..."
    },
    "priority_actions": [...],
    "estimated_fix_time": "1-2 days",
    "provider": "openai"  // or "anthropic" or "google"
  },
  "findings": [
    {
      "title": "Missing authentication",
      "ai_explanation": "This API lacks...",
      "ai_suggested_fix": "# Add OAuth2\n..."
    }
  ]
}
```

---

## 🔄 Migration Guide

### From OpenAI-only to Multi-Provider

**Before**:
```python
from src.engine.ai_agent import SpecSentinelAIAgent
agent = SpecSentinelAIAgent()
```

**After**:
```python
from src.engine.ai_agent_universal import UniversalAIAgent
agent = UniversalAIAgent()  # Auto-detects provider
```

**No other code changes needed!** The API is identical.

---

## 📞 Support

### Provider Support

- **OpenAI**: https://help.openai.com/
- **Anthropic**: https://support.anthropic.com/
- **IBM WatsonX**: https://www.ibm.com/support
- **Google**: https://ai.google.dev/support

### SpecSentinel Issues

Check logs for provider-specific errors:
```
[AI-AGENT] Using openai (gpt-4o-mini)
[AI-AGENT] Enhanced 5 findings with openai
```

---

## ✅ Setup Checklist

- [ ] Install at least one LLM package
- [ ] Set at least one API key
- [ ] Test with `python setup_ai_agent.py`
- [ ] Run analysis and verify AI insights appear
- [ ] Check logs for active provider
- [ ] Monitor costs in provider dashboard

---

**Multi-LLM Support** - Choose the best provider for your needs!
Version 1.1.0 | SpecSentinel AI Agent | Now with WatsonX.ai Support!