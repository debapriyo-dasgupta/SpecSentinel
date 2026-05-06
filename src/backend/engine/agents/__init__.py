"""
SpecSentinel Multi-Agent System
Specialized agents for different analysis categories
"""

from .security_agent import SecurityAgent
from .design_agent import DesignAgent
from .error_handling_agent import ErrorHandlingAgent
from .documentation_agent import DocumentationAgent
from .governance_agent import GovernanceAgent
from .orchestrator import AgentOrchestrator

__all__ = [
    'SecurityAgent',
    'DesignAgent',
    'ErrorHandlingAgent',
    'DocumentationAgent',
    'GovernanceAgent',
    'AgentOrchestrator'
]

# Made with Bob
