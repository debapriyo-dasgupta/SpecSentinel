"""
Security Agent
Specialized agent for security analysis
"""

from .base_agent import BaseAgent, AgentAnalysis


class SecurityAgent(BaseAgent):
    """
    Specialized agent for API security analysis.
    Focuses on authentication, authorization, data protection, and security best practices.
    """
    
    def _get_category(self) -> str:
        return "Security"
    
    def analyze(self, spec: dict, signals: list, findings: list) -> AgentAnalysis:
        """
        Analyze security aspects of the API.
        
        Focus areas:
        - Authentication schemes
        - Authorization patterns
        - Sensitive data exposure
        - Security headers
        - Rate limiting
        - HTTPS enforcement
        """
        # Filter relevant findings
        security_findings = self._filter_findings(findings)
        security_signals = self._filter_signals(signals)
        
        # Assess risk
        risk_level = self._assess_risk(security_findings)
        
        # Generate summary
        summary = self._generate_summary(security_findings)
        
        # Extract recommendations
        recommendations = self._extract_recommendations(security_findings)
        
        # Add security-specific recommendations
        if not spec.get('components', {}).get('securitySchemes'):
            recommendations.insert(0, "Implement authentication (OAuth2, JWT, or API Key)")
        
        if not spec.get('security'):
            recommendations.insert(0, "Add global security requirements")
        
        # Calculate confidence
        confidence = self._calculate_confidence(security_findings)
        
        # Use LLM for deeper analysis if available
        llm_insights = self._use_llm_analysis(spec, security_findings)
        if llm_insights:
            summary += f"\n\nAI Analysis: {llm_insights}"
        
        return AgentAnalysis(
            category=self.category,
            agent_name=self.name,
            findings=[self._finding_to_dict(f) for f in security_findings],
            summary=summary,
            risk_level=risk_level,
            recommendations=recommendations[:5],  # Top 5
            confidence=confidence
        )

# Made with Bob
