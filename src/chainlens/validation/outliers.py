"""Gap detection, outlier flagging, and minimum-sample enforcement."""

from __future__ import annotations

import numpy as np

from chainlens.models import PriceSeries


def detect_gaps(series: PriceSeries) -> int:
    """Count gaps (missing expected candles) in a price series."""
    if len(series.candles) < 2:
        return 0
    timestamps = np.array([c.timestamp.timestamp() for c in series.candles])
    deltas = np.diff(timestamps)
    median_delta = np.median(deltas)
    if median_delta <= 0:
        return 0
    gaps = int(np.sum(deltas > median_delta * 2))
    series.gaps_detected = gaps
    return gaps


def detect_outliers(
    series: PriceSeries, zscore_threshold: float = 3.0
) -> list[int]:
    """Flag outlier candles by z-score of log returns."""
    if len(series.candles) < 10:
        return []

    closes = np.array([c.close for c in series.candles])
    log_rets = np.diff(np.log(closes[closes > 0]))
    if len(log_rets) < 5:
        return []

    mean = np.mean(log_rets)
    std = np.std(log_rets)
    if std == 0:
        return []

    zscores = np.abs((log_rets - mean) / std)
    outlier_indices = list(np.where(zscores > zscore_threshold)[0])
    series.outliers_flagged = len(outlier_indices)
    return outlier_indices


def quarantine_flagged(series: PriceSeries) -> PriceSeries:
    """Mark gaps and outliers on the series and return it."""
    detect_gaps(series)
    detect_outliers(series)
    return series


def reject_insufficient_data(
    series: PriceSeries, n_min: int = 30
) -> bool:
    """Return True if the series should be rejected (too few good samples)."""
    usable = len(series.candles) - series.gaps_detected - series.outliers_flagged
    return usable < n_min
