"""
Base Agent Class
Foundation for all specialized agents
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgentAnalysis:
    """Result from an agent's analysis"""
    category: str
    agent_name: str
    findings: List[Dict[str, Any]]
    summary: str
    risk_level: str
    recommendations: List[str]
    confidence: float  # 0.0 to 1.0


class BaseAgent(ABC):
    """
    Base class for all specialized agents.
    Each agent focuses on a specific category of API analysis.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the agent.
        
        Args:
            llm_client: Optional LLM client for AI-powered analysis
        """
        self.llm_client = llm_client
        self.category = self._get_category()
        self.name = self.__class__.__name__
        logger.info(f"Initialized {self.name} for {self.category} analysis")
    
    @abstractmethod
    def _get_category(self) -> str:
        """Return the category this agent handles."""
        pass
    
    @abstractmethod
    def analyze(self, spec: dict, signals: list, findings: list) -> AgentAnalysis:
        """
        Analyze the spec for this agent's category.
        
        Args:
            spec: OpenAPI specification dict
            signals: Extracted signals from signal extractor
            findings: Matched findings from rule matcher
            
        Returns:
            AgentAnalysis with category-specific insights
        """
        pass
    
    def _finding_to_dict(self, finding) -> dict:
        """Convert a FindingGroup object to a dictionary."""
        if isinstance(finding, dict):
            return finding
        
        # Handle FindingGroup objects
        if hasattr(finding, 'top_match') and finding.top_match:
            match = finding.top_match
            return {
                'signal_id': finding.signal.signal_id,
                'title': match.title,
                'severity': match.severity,
                'category': match.category,
                'source': match.source,
                'benchmark': match.benchmark,
                'evidence': finding.signal.evidence,
                'context': finding.signal.context,
                'check_pattern': match.check_pattern,
                'fix_guidance': match.fix_guidance,
                'tags': match.tags,
                'rule_id': match.rule_id,
                'similarity': match.similarity,
            }
        
        # Fallback for unknown types
        return {
            'title': 'Unknown finding',
            'severity': 'Low',
            'category': 'Unknown',
        }
    
    def _filter_findings(self, findings: list) -> list:
        """Filter findings relevant to this agent's category."""
        filtered = []
        for f in findings:
            # Handle FindingGroup objects
            if hasattr(f, 'top_match') and f.top_match:
                if f.top_match.category.lower() == self.category.lower():
                    filtered.append(f)
            # Handle dict objects (for backward compatibility)
            elif isinstance(f, dict):
                if f.get('category', '').lower() == self.category.lower():
                    filtered.append(f)
        return filtered
    
    def _filter_signals(self, signals: list) -> list:
        """Filter signals relevant to this agent's category."""
        return [
            s for s in signals 
            if s.category.lower() == self.category.lower()
        ]
    
    def _assess_risk(self, findings: list) -> str:
        """Assess risk level based on findings."""
        if not findings:
            return "LOW"
        
        severities = []
        for f in findings:
            # Handle FindingGroup objects
            if hasattr(f, 'top_match') and f.top_match:
                severities.append(f.top_match.severity)
            # Handle dict objects
            elif isinstance(f, dict):
                severities.append(f.get('severity', 'Low'))
        
        if 'Critical' in severities:
            return "CRITICAL"
        elif 'High' in severities:
            return "HIGH"
        elif 'Medium' in severities:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence(self, findings: list) -> float:
        """Calculate confidence score based on findings quality."""
        if not findings:
            return 1.0
        
        # Higher similarity = higher confidence
        similarities = []
        for f in findings:
            # Handle FindingGroup objects
            if hasattr(f, 'top_match') and f.top_match:
                similarities.append(f.top_match.similarity)
            # Handle dict objects
            elif isinstance(f, dict):
                similarities.append(f.get('similarity', 0.5))
        
        return sum(similarities) / len(similarities) if similarities else 0.5
    
    def _generate_summary(self, findings: list) -> str:
        """Generate a summary of findings."""
        if not findings:
            return f"No {self.category} issues detected."
        
        count = len(findings)
        severities = {}
        for f in findings:
            # Handle FindingGroup objects
            if hasattr(f, 'top_match') and f.top_match:
                sev = f.top_match.severity
            # Handle dict objects
            elif isinstance(f, dict):
                sev = f.get('severity', 'Unknown')
            else:
                sev = 'Unknown'
            severities[sev] = severities.get(sev, 0) + 1
        
        summary_parts = [f"{count} {self.category} issue(s) found:"]
        for sev in ['Critical', 'High', 'Medium', 'Low']:
            if sev in severities:
                summary_parts.append(f"{severities[sev]} {sev}")
        
        return " ".join(summary_parts)
    
    def _extract_recommendations(self, findings: list) -> List[str]:
        """Extract top recommendations from findings."""
        recommendations = []
        
        # Sort by severity
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        
        def get_severity(f):
            if hasattr(f, 'top_match') and f.top_match:
                return severity_order.get(f.top_match.severity, 99)
            elif isinstance(f, dict):
                return severity_order.get(f.get('severity', 'Low'), 99)
            return 99
        
        sorted_findings = sorted(findings, key=get_severity)
        
        # Get top 3 recommendations
        for finding in sorted_findings[:3]:
            # Handle FindingGroup objects
            if hasattr(finding, 'top_match') and finding.top_match:
                rec = finding.top_match.fix_guidance or finding.top_match.title or 'Review required'
            # Handle dict objects
            elif isinstance(finding, dict):
                rec = finding.get('fix_guidance', finding.get('title', 'Review required'))
            else:
                rec = 'Review required'
            
            if rec and rec not in recommendations:
                recommendations.append(rec)
        
        return recommendations
    
    def _use_llm_analysis(self, spec: dict, findings: list) -> Optional[str]:
        """Use LLM for deeper analysis if available."""
        if not self.llm_client or not findings:
            return None
        
        try:
            prompt = self._build_llm_prompt(spec, findings)
            response = self._call_llm(prompt)
            return response
        except Exception as e:
            logger.warning(f"{self.name} LLM analysis failed: {e}")
            return None
    
    def _build_llm_prompt(self, spec: dict, findings: list) -> str:
        """Build prompt for LLM analysis."""
        api_name = spec.get('info', {}).get('title', 'Unknown API')
        
        findings_summary = "\n".join([
            f"- {f.get('title', 'Unknown')} ({f.get('severity', 'Unknown')})"
            for f in findings[:5]
        ])
        
        return f"""
Analyze these {self.category} issues in the {api_name} API:

{findings_summary}

Provide:
1. Root cause analysis
2. Business impact
3. Priority recommendations
4. Best practices to follow

Keep it concise (2-3 paragraphs).
"""
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt."""
        if hasattr(self.llm_client, 'analyze_findings'):
            # Universal agent
            return self.llm_client._call_llm(prompt, max_tokens=500, temperature=0.3)
        else:
            # Direct LLM client
            return "LLM analysis not available"

# Made with Bob
