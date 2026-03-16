"""
Test script to verify batch querying performance improvement
"""

import sys
import time
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.vectordb.store.chroma_client import SpecSentinelVectorStore
from src.engine.signal_extractor import Signal
from src.engine.rule_matcher import RuleMatcher

def test_batch_vs_sequential():
    """Compare batch querying vs sequential querying performance"""
    
    print("=" * 70)
    print("Batch Querying Performance Test")
    print("=" * 70)
    print()
    
    # Initialize store
    print("Initializing vector store...")
    store = SpecSentinelVectorStore()
    store.initialize()
    print("[OK] Store initialized")
    print()
    
    # Create test signals
    test_signals = [
        Signal(
            signal_id="TEST-SEC-001",
            category="security",
            description="missing 401 Unauthorized response on authenticated endpoint",
            context={"path": "/api/users", "method": "GET"}
        ),
        Signal(
            signal_id="TEST-SEC-002",
            category="security",
            description="no authentication scheme defined, missing OAuth2 JWT API key",
            context={}
        ),
        Signal(
            signal_id="TEST-DES-001",
            category="design",
            description="missing pagination parameters for list endpoint",
            context={"path": "/api/items", "method": "GET"}
        ),
        Signal(
            signal_id="TEST-ERR-001",
            category="error_handling",
            description="missing 400 Bad Request response for POST endpoint",
            context={"path": "/api/create", "method": "POST"}
        ),
        Signal(
            signal_id="TEST-DOC-001",
            category="documentation",
            description="missing description for endpoint operation",
            context={"path": "/api/test", "method": "GET"}
        ),
    ]
    
    print(f"Testing with {len(test_signals)} signals across {len(set(s.category for s in test_signals))} categories")
    print()
    
    # Test batch querying (new method)
    print("Testing BATCH querying...")
    matcher_batch = RuleMatcher(store, n_results_per_signal=3)
    
    start_batch = time.time()
    findings_batch = matcher_batch.match_signals(test_signals)
    duration_batch = time.time() - start_batch
    
    print(f"[OK] Batch querying completed in {duration_batch:.3f}s")
    print(f"  Found {len(findings_batch)} findings")
    print()
    
    # Test sequential querying (legacy method)
    print("Testing SEQUENTIAL querying...")
    matcher_seq = RuleMatcher(store, n_results_per_signal=3)
    
    start_seq = time.time()
    findings_seq = matcher_seq.match_signals_sequential(test_signals)
    duration_seq = time.time() - start_seq
    
    print(f"[OK] Sequential querying completed in {duration_seq:.3f}s")
    print(f"  Found {len(findings_seq)} findings")
    print()
    
    # Compare results
    print("=" * 70)
    print("Performance Comparison")
    print("=" * 70)
    print(f"Batch querying:      {duration_batch:.3f}s")
    print(f"Sequential querying: {duration_seq:.3f}s")
    
    if duration_seq > 0:
        speedup = duration_seq / duration_batch
        improvement = ((duration_seq - duration_batch) / duration_seq) * 100
        print(f"Speedup:             {speedup:.2f}x faster")
        print(f"Improvement:         {improvement:.1f}% reduction in time")
    
    print()
    print(f"Results match:       {len(findings_batch) == len(findings_seq)}")
    print()
    
    # Show sample findings
    if findings_batch:
        print("Sample finding (batch method):")
        sample = findings_batch[0]
        print(f"  Signal: {sample.signal.signal_id}")
        print(f"  Category: {sample.signal.category}")
        print(f"  Matches: {len(sample.matches)}")
        if sample.top_match:
            print(f"  Top match: {sample.top_match.rule_id} ({sample.top_match.similarity:.2f})")
    
    print()
    print("=" * 70)
    print("Test completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    test_batch_vs_sequential()

# Made with Bob
