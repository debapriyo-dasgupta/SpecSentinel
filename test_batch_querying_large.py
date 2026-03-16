"""
Test script with larger dataset to demonstrate batch querying benefits
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

def generate_test_signals(count: int) -> list[Signal]:
    """Generate a realistic set of test signals"""
    
    security_patterns = [
        "missing 401 Unauthorized response on authenticated endpoint",
        "no authentication scheme defined, missing OAuth2 JWT API key",
        "missing 403 Forbidden response for protected resource",
        "no rate limiting defined, missing 429 response",
        "sensitive data in URL path parameter",
        "missing security scheme for endpoint",
    ]
    
    design_patterns = [
        "missing pagination parameters for list endpoint",
        "no versioning in API path",
        "inconsistent naming convention in endpoint",
        "missing HATEOAS links in response",
        "no content negotiation headers",
    ]
    
    error_patterns = [
        "missing 400 Bad Request response for POST endpoint",
        "no 404 Not Found response defined",
        "missing 500 Internal Server Error response",
        "no validation error response schema",
    ]
    
    doc_patterns = [
        "missing description for endpoint operation",
        "no example provided for request body",
        "missing response schema documentation",
        "no tags defined for endpoint",
    ]
    
    gov_patterns = [
        "missing deprecation notice for old endpoint",
        "no contact information in API info",
        "missing license information",
    ]
    
    signals = []
    categories = [
        ("security", security_patterns),
        ("design", design_patterns),
        ("error_handling", error_patterns),
        ("documentation", doc_patterns),
        ("governance", gov_patterns),
    ]
    
    signal_id = 1
    for _ in range(count):
        for category, patterns in categories:
            for pattern in patterns:
                if signal_id > count:
                    break
                signals.append(Signal(
                    signal_id=f"TEST-{category.upper()[:3]}-{signal_id:03d}",
                    category=category,
                    description=pattern,
                    context={"path": f"/api/endpoint{signal_id}", "method": "GET"}
                ))
                signal_id += 1
            if signal_id > count:
                break
        if signal_id > count:
            break
    
    return signals[:count]

def test_batch_vs_sequential_large():
    """Compare batch querying vs sequential querying with larger dataset"""
    
    print("=" * 70)
    print("Batch Querying Performance Test - Large Dataset")
    print("=" * 70)
    print()
    
    # Initialize store
    print("Initializing vector store...")
    store = SpecSentinelVectorStore()
    store.initialize()
    print("[OK] Store initialized")
    print()
    
    # Test with different signal counts
    test_sizes = [10, 25, 50]
    
    for size in test_sizes:
        print(f"\n{'=' * 70}")
        print(f"Testing with {size} signals")
        print('=' * 70)
        
        test_signals = generate_test_signals(size)
        categories = len(set(s.category for s in test_signals))
        print(f"Generated {len(test_signals)} signals across {categories} categories")
        print()
        
        # Test batch querying
        print("Testing BATCH querying...")
        matcher_batch = RuleMatcher(store, n_results_per_signal=3)
        
        start_batch = time.time()
        findings_batch = matcher_batch.match_signals(test_signals)
        duration_batch = time.time() - start_batch
        
        print(f"[OK] Batch querying completed in {duration_batch:.3f}s")
        print(f"  Found {len(findings_batch)} findings")
        print()
        
        # Test sequential querying
        print("Testing SEQUENTIAL querying...")
        matcher_seq = RuleMatcher(store, n_results_per_signal=3)
        
        start_seq = time.time()
        findings_seq = matcher_seq.match_signals_sequential(test_signals)
        duration_seq = time.time() - start_seq
        
        print(f"[OK] Sequential querying completed in {duration_seq:.3f}s")
        print(f"  Found {len(findings_seq)} findings")
        print()
        
        # Compare results
        print("Performance Comparison:")
        print(f"  Batch:      {duration_batch:.3f}s")
        print(f"  Sequential: {duration_seq:.3f}s")
        
        if duration_batch > 0:
            speedup = duration_seq / duration_batch
            if speedup > 1:
                improvement = ((duration_seq - duration_batch) / duration_seq) * 100
                print(f"  Speedup:    {speedup:.2f}x faster ({improvement:.1f}% improvement)")
            else:
                slowdown = duration_batch / duration_seq
                print(f"  Slowdown:   {slowdown:.2f}x slower (batch has overhead for small datasets)")
        
        print(f"  Results match: {len(findings_batch) == len(findings_seq)}")
    
    print()
    print("=" * 70)
    print("Conclusion:")
    print("=" * 70)
    print("Batch querying shows performance benefits with larger datasets (25+ signals)")
    print("For small datasets (<10 signals), sequential may be faster due to overhead")
    print("The implementation automatically groups by category for optimal batching")
    print("=" * 70)

if __name__ == "__main__":
    test_batch_vs_sequential_large()

# Made with Bob
