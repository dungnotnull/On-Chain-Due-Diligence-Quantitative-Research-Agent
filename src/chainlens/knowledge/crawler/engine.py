"""CrawlEngine — orchestrates multi-source crawling."""

from __future__ import annotations

from typing import Any

from chainlens.knowledge.crawler.sources import ArxivCrawler


class CrawlEngine:
    """Orchestrates crawling across all configured sources."""

    def __init__(self) -> None:
        self.arxiv = ArxivCrawler()

    async def run(
        self,
        topics: list[str] | None = None,  # noqa: ARG002
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Crawl all sources and return raw source entries."""
        all_sources: list[dict[str, Any]] = []

        try:
            audit_papers = await self.arxiv.crawl_audit_papers(max_results)
            all_sources.extend(audit_papers)
        except Exception:
            pass

        try:
            quant_papers = await self.arxiv.crawl_quant_papers(max_results)
            all_sources.extend(quant_papers)
        except Exception:
            pass

        return all_sources
