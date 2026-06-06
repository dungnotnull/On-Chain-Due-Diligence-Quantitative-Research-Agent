"""Individual risk-signal extractors. Each returns a cited Finding."""

from __future__ import annotations

from datetime import UTC, datetime

from chainlens.models import Citation, ContractData, Finding, FindingType


def _citation(contract: ContractData) -> Citation:
    return Citation(
        ref_type="contract",
        ref=contract.address,
        source=f"on-chain ({contract.chain})",
        retrieved_at=datetime.now(UTC),
    )


def check_owner_privileges(contract: ContractData) -> Finding:
    has_owner = len(contract.admin_privileges) > 0
    return Finding(
        signal="owner_admin_privileges",
        severity="high" if has_owner else "info",
        value=contract.admin_privileges,
        type=FindingType.fact,
        citation=_citation(contract),
    )


def check_mint_authority(contract: ContractData) -> Finding:
    return Finding(
        signal="mint_authority",
        severity="high" if contract.mint_authority else "info",
        value=contract.mint_authority,
        type=FindingType.fact,
        citation=_citation(contract),
    )


def check_pausable(contract: ContractData) -> Finding:
    return Finding(
        signal="pausable",
        severity="medium" if contract.pausable else "info",
        value=contract.pausable,
        type=FindingType.fact,
        citation=_citation(contract),
    )


def check_blacklist(contract: ContractData) -> Finding:
    return Finding(
        signal="blacklist",
        severity="medium" if contract.blacklist else "info",
        value=contract.blacklist,
        type=FindingType.fact,
        citation=_citation(contract),
    )


def check_verified_source(contract: ContractData) -> Finding:
    return Finding(
        signal="unverified_source",
        severity="medium" if not contract.verified else "info",
        value=contract.verified,
        type=FindingType.fact,
        citation=_citation(contract),
    )


def check_contract_age(contract: ContractData) -> Finding:
    young = contract.age_days < 30
    return Finding(
        signal="contract_age",
        severity="low" if young else "info",
        value=contract.age_days,
        type=FindingType.fact,
        citation=_citation(contract),
    )
