"""Registry of all quantitative formulas with canonical definitions."""

from __future__ import annotations

FORMULA_REGISTRY: dict[str, dict[str, str]] = {
    "RET-001": {
        "name": "log_returns",
        "formula": "r_t = ln(P_t / P_{t-1})",
        "description": "Compounding-correct continuous returns",
        "params": "P_t: price at time t",
    },
    "VOL-001": {
        "name": "annualized_volatility",
        "formula": "sigma_ann = sqrt(1/(n-1) * sum((r_i - r_bar)^2)) * sqrt(N)",
        "description": "Annualized standard deviation of log returns",
        "params": "N: periods per year (365 for daily crypto data)",
    },
    "SHR-001": {
        "name": "sharpe_ratio",
        "formula": "S = (mean(r) - r_f/N) / sigma(r) * sqrt(N)",
        "description": "Historical risk-adjusted return descriptor (not a prediction)",
        "params": "r_f: annual risk-free rate (default 0), N: periods per year",
    },
    "MDD-001": {
        "name": "max_drawdown",
        "formula": "MDD = min((P_t - peak_{tau<=t}) / peak_{tau<=t})",
        "description": "Largest peak-to-trough decline in the window",
        "params": "Peak is the running maximum up to time t",
    },
    "VAR-001": {
        "name": "historical_var",
        "formula": "VaR_alpha = -quantile_alpha(returns)",
        "description": "Historical Value at Risk — descriptive statistic only, not a forecast",
        "params": "alpha: confidence level (default 0.05 for 95% VaR)",
    },
    "HHI-001": {
        "name": "herfindahl_index",
        "formula": "HHI = sum(s_i^2)",
        "description": "Holder concentration index. 0 = perfectly distributed, 1 = single holder",
        "params": "s_i: wallet i's share of total supply",
    },
    "GIN-001": {
        "name": "gini_coefficient",
        "formula": "G = (2 * sum(i * v_i) / (n * sum(v_i))) - (n+1)/n",
        "description": "Distribution inequality coefficient. 0 = equal, 1 = max inequality",
        "params": "v_i: sorted holder balances, n: holder count",
    },
    "LIQ-001": {
        "name": "liquidity_depth",
        "formula": "price_impact = |P_after - P_before| / P_before",
        "description": "Estimated price impact for a given trade size using AMM constant product",
        "params": "reserve_token, reserve_quote: pool reserves; trade_size: token amount to trade",
    },
    "SLP-001": {
        "name": "slippage_estimate",
        "formula": "slippage = trade_size / (reserve + trade_size)",
        "description": "Simple slippage estimate as a fraction of pool depth",
        "params": "reserve: pool token reserve; trade_size: token amount",
    },
}
