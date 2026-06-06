"""Schema, type, and range checks on data models."""

from __future__ import annotations

import re
from typing import Any

from chainlens.models import ContractData, PriceSeries

VALIDATION_WARNINGS: list[str] = []


def reset_warnings() -> None:
    VALIDATION_WARNINGS.clear()


def _warn(msg: str) -> None:
    VALIDATION_WARNINGS.append(msg)


def validate_address(address: str) -> str:
    """Validate an Ethereum-style address. Returns checksummed form or raises."""
    if not re.match(r"^0x[0-9a-fA-F]{40}$", address):
        msg = f"Invalid address format: {address}"
        raise ValueError(msg)
    return address.lower()


def validate_price_series(series: PriceSeries) -> PriceSeries:
    """Validate a price series. Returns annotated series or raises."""
    if not series.candles:
        msg = "Price series has zero candles"
        raise ValueError(msg)

    series.sample_size = len(series.candles)

    # Check for NaNs in numeric fields
    for i, c in enumerate(series.candles):
        for field in ("open_", "high", "low", "close", "volume"):
            val = getattr(c, field, None)
            if val is None or (isinstance(val, float) and val != val):  # NaN check
                _warn(f"Candle {i}: {field} is NaN")

    # Check timestamps are ascending
    timestamps = [c.timestamp for c in series.candles]
    for i in range(1, len(timestamps)):
        if timestamps[i] <= timestamps[i - 1]:
            _warn(f"Candle {i}: timestamp not ascending ({timestamps[i]} <= {timestamps[i-1]})")

    # Check O-H-L-C consistency
    for i, c in enumerate(series.candles):
        if c.high < c.low:
            _warn(f"Candle {i}: high ({c.high}) < low ({c.low})")
        if c.high < c.close or c.high < c.open:
            _warn(f"Candle {i}: high ({c.high}) < open/close")
        if c.low > c.close or c.low > c.open:
            _warn(f"Candle {i}: low ({c.low}) > open/close")
        if c.volume < 0:
            _warn(f"Candle {i}: negative volume ({c.volume})")

    return series


def validate_contract_data(data: ContractData) -> ContractData:
    """Validate contract data fields."""
    if not data.address:
        msg = "Contract address is empty"
        raise ValueError(msg)
    if not data.chain:
        msg = "Chain is empty"
        raise ValueError(msg)
    if data.verified and not data.source_summary:
        _warn("Contract marked verified but has no source summary")
    return data


def validate_type(value: Any, expected_type: type, name: str) -> None:
    if not isinstance(value, expected_type):
        msg = f"{name}: expected {expected_type.__name__}, got {type(value).__name__}"
        raise TypeError(msg)


def validate_range(value: float, lo: float, hi: float, name: str) -> None:
    if value < lo or value > hi:
        msg = f"{name}: {value} out of range [{lo}, {hi}]"
        raise ValueError(msg)
