# IBM WatsonX.ai Integration Guide

This guide explains how to set up and use IBM WatsonX.ai as an LLM provider in SpecSentinel.

## Overview

SpecSentinel now supports IBM WatsonX.ai as one of its LLM providers, alongside OpenAI, Anthropic Claude, and Google Gemini. WatsonX.ai provides access to powerful foundation models including:

- **IBM Granite** - IBM's enterprise-grade language models
- **Meta Llama** - Open-source large language models
- **Mistral Mixtral** - High-performance mixture-of-experts models

## Prerequisites

1. **IBM Cloud Account**: You need an active IBM Cloud account
2. **WatsonX.ai Project**: Create a project in IBM WatsonX.ai
3. **API Key**: Generate an API key with WatsonX.ai access

## Setup Instructions

### Step 1: Get Your WatsonX.ai Credentials

1. Log in to [IBM Cloud](https://cloud.ibm.com/)
2. Navigate to **WatsonX.ai** service
3. Create a new project or select an existing one
4. Note your **Project ID** (found in project settings)
5. Generate an **API Key**:
   - Go to **Manage** → **Access (IAM)** → **API keys**
   - Click **Create an IBM Cloud API key**
   - Save the API key securely

### Step 2: Install Dependencies

Install the IBM WatsonX.ai Python SDK:

```bash
pip install ibm-watsonx-ai
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Add the following to your `.env` file:

```bash
# IBM WatsonX.ai Configuration
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL=ibm/granite-13b-chat-v2
```

#### Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WATSONX_API_KEY` | Yes | - | Your IBM Cloud API key |
| `WATSONX_PROJECT_ID` | Yes | - | Your WatsonX.ai project ID |
| `WATSONX_URL` | No | `https://us-south.ml.cloud.ibm.com` | WatsonX.ai service endpoint |
| `WATSONX_MODEL` | No | `ibm/granite-13b-chat-v2` | Model to use |

#### Available Regions

Choose the appropriate URL for your region:

- **US South**: `https://us-south.ml.cloud.ibm.com`
- **EU Germany**: `https://eu-de.ml.cloud.ibm.com`
- **Japan Tokyo**: `https://jp-tok.ml.cloud.ibm.com`

### Step 4: Select a Model

WatsonX.ai supports various foundation models. Choose based on your needs:

#### IBM Granite Models (Recommended)
```bash
WATSONX_MODEL=ibm/granite-13b-chat-v2      # Balanced performance
WATSONX_MODEL=ibm/granite-20b-multilingual # Multilingual support
```

#### Meta Llama Models
```bash
WATSONX_MODEL=meta-llama/llama-3-70b-instruct    # High performance
WATSONX_MODEL=meta-llama/llama-3-8b-instruct     # Fast, efficient
```

#### Mistral Models
```bash
WATSONX_MODEL=mistralai/mixtral-8x7b-instruct-v01  # Mixture-of-experts
WATSONX_MODEL=mistralai/mistral-large              # Latest large model
```

## Usage

### Automatic Provider Detection

SpecSentinel automatically detects available LLM providers based on configured API keys. The priority order is:

1. OpenAI
2. Anthropic Claude
3. **IBM WatsonX.ai** ← New!
4. Google Gemini

If WatsonX.ai credentials are configured, it will be used if OpenAI and Anthropic are not available.

### Explicit Provider Selection

You can explicitly request WatsonX.ai:

```python
from src.engine.ai_agent_universal import UniversalAIAgent

# Initialize with WatsonX.ai
agent = UniversalAIAgent(preferred_provider="watsonx")

# Check if available
if agent.is_available():
    print(f"Using: {agent.get_provider_info()}")
    
# Analyze findings
insights = agent.analyze_findings(spec, findings, health_score)
```

### API Usage

When running the SpecSentinel API, WatsonX.ai will be automatically used if configured:

```bash
# Start the backend
uvicorn src.api.app:app --reload

# The startup logs will show:
# Available LLM Providers: openai, anthropic, watsonx, google
```

## Features

WatsonX.ai integration provides all standard SpecSentinel AI features:

### 1. Comprehensive Analysis
- Executive summary of API health
- Risk assessment and scoring
- Priority action recommendations
- Business impact analysis

### 2. Finding Explanations
- Detailed explanations of each issue
- Security and compliance context
- Practical consequences

### 3. Fix Code Generation
- YAML code snippets to fix issues
- Inline comments explaining changes
- Proper indentation and formatting

## Troubleshooting

### Issue: "WatsonX package not installed"

**Solution**: Install the package:
```bash
pip install ibm-watsonx-ai
```

### Issue: "Failed to initialize WatsonX"

**Possible causes**:
1. Invalid API key or Project ID
2. Incorrect region URL
3. Network connectivity issues
4. Insufficient permissions

**Solution**: Verify your credentials and ensure your API key has WatsonX.ai access.

### Issue: Model not found

**Solution**: Ensure the model ID is correct and available in your region. Check the [WatsonX.ai documentation](https://www.ibm.com/docs/en/watsonx-as-a-service) for available models.

### Issue: Rate limiting

**Solution**: WatsonX.ai has rate limits. If you hit them:
1. Reduce request frequency
2. Upgrade your IBM Cloud plan
3. Use a different model with higher limits

## Cost Considerations

WatsonX.ai pricing varies by:
- Model size and type
- Number of tokens processed
- Region

**Cost-saving tips**:
1. Use smaller models (e.g., `granite-13b` instead of `llama-3-70b`) for routine analysis
2. Monitor token usage in IBM Cloud dashboard
3. Set up billing alerts

## Performance Comparison

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| Granite 13B | Fast | Good | Low | General analysis |
| Granite 20B | Medium | Excellent | Medium | Multilingual APIs |
| Llama 3 70B | Slow | Excellent | High | Complex analysis |
| Mixtral 8x7B | Fast | Very Good | Medium | Balanced performance |

## Security & Privacy

### Data Handling
- API specifications are sent to IBM WatsonX.ai for analysis
- IBM's data handling policies apply
- Consider using IBM Cloud Private for sensitive data

### Best Practices
1. Never commit API keys to version control
2. Use environment variables for credentials
3. Rotate API keys regularly
4. Monitor API usage in IBM Cloud dashboard
5. Use IAM policies to restrict access

## Advanced Configuration

### Custom Parameters

You can customize WatsonX.ai behavior by modifying the `_call_watsonx` method in `src/engine/ai_agent_universal.py`:

```python
def _call_watsonx(self, prompt: str, max_tokens: int, temperature: float) -> str:
    parameters = {
        self.watsonx_params.MAX_NEW_TOKENS: max_tokens,
        self.watsonx_params.TEMPERATURE: temperature,
        self.watsonx_params.DECODING_METHOD: "greedy",
        # Add custom parameters:
        self.watsonx_params.TOP_P: 0.9,
        self.watsonx_params.TOP_K: 50,
        self.watsonx_params.REPETITION_PENALTY: 1.1
    }
    response = self.client.generate_text(prompt=prompt, params=parameters)
    return response
```

### Multi-Agent Mode

WatsonX.ai works seamlessly with SpecSentinel's multi-agent system:

```bash
# Enable multi-agent mode
USE_MULTI_AGENT=true
```

This runs 5 specialized agents in parallel, all powered by WatsonX.ai.

## Support

For issues specific to:
- **SpecSentinel integration**: Open an issue on GitHub
- **WatsonX.ai service**: Contact [IBM Support](https://www.ibm.com/support)
- **API keys/billing**: Use IBM Cloud dashboard

## References

- [IBM WatsonX.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [WatsonX.ai Python SDK](https://ibm.github.io/watsonx-ai-python-sdk/)
- [IBM Cloud API Keys](https://cloud.ibm.com/docs/account?topic=account-userapikey)
- [Foundation Models Catalog](https://www.ibm.com/products/watsonx-ai/foundation-models)

## Example: Complete Setup

```bash
# 1. Install dependencies
pip install ibm-watsonx-ai

# 2. Configure .env
cat >> .env << EOF
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_actual_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL=ibm/granite-13b-chat-v2
EOF

# 3. Start SpecSentinel
uvicorn src.api.app:app --reload

# 4. Check logs for confirmation
# You should see: "Available LLM Providers: ..., watsonx, ..."
```

---

**Last Updated**: 2026-03-16  
**Version**: 1.0.0