"""
Error Handling Agent
Specialized agent for error handling analysis
"""

from .base_agent import BaseAgent, AgentAnalysis


class ErrorHandlingAgent(BaseAgent):
    """
    Specialized agent for error handling analysis.
    Focuses on error responses, status codes, and RFC 7807 compliance.
    """
    
    def _get_category(self) -> str:
        return "ErrorHandling"
    
    def analyze(self, spec: dict, signals: list, findings: list) -> AgentAnalysis:
        """
        Analyze error handling aspects of the API.
        
        Focus areas:
        - Error response schemas
        - HTTP status codes
        - RFC 7807 Problem Details
        - Consistent error format
        - Error messages
        """
        error_findings = self._filter_findings(findings)
        error_signals = self._filter_signals(signals)
        
        risk_level = self._assess_risk(error_findings)
        summary = self._generate_summary(error_findings)
        recommendations = self._extract_recommendations(error_findings)
        
        # Add error-handling specific recommendations
        paths = spec.get('paths', {})
        if paths:
            # Check for error schemas
            has_error_schema = False
            schemas = spec.get('components', {}).get('schemas', {})
            for schema_name in schemas.keys():
                if 'error' in schema_name.lower() or 'problem' in schema_name.lower():
                    has_error_schema = True
                    break
            
            if not has_error_schema:
                recommendations.insert(0, "Define standardized error response schema (RFC 7807)")
            
            # Check for common error responses
            common_errors = ['400', '401', '403', '404', '500']
            missing_errors = []
            
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method in ['get', 'post', 'put', 'delete', 'patch']:
                        responses = operation.get('responses', {})
                        for error_code in common_errors:
                            if error_code not in responses:
                                missing_errors.append(error_code)
            
            if missing_errors:
                unique_missing = list(set(missing_errors))
                recommendations.insert(0, f"Add missing error responses: {', '.join(unique_missing)}")
        
        confidence = self._calculate_confidence(error_findings)
        
        llm_insights = self._use_llm_analysis(spec, error_findings)
        if llm_insights:
            summary += f"\n\nAI Analysis: {llm_insights}"
        
        return AgentAnalysis(
            category=self.category,
            agent_name=self.name,
            findings=[self._finding_to_dict(f) for f in error_findings],
            summary=summary,
            risk_level=risk_level,
            recommendations=recommendations[:5],
            confidence=confidence
        )

# Made with Bob
