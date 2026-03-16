"""
Test to demonstrate detailed MATCH step logging
"""

import sys
import os
from pathlib import Path

# Set DEBUG logging to see all details
os.environ['LOG_LEVEL'] = 'INFO'

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.vectordb.store.chroma_client import SpecSentinelVectorStore
from src.engine.signal_extractor import Signal
from src.engine.rule_matcher import RuleMatcher
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def test_match_logging():
    """Test detailed logging for MATCH step"""
    
    print("\n" + "=" * 70)
    print("MATCH Step Detailed Logging Test")
    print("=" * 70 + "\n")
    
    # Initialize store
    logger.info("Initializing vector store...")
    store = SpecSentinelVectorStore()
    store.initialize()
    
    # Create test signals across multiple categories
    test_signals = [
        # Security signals
        Signal("SEC-001", "security", "missing 401 Unauthorized response on authenticated endpoint", {"path": "/api/users"}),
        Signal("SEC-002", "security", "no authentication scheme defined, missing OAuth2 JWT", {}),
        Signal("SEC-003", "security", "missing 403 Forbidden response for protected resource", {"path": "/api/admin"}),
        Signal("SEC-004", "security", "no rate limiting defined, missing 429 response", {}),
        Signal("SEC-005", "security", "sensitive data in URL path parameter", {"path": "/api/user/{ssn}"}),
        
        # Design signals
        Signal("DES-001", "design", "missing pagination parameters for list endpoint", {"path": "/api/items"}),
        Signal("DES-002", "design", "no versioning in API path", {}),
        Signal("DES-003", "design", "inconsistent naming convention in endpoint", {"path": "/api/getUser"}),
        
        # Error handling signals
        Signal("ERR-001", "error_handling", "missing 400 Bad Request response for POST endpoint", {"path": "/api/create"}),
        Signal("ERR-002", "error_handling", "no 404 Not Found response defined", {}),
        Signal("ERR-003", "error_handling", "missing 500 Internal Server Error response", {}),
        
        # Documentation signals
        Signal("DOC-001", "documentation", "missing description for endpoint operation", {"path": "/api/test"}),
        Signal("DOC-002", "documentation", "no example provided for request body", {}),
        
        # Governance signals
        Signal("GOV-001", "governance", "missing deprecation notice for old endpoint", {"path": "/api/v1/old"}),
        Signal("GOV-002", "governance", "no contact information in API info", {}),
    ]
    
    logger.info(f"\nCreated {len(test_signals)} test signals")
    logger.info(f"Categories: {len(set(s.category for s in test_signals))}")
    
    # Create matcher and run
    print("\n" + "=" * 70)
    print("Starting MATCH Step")
    print("=" * 70 + "\n")
    
    matcher = RuleMatcher(store, n_results_per_signal=3)
    findings = matcher.match_signals(test_signals)
    
    print("\n" + "=" * 70)
    print("MATCH Step Complete")
    print("=" * 70)
    print(f"\nTotal findings: {len(findings)}")
    print(f"Total signals: {len(test_signals)}")
    print(f"Match rate: {len(findings)/len(test_signals)*100:.1f}%")
    
    # Show sample findings
    if findings:
        print("\nSample findings by category:")
        by_category = {}
        for finding in findings:
            cat = finding.signal.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(finding)
        
        for cat, cat_findings in by_category.items():
            print(f"\n  {cat}: {len(cat_findings)} findings")
            if cat_findings:
                sample = cat_findings[0]
                if sample.top_match:
                    print(f"    Example: {sample.top_match.rule_id} (similarity: {sample.top_match.similarity:.2f})")

if __name__ == "__main__":
    test_match_logging()

# Made with Bob
