"""
Documentation Agent
Specialized agent for documentation analysis
"""

from .base_agent import BaseAgent, AgentAnalysis


class DocumentationAgent(BaseAgent):
    """
    Specialized agent for API documentation analysis.
    Focuses on descriptions, examples, and developer experience.
    """
    
    def _get_category(self) -> str:
        return "Documentation"
    
    def analyze(self, spec: dict, signals: list, findings: list) -> AgentAnalysis:
        """
        Analyze documentation aspects of the API.
        
        Focus areas:
        - Endpoint descriptions
        - Parameter descriptions
        - Request/response examples
        - Schema descriptions
        - API overview
        """
        doc_findings = self._filter_findings(findings)
        doc_signals = self._filter_signals(signals)
        
        risk_level = self._assess_risk(doc_findings)
        summary = self._generate_summary(doc_findings)
        recommendations = self._extract_recommendations(doc_findings)
        
        # Add documentation-specific recommendations
        info = spec.get('info', {})
        if not info.get('description'):
            recommendations.insert(0, "Add API description in info section")
        
        paths = spec.get('paths', {})
        missing_descriptions = 0
        missing_examples = 0
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    if not operation.get('summary') and not operation.get('description'):
                        missing_descriptions += 1
                    
                    # Check for examples
                    request_body = operation.get('requestBody', {})
                    if request_body and not request_body.get('content', {}).get('application/json', {}).get('example'):
                        missing_examples += 1
        
        if missing_descriptions > 0:
            recommendations.insert(0, f"Add descriptions to {missing_descriptions} endpoint(s)")
        
        if missing_examples > 0:
            recommendations.insert(0, f"Add request examples to {missing_examples} endpoint(s)")
        
        confidence = self._calculate_confidence(doc_findings)
        
        llm_insights = self._use_llm_analysis(spec, doc_findings)
        if llm_insights:
            summary += f"\n\nAI Analysis: {llm_insights}"
        
        return AgentAnalysis(
            category=self.category,
            agent_name=self.name,
            findings=[self._finding_to_dict(f) for f in doc_findings],
            summary=summary,
            risk_level=risk_level,
            recommendations=recommendations[:5],
            confidence=confidence
        )

# Made with Bob
