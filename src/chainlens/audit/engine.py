"""AuditEngine — orchestrates scanner + heuristics into findings and risk score."""

from __future__ import annotations

from datetime import UTC, datetime

from chainlens.audit.heuristics import (
    check_blacklist,
    check_contract_age,
    check_mint_authority,
    check_owner_privileges,
    check_pausable,
    check_verified_source,
)
from chainlens.audit.scanner import ContractScanner
from chainlens.audit.scoring import compute_risk_score
from chainlens.audit.signals.honeypot import check_honeypot
from chainlens.audit.signals.liquidity import check_liquidity_locked
from chainlens.config.settings import ScoringWeights
from chainlens.models import Finding, Report, ReportMeta, RiskScore


class AuditEngine:
    """Runs the full audit pipeline: scan -> heuristics -> scoring -> Report."""

    def __init__(
        self,
        scanner: ContractScanner | None = None,
        scoring_weights: ScoringWeights | None = None,
    ) -> None:
        self.scanner = scanner or ContractScanner()
        self.weights = scoring_weights

    async def run(
        self,
        address: str,
        chain: str = "ethereum",
        scoring_weights: dict[str, float] | None = None,
    ) -> tuple[list[Finding], RiskScore | None]:
        """Execute a full audit with all signals and scoring."""
        contract = await self.scanner.scan_detailed(address, chain)

        base_findings = [
            check_owner_privileges(contract),
            check_mint_authority(contract),
            check_pausable(contract),
            check_blacklist(contract),
            check_verified_source(contract),
            check_contract_age(contract),
        ]

        # Advanced signals (async)
        honey = await check_honeypot(contract)
        liq = await check_liquidity_locked(contract)
        findings = base_findings + [honey, liq]

        # Scoring
        risk_score = None
        if scoring_weights:
            w = {
                "owner_admin_privileges": scoring_weights.get("owner_admin_privileges", 25.0),
                "mint_authority": scoring_weights.get("mint_authority", 20.0),
                "honeypot": scoring_weights.get("honeypot", 30.0),
                "liquidity_not_locked": scoring_weights.get("liquidity_not_locked", 20.0),
                "pausable": scoring_weights.get("pausable", 10.0),
                "blacklist": scoring_weights.get("blacklist", 10.0),
                "unverified_source": scoring_weights.get("unverified_source", 10.0),
                "contract_age": scoring_weights.get("contract_age", 5.0),
            }
            risk_score = compute_risk_score(findings, w)

        return findings, risk_score

    def build_report(
        self,
        findings: list[Finding],
        risk_score: RiskScore | None,
        address: str,
        chain: str = "ethereum",
    ) -> Report:
        """Build a complete Report model from audit results."""
        meta = ReportMeta(
            timestamp=datetime.now(UTC),
            mode="audit",
            target=address,
            chain=chain,
            window_days=0,
        )
        return Report(
            meta=meta,
            findings=findings,
            risk_score=risk_score,
            data_quality={
                "contract_verified": any(
                    f.signal == "unverified_source" and f.value is False
                    for f in findings
                )
            },
        )
