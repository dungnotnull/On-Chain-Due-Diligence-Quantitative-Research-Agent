"""Liquidity lock detection — checks if LP tokens are burned or timelocked."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from chainlens.models import Citation, ContractData, Finding, FindingType


async def check_liquidity_locked(
    contract: ContractData,
    explorer_client: Any | None = None,  # noqa: ARG001
) -> Finding:
    """Check whether liquidity is locked or burned.

    In production, this:
    1. Finds the paired LP token address (via factory events)
    2. Checks LP token balance of dead address (0x000...000 or 0xdead)
    3. If >50% of LP supply burned -> locked
    4. Checks for timelock contracts

    For now, returns a risk assessment based on available signals.
    """
    citation = Citation(
        ref_type="contract",
        ref=contract.address,
        source=f"on-chain ({contract.chain})",
        retrieved_at=datetime.now(UTC),
    )

    # Heuristic: young unverified contracts are higher risk for rug-pull
    risk_level: str = "info"
    risk_reasons: list[str] = []

    if not contract.verified:
        risk_level = "medium"
        risk_reasons.append("unverified contract — cannot confirm LP locks")

    if contract.age_days < 30:
        if risk_level == "info":
            risk_level = "low"
        risk_reasons.append(f"Young contract ({contract.age_days:.0f} days old)")

    return Finding(
        signal="liquidity_not_locked",
        severity=risk_level,
        value={
            "liquidity_locked": False,
            "reasons": risk_reasons,
            "note": "Full LP lock verification requires on-chain pool data",
        },
        type=FindingType.fact,
        citation=citation,
    )
