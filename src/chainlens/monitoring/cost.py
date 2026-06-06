"""CostTracker — per-run API cost tracking with ceiling enforcement."""

from __future__ import annotations

from typing import Any

from rich.console import Console

console = Console()

COST_PER_CALL: dict[str, float] = {
    "rpc_eth_call": 0.0001,
    "rpc_get_code": 0.0001,
    "rpc_get_storage": 0.0003,
    "etherscan_source": 0.001,
    "etherscan_abi": 0.001,
    "etherscan_holders": 0.005,
    "coingecko_ohlcv": 0.0,
    "coingecko_search": 0.0,
    "coingecko_price": 0.0,
    "arxiv_api": 0.0,
}


class CostTracker:
    """Track per-run API cost and abort if ceiling exceeded."""

    def __init__(self, cost_ceiling: float = 5.0) -> None:
        self.cost_ceiling = cost_ceiling
        self._calls: list[dict[str, Any]] = []
        self._total_cost = 0.0

    def track_call(self, api_name: str, estimated_cost: float | None = None) -> None:
        if estimated_cost is None:
            estimated_cost = COST_PER_CALL.get(api_name, 0.0)

        self._calls.append({"api": api_name, "cost": estimated_cost})
        self._total_cost += estimated_cost

        if self._total_cost > self.cost_ceiling:
            console.print(
                f"[red]Cost ceiling (${self.cost_ceiling:.2f}) exceeded. "
                f"Total: ${self._total_cost:.2f}. Aborting.[/red]"
            )
            msg = f"Cost ceiling ${self.cost_ceiling:.2f} exceeded (${self._total_cost:.2f})"
            raise RuntimeError(msg)

    def check_ceiling(self) -> bool:
        """Return True if under ceiling, False if exceeded."""
        return self._total_cost <= self.cost_ceiling

    def get_total_cost(self) -> float:
        return round(self._total_cost, 4)

    def get_call_count(self) -> int:
        return len(self._calls)

    def summary(self) -> str:
        return (
            f"Calls: {self.get_call_count()} | "
            f"Total cost: ${self.get_total_cost():.4f} | "
            f"Ceiling: ${self.cost_ceiling:.2f}"
        )

    def reset(self) -> None:
        self._calls.clear()
        self._total_cost = 0.0
