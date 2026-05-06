"""
Design Agent
Specialized agent for API design analysis
"""

from .base_agent import BaseAgent, AgentAnalysis


class DesignAgent(BaseAgent):
    """
    Specialized agent for API design analysis.
    Focuses on RESTful principles, naming conventions, versioning, and usability.
    """
    
    def _get_category(self) -> str:
        return "Design"
    
    def analyze(self, spec: dict, signals: list, findings: list) -> AgentAnalysis:
        """
        Analyze design aspects of the API.
        
        Focus areas:
        - RESTful naming conventions
        - HTTP method usage
        - Resource modeling
        - API versioning
        - Pagination
        - Filtering and sorting
        """
        design_findings = self._filter_findings(findings)
        design_signals = self._filter_signals(signals)
        
        risk_level = self._assess_risk(design_findings)
        summary = self._generate_summary(design_findings)
        recommendations = self._extract_recommendations(design_findings)
        
        # Add design-specific recommendations
        paths = spec.get('paths', {})
        if paths:
            # Check for versioning
            has_version = any('/v' in path or '/api/v' in path for path in paths.keys())
            if not has_version:
                recommendations.insert(0, "Add API versioning (e.g., /v1/resource)")
            
            # Check for verbs in paths
            verbs = ['get', 'post', 'put', 'delete', 'create', 'update', 'remove']
            has_verbs = any(
                any(verb in path.lower() for verb in verbs)
                for path in paths.keys()
            )
            if has_verbs:
                recommendations.insert(0, "Remove verbs from paths, use HTTP methods instead")
        
        confidence = self._calculate_confidence(design_findings)
        
        llm_insights = self._use_llm_analysis(spec, design_findings)
        if llm_insights:
            summary += f"\n\nAI Analysis: {llm_insights}"
        
        return AgentAnalysis(
            category=self.category,
            agent_name=self.name,
            findings=[self._finding_to_dict(f) for f in design_findings],
            summary=summary,
            risk_level=risk_level,
            recommendations=recommendations[:5],
            confidence=confidence
        )

# Made with Bob
