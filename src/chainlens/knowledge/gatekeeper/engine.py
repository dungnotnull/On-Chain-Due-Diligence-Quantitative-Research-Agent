"""GateKeeper — runs all quality checks and returns passed/quarantined/conflict lists."""

from __future__ import annotations

from typing import Any

from chainlens.knowledge.brain.models import ReviewItem
from chainlens.knowledge.gatekeeper.checks import (
    check_conflict,
    check_dedup,
    check_extractability,
    check_provenance,
    check_recency,
    check_relevance,
    check_source_credibility,
)
from chainlens.models import KnowledgeEntry


class GateKeeper:
    """Quality gate orchestrator — runs 7 checks on each source."""

    def __init__(self) -> None:
        self.check_results: dict[str, list[tuple[str, bool]]] = {}

    def gate(
        self,
        raw_sources: list[dict[str, Any]],
        existing_entries: list[KnowledgeEntry],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[ReviewItem]]:
        """Run all quality checks. Returns (passed, quarantined, conflicts)."""
        passed: list[dict[str, Any]] = []
        quarantined: list[dict[str, Any]] = []
        conflicts: list[ReviewItem] = []

        for source in raw_sources:
            source_id = source.get("id", "unknown")
            results: list[tuple[str, bool]] = []

            # Run all checks
            checks = [
                ("source_credibility", check_source_credibility(source)),
                ("relevance", check_relevance(source)),
                ("recency", check_recency(source)),
                ("dedup", check_dedup(source, existing_entries)),
                ("extractability", check_extractability(source)),
                ("provenance", check_provenance(source)),
            ]

            for check_name, passed_check in checks:
                results.append((check_name, passed_check))

            self.check_results[source_id] = results

            if not all(r[1] for r in results):
                quarantined.append(source)
                continue

            # Conflict check
            conflict_id = check_conflict(source, existing_entries)
            if conflict_id:
                review = ReviewItem(
                    entry_id=source_id,
                    conflict_ids=[conflict_id],
                    reason="Contradicts existing entry",
                )
                conflicts.append(review)
                continue

            passed.append(source)

        return passed, quarantined, conflicts
