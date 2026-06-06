"""Quality gate checks — each returns True (pass) or False (reject)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from chainlens.models import KnowledgeEntry

REPUTABLE_DOMAINS = [
    "arxiv.org",
    "ieee.org",
    "acm.org",
    "springer.com",
    "tandfonline.com",
    "wiley.com",
    "sciencedirect.com",
    "trailofbits.com",
    "blog.trailofbits.com",
    "consensys.net",
    "openzeppelin.com",
    "github.com/ethereum/EIPs",
    "eips.ethereum.org",
]

REPUTABLE_AUDIT_FIRMS = [
    "trailofbits",
    "consensys diligence",
    "openzeppelin",
    "certik",
    "slowmist",
    "quantstamp",
    "hacken",
    "halborn",
]

TRACKED_TOPICS = {
    "smart-contract-security",
    "tokenomics",
    "on-chain-analytics",
    "quant-methodology",
    "regulatory-compliance",
}


def check_source_credibility(source: dict[str, Any]) -> bool:
    """Reject if source is not from a reputable venue."""
    url = source.get("url", "").lower()
    venue = source.get("venue", "").lower()
    source_type = source.get("type", "").lower()

    for domain in REPUTABLE_DOMAINS:
        if domain in url:
            return True
    for firm in REPUTABLE_AUDIT_FIRMS:
        if firm in venue or firm in url:
            return True
    return source_type in ("peer_reviewed", "eip", "official_doc")


def check_relevance(source: dict[str, Any], topics: list[str] | None = None) -> bool:
    """Check if source matches tracked topics."""
    if topics is None:
        topics = list(TRACKED_TOPICS)
    title = (source.get("title", "") + " " + source.get("summary", "")).lower()
    return any(topic.replace("-", " ") in title for topic in topics)


def check_recency(source: dict[str, Any], max_age_days: int = 365) -> bool:
    """Reject sources older than max_age_days."""
    published = source.get("published")
    if not published:
        return False
    try:
        pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return False
    age = (datetime.now(UTC) - pub_date).days
    return age <= max_age_days


def check_dedup(
    source: dict[str, Any],
    existing_entries: list[KnowledgeEntry],
    similarity_threshold: float = 0.8,
) -> bool:
    """Return False if a similar entry already exists (simple word-overlap dedup)."""
    title = (source.get("title", "") or "").lower()
    summary = (source.get("summary", "") or "").lower()
    source_words = set((title + " " + summary).split())
    if not source_words:
        return False
    for entry in existing_entries:
        entry_words = set((entry.title + " " + entry.summary).split())
        if not entry_words:
            continue
        overlap = len(source_words & entry_words) / len(source_words | entry_words)
        if overlap >= similarity_threshold:
            return False
    return True


def check_conflict(
    source: dict[str, Any],
    existing_entries: list[KnowledgeEntry],
) -> str | None:
    """Return entry_id of conflicting entry, or None if no conflict."""
    summary = (source.get("summary", "") or "").lower()
    for entry in existing_entries:
        if entry.status != "active":
            continue
        entry_summary = entry.summary.lower()
        # Simple heuristic: if one says "high" and other says "low" -> conflict
        conflict_indicators = [
            ("high risk", "low risk"),
            ("significant", "negligible"),
            ("always", "never"),
        ]
        for a, b in conflict_indicators:
            if (a in summary and b in entry_summary) or (
                b in summary and a in entry_summary
            ):
                return entry.id
    return None


def check_extractability(source: dict[str, Any]) -> bool:
    """Check source contains a concrete, usable insight."""
    summary = source.get("summary", "") or ""
    has_numbers = any(c.isdigit() for c in summary)
    has_method_words = any(
        w in summary.lower()
        for w in ["method", "pattern", "threshold", "metric", "finding", "analysis"]
    )
    return has_numbers or has_method_words


def check_provenance(source: dict[str, Any]) -> bool:
    """Check source has required provenance fields."""
    return bool(source.get("url")) and bool(source.get("title"))
