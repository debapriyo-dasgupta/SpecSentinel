"""
specsentinel/engine/scorer.py

Computes the SpecSentinel API Health Score (0–100) from rule match findings.
Applies weighted deductions per category and severity, and produces a
maturity band and per-category breakdown.
"""

from dataclasses import dataclass, field
from src.backend.engine.rule_matcher import FindingGroup


# ── Scoring weights per category (must sum to 100) ────────────────────────────
CATEGORY_WEIGHTS = {
    "Security":      35,
    "Design":        20,
    "ErrorHandling": 15,
    "Documentation": 15,
    "Governance":    15,
}

# ── Severity deduction points ─────────────────────────────────────────────────
SEVERITY_DEDUCTIONS = {
    "Critical": 20,
    "High":     12,
    "Medium":    6,
    "Low":       2,
}

# ── Maturity bands ────────────────────────────────────────────────────────────
MATURITY_BANDS = [
    (86, 100, "Excellent", "✅"),
    (71, 85,  "Good",      "🟢"),
    (41, 70,  "Moderate",  "🟡"),
    (0,  40,  "Poor",      "🔴"),
]


@dataclass
class CategoryScore:
    category:    str
    weight:      int           # contribution % to total
    raw_score:   float         # 0–100 within category
    weighted:    float         # raw_score * weight/100
    findings:    int           # number of issues found
    deductions:  dict = field(default_factory=dict)   # severity → count


@dataclass
class HealthScore:
    total:         float                      # 0–100
    band:          str                        # Poor / Moderate / Good / Excellent
    band_emoji:    str
    categories:    dict[str, CategoryScore]   # keyed by category name
    finding_count: int
    critical_count: int
    high_count:     int
    medium_count:   int
    low_count:      int
    projected_after_fixes: float              # projected score if all Critical+High fixed


def compute_health_score(findings: list[FindingGroup]) -> HealthScore:
    """
    Compute the overall API Health Score from a list of FindingGroups.

    Each finding group contributes deductions to its category based on
    the severity of matched rules.
    """

    # Initialise per-category deduction tracking
    cat_deductions: dict[str, list[str]] = {c: [] for c in CATEGORY_WEIGHTS}

    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

    for group in findings:
        top = group.top_match
        if not top:
            continue

        cat_key = _normalize_category(top.category)
        if cat_key not in cat_deductions:
            cat_key = "Design"   # fallback

        cat_deductions[cat_key].append(top.severity)
        if top.severity in severity_counts:
            severity_counts[top.severity] += 1

    # Compute per-category scores
    category_scores: dict[str, CategoryScore] = {}
    weighted_total = 0.0

    for cat, weight in CATEGORY_WEIGHTS.items():
        sevs = cat_deductions.get(cat, [])
        deduction_map: dict[str, int] = {}
        total_deduction = 0

        for sev in sevs:
            pts = SEVERITY_DEDUCTIONS.get(sev, 0)
            total_deduction += pts
            deduction_map[sev] = deduction_map.get(sev, 0) + 1

        raw = max(0.0, 100.0 - total_deduction)
        weighted = raw * weight / 100.0

        category_scores[cat] = CategoryScore(
            category=cat,
            weight=weight,
            raw_score=round(raw, 1),
            weighted=round(weighted, 2),
            findings=len(sevs),
            deductions=deduction_map,
        )
        weighted_total += weighted

    total = round(min(100.0, max(0.0, weighted_total)), 1)

    # Maturity band
    band, emoji = "Poor", "🔴"
    for lo, hi, label, em in MATURITY_BANDS:
        if lo <= total <= hi:
            band, emoji = label, em
            break

    # Projected score: what if all Critical + High are fixed?
    projected_deduction = (
        severity_counts["Critical"] * SEVERITY_DEDUCTIONS["Critical"] +
        severity_counts["High"]     * SEVERITY_DEDUCTIONS["High"]
    )
    projected = round(min(100.0, total + projected_deduction * 0.4), 1)

    return HealthScore(
        total=total,
        band=band,
        band_emoji=emoji,
        categories=category_scores,
        finding_count=len(findings),
        critical_count=severity_counts["Critical"],
        high_count=severity_counts["High"],
        medium_count=severity_counts["Medium"],
        low_count=severity_counts["Low"],
        projected_after_fixes=projected,
    )


def _normalize_category(cat: str) -> str:
    """Map category strings to CATEGORY_WEIGHTS keys."""
    mapping = {
        "security":       "Security",
        "Security":       "Security",
        "design":         "Design",
        "Design":         "Design",
        "error_handling": "ErrorHandling",
        "ErrorHandling":  "ErrorHandling",
        "documentation":  "Documentation",
        "Documentation":  "Documentation",
        "governance":     "Governance",
        "Governance":     "Governance",
    }
    return mapping.get(cat, "Design")
