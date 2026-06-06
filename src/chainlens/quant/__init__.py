"""Formula-based quantitative metrics engine (volatility, returns, drawdown, etc.)."""

from chainlens.quant.engine import QuantEngine
from chainlens.quant.formulas import FORMULA_REGISTRY
from chainlens.quant.metrics import (
    annualized_volatility,
    gini_coefficient,
    herfindahl_index,
    historical_var,
    liquidity_depth,
    log_returns,
    max_drawdown,
    sharpe_ratio,
    slippage_estimate,
)

__all__ = [
    "QuantEngine",
    "FORMULA_REGISTRY",
    "log_returns",
    "annualized_volatility",
    "sharpe_ratio",
    "max_drawdown",
    "historical_var",
    "herfindahl_index",
    "gini_coefficient",
    "liquidity_depth",
    "slippage_estimate",
]

