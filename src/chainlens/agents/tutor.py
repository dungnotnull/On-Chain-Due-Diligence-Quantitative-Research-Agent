"""Tutor — learn mode engine with topic explanations, levels, and real examples."""

from __future__ import annotations

from datetime import UTC, datetime

from chainlens.agents.curriculum import get_curriculum
from chainlens.knowledge.brain.store import BrainStore
from chainlens.knowledge.indexer.engine import VectorIndex
from chainlens.models import Report, ReportMeta


class Tutor:
    """Learn mode — explains concepts step by step with real cited examples."""

    def __init__(
        self,
        brain: BrainStore | None = None,
        index: VectorIndex | None = None,
    ) -> None:
        self.brain = brain or BrainStore()
        self.index = index or VectorIndex()
        if not self.index._entries and self.brain.load_entries():
            self.index.rebuild(self.brain.load_entries())

    def explain_topic(
        self,
        topic: str,
        level: str = "beginner",
    ) -> Report:
        """Generate a learn report for a given topic at the specified level."""
        curriculum = get_curriculum(topic, level)

        # Retrieve relevant knowledge
        kb_entries = self.index.search(topic, top_k=3) if self.index._entries else []

        lines: list[str] = []
        lines.append(f"# Learn: {curriculum['title']}\n")
        lines.append(f"**Level:** {level}\n")
        lines.append(f"**Generated:** {datetime.now(UTC).isoformat()}\n")
        lines.append("---\n")

        # Concept explanation
        lines.append("## What Is This?\n")
        lines.append(curriculum["explanation"] + "\n")

        # Section-by-section
        for section in curriculum.get("sections", []):
            lines.append(f"## {section['title']}\n")
            lines.append(section["content"] + "\n")
            if section.get("example"):
                lines.append(f"> **Example:** {section['example']}\n")

        # Real examples from knowledge base
        if kb_entries:
            lines.append("## Real-World Examples\n")
            for entry in kb_entries:
                lines.append(f"- **{entry.title}** — {entry.summary[:200]}\n")
                url = entry.source.get("url", "N/A")
                lines.append(f"  *Source: {url} | Confidence: {entry.confidence}*\n")

        lines.append("---\n")
        lines.append("## Key Takeaways\n")
        for tip in curriculum.get("takeaways", []):
            lines.append(f"- {tip}\n")

        lines.append("\n---\n")
        lines.append(f"*Brain version: {self.brain.get_version()} | "
                      f"Knowledge entries consulted: {len(kb_entries)}*\n")

        meta = ReportMeta(
            timestamp=datetime.now(UTC),
            mode="learn",
            target=topic,
            chain="",
            brain_version=str(self.brain.get_version()),
        )

        return Report(
            meta=meta,
            knowledge_entries=[e.id for e in kb_entries],
        )
