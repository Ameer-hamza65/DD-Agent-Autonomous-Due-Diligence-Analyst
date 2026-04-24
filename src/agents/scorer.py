"""Deterministic, explainable red-flag scorer."""
from typing import Dict, List

WEIGHTS = {"financial": 0.30, "risk": 0.25, "news": 0.20, "market": 0.15, "tech": 0.10}
SEVERITY_VALUE = {"red": 1.0, "yellow": 0.5, "info": 0.0}


def _rating(score: float) -> str:
    if score < 0.15: return "Strong Buy"
    if score < 0.30: return "Buy"
    if score < 0.50: return "Hold"
    if score < 0.70: return "Caution"
    return "Avoid"


def scoring_node(state: dict) -> dict:
    findings: List[Dict] = state.get("findings", [])
    breakdown = {}
    for category in WEIGHTS:
        cat_findings = [f for f in findings if f.get("category") == category]
        if not cat_findings:
            breakdown[category] = 0.0
            continue
        breakdown[category] = round(sum(
            SEVERITY_VALUE.get(f["severity"], 0) * f["confidence"]
            for f in cat_findings
        ) / len(cat_findings), 3)
    final = round(sum(breakdown[c] * w for c, w in WEIGHTS.items()), 3)
    red_flags = sorted([f for f in findings if f["severity"] == "red"],
                       key=lambda f: -f["confidence"])[:5]
    strengths = sorted(
        [f for f in findings if f["severity"] == "info" and f["confidence"] >= 0.7],
        key=lambda f: -f["confidence"])[:5]
    return {
        "red_flag_score": final,
        "score_breakdown": breakdown,
        "rating": _rating(final),
        "top_red_flags": red_flags,
        "top_strengths": strengths,
    }
