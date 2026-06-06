"""Deterministic risk scoring — weighted formula with hard-cap logic."""

from __future__ import annotations

from chainlens.models import Finding, RiskScore

SEVERITY_MAP = {
    "critical": 1.0,
    "high": 0.8,
    "medium": 0.5,
    "low": 0.25,
    "info": 0.0,
}

DEFAULT_CRITICAL_SIGNALS = ["honeypot"]


def compute_risk_score(
    findings: list[Finding],
    weights: dict[str, float],
    critical_signals: list[str] | None = None,
) -> RiskScore:
    """Compute 0-100 deterministic risk score from findings.

    Formula:
        score = 100 * sum(w_i * s_i) / sum(w_i)
        where s_i = severity score (0.0 to 1.0)
        and w_i = configured weight for that signal

    Hard caps: if any critical signal has severity >= 'high',
    the score is floored at 85.
    """
    if critical_signals is None:
        critical_signals = DEFAULT_CRITICAL_SIGNALS

    total_weight = 0.0
    weighted_sum = 0.0
    breakdown: dict[str, float] = {}

    for f in findings:
        w = weights.get(f.signal, 0.0)
        if w <= 0:
            continue
        s = SEVERITY_MAP.get(f.severity, 0.0)
        weighted_sum += w * s
        total_weight += w
        # Per-signal contribution as percentage of max possible
        breakdown[f.signal] = round(w * s / total_weight * 100, 1) if total_weight > 0 else 0.0

    score = 0.0
    if total_weight > 0:
        score = round(100.0 * weighted_sum / total_weight, 1)
        score = min(score, 100.0)

    # Hard-cap logic: if any critical signal fires, floor at 85
    hard_caps: list[str] = []
    for f in findings:
        if f.signal in critical_signals and SEVERITY_MAP.get(f.severity, 0) >= 0.8:
            hard_caps.append(f.signal)
            score = max(score, 85.0)

    return RiskScore(score=score, breakdown=breakdown, hard_caps=hard_caps)
