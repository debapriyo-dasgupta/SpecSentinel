"""
specsentinel/tests/test_pipeline.py

Quick integration test — runs the full SpecSentinel pipeline locally
without needing to start the FastAPI server.

Run from the specsentinel/ directory:
    python tests/test_pipeline.py
"""

import sys
import yaml
import json
from pathlib import Path

# Path setup
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.vectordb.store.chroma_client import SpecSentinelVectorStore
from src.backend.engine.signal_extractor import OpenAPISignalExtractor
from src.backend.engine.rule_matcher import RuleMatcher
from src.backend.engine.scorer import compute_health_score
from src.backend.engine.reporter import build_report, render_text_report


def main():
    print("=" * 60)
    print("  SpecSentinel — Pipeline Integration Test")
    print("=" * 60)

    # ── Step 1: Initialize vector store ──────────────────────────────
    print("\n[1/5] Initializing Vector Store...")
    store = SpecSentinelVectorStore()
    store.initialize()

    stats = store.get_collection_stats()
    print(f"  Rule counts: {stats}")

    # ── Step 2: Load test spec ────────────────────────────────────────
    print("\n[2/5] Loading test spec...")
    spec_path = Path(__file__).parent / "sample_bad_spec.yaml"
    if not spec_path.exists():
        spec_path = Path("sample_bad_spec.yaml")
    with open(spec_path) as f:
        spec = yaml.safe_load(f)
    print(f"  Paths: {len(spec.get('paths', {}))}")

    # ── Step 3: Extract signals ───────────────────────────────────────
    print("\n[3/5] Extracting signals...")
    extractor = OpenAPISignalExtractor(spec)
    signals   = extractor.extract_all()
    print(f"  {len(signals)} signals extracted:")
    for s in signals[:8]:
        print(f"    [{s.category}] {s.signal_id}: {s.description[:70]}...")

    # ── Step 4: Match rules from vector DB ────────────────────────────
    print("\n[4/5] Matching rules from Vector DB...")
    matcher  = RuleMatcher(store, n_results_per_signal=3)
    findings = matcher.match_signals(signals)
    print(f"  {len(findings)} findings matched:")
    for f in findings[:5]:
        top = f.top_match
        if top:
            print(f"    [{top.severity}] {top.rule_id}: {top.title[:60]} (sim={top.similarity:.2f})")

    # ── Step 5: Score + Report ────────────────────────────────────────
    print("\n[5/5] Computing health score and generating report...")
    health = compute_health_score(findings)
    report = build_report("sample_bad_spec.yaml", health, findings)

    print("\n" + render_text_report(report))

    # Save JSON report
    output_path = Path(__file__).parent / "report_output.json"
    if not output_path.parent.exists():
        output_path = Path("report_output.json")
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n✅ Full JSON report saved to: {output_path}")


if __name__ == "__main__":
    main()
