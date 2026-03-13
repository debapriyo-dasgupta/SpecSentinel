"""
Agent Orchestrator
Coordinates multiple specialized agents for parallel analysis
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from .security_agent import SecurityAgent
from .design_agent import DesignAgent
from .error_handling_agent import ErrorHandlingAgent
from .documentation_agent import DocumentationAgent
from .governance_agent import GovernanceAgent
from .base_agent import AgentAnalysis

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationResult:
    """Result from orchestrated multi-agent analysis"""
    agent_analyses: List[AgentAnalysis]
    execution_time: float
    agents_used: List[str]
    parallel_execution: bool
    summary: str
    overall_risk: str
    top_recommendations: List[str]


class AgentOrchestrator:
    """
    Orchestrates multiple specialized agents for comprehensive API analysis.
    
    Features:
    - Parallel agent execution for speed
    - Agent coordination and result aggregation
    - Conflict resolution between agents
    - Unified reporting
    
    Usage:
        orchestrator = AgentOrchestrator(llm_client=llm)
        result = orchestrator.analyze(spec, signals, findings)
    """
    
    def __init__(self, llm_client=None, max_workers: int = 5):
        """
        Initialize the orchestrator with specialized agents.
        
        Args:
            llm_client: Optional LLM client for AI-powered analysis
            max_workers: Maximum number of parallel agent threads
        """
        self.llm_client = llm_client
        self.max_workers = max_workers
        
        # Initialize all specialized agents
        self.agents = [
            SecurityAgent(llm_client),
            DesignAgent(llm_client),
            ErrorHandlingAgent(llm_client),
            DocumentationAgent(llm_client),
            GovernanceAgent(llm_client)
        ]
        
        logger.info(f"Orchestrator initialized with {len(self.agents)} agents")
    
    def analyze(
        self,
        spec: dict,
        signals: list,
        findings: list,
        parallel: bool = True
    ) -> OrchestrationResult:
        """
        Run all agents and aggregate results.
        
        Args:
            spec: OpenAPI specification dict
            signals: Extracted signals from signal extractor
            findings: Matched findings from rule matcher
            parallel: Whether to run agents in parallel (default: True)
            
        Returns:
            OrchestrationResult with aggregated analysis
        """
        start_time = time.time()
        
        logger.info(f"Starting {'parallel' if parallel else 'sequential'} agent analysis...")
        
        if parallel:
            analyses = self._run_parallel(spec, signals, findings)
        else:
            analyses = self._run_sequential(spec, signals, findings)
        
        execution_time = time.time() - start_time
        
        # Aggregate results
        result = self._aggregate_results(analyses, execution_time, parallel)
        
        logger.info(
            f"Orchestration complete: {len(analyses)} agents, "
            f"{execution_time:.2f}s, risk={result.overall_risk}"
        )
        
        return result
    
    def _run_parallel(
        self,
        spec: dict,
        signals: list,
        findings: list
    ) -> List[AgentAnalysis]:
        """Run all agents in parallel using ThreadPoolExecutor."""
        analyses = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(agent.analyze, spec, signals, findings): agent
                for agent in self.agents
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    analysis = future.result()
                    analyses.append(analysis)
                    logger.info(f"{agent.name} completed: {len(analysis.findings)} findings")
                except Exception as e:
                    logger.error(f"{agent.name} failed: {e}")
        
        return analyses
    
    def _run_sequential(
        self,
        spec: dict,
        signals: list,
        findings: list
    ) -> List[AgentAnalysis]:
        """Run all agents sequentially."""
        analyses = []
        
        for agent in self.agents:
            try:
                analysis = agent.analyze(spec, signals, findings)
                analyses.append(analysis)
                logger.info(f"{agent.name} completed: {len(analysis.findings)} findings")
            except Exception as e:
                logger.error(f"{agent.name} failed: {e}")
        
        return analyses
    
    def _aggregate_results(
        self,
        analyses: List[AgentAnalysis],
        execution_time: float,
        parallel: bool
    ) -> OrchestrationResult:
        """Aggregate results from all agents."""
        
        # Collect agent names
        agents_used = [a.agent_name for a in analyses]
        
        # Determine overall risk (highest risk wins)
        risk_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        overall_risk = "LOW"
        max_risk_value = 0
        
        for analysis in analyses:
            risk_value = risk_order.get(analysis.risk_level, 0)
            if risk_value > max_risk_value:
                max_risk_value = risk_value
                overall_risk = analysis.risk_level
        
        # Generate unified summary
        summary = self._generate_unified_summary(analyses, overall_risk)
        
        # Aggregate top recommendations (avoid duplicates)
        top_recommendations = self._aggregate_recommendations(analyses)
        
        return OrchestrationResult(
            agent_analyses=analyses,
            execution_time=execution_time,
            agents_used=agents_used,
            parallel_execution=parallel,
            summary=summary,
            overall_risk=overall_risk,
            top_recommendations=top_recommendations
        )
    
    def _generate_unified_summary(
        self,
        analyses: List[AgentAnalysis],
        overall_risk: str
    ) -> str:
        """Generate a unified summary from all agent analyses."""
        
        total_findings = sum(len(a.findings) for a in analyses)
        
        summary_parts = [
            f"Multi-Agent Analysis Complete ({overall_risk} Risk)",
            f"Total Findings: {total_findings}",
            ""
        ]
        
        # Add per-category summaries
        for analysis in analyses:
            if analysis.findings:
                summary_parts.append(
                    f"• {analysis.category}: {len(analysis.findings)} issues "
                    f"({analysis.risk_level} risk, {analysis.confidence:.0%} confidence)"
                )
        
        return "\n".join(summary_parts)
    
    def _aggregate_recommendations(
        self,
        analyses: List[AgentAnalysis]
    ) -> List[str]:
        """Aggregate and prioritize recommendations from all agents."""
        
        # Collect all recommendations with their risk levels
        rec_with_risk = []
        for analysis in analyses:
            risk_value = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(
                analysis.risk_level, 0
            )
            for rec in analysis.recommendations:
                rec_with_risk.append((rec, risk_value, analysis.category))
        
        # Sort by risk level (highest first)
        rec_with_risk.sort(key=lambda x: x[1], reverse=True)
        
        # Remove duplicates while preserving order
        seen = set()
        top_recommendations = []
        
        for rec, risk, category in rec_with_risk:
            if rec not in seen:
                seen.add(rec)
                top_recommendations.append(f"[{category}] {rec}")
                if len(top_recommendations) >= 10:  # Top 10
                    break
        
        return top_recommendations
    
    def to_dict(self, result: OrchestrationResult) -> Dict[str, Any]:
        """Convert orchestration result to dictionary for JSON serialization."""
        return {
            "summary": result.summary,
            "overall_risk": result.overall_risk,
            "execution_time": round(result.execution_time, 2),
            "parallel_execution": result.parallel_execution,
            "agents_used": result.agents_used,
            "top_recommendations": result.top_recommendations,
            "agent_analyses": [
                {
                    "category": a.category,
                    "agent": a.agent_name,
                    "findings_count": len(a.findings),
                    "risk_level": a.risk_level,
                    "confidence": round(a.confidence, 2),
                    "summary": a.summary,
                    "recommendations": a.recommendations
                }
                for a in result.agent_analyses
            ]
        }

# Made with Bob
