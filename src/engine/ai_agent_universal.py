"""
SpecSentinel Universal AI Agent
Supports multiple LLM providers with automatic fallback:
- OpenAI (GPT-4o-mini, GPT-4o)
- Anthropic Claude (Claude 3.5 Sonnet, Claude 3 Haiku)
- Google Gemini (Gemini 1.5 Pro, Gemini 1.5 Flash)
"""

import os
import logging
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    NONE = "none"


@dataclass
class AIInsights:
    """Container for AI-generated insights"""
    summary: str
    risk_level: str
    risk_score: int
    priority_actions: List[Dict[str, Any]]
    estimated_fix_time: str
    business_impact: str
    provider: str  # Which LLM was used


class UniversalAIAgent:
    """
    Universal AI Agent that supports multiple LLM providers.
    Automatically detects available API keys and uses the best available provider.
    
    Priority order: OpenAI → Anthropic → Google → None
    
    Usage:
        agent = UniversalAIAgent()
        if agent.is_available():
            insights = agent.analyze_findings(spec, findings, health_score)
    """
    
    def __init__(self, preferred_provider: Optional[str] = None):
        """
        Initialize the Universal AI Agent.
        
        Args:
            preferred_provider: Preferred LLM provider ("openai", "anthropic", "google")
                               If None, auto-detects based on available API keys
        """
        self.provider = LLMProvider.NONE
        self.client = None
        self.model = None
        
        # Try to initialize in priority order
        if preferred_provider:
            self._init_provider(preferred_provider)
        else:
            self._auto_detect_provider()
        
        if self.provider != LLMProvider.NONE:
            logger.info(f"AI Agent initialized with {self.provider.value} ({self.model})")
        else:
            logger.info("AI Agent disabled - no API keys found")
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        return self.provider != LLMProvider.NONE
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the active provider."""
        return {
            "provider": self.provider.value,
            "model": self.model or "none",
            "available": self.is_available()
        }
    
    # ── Provider Initialization ───────────────────────────────────────────────
    
    def _auto_detect_provider(self):
        """Auto-detect and initialize the best available provider."""
        # Try OpenAI first
        if self._init_openai():
            return
        
        # Try Anthropic second
        if self._init_anthropic():
            return
        
        # Try Google third
        if self._init_google():
            return
        
        # No providers available
        self.provider = LLMProvider.NONE
    
    def _init_provider(self, provider_name: str) -> bool:
        """Initialize a specific provider."""
        provider_name = provider_name.lower()
        
        if provider_name == "openai":
            return self._init_openai()
        elif provider_name in ["anthropic", "claude"]:
            return self._init_anthropic()
        elif provider_name in ["google", "gemini"]:
            return self._init_google()
        else:
            logger.warning(f"Unknown provider: {provider_name}")
            return False
    
    def _init_openai(self) -> bool:
        """Initialize OpenAI provider."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.provider = LLMProvider.OPENAI
            return True
        except ImportError:
            logger.warning("OpenAI package not installed. Install with: pip install openai")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            return False
    
    def _init_anthropic(self) -> bool:
        """Initialize Anthropic Claude provider."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return False
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            self.provider = LLMProvider.ANTHROPIC
            return True
        except ImportError:
            logger.warning("Anthropic package not installed. Install with: pip install anthropic")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic: {e}")
            return False
    
    def _init_google(self) -> bool:
        """Initialize Google Gemini provider."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
            self.client = genai.GenerativeModel(model_name)
            self.model = model_name
            self.provider = LLMProvider.GOOGLE
            return True
        except ImportError:
            logger.warning("Google AI package not installed. Install with: pip install google-generativeai")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Google: {e}")
            return False
    
    # ── Core AI Methods ───────────────────────────────────────────────────────
    
    def analyze_findings(
        self, 
        spec: dict, 
        findings: list, 
        health_score: dict
    ) -> AIInsights:
        """
        Generate comprehensive analysis using available LLM.
        
        Args:
            spec: OpenAPI specification dict
            findings: List of findings from analysis
            health_score: Health score dict with category breakdown
            
        Returns:
            AIInsights object with analysis
        """
        if not self.is_available():
            return self._fallback_insights(findings, health_score)
        
        try:
            prompt = self._build_analysis_prompt(spec, findings, health_score)
            summary = self._call_llm(prompt, max_tokens=1000, temperature=0.3)
            
            # Generate structured insights
            risk_level, risk_score = self._assess_risk(findings, health_score)
            priority_actions = self._generate_priorities(findings)
            estimated_time = self._estimate_effort(findings)
            business_impact = self._assess_business_impact(findings, health_score)
            
            return AIInsights(
                summary=summary,
                risk_level=risk_level,
                risk_score=risk_score,
                priority_actions=priority_actions,
                estimated_fix_time=estimated_time,
                business_impact=business_impact,
                provider=self.provider.value
            )
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._fallback_insights(findings, health_score)
    
    def explain_finding(self, finding: dict) -> str:
        """Generate detailed explanation of a finding."""
        if not self.is_available():
            return f"Issue: {finding.get('title')}. {finding.get('fix_guidance', 'No guidance available.')}"
        
        try:
            prompt = f"""
Explain this API specification issue in clear, simple terms:

**Issue**: {finding.get('title', 'Unknown issue')}
**Severity**: {finding.get('severity', 'Unknown')}
**Category**: {finding.get('category', 'Unknown')}
**Evidence**: {finding.get('evidence', 'Not provided')}

Provide a 2-3 paragraph explanation covering:
1. What this issue means in practical terms
2. Why it matters (security, usability, compliance)
3. Potential consequences if not fixed

Keep it concise and actionable.
"""
            
            return self._call_llm(prompt, max_tokens=400, temperature=0.4)
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"Issue: {finding.get('title')}. {finding.get('fix_guidance', 'Manual review required.')}"
    
    def generate_fix_code(self, finding: dict, spec: dict) -> str:
        """Generate YAML code to fix the issue."""
        if not self.is_available():
            return f"# Fix for: {finding.get('title')}\n# {finding.get('fix_guidance', 'Manual fix required')}"
        
        try:
            context = finding.get('context', {})
            path = context.get('path', '')
            method = context.get('method', '')
            
            prompt = f"""
Generate the exact YAML code to fix this OpenAPI specification issue:

**Issue**: {finding.get('title', 'Unknown')}
**Evidence**: {finding.get('evidence', 'Not provided')}
**Location**: {path} {method}
**Fix Guidance**: {finding.get('fix_guidance', 'Not provided')}

Provide ONLY the YAML code snippet that should be added or modified.
Include comments explaining the fix.
Format it properly with correct indentation.
"""
            
            return self._call_llm(prompt, max_tokens=500, temperature=0.2)
            
        except Exception as e:
            logger.error(f"Failed to generate fix code: {e}")
            return f"# Fix for: {finding.get('title')}\n# {finding.get('fix_guidance', 'Manual fix required')}"
    
    # ── LLM Call Dispatcher ──────────────────────────────────────────────────
    
    def _call_llm(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """Call the appropriate LLM based on active provider."""
        if self.provider == LLMProvider.OPENAI:
            return self._call_openai(prompt, max_tokens, temperature)
        elif self.provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(prompt, max_tokens, temperature)
        elif self.provider == LLMProvider.GOOGLE:
            return self._call_google(prompt, max_tokens, temperature)
        else:
            raise RuntimeError("No LLM provider available")
    
    def _call_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert API security and design consultant."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call Anthropic Claude API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _call_google(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Call Google Gemini API."""
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature
        }
        response = self.client.generate_content(
            prompt,
            generation_config=generation_config
        )
        return response.text
    
    # ── Helper Methods ────────────────────────────────────────────────────────
    
    def _build_analysis_prompt(self, spec: dict, findings: list, health_score: dict) -> str:
        """Build prompt for overall analysis."""
        api_name = spec.get('info', {}).get('title', 'Unknown API')
        total_score = health_score.get('total', 0)
        finding_counts = health_score.get('finding_counts', {})
        
        critical_issues = [f for f in findings if f.get('severity') == 'Critical']
        high_issues = [f for f in findings if f.get('severity') == 'High']
        
        prompt = f"""
Analyze this API specification health report:

**API**: {api_name}
**Health Score**: {total_score}/100
**Issues Found**: {finding_counts.get('critical', 0)} Critical, {finding_counts.get('high', 0)} High, {finding_counts.get('medium', 0)} Medium, {finding_counts.get('low', 0)} Low

**Top Critical Issues**:
{self._format_issues(critical_issues[:3])}

**Top High Priority Issues**:
{self._format_issues(high_issues[:3])}

Provide a concise executive summary (3-4 paragraphs) covering:
1. Overall API health assessment
2. Most critical security/design concerns
3. Recommended immediate actions
4. Long-term improvement suggestions

Be specific and actionable.
"""
        return prompt
    
    def _format_issues(self, issues: list) -> str:
        """Format issues for prompt."""
        if not issues:
            return "- None"
        return "\n".join([f"- {issue.get('title', 'Unknown')}" for issue in issues[:5]])
    
    def _assess_risk(self, findings: list, health_score: dict) -> Tuple[str, int]:
        """Assess overall risk level."""
        critical = health_score.get('finding_counts', {}).get('critical', 0)
        high = health_score.get('finding_counts', {}).get('high', 0)
        total_score = health_score.get('total', 100)
        
        risk_score = 100 - total_score
        risk_score += (critical * 10) + (high * 5)
        risk_score = min(100, risk_score)
        
        if risk_score >= 70 or critical >= 3:
            return "CRITICAL", risk_score
        elif risk_score >= 50 or critical >= 1:
            return "HIGH", risk_score
        elif risk_score >= 30:
            return "MEDIUM", risk_score
        else:
            return "LOW", risk_score
    
    def _generate_priorities(self, findings: list) -> List[Dict[str, Any]]:
        """Generate prioritized action items."""
        priorities = []
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.get('severity', 'Low'), 99)
        )
        
        for i, finding in enumerate(sorted_findings[:5], 1):
            priorities.append({
                "rank": i,
                "title": finding.get('title', 'Unknown'),
                "severity": finding.get('severity', 'Unknown'),
                "category": finding.get('category', 'Unknown'),
                "action": finding.get('fix_guidance', 'Review and fix')[:100]
            })
        
        return priorities
    
    def _estimate_effort(self, findings: list) -> str:
        """Estimate time to fix all issues."""
        critical = sum(1 for f in findings if f.get('severity') == 'Critical')
        high = sum(1 for f in findings if f.get('severity') == 'High')
        medium = sum(1 for f in findings if f.get('severity') == 'Medium')
        low = sum(1 for f in findings if f.get('severity') == 'Low')
        
        hours = (critical * 4) + (high * 2) + (medium * 1) + (low * 0.5)
        
        if hours < 4:
            return "2-4 hours"
        elif hours < 8:
            return "4-8 hours (1 day)"
        elif hours < 16:
            return "1-2 days"
        elif hours < 40:
            return "1 week"
        else:
            return "2+ weeks"
    
    def _assess_business_impact(self, findings: list, health_score: dict) -> str:
        """Assess business impact of issues."""
        critical = health_score.get('finding_counts', {}).get('critical', 0)
        high = health_score.get('finding_counts', {}).get('high', 0)
        
        if critical >= 3:
            return "SEVERE: Critical security vulnerabilities present. Immediate action required."
        elif critical >= 1:
            return "HIGH: Security issues detected that could lead to unauthorized access."
        elif high >= 5:
            return "MODERATE: Multiple issues that may impact API reliability."
        elif high >= 1:
            return "LOW-MODERATE: Some improvements needed for better security."
        else:
            return "MINIMAL: API follows most best practices."
    
    def _fallback_insights(self, findings: list, health_score: dict) -> AIInsights:
        """Provide fallback insights when LLM unavailable."""
        risk_level, risk_score = self._assess_risk(findings, health_score)
        
        return AIInsights(
            summary="AI analysis unavailable. Review findings below for detailed issues.",
            risk_level=risk_level,
            risk_score=risk_score,
            priority_actions=self._generate_priorities(findings),
            estimated_fix_time=self._estimate_effort(findings),
            business_impact=self._assess_business_impact(findings, health_score),
            provider="none"
        )


# ── Convenience Functions ─────────────────────────────────────────────────────

def get_available_providers() -> List[str]:
    """Get list of available LLM providers based on API keys."""
    providers = []
    
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    if os.getenv("GOOGLE_API_KEY"):
        providers.append("google")
    
    return providers


def is_any_llm_available() -> bool:
    """Check if any LLM provider is available."""
    return len(get_available_providers()) > 0

# Made with Bob
