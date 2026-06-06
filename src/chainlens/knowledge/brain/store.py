"""BrainStore — manages brain state: loading, appending, versioning, markdown sync."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from chainlens.knowledge.brain.models import BrainVersion, CrawlResult, ReviewItem
from chainlens.models import KnowledgeEntry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DEFAULT_BRAIN_PATH = PROJECT_ROOT / "SECOND-KNOWLEDGE-BRAIN.md"
DEFAULT_STATE_PATH = PROJECT_ROOT / ".cache" / "brain_state.json"


class BrainStore:
    """Persistent brain state management."""

    def __init__(
        self,
        brain_path: str | Path | None = None,
        state_path: str | Path | None = None,
    ) -> None:
        self.brain_path = Path(brain_path or DEFAULT_BRAIN_PATH)
        self.state_path = Path(state_path or DEFAULT_STATE_PATH)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[KnowledgeEntry] = []
        self._version = BrainVersion()
        self._crawl_results: list[CrawlResult] = []
        self._conflict_queue: list[ReviewItem] = []
        self._quarantine: list[dict[str, Any]] = []
        self._load_state()

    # --- Entry management ---

    def load_entries(self) -> list[KnowledgeEntry]:
        return list(self._entries)

    def append_entry(self, entry: KnowledgeEntry) -> None:
        self._entries.append(entry)
        self._save_state()

    def get_version(self) -> BrainVersion:
        return self._version

    def bump_version(self) -> BrainVersion:
        self._version.bump()
        self._save_state()
        return self._version

    # --- Crawl results ---

    def record_crawl(self, result: CrawlResult) -> None:
        self._crawl_results.append(result)
        self._save_state()

    def get_last_crawl(self) -> CrawlResult | None:
        return self._crawl_results[-1] if self._crawl_results else None

    # --- Conflict & review ---

    def get_conflict_queue(self) -> list[ReviewItem]:
        return list(self._conflict_queue)

    def add_conflict(self, item: ReviewItem) -> None:
        self._conflict_queue.append(item)
        self._save_state()

    def resolve_conflict(self, entry_id: str, resolution: str) -> bool:
        for item in self._conflict_queue:
            if item.entry_id == entry_id and item.status == "pending":
                item.status = "resolved"
                item.resolution = resolution
                item.resolved_at = datetime.now(UTC)
                self._save_state()
                return True
        return False

    # --- Quarantine ---

    def add_to_quarantine(self, entry: dict[str, Any], reason: str) -> None:
        self._quarantine.append({
            "entry": entry,
            "reason": reason,
            "timestamp": datetime.now(UTC).isoformat(),
        })
        self._save_state()

    def get_quarantine(self) -> list[dict[str, Any]]:
        return list(self._quarantine)

    # --- Persistence ---

    def _state_dict(self) -> dict[str, Any]:
        return {
            "version": {"major": self._version.major, "minor": self._version.minor,
                         "batch_count": self._version.batch_count},
            "crawl_results": [
                {
                    "started_at": r.started_at.isoformat()
                    if isinstance(r.started_at, datetime)
                    else r.started_at,
                    "completed_at": r.completed_at.isoformat() if r.completed_at else None,
                    "entries_accepted": r.entries_accepted,
                    "entries_rejected": r.entries_rejected,
                    "conflicts_found": r.conflicts_found,
                    "quarantined": r.quarantined,
                }
                for r in self._crawl_results
            ],
            "conflict_queue": [
                {
                    "entry_id": q.entry_id,
                    "conflict_ids": q.conflict_ids,
                    "reason": q.reason,
                    "status": q.status,
                }
                for q in self._conflict_queue
            ],
            "quarantine": self._quarantine,
        }

    def _save_state(self) -> None:
        data = self._state_dict()
        data["entries"] = [e.model_dump() for e in self._entries]
        self.state_path.write_text(json.dumps(data, indent=2, default=str))

    def _load_state(self) -> None:
        if not self.state_path.exists():
            return
        try:
            data = json.loads(self.state_path.read_text())
            v = data.get("version", {})
            self._version = BrainVersion(
                major=v.get("major", 1),
                minor=v.get("minor", 0),
                batch_count=v.get("batch_count", 0),
            )
            self._entries = [KnowledgeEntry(**e) for e in data.get("entries", [])]
            self._crawl_results = [CrawlResult(**r) for r in data.get("crawl_results", [])]
            self._conflict_queue = [ReviewItem(**q) for q in data.get("conflict_queue", [])]
            self._quarantine = data.get("quarantine", [])
        except Exception:
            pass

    def sync_with_markdown(self) -> None:
        """Sync brain state to SECOND-KNOWLEDGE-BRAIN.md (append-only)."""
        if not self._entries:
            return
        latest = self._entries[-1]
        line = (
            f"- **{latest.id}** · *{latest.title}* · {latest.insight_type}\n"
            f"  - applies_to: {', '.join(latest.applies_to)}\n"
            f"  - Summary: {latest.summary}\n"
            f"  - Source: {latest.source.get('url', 'internal')}\n"
            f"  - Confidence: {latest.confidence} · Status: {latest.status}\n"
        )
        marker = "<!-- Future entries appended below by the Knowledge-Updater agent -->"
        content = self.brain_path.read_text(encoding="utf-8")
        if marker in content:
            content = content.replace(marker, line + "\n" + marker)
            self.brain_path.write_text(content, encoding="utf-8")
