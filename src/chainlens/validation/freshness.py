"""Freshness tagging and staleness detection."""

from __future__ import annotations

from datetime import UTC, datetime

DEFAULT_MAX_AGE_HOURS: dict[str, int] = {
    "price_series": 1,  # 1 hour for price data
    "contract_data": 24,  # 24 hours for contract state
    "holder_data": 24,
    "verified_source": 168,  # 7 days for verified source
}


def check_freshness(
    retrieved_at: datetime | None,
    max_age_hours: int | None = None,
    data_type: str = "default",
) -> bool:
    """Return True if data is fresh (within max_age), False if stale."""
    if retrieved_at is None:
        return False
    if max_age_hours is None:
        max_age_hours = DEFAULT_MAX_AGE_HOURS.get(data_type, 6)
    age = (datetime.now(UTC) - retrieved_at).total_seconds() / 3600
    return age <= max_age_hours


def format_freshness(retrieved_at: datetime | None, data_type: str = "default") -> str:
    """Return a human-readable freshness label."""
    if retrieved_at is None:
        return "unknown"
    max_hours = DEFAULT_MAX_AGE_HOURS.get(data_type, 6)
    if check_freshness(retrieved_at, None, data_type):
        return "fresh"
    age_hours = (datetime.now(UTC) - retrieved_at).total_seconds() / 3600
    return f"stale ({age_hours:.1f}h old, max {max_hours}h)"


def tag_with_freshness(
    data: dict,
    max_age_hours: int | None = None,
    data_type: str = "default",
) -> dict:
    """Add freshness metadata to a data dict."""
    retrieved_at = data.get("retrieved_at")
    data["fresh"] = check_freshness(retrieved_at, max_age_hours, data_type)
    data["freshness_label"] = format_freshness(retrieved_at, data_type)
    return data
