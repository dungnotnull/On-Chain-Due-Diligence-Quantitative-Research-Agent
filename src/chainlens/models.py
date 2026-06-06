"""Core data models shared across ChainLens modules."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Provenance for a single finding or metric value."""

    ref_type: Literal["tx", "contract", "source_line", "api", "paper", "internal"]
    ref: str
    source: str
    retrieved_at: datetime


class FindingType(StrEnum):
    """Whether a finding is a deterministic fact or a statistical estimate."""

    fact = "fact"
    estimate = "estimate"


class Finding(BaseModel):
    """A single deterministic finding (Audit mode)."""

    signal: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    value: Any
    type: FindingType = FindingType.fact
    citation: Citation


class Metric(BaseModel):
    """A single quantitative metric (Quant mode)."""

    formula_id: str
    name: str
    value: float
    window_days: int
    sample_size: int
    source: str
    retrieved_at: datetime
    type: FindingType = FindingType.estimate


class ContractData(BaseModel):
    """On-chain contract data for audit analysis."""

    address: str = ""
    chain: str = ""
    verified: bool = False
    source_summary: str = ""
    functions: list[str] = Field(default_factory=list)
    admin_privileges: list[str] = Field(default_factory=list)
    mint_authority: bool = False
    pausable: bool = False
    blacklist: bool = False
    age_days: float = 0.0
    last_activity_days: float = 0.0


class PriceCandle(BaseModel):
    """A single OHLCV price data point."""

    timestamp: datetime
    open_: float = Field(alias="open")
    high: float
    low: float
    close: float
    volume: float


class PriceSeries(BaseModel):
    """A validated series of OHLCV price data."""

    symbol: str
    source: str
    interval: str
    candles: list[PriceCandle]
    retrieved_at: datetime
    sample_size: int = 0
    gaps_detected: int = 0
    outliers_flagged: int = 0


class RiskScore(BaseModel):
    """Deterministic 0-100 risk score with per-signal breakdown."""

    score: float = 0.0
    breakdown: dict[str, float] = Field(default_factory=dict)
    hard_caps: list[str] = Field(default_factory=list)


class KnowledgeEntry(BaseModel):
    """A validated entry in the evolving knowledge core."""

    id: str
    title: str
    topic: str
    summary: str
    insight_type: Literal["pattern", "metric", "threshold", "methodology", "finding"]
    applies_to: list[Literal["audit", "quant", "research", "learn"]]
    source: dict[str, Any]
    retrieved_at: datetime
    confidence: Literal["high", "medium", "low"]
    status: Literal["active", "superseded", "quarantined"] = "active"
    supersedes: str | None = None
    conflicts_with: str | None = None


class ReportMeta(BaseModel):
    """Metadata for a single ChainLens report."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    mode: str
    target: str
    chain: str = "ethereum"
    window_days: int = 90
    brain_version: str | None = None


class Report(BaseModel):
    """Complete report: findings, metrics, knowledge context, and disclaimer."""

    meta: ReportMeta
    data_quality: dict[str, Any] = Field(default_factory=dict)
    risk_score: RiskScore | None = None
    findings: list[Finding] = Field(default_factory=list)
    metrics: list[Metric] = Field(default_factory=list)
    knowledge_entries: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "Educational/informational only — not financial advice. "
        "Quantitative metrics describe historical/current data "
        "and do not predict future performance."
    )
