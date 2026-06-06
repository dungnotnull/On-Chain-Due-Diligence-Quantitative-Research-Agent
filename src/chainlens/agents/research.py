"""ResearchAgent — combines audit + quant + tokenomics + knowledge context."""

from __future__ import annotations

from datetime import UTC, datetime

from chainlens.models import Report, ReportMeta


class ResearchAgent:
    """Produces a combined research dossier from all engines."""

    def __init__(self, orchestrator) -> None:
        self.orch = orchestrator

    def run(
        self,
        token: str,
        chain: str = "ethereum",
        window_days: int = 90,
    ) -> Report:
        """Run audit + quant + knowledge retrieval, then combine into one report."""
        address = token if token.startswith("0x") else ""
        symbol = token if not address else ""

        # Run audit
        audit_report = self.orch.run_audit(address, chain)

        # Run quant
        quant_report = self.orch.run_quant(symbol or address, window_days, chain)

        # Knowledge context
        kb_entries: list[str] = []
        search_terms = f"{symbol} {chain} token risk analysis"
        if self.orch.index:
            entries = self.orch.index.search(search_terms, top_k=3)
            kb_entries = [e.id for e in entries]

        # Merge into single report
        meta = ReportMeta(
            timestamp=datetime.now(UTC),
            mode="research",
            target=token,
            chain=chain,
            window_days=window_days,
            brain_version=str(self.orch.brain.get_version()),
        )

        return Report(
            meta=meta,
            findings=audit_report.findings,
            metrics=quant_report.metrics,
            risk_score=audit_report.risk_score,
            knowledge_entries=kb_entries,
            data_quality={
                "audit_complete": len(audit_report.findings) > 0,
                "quant_complete": len(quant_report.metrics) > 0,
            },
        )
