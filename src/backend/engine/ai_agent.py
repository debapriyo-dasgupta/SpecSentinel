"""
SpecSentinel AI Agent
LLM-powered agent for intelligent API analysis and recommendations
"""

import os
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Check if OpenAI is available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. AI Agent features will be disabled.")


@dataclass
class AIInsights:
    """Container for AI-generated insights"""
    summary: str
    risk_level: str
    risk_score: int  # 0-100
    priority_actions: List[Dict[str, Any]]
    estimated_fix_time: str
    business_impact: str


class SpecSentinelAIAgent:
    """
    Agentic AI that provides:
    - Contextual explanations of findings
    - Prioritized fix recommendations
    - Security risk assessment
    - Auto-generated fix code snippets
    
    Usage:
        agent = SpecSentinelAIAgent()
        insights = agent.analyze_findings(spec, findings, health_score)
        explanation = agent.explain_finding(finding)
        fix_code = agent.generate_fix_code(finding, spec)
    """
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        """
        Initialize the AI Agent.
        
        Args:
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package is required for AI Agent. "
                "Install with: pip install openai"
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"AI Agent initialized with model: {model}")
    
    def analyze_findings(
        self, 
        spec: dict, 
        findings: list, 
        health_score: dict
    ) -> AIInsights:
        """
        Use LLM to provide intelligent analysis of findings.
        
        Args:
            spec: The OpenAPI specification dict
            findings: List of finding groups from rule matcher
            health_score: Health score object with category breakdown
            
        Returns:
            AIInsights object with comprehensive analysis
        """
        try:
            prompt = self._build_analysis_prompt(spec, findings, health_score)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are an expert API security and design consultant. "
                            "Provide concise, actionable insights about API specifications. "
                            "Focus on business impact and practical recommendations."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content
            
            # Generate structured insights
            risk_level, risk_score = self._assess_risk(findings, health_score)
            priority_actions = self._generate_priorities(findings)
            estimated_time = self._estimate_effort(findings)
            business_impact = self._assess_business_impact(findings, health_score)
            
            logger.info(f"AI Agent generated insights: Risk={risk_level}, Actions={len(priority_actions)}")
            
            return AIInsights(
                summary=summary,
                risk_level=risk_level,
                risk_score=risk_score,
                priority_actions=priority_actions,
                estimated_fix_time=estimated_time,
                business_impact=business_impact
            )
            
        except Exception as e:
            logger.error(f"AI Agent analysis failed: {e}")
            return self._fallback_insights(findings, health_score)
    
    def explain_finding(self, finding: dict) -> str:
        """
        Provide detailed explanation of why this is an issue.
        
        Args:
            finding: A single finding dict with title, severity, category, etc.
            
        Returns:
            Detailed explanation string
        """
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an API security expert explaining issues to developers."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"Issue: {finding.get('title')}. {finding.get('fix_guidance', 'No guidance available.')}"
    
    def generate_fix_code(self, finding: dict, spec: dict) -> str:
        """
        Generate actual code to fix the issue in the OpenAPI spec.
        
        Args:
            finding: The finding to fix
            spec: The full OpenAPI specification
            
        Returns:
            YAML code snippet showing the fix
        """
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an OpenAPI specification expert. "
                            "Generate valid YAML code snippets for OpenAPI 3.x specs."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate fix code: {e}")
            return f"# Fix for: {finding.get('title')}\n# {finding.get('fix_guidance', 'Manual fix required')}"
    
    # ── Private helper methods ────────────────────────────────────────────────
    
    def _build_analysis_prompt(self, spec: dict, findings: list, health_score: dict) -> str:
        """Build the prompt for overall analysis."""
        api_name = spec.get('info', {}).get('title', 'Unknown API')
        total_score = health_score.get('total', 0)
        finding_counts = health_score.get('finding_counts', {})
        
        # Summarize top issues
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
    
    def _assess_risk(self, findings: list, health_score: dict) -> tuple[str, int]:
        """Assess overall risk level."""
        critical = health_score.get('finding_counts', {}).get('critical', 0)
        high = health_score.get('finding_counts', {}).get('high', 0)
        total_score = health_score.get('total', 100)
        
        # Calculate risk score (inverse of health score with severity weighting)
        risk_score = 100 - total_score
        risk_score += (critical * 10) + (high * 5)
        risk_score = min(100, risk_score)
        
        # Determine risk level
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
        
        # Sort by severity
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
        
        # Rough estimates: Critical=4h, High=2h, Medium=1h, Low=0.5h
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
            return "SEVERE: Critical security vulnerabilities present. Immediate action required to prevent data breaches or service disruption."
        elif critical >= 1:
            return "HIGH: Security issues detected that could lead to unauthorized access or data exposure."
        elif high >= 5:
            return "MODERATE: Multiple design and security issues that may impact API reliability and user trust."
        elif high >= 1:
            return "LOW-MODERATE: Some improvements needed for better security and maintainability."
        else:
            return "MINIMAL: API follows most best practices. Minor improvements recommended."
    
    def _fallback_insights(self, findings: list, health_score: dict) -> AIInsights:
        """Provide fallback insights if AI call fails."""
        risk_level, risk_score = self._assess_risk(findings, health_score)
        
        return AIInsights(
            summary="AI analysis unavailable. Review findings below for detailed issues.",
            risk_level=risk_level,
            risk_score=risk_score,
            priority_actions=self._generate_priorities(findings),
            estimated_fix_time=self._estimate_effort(findings),
            business_impact=self._assess_business_impact(findings, health_score)
        )


def is_ai_agent_available() -> bool:
    """Check if AI Agent can be used."""
    return OPENAI_AVAILABLE and bool(os.getenv("OPENAI_API_KEY"))

# Made with Bob
