"""Quality gate: credibility, relevance, recency, dedup, and conflict checks."""

from chainlens.knowledge.gatekeeper.checks import (
    check_conflict,
    check_dedup,
    check_extractability,
    check_provenance,
    check_recency,
    check_relevance,
    check_source_credibility,
)
from chainlens.knowledge.gatekeeper.engine import GateKeeper

__all__ = [
    "GateKeeper",
    "check_source_credibility",
    "check_relevance",
    "check_recency",
    "check_dedup",
    "check_conflict",
    "check_extractability",
    "check_provenance",
]
