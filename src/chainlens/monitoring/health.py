"""Health checks — data-freshness and API-connectivity monitoring."""

from __future__ import annotations

from datetime import UTC, datetime

from chainlens.validation.freshness import check_freshness

HealthStatus = dict[str, str | bool | float]


class HealthChecker:
    """Monitor data freshness and API health."""

    def __init__(self) -> None:
        self._checks: list[HealthStatus] = []

    def check_data_freshness(
        self,
        data_type: str,
        retrieved_at: datetime | None,
        max_age_hours: int | None = None,
    ) -> HealthStatus:
        fresh = check_freshness(retrieved_at, max_age_hours, data_type)
        status: HealthStatus = {
            "check": f"freshness/{data_type}",
            "healthy": fresh,
            "detail": f"{'fresh' if fresh else 'stale'}",
        }
        if not fresh and retrieved_at:
            age = (datetime.now(UTC) - retrieved_at).total_seconds() / 3600
            status["detail"] = f"stale ({age:.1f}h old)"
        self._checks.append(status)
        return status

    def check_api_reachability(self, api_name: str, reachable: bool) -> HealthStatus:
        status: HealthStatus = {
            "check": f"api/{api_name}",
            "healthy": reachable,
            "detail": "reachable" if reachable else "unreachable",
        }
        self._checks.append(status)
        return status

    def get_summary(self) -> list[HealthStatus]:
        return list(self._checks)

    def all_healthy(self) -> bool:
        return all(c.get("healthy", False) for c in self._checks)

    def reset(self) -> None:
        self._checks.clear()
