"""Extractor — converts gated sources into KnowledgeEntry objects."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from chainlens.models import KnowledgeEntry

_next_id_counter = 0


def _next_kb_id() -> str:
    global _next_id_counter
    _next_id_counter += 1
    date_part = datetime.now(UTC).strftime("%Y%m%d")
    return f"KB-{date_part}-{_next_id_counter:04d}"


TOPIC_MAP: dict[str, str] = {
    "cs.CR": "smart-contract-security",
    "q-fin": "quant-methodology",
    "security": "smart-contract-security",
    "tokenomics": "tokenomics",
    "onchain": "on-chain-analytics",
    "quant": "quant-methodology",
    "regulation": "regulatory-compliance",
}


class Extractor:
    """Convert gated sources into KnowledgeEntry objects."""

    def extract(
        self,
        source: dict[str, Any],
        topic: str | None = None,
    ) -> KnowledgeEntry:
        title = source.get("title", "Untitled")[:200]
        summary = source.get("summary", "")[:500]

        resolved_topic = topic or "smart-contract-security"
        for key, val in TOPIC_MAP.items():
            if key in (title + summary).lower():
                resolved_topic = val
                break

        applies_to: list[Literal["audit", "quant", "research", "learn"]] = ["research"]
        if "security" in resolved_topic or "audit" in resolved_topic.lower():
            applies_to = ["audit", "research"]
        elif "quant" in resolved_topic:
            applies_to = ["quant", "research"]

        confidence: Literal["high", "medium", "low"] = "medium"
        source_type = source.get("source_type", "")
        if source_type == "peer_reviewed" or "arxiv" in source_type:
            confidence = "high"
        elif source_type == "blog" or "medium" in source_type:
            confidence = "low"

        entry = KnowledgeEntry(
            id=_next_kb_id(),
            title=title,
            topic=resolved_topic,
            summary=summary,
            insight_type="finding",
            applies_to=applies_to,
            source={
                "type": source.get("source_type", "unknown"),
                "url": source.get("url", ""),
                "authors": source.get("authors", []),
                "venue": source.get("venue", ""),
                "year": source.get("published", "")[:4] if source.get("published") else "",
            },
            retrieved_at=datetime.now(UTC),
            confidence=confidence,
            status="active",
        )
        return entry
