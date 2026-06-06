"""Knowledge-specific models: versioning, crawl results, review queue items."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BrainVersion:
    major: int = 1
    minor: int = 0
    batch_count: int = 0

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}"

    def bump(self) -> BrainVersion:
        self.minor += 1
        self.batch_count += 1
        return self


@dataclass
class CrawlResult:
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    entries_scanned: int = 0
    entries_accepted: int = 0
    entries_rejected: int = 0
    conflicts_found: int = 0
    quarantined: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class ReviewItem:
    entry_id: str
    conflict_ids: list[str]
    reason: str
    status: str = "pending"  # pending | resolved | rejected
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = None
    resolution: str | None = None
