"""
Governance Agent
Specialized agent for API governance analysis
"""

from .base_agent import BaseAgent, AgentAnalysis


class GovernanceAgent(BaseAgent):
    """
    Specialized agent for API governance analysis.
    Focuses on metadata, licensing, versioning, and compliance.
    """
    
    def _get_category(self) -> str:
        return "Governance"
    
    def analyze(self, spec: dict, signals: list, findings: list) -> AgentAnalysis:
        """
        Analyze governance aspects of the API.
        
        Focus areas:
        - API metadata (title, version, contact)
        - License information
        - Terms of service
        - Deprecation notices
        - Change management
        """
        gov_findings = self._filter_findings(findings)
        gov_signals = self._filter_signals(signals)
        
        risk_level = self._assess_risk(gov_findings)
        summary = self._generate_summary(gov_findings)
        recommendations = self._extract_recommendations(gov_findings)
        
        # Add governance-specific recommendations
        info = spec.get('info', {})
        
        if not info.get('version'):
            recommendations.insert(0, "Add API version in info section")
        
        if not info.get('contact'):
            recommendations.insert(0, "Add contact information for API support")
        
        if not info.get('license'):
            recommendations.insert(0, "Add license information")
        
        if not info.get('termsOfService'):
            recommendations.insert(0, "Add terms of service URL")
        
        # Check for deprecated endpoints without proper marking
        paths = spec.get('paths', {})
        deprecated_count = 0
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    if operation.get('deprecated'):
                        deprecated_count += 1
        
        if deprecated_count > 0:
            recommendations.insert(0, f"Document migration path for {deprecated_count} deprecated endpoint(s)")
        
        confidence = self._calculate_confidence(gov_findings)
        
        llm_insights = self._use_llm_analysis(spec, gov_findings)
        if llm_insights:
            summary += f"\n\nAI Analysis: {llm_insights}"
        
        return AgentAnalysis(
            category=self.category,
            agent_name=self.name,
            findings=[self._finding_to_dict(f) for f in gov_findings],
            summary=summary,
            risk_level=risk_level,
            recommendations=recommendations[:5],
            confidence=confidence
        )

# Made with Bob
