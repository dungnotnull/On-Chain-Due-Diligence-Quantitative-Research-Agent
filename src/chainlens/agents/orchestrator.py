"""Orchestrator — top-level agent that runs any mode pipeline."""

from __future__ import annotations

from datetime import UTC, datetime

from chainlens.audit.engine import AuditEngine
from chainlens.collectors.explorer import ExplorerClient
from chainlens.collectors.market_data import MarketDataClient
from chainlens.collectors.rpc import RPCClient
from chainlens.config.settings import AppConfig, ChainConfig, get_config
from chainlens.knowledge.brain.store import BrainStore
from chainlens.knowledge.indexer.engine import VectorIndex
from chainlens.models import Report, ReportMeta
from chainlens.quant.engine import QuantEngine


class Orchestrator:
    """Top-level orchestrator — wires engines together for any mode."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config()
        self.brain = BrainStore()
        self.index = VectorIndex()
        if self.brain.load_entries():
            self.index.rebuild(self.brain.load_entries())

    def _get_chain_config(self, chain: str) -> ChainConfig:
        return self.config.chains.get(
            chain,
            ChainConfig(rpc_url="", explorer_api_url=""),
        )

    def _get_rpc(self, chain: str) -> RPCClient:
        return RPCClient(self._get_chain_config(chain))

    def _get_explorer(self, chain: str) -> ExplorerClient:
        return ExplorerClient(self._get_chain_config(chain))

    def _get_market(self) -> MarketDataClient:
        return MarketDataClient(
            provider=self.config.market_data_provider,
            api_key=self.config.market_data_api_key,
        )

    def run_audit(
        self,
        address: str,
        chain: str = "ethereum",
    ) -> Report:
        """Run a full audit and return a Report."""
        import asyncio

        engine = AuditEngine()
        findings, risk_score = asyncio.run(engine.run(address, chain))

        meta = ReportMeta(
            timestamp=datetime.now(UTC),
            mode="audit",
            target=address,
            chain=chain,
            window_days=0,
            brain_version=str(self.brain.get_version()),
        )
        return Report(
            meta=meta,
            findings=findings,
            risk_score=risk_score,
            knowledge_entries=[],
        )

    def run_quant(
        self,
        token: str,
        window_days: int = 90,
        chain: str = "ethereum",
    ) -> Report:
        """Run quant analysis and return a Report."""
        import asyncio

        engine = QuantEngine(
            market_client=self._get_market(),
        )
        metrics = asyncio.run(engine.run(token, window_days, chain))

        meta = ReportMeta(
            timestamp=datetime.now(UTC),
            mode="quant",
            target=token,
            chain=chain,
            window_days=window_days,
            brain_version=str(self.brain.get_version()),
        )
        return Report(meta=meta, metrics=metrics)

    def run_research(
        self,
        token: str,
        chain: str = "ethereum",
        window_days: int = 90,
    ) -> Report:
        """Run combined research (audit + quant + knowledge context)."""
        from chainlens.agents.research import ResearchAgent

        agent = ResearchAgent(self)
        return agent.run(token, chain, window_days)

    def run_learn(
        self,
        topic: str,
        level: str = "beginner",
    ) -> Report:
        """Run learn mode."""
        from chainlens.agents.tutor import Tutor

        tutor = Tutor(self.brain, self.index)
        return tutor.explain_topic(topic, level)
