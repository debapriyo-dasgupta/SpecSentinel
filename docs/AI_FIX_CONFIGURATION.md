# AI Fix Generation Configuration

This document explains how to configure the AI-powered fix generation feature in SpecSentinel.

## Overview

SpecSentinel can automatically generate human-readable fixes for API specification issues using AI/LLM providers (OpenAI, Anthropic, WatsonX, Google Gemini). You can control which findings get AI-enhanced fixes through environment variables.

## Configuration Parameters

### 1. AI_FIX_MAX_COUNT

**Description**: Maximum number of findings to enhance with AI-generated fixes **PER SEVERITY LEVEL**.

**Default**: `2`

**Valid Values**: Any positive integer (1-20 recommended)

**Example**:
```env
AI_FIX_MAX_COUNT=2
```

**How It Works**:
- This count applies **per severity category**, not total
- Example: `AI_FIX_MAX_COUNT=2` with 3 severities = 2×3 = **6 total fixes**
- Example: `AI_FIX_MAX_COUNT=5` with 4 severities = 5×4 = **20 total fixes**

**Notes**:
- Higher values = more findings per category, but slower processing and higher API costs
- Lower values = faster processing, lower costs, but fewer findings per category
- Recommended: 2-5 per category for balanced performance

### 2. AI_FIX_SEVERITIES

**Description**: Comma-separated list of severity levels to include for AI fix generation.

**Default**: `Critical,High,Medium`

**Valid Values**: Any combination of: `Critical`, `High`, `Medium`, `Low`

**Examples**:

Only critical issues:
```env
AI_FIX_SEVERITIES=Critical
```

Critical and high priority:
```env
AI_FIX_SEVERITIES=Critical,High
```

All severity levels:
```env
AI_FIX_SEVERITIES=Critical,High,Medium,Low
```

Only medium and low:
```env
AI_FIX_SEVERITIES=Medium,Low
```

**Notes**:
- Values are case-sensitive (use proper capitalization)
- No spaces between values
- Order doesn't matter (findings are processed by severity automatically)

## Configuration Examples

### Conservative (Fast, Low Cost)
```env
AI_FIX_MAX_COUNT=1
AI_FIX_SEVERITIES=Critical
```
- Only fixes 1 critical issue
- Fastest processing
- Lowest API costs
- **Total fixes**: 1

### Balanced (Recommended)
```env
AI_FIX_MAX_COUNT=2
AI_FIX_SEVERITIES=Critical,High,Medium
```
- Fixes 2 issues per severity (Critical, High, Medium)
- Good balance of coverage and performance
- Moderate API costs
- **Total fixes**: 2×3 = 6

### Comprehensive (Moderate Cost)
```env
AI_FIX_MAX_COUNT=5
AI_FIX_SEVERITIES=Critical,High,Medium,Low
```
- Fixes 5 issues per severity across all levels
- Comprehensive coverage
- Higher API costs and processing time
- **Total fixes**: 5×4 = 20

### Development/Testing
```env
AI_FIX_MAX_COUNT=1
AI_FIX_SEVERITIES=Critical,High
```
- Quick testing with minimal API usage
- 1 fix per category (Critical and High)
- **Total fixes**: 1×2 = 2

## How It Works

1. **Analysis Phase**: SpecSentinel analyzes your API spec and identifies issues
2. **Filtering**: Findings are filtered based on `AI_FIX_SEVERITIES`
3. **Limiting**: Top N findings (based on `AI_FIX_MAX_COUNT`) are selected
4. **AI Enhancement**: Selected findings get AI-generated explanations and fixes
5. **Display**: Enhanced findings show with 🤖 icon in the UI

## Performance Considerations

### Processing Time
- Each AI fix takes ~2-5 seconds to generate
- Parallel processing (5 workers) speeds this up
- Total time ≈ (Total Fixes / 5) × 3 seconds

**Examples** (with AI_FIX_MAX_COUNT per category):
- 1 fix × 2 severities = 2 total: ~2 seconds
- 2 fixes × 3 severities = 6 total: ~4 seconds
- 5 fixes × 4 severities = 20 total: ~12 seconds
- 10 fixes × 4 severities = 40 total: ~24 seconds

### API Costs

Approximate costs per finding (varies by provider):
- **OpenAI GPT-4o-mini**: $0.0001-0.0003 per fix
- **Anthropic Claude**: $0.0002-0.0005 per fix
- **WatsonX Granite**: Varies by plan
- **Google Gemini**: $0.0001-0.0002 per fix

**Example monthly costs** (100 API analyses):
- Conservative (1 fix × 1 severity = 1 total): $0.01-0.03/month
- Balanced (2 fixes × 3 severities = 6 total): $0.06-0.18/month
- Comprehensive (5 fixes × 4 severities = 20 total): $0.20-0.60/month

## Viewing Configuration

When the backend starts, it logs the current configuration:

```
INFO: AI Fix Generation Config:
INFO:   - Max Findings: 20
INFO:   - Severities: Critical, High, Medium
```

## Troubleshooting

### No AI Fixes Appearing

1. **Check LLM Provider**: Ensure you have a valid API key configured
2. **Check Severities**: Verify findings match configured severity levels
3. **Check Count**: Ensure `AI_FIX_MAX_COUNT` > 0
4. **Check Logs**: Look for "AI-ENHANCE" stage in backend logs

### Too Slow

1. Reduce `AI_FIX_MAX_COUNT` (try 1 or 2 per category)
2. Limit severities to `Critical,High` only
3. Use faster LLM provider (GPT-4o-mini, Gemini Flash)

### Too Expensive

1. Reduce `AI_FIX_MAX_COUNT` to 1-2 per category
2. Use only `Critical` severity
3. Switch to cheaper LLM provider (GPT-4o-mini, Gemini Flash)

## Best Practices

1. **Start Conservative**: Begin with low values and increase as needed
2. **Monitor Costs**: Track API usage in your LLM provider dashboard
3. **Match Use Case**: 
   - Production APIs: Use `Critical,High` only
   - Development: Use all severities for learning
   - CI/CD: Use `Critical` only for fast feedback
4. **Adjust Based on Spec Size**: Larger specs may need lower counts

## Related Configuration

These settings work alongside:
- `USE_MULTI_AGENT`: Enable/disable multi-agent analysis
- LLM provider settings (API keys, models)
- `MAX_AI_ENHANCED_FINDINGS`: (deprecated, use `AI_FIX_MAX_COUNT`)

## Support

For issues or questions:
1. Check backend logs for configuration values
2. Verify .env file syntax (no spaces, proper capitalization)
3. Restart backend after changing configuration
4. Review LLM provider API key validity