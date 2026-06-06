"""QuantEngine — orchestrates data fetching, validation, and metric computation."""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np

from chainlens.collectors.market_data import MarketDataClient
from chainlens.config.settings import QuantParams
from chainlens.models import Metric, PriceSeries
from chainlens.quant.metrics import (
    annualized_volatility,
    historical_var,
    log_returns,
    max_drawdown,
    sharpe_ratio,
)
from chainlens.validation.outliers import quarantine_flagged, reject_insufficient_data
from chainlens.validation.schema import validate_price_series

METRIC_DEFS: list[tuple[str, str, callable, dict]] = [
    ("VOL-001", "annualized_volatility", annualized_volatility, {"periods": 365}),
    ("SHR-001", "sharpe_ratio", sharpe_ratio, {"risk_free_rate": 0.0, "periods": 365}),
    ("MDD-001", "max_drawdown", max_drawdown, {}),
    ("VAR-001", "historical_var_95", historical_var, {"alpha": 0.05}),
    ("VAR-001", "historical_var_99", historical_var, {"alpha": 0.01}),
]


class QuantEngine:
    """Compute validated quantitative metrics from market data."""

    def __init__(
        self,
        market_client: MarketDataClient | None = None,
        params: QuantParams | None = None,
    ) -> None:
        self.market = market_client or MarketDataClient()
        self.params = params or QuantParams()

    async def run(
        self,
        token: str,
        window_days: int = 90,
        chain: str = "ethereum",  # noqa: ARG002
    ) -> list[Metric]:
        """Run the full quant pipeline: fetch -> validate -> compute.

        Args:
            token: CoinGecko coin ID or contract address.
            window_days: Lookback window in days.
            chain: Blockchain label.

        Returns:
            List of Metric objects with formula_id, window, sample_size, source.

        """
        series = await self.market.get_ohlcv(token, days=window_days)
        series = await self._process_series(series)
        return self._compute_metrics(series, token, window_days)

    async def _process_series(self, series: PriceSeries) -> PriceSeries:
        """Validate and clean a price series."""
        series = validate_price_series(series)
        series = quarantine_flagged(series)

        if reject_insufficient_data(series, self.params.n_min_samples):
            msg = (
                f"Insufficient data: {series.sample_size} samples, "
                f"{series.gaps_detected} gaps, {series.outliers_flagged} outliers, "
                f"min required: {self.params.n_min_samples}"
            )
            raise ValueError(msg)

        return series

    def _compute_metrics(
        self,
        series: PriceSeries,
        token: str,  # noqa: ARG002
        window_days: int,
    ) -> list[Metric]:
        """Compute all metrics from a validated price series."""
        closes = np.array([c.close for c in series.candles], dtype=float)
        returns = log_returns(closes)

        now = datetime.now(UTC)
        metrics: list[Metric] = []

        for formula_id, name, fn, kwargs in METRIC_DEFS:
            try:
                needs_returns = any(
                    kw in name for kw in ["returns", "var", "sharpe", "volatility"]
                )
                value = fn(returns if needs_returns else closes, **kwargs)
                metrics.append(Metric(
                    formula_id=formula_id,
                    name=name,
                    value=float(value),
                    window_days=window_days,
                    sample_size=series.sample_size,
                    source=series.source,
                    retrieved_at=now,
                ))
            except Exception:
                continue

        return metrics
