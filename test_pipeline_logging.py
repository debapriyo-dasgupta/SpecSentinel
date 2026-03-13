"""
Test script to verify pipeline logging is working
This directly tests the _run_pipeline function
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import after path is set
from src.api.app import _run_pipeline, store
from src.vectordb.store.chroma_client import SpecSentinelVectorStore

print("=" * 70)
print("Testing Pipeline Logging")
print("=" * 70)
print()

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
    print("Please provide a valid OpenAPI spec file")
    sys.exit(1)

print(f"Loading test spec: {test_spec_path}")
with open(test_spec_path) as f:
    spec = json.load(f)

print(f"Spec loaded: {spec.get('info', {}).get('title', 'Unknown')}")
print()

print("Running pipeline with logging...")
print("-" * 70)
print()

try:
    # Run the pipeline - this should generate pipeline logs
    report = _run_pipeline(spec, "petStoreSwagger.json")
    
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
print("Check the logs:")
print("=" * 70)
print()
print("  Get-Content logs\\specsentinel.pipeline.log")
print("  Get-Content logs\\specsentinel.api.log")
print()
print("If you see pipeline stages above, logging is working!")
print()

# Made with Bob
