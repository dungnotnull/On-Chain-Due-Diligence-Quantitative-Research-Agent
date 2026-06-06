"""Source-specific crawlers: arXiv, audit reports, EIPs."""

from __future__ import annotations

from typing import Any

from chainlens.collectors.base import AsyncCollectorBase


class ArxivCrawler(AsyncCollectorBase):
    """Crawl recent papers from arXiv by category."""

    def __init__(self) -> None:
        super().__init__(ttl_hours=24)
        self.base_url = "http://export.arxiv.org/api/query"

    async def fetch_by_category(
        self, category: str = "cs.CR", max_results: int = 10
    ) -> list[dict[str, Any]]:
        params = {
            "search_query": f"cat:{category}",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(max_results),
        }
        resp = await self._request("GET", self.base_url, params=params)
        raw = resp.text
        entries: list[dict[str, Any]] = []
        # Simple XML parsing — extract entry blocks
        for block in raw.split("<entry>")[1:]:
            title = _extract_xml(block, "title")
            summary = _extract_xml(block, "summary")
            entry_id = _extract_xml(block, "id")
            published = _extract_xml(block, "published")
            entries.append({
                "id": entry_id,
                "title": title,
                "summary": summary[:500] if summary else "",
                "published": published,
                "source_type": "arxiv",
                "url": entry_id,
                "authors": [a.strip() for a in block.split("<name>")[1:]]
                if "<name>" in block
                else [],
            })
        return entries

    async def crawl_audit_papers(self, max_results: int = 10) -> list[dict[str, Any]]:
        return await self.fetch_by_category("cs.CR", max_results)

    async def crawl_quant_papers(self, max_results: int = 10) -> list[dict[str, Any]]:
        return await self.fetch_by_category("q-fin", max_results)


def _extract_xml(block: str, tag: str) -> str:
    """Extract a single XML tag's text content."""
    start = block.find(f"<{tag}>")
    end = block.find(f"</{tag}>")
    if start == -1 or end == -1:
        return ""
    return block[start + len(tag) + 2 : end].strip()
