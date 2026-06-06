"""Honeypot detection — simulates buy/sell to detect sell-restriction patterns."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from chainlens.models import Citation, ContractData, Finding, FindingType


async def check_honeypot(
    contract: ContractData,
    rpc_client: Any | None = None,  # noqa: ARG001
) -> Finding:
    """Detect honeypot patterns: can buy but cannot sell.

    In production, this simulates a buy + sell via eth_call:
    1. Buy: call swapExactETHForTokens with a small amount
    2. Sell: call swapExactTokensForETH on the received tokens
    3. If buy succeeds but sell reverts -> honeypot

    For now, returns a mock finding based on contract data patterns.
    """
    citation = Citation(
        ref_type="contract",
        ref=contract.address,
        source=f"on-chain ({contract.chain})",
        retrieved_at=datetime.now(UTC),
    )

    # Heuristic: unverified + high mint authority + pausable is suspicious
    score = 0
    reasons: list[str] = []

    if not contract.verified:
        score += 1
        reasons.append("unverified source")
    if contract.mint_authority:
        score += 1
        reasons.append("active mint authority")
    if contract.pausable:
        score += 1
        reasons.append("pausable transfers")

    is_honeypot = score >= 2

    return Finding(
        signal="honeypot",
        severity="critical" if is_honeypot else "info",
        value={
            "detected": is_honeypot,
            "reasons": reasons if is_honeypot else [],
            "confidence": "medium",
        },
        type=FindingType.fact,
        citation=citation,
    )
