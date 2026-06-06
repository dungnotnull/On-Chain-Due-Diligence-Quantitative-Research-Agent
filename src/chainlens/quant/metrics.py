"""Pure numpy implementations of all quantitative metrics.

Each function is annotated with its formula_id matching FORMULA_REGISTRY.
All functions operate on numpy arrays and return float values.
"""

from __future__ import annotations

import numpy as np

# --- RET-001: Log Returns ---

def log_returns(prices: np.ndarray) -> np.ndarray:
    """r_t = ln(P_t / P_{t-1})"""
    if len(prices) < 2:
        return np.array([])
    return np.diff(np.log(prices[prices > 0]))


# --- VOL-001: Annualized Volatility ---

def annualized_volatility(returns: np.ndarray, periods: int = 365) -> float:
    """sigma_ann = sqrt(1/(n-1) * sum((r_i - r_bar)^2)) * sqrt(N)"""
    if len(returns) < 2:
        return 0.0
    sigma = np.std(returns, ddof=1)
    return float(round(sigma * np.sqrt(periods), 6))


# --- SHR-001: Sharpe Ratio (descriptive) ---

def sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.0,
    periods: int = 365,
) -> float:
    """S = (mean(r) - r_f) / sigma(r)"""
    if len(returns) < 2:
        return 0.0
    sigma = np.std(returns, ddof=1)
    if sigma == 0:
        return 0.0
    rfr_per_period = risk_free_rate / periods
    excess = np.mean(returns) - rfr_per_period
    return float(round(excess / sigma * np.sqrt(periods), 4))


# --- MDD-001: Maximum Drawdown ---

def max_drawdown(prices: np.ndarray) -> float:
    """MDD = min((P_t - max_{tau<=t} P_tau) / max_{tau<=t} P_tau)"""
    if len(prices) < 2:
        return 0.0
    peak = np.maximum.accumulate(prices)
    drawdowns = (prices - peak) / peak
    return float(round(abs(np.min(drawdowns)), 6))


# --- VAR-001: Historical Value at Risk ---

def historical_var(returns: np.ndarray, alpha: float = 0.05) -> float:
    """VaR_alpha = -quantile_alpha(returns)"""
    if len(returns) < 10:
        return 0.0
    var = float(-np.quantile(returns, alpha))
    return round(var, 6)


# --- HHI-001: Herfindahl-Hirschman Index ---

def herfindahl_index(shares: np.ndarray) -> float:
    """HHI = sum(s_i^2) where s_i is wallet i's share of supply."""
    if len(shares) == 0:
        return 0.0
    normalized = np.array(shares, dtype=float)
    total = normalized.sum()
    if total == 0:
        return 0.0
    normalized = normalized / total
    hhi = float(np.sum(normalized**2))
    return round(hhi, 6)


# --- GIN-001: Gini Coefficient ---

def gini_coefficient(values: np.ndarray) -> float:
    """Gini = (2 * sum(i * v_i) / (n * sum(v_i))) - (n+1)/n"""
    v = np.array(values, dtype=float)
    v_sorted = np.sort(v)
    n = len(v_sorted)
    if n == 0 or v_sorted.sum() == 0:
        return 0.0
    gini = (2.0 * np.sum(np.arange(1, n + 1) * v_sorted) / (n * v_sorted.sum())) - (n + 1.0) / n
    return float(round(gini, 6))


# --- LIQ-001: Liquidity Depth ---

def liquidity_depth(
    reserve_token: float,
    reserve_quote: float,
    trade_size: float,
) -> dict[str, float]:
    """Estimate price impact for a given trade size using constant product formula."""
    if reserve_token <= 0 or reserve_quote <= 0:
        return {"price_impact_pct": 0.0, "effective_price": 0.0}
    k = reserve_token * reserve_quote
    new_reserve_token = reserve_token + trade_size
    new_reserve_quote = k / new_reserve_token
    quote_out = reserve_quote - new_reserve_quote
    price_before = reserve_quote / reserve_token
    price_after = new_reserve_quote / new_reserve_token
    price_impact = abs(price_after - price_before) / price_before * 100
    return {
        "price_impact_pct": round(price_impact, 4),
        "effective_price": round(quote_out / trade_size if trade_size > 0 else 0, 6),
    }


# --- SLP-001: Slippage Estimate ---

def slippage_estimate(
    reserve_token: float,
    reserve_quote: float,  # noqa: ARG001
    trade_size: float,
) -> float:
    """Simple slippage estimate as fraction of trade size."""
    if reserve_token <= 0:
        return 0.0
    impact = trade_size / (reserve_token + trade_size)
    return float(round(impact, 6))
