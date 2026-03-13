# SpecSentinel AI Agent Guide 🤖

## Overview

The SpecSentinel AI Agent is an LLM-powered enhancement that provides intelligent analysis, explanations, and recommendations for your API specifications. It uses OpenAI's GPT models to generate human-readable insights beyond the standard rule-based analysis.

## Features

### 1. **AI-Generated Executive Summary** 📊
- Comprehensive analysis of overall API health
- Business impact assessment
- Strategic recommendations

### 2. **Intelligent Risk Assessment** ⚠️
- Risk level classification (CRITICAL/HIGH/MEDIUM/LOW)
- Risk score (0-100)
- Business impact analysis

### 3. **Detailed Finding Explanations** 💡
- Plain-language explanations of technical issues
- Why each issue matters
- Potential consequences if not fixed

### 4. **Auto-Generated Fix Code** 🔧
- YAML code snippets to fix issues
- Properly formatted with comments
- Ready to copy-paste into your spec

### 5. **Priority Action Plan** 📋
- Ranked list of actions to take
- Estimated effort for fixes
- Category-based organization

---

## Setup

### Step 1: Install OpenAI Package

```bash
# Activate your virtual environment
.\venv\Scripts\Activate.ps1

# Install OpenAI
pip install openai>=1.12.0

# Or install all dependencies
pip install -r requirements.txt
```

### Step 2: Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### Step 3: Configure Environment Variable

**Windows PowerShell:**
```powershell
# Set for current session
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Set permanently (user level)
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-api-key-here', 'User')
```

**Windows Command Prompt:**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export OPENAI_API_KEY=sk-your-api-key-here' >> ~/.bashrc
```

**Using .env file:**
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
```

### Step 4: Verify Setup

```bash
# Test AI Agent availability
python -c "from src.engine.ai_agent import is_ai_agent_available; print('AI Agent Available:', is_ai_agent_available())"
```

Expected output: `AI Agent Available: True`

---

## Usage

### Via API

The AI Agent automatically enhances reports when the OpenAI API key is configured.

```bash
# Analyze with AI insights
curl -X POST http://localhost:8000/analyze \
  -F "file=@myapi.yaml" \
  -H "accept: application/json"
```

**Response includes:**
```json
{
  "meta": {...},
  "health_score": {...},
  "findings": [
    {
      "title": "Missing authentication scheme",
      "severity": "Critical",
      "ai_explanation": "This API lacks authentication...",
      "ai_suggested_fix": "# Add security scheme\ncomponents:\n  securitySchemes:..."
    }
  ],
  "ai_insights": {
    "summary": "This API has critical security gaps...",
    "risk_assessment": {
      "level": "HIGH",
      "score": 75,
      "business_impact": "HIGH: Security issues detected..."
    },
    "priority_actions": [
      {
        "rank": 1,
        "title": "Add authentication",
        "severity": "Critical",
        "action": "Implement OAuth2 or JWT..."
      }
    ],
    "estimated_fix_time": "1-2 days"
  }
}
```

### Via Python Code

```python
from src.engine.ai_agent import SpecSentinelAIAgent

# Initialize agent
agent = SpecSentinelAIAgent(model="gpt-4o-mini")

# Get overall insights
insights = agent.analyze_findings(spec, findings, health_score)
print(insights.summary)
print(f"Risk Level: {insights.risk_level}")
print(f"Estimated Fix Time: {insights.estimated_fix_time}")

# Explain a specific finding
explanation = agent.explain_finding(finding)
print(explanation)

# Generate fix code
fix_code = agent.generate_fix_code(finding, spec)
print(fix_code)
```

---

## Configuration

### Model Selection

Choose different OpenAI models based on your needs:

```python
# Fast and cost-effective (recommended)
agent = SpecSentinelAIAgent(model="gpt-4o-mini")

# More powerful but slower/expensive
agent = SpecSentinelAIAgent(model="gpt-4o")

# Legacy model
agent = SpecSentinelAIAgent(model="gpt-3.5-turbo")
```

### Cost Optimization

**Model Pricing (as of 2024):**
- `gpt-4o-mini`: $0.15/1M input tokens, $0.60/1M output tokens
- `gpt-4o`: $2.50/1M input tokens, $10.00/1M output tokens

**Typical Analysis Costs:**
- Small API (5-10 endpoints): ~$0.01-0.02 per analysis
- Medium API (20-50 endpoints): ~$0.03-0.05 per analysis
- Large API (100+ endpoints): ~$0.10-0.20 per analysis

**Tips to reduce costs:**
1. Use `gpt-4o-mini` (default) - 10x cheaper than GPT-4
2. Cache results for identical specs
3. Only enhance top 5 findings (already implemented)
4. Disable AI for development/testing

### Disable AI Agent

```bash
# Temporarily disable
unset OPENAI_API_KEY

# Or don't set it at all
# The system will work fine without AI enhancement
```

---

## Output Examples

### AI Summary Example

```
This API specification has significant security vulnerabilities that require 
immediate attention. The most critical issue is the complete absence of 
authentication mechanisms, leaving all endpoints publicly accessible. 

Additionally, the API lacks proper error handling standards and comprehensive 
documentation, which will impact both security and developer experience. 

Immediate actions should focus on implementing OAuth2 or JWT authentication, 
adding standardized error responses following RFC 7807, and documenting all 
endpoints with examples.

Long-term improvements should include implementing rate limiting, adding API 
versioning, and establishing a comprehensive API governance framework.
```

### AI Explanation Example

```
**Missing 401 Unauthorized Response**

This issue indicates that your authenticated endpoint doesn't specify a 401 
response, which is returned when authentication fails or is missing. This is 
problematic for several reasons:

1. **API Contract Clarity**: Consumers of your API won't know what to expect 
   when authentication fails, leading to poor error handling in client applications.

2. **Security Best Practices**: Properly documented authentication failures help 
   developers implement correct security measures and understand the API's 
   security model.

3. **Debugging and Monitoring**: Without documented 401 responses, it's harder 
   to track authentication issues in production and provide meaningful error 
   messages to users.

The fix is straightforward: add a 401 response definition to your endpoint 
specification with a clear description and example response body.
```

### AI Fix Code Example

```yaml
# Fix for: Missing 401 Unauthorized response
# Add this to your endpoint's responses section

responses:
  '401':
    description: Unauthorized - Authentication required or failed
    content:
      application/json:
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Authentication required"
            message:
              type: string
              example: "Please provide valid credentials"
        example:
          error: "Unauthorized"
          message: "Invalid or missing authentication token"
```

---

## Troubleshooting

### Issue: "OpenAI package not installed"

```bash
pip install openai>=1.12.0
```

### Issue: "OpenAI API key not found"

```bash
# Check if key is set
echo $env:OPENAI_API_KEY  # PowerShell
echo $OPENAI_API_KEY      # Linux/Mac

# Set the key
$env:OPENAI_API_KEY = "sk-your-key"  # PowerShell
export OPENAI_API_KEY="sk-your-key"  # Linux/Mac
```

### Issue: "Rate limit exceeded"

OpenAI has rate limits. If you hit them:
1. Wait a few minutes
2. Upgrade your OpenAI plan
3. Reduce analysis frequency
4. Use caching for duplicate specs

### Issue: "AI insights not appearing in report"

Check logs for:
```
[AI-AGENT] Skipped (OpenAI API key not configured)
```

This means the API key isn't set. Follow setup steps above.

### Issue: "AI enhancement failed"

The system gracefully degrades - you'll still get the full analysis without AI insights. Check:
1. API key is valid
2. You have OpenAI credits
3. Network connectivity
4. Check logs for specific error

---

## Best Practices

### 1. **Use AI Selectively**
- Enable for production API reviews
- Disable for rapid development iterations
- Cache results for frequently analyzed specs

### 2. **Review AI Suggestions**
- AI-generated fixes are suggestions, not guaranteed solutions
- Always review and test before applying
- Use as a starting point for improvements

### 3. **Combine with Human Expertise**
- AI provides insights, but human judgment is crucial
- Use AI to identify issues, experts to prioritize
- Validate AI recommendations against your specific context

### 4. **Monitor Costs**
- Track OpenAI usage in your dashboard
- Set up billing alerts
- Use `gpt-4o-mini` for cost efficiency

### 5. **Privacy Considerations**
- OpenAI processes your API specs
- Don't analyze specs with sensitive data
- Review OpenAI's data usage policy
- Consider using Azure OpenAI for enterprise compliance

---

## Advanced Usage

### Custom Prompts

Modify prompts in `src/engine/ai_agent.py`:

```python
def _build_analysis_prompt(self, spec, findings, health_score):
    # Customize this method to adjust AI behavior
    prompt = f"""
    Your custom prompt here...
    """
    return prompt
```

### Integration with CI/CD

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
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          curl -X POST http://localhost:8000/analyze \
            -F "file=@api-spec.yaml" > report.json
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const report = require('./report.json');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: report.ai_insights.summary
            });
```

---

## FAQ

**Q: Is the AI Agent required?**  
A: No, SpecSentinel works perfectly without it. AI enhancement is optional.

**Q: Which model should I use?**  
A: `gpt-4o-mini` (default) offers the best balance of cost and quality.

**Q: How much does it cost?**  
A: Typically $0.01-0.05 per API analysis with gpt-4o-mini.

**Q: Is my data sent to OpenAI?**  
A: Yes, your API spec is sent to OpenAI for analysis. Don't use for sensitive specs.

**Q: Can I use other LLM providers?**  
A: Currently only OpenAI is supported. Support for Anthropic, Google, etc. can be added.

**Q: Does it work offline?**  
A: No, it requires internet connection to OpenAI API.

---

## Support

For issues or questions:
- Check logs: `[AI-AGENT]` prefix in console
- Review OpenAI status: https://status.openai.com/
- Verify API key: https://platform.openai.com/api-keys
- Test without AI: unset OPENAI_API_KEY

---

**SpecSentinel AI Agent** - Powered by OpenAI GPT-4o-mini  
Version 1.0.0 | IBM Hackathon 2026