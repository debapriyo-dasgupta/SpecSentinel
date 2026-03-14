"""
Test script to verify streaming endpoint generates pipeline logs
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("Testing Streaming Endpoint Pipeline Logging")
print("=" * 70)
print()

# Import after path is set
from src.api.app import store
from src.vectordb.store.chroma_client import SpecSentinelVectorStore

# Initialize store if needed
if store is None:
    print("Initializing vector store...")
    from src.api import app as app_module
    app_module.store = SpecSentinelVectorStore()
    app_module.store.initialize()
    print("Store initialized")
    print()

# Load a test spec
test_spec_path = Path(__file__).parent / "tests" / "petStoreSwagger.json"

if not test_spec_path.exists():
    print(f"ERROR: Test spec not found at {test_spec_path}")
    sys.exit(1)

print(f"Loading test spec: {test_spec_path}")
with open(test_spec_path) as f:
    spec = json.load(f)

print(f"Spec loaded: {spec.get('info', {}).get('title', 'Unknown')}")
print()

print("Simulating streaming endpoint pipeline...")
print("-" * 70)
print()

# Import the necessary components
from src.utils.logging_config import PipelineLogger
from src.engine.signal_extractor import OpenAPISignalExtractor
from src.engine.rule_matcher import RuleMatcher
from src.engine.scorer import compute_health_score
from src.engine.reporter import build_report

try:
    # Create pipeline logger (same as streaming endpoint)
    pipeline = PipelineLogger()
    spec_name = "petStoreSwagger.json"
    
    # PLAN stage
    pipeline.start_stage("PLAN", spec_name=spec_name)
    paths_count = len(spec.get('paths', {}))
    schemas_count = len(spec.get('components', {}).get('schemas', {}) or {})
    pipeline.end_stage("PLAN", paths=paths_count, schemas=schemas_count)
    
    # ANALYZE stage
    pipeline.start_stage("ANALYZE", spec_name=spec_name)
    extractor = OpenAPISignalExtractor(spec)
    signals = extractor.extract_all()
    pipeline.end_stage("ANALYZE", signals_count=len(signals))
    
    # MATCH stage
    pipeline.start_stage("MATCH", signals_count=len(signals))
    matcher = RuleMatcher(store, n_results_per_signal=3)
    findings = matcher.match_signals(signals)
    pipeline.end_stage("MATCH", findings_count=len(findings))
    
    # SCORE stage
    pipeline.start_stage("SCORE", findings_count=len(findings))
    health = compute_health_score(findings)
    pipeline.end_stage("SCORE", health_score=health.total, band=health.band)
    
    # REPORT stage
    pipeline.start_stage("REPORT", spec_name=spec_name)
    report = build_report(spec_name, health, findings)
    pipeline.end_stage("REPORT", findings_count=len(report['findings']))
    
    print()
    print("-" * 70)
    print("Pipeline completed successfully!")
    print()
    print(f"Health Score: {report['health_score']['total']}/100")
    print(f"Findings: {len(report['findings'])}")
    print()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
print("SUCCESS! Pipeline logs should now appear above.")
print("=" * 70)
print()
print("Now restart your backend server and try uploading a file.")
print("You should see pipeline logs in the console!")
print()

# Made with Bob
