"""
specsentinel/engine/reporter.py

Generates a structured API Health Report from scorer output and findings.
Produces both dict (JSON-serializable) and human-readable text formats.
"""

import json
from datetime import datetime
from src.backend.engine.rule_matcher import FindingGroup, RuleMatch
from src.backend.engine.scorer import HealthScore, CategoryScore


def build_report(
    spec_name: str,
    health: HealthScore,
    findings: list[FindingGroup],
) -> dict:
    """
    Build a full JSON-serializable API Health Report.

    Returns:
        dict with keys: meta, health_score, category_breakdown,
                        findings, benchmark_alignment, recommendations
    """
    now = datetime.utcnow().isoformat() + "Z"

    # ── Findings list ──────────────────────────────────────────────────────────
    finding_items = []
    for group in sorted(
        findings,
        key=lambda g: _severity_order(g.highest_severity),
        reverse=True,
    ):
        top = group.top_match
        if not top:
            continue

        finding_items.append({
            "signal_id":     group.signal.signal_id,
            "title":         top.title,
            "severity":      top.severity,
            "category":      top.category,
            "source":        top.source,
            "benchmark":     top.benchmark,
            "evidence":      group.signal.evidence,
            "context":       group.signal.context,
            "check_pattern": top.check_pattern,
            "fix_guidance":  top.fix_guidance,
            "tags":          top.tags,
            "rule_id":       top.rule_id,
            "similarity":    top.similarity,
        })

    # ── Category breakdown ────────────────────────────────────────────────────
    category_rows = []
    for cat, cs in health.categories.items():
        category_rows.append({
            "category":  cat,
            "weight_pct": cs.weight,
            "score":     cs.raw_score,
            "weighted":  cs.weighted,
            "findings":  cs.findings,
            "deductions": cs.deductions,
        })

    # ── Benchmark alignment ───────────────────────────────────────────────────
    benchmark_map: dict[str, dict] = {}
    for group in findings:
        top = group.top_match
        if not top:
            continue
        bm = top.benchmark or "General"
        if bm not in benchmark_map:
            benchmark_map[bm] = {"total": 0, "issues": 0, "critical": 0, "high": 0}
        benchmark_map[bm]["total"] += 1
        benchmark_map[bm]["issues"] += 1
        if top.severity == "Critical":
            benchmark_map[bm]["critical"] += 1
        elif top.severity == "High":
            benchmark_map[bm]["high"] += 1

    benchmark_alignment = []
    for bm, data in benchmark_map.items():
        compliance_pct = max(0, round(100 - (data["issues"] / max(data["total"], 1)) * 40, 1))
        benchmark_alignment.append({
            "benchmark":      bm,
            "issues_found":   data["issues"],
            "critical":       data["critical"],
            "high":           data["high"],
            "compliance_pct": compliance_pct,
        })

    # ── Top recommendations (Critical + High only) ────────────────────────────
    recommendations = []
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    priority_findings = sorted(
        [g for g in findings if g.top_match and g.top_match.severity in ("Critical", "High")],
        key=lambda g: priority_order.get(g.top_match.severity, 99),
    )
    for group in priority_findings[:10]:
        top = group.top_match
        recommendations.append({
            "priority":     top.severity,
            "title":        top.title,
            "issue":        group.signal.description,
            "evidence":     group.signal.evidence,
            "fix":          top.fix_guidance,
            "benchmark":    top.benchmark,
            "rule_id":      top.rule_id,
        })

    return {
        "meta": {
            "spec_name":    spec_name,
            "generated_at": now,
            "tool":         "SpecSentinel v1.0",
        },
        "health_score": {
            "total":                 health.total,
            "band":                  health.band,
            "band_emoji":            health.band_emoji,
            "projected_after_fixes": health.projected_after_fixes,
            "finding_counts": {
                "total":    health.finding_count,
                "critical": health.critical_count,
                "high":     health.high_count,
                "medium":   health.medium_count,
                "low":      health.low_count,
            },
        },
        "category_breakdown":  category_rows,
        "benchmark_alignment": benchmark_alignment,
        "findings":            finding_items,
        "recommendations":     recommendations,
    }


def render_text_report(report: dict) -> str:
    """Render a human-readable text version of the report."""
    hs = report["health_score"]
    meta = report["meta"]
    lines = [
        "=" * 65,
        f"  SPECSENTINEL API HEALTH REPORT",
        f"  Spec: {meta['spec_name']}",
        f"  Generated: {meta['generated_at']}",
        "=" * 65,
        "",
        f"  OVERALL HEALTH SCORE: {hs['total']}/100  {hs['band_emoji']} {hs['band']}",
        f"  Projected after fixes: {hs['projected_after_fixes']}/100",
        "",
        f"  Issues: {hs['finding_counts']['critical']} Critical | "
        f"{hs['finding_counts']['high']} High | "
        f"{hs['finding_counts']['medium']} Medium | "
        f"{hs['finding_counts']['low']} Low",
        "",
        "─" * 65,
        "  CATEGORY BREAKDOWN",
        "─" * 65,
    ]

    for row in report["category_breakdown"]:
        bar_len = int(row["score"] / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(
            f"  {row['category']:<16} [{bar}] {row['score']:>5}/100  "
            f"({row['findings']} issues, weight {row['weight_pct']}%)"
        )

    lines += [
        "",
        "─" * 65,
        "  BENCHMARK ALIGNMENT",
        "─" * 65,
    ]
    for bm in report["benchmark_alignment"]:
        lines.append(
            f"  {bm['benchmark']:<35} {bm['compliance_pct']:>5}% compliant  "
            f"({bm['issues_found']} issues)"
        )

    lines += [
        "",
        "─" * 65,
        "  TOP PRIORITY FIXES",
        "─" * 65,
    ]
    for i, rec in enumerate(report["recommendations"], 1):
        lines += [
            f"",
            f"  [{rec['priority']}] {i}. {rec['title']}",
            f"     Issue:   {rec['issue']}",
            f"     Fix:     {rec['fix'][:120]}{'...' if len(rec['fix']) > 120 else ''}",
            f"     Source:  {rec['benchmark']} | Rule: {rec['rule_id']}",
        ]

    lines += [
        "",
        "=" * 65,
        f"  Total findings: {hs['finding_counts']['total']}  |  "
        f"SpecSentinel v1.0  |  Agentic API Governance",
        "=" * 65,
    ]
    return "\n".join(lines)


def _severity_order(sev: str) -> int:
    return {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}.get(sev, 0)
