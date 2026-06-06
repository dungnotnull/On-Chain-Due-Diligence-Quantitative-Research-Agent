"""Data-integrity checks: schema, type, range, freshness, and outlier detection."""

from chainlens.validation.freshness import check_freshness, format_freshness, tag_with_freshness
from chainlens.validation.outliers import (
    detect_gaps,
    detect_outliers,
    quarantine_flagged,
    reject_insufficient_data,
)
from chainlens.validation.schema import (
    VALIDATION_WARNINGS,
    reset_warnings,
    validate_address,
    validate_contract_data,
    validate_price_series,
    validate_range,
    validate_type,
)

__all__ = [
    "VALIDATION_WARNINGS",
    "reset_warnings",
    "validate_address",
    "validate_contract_data",
    "validate_price_series",
    "validate_range",
    "validate_type",
    "check_freshness",
    "format_freshness",
    "tag_with_freshness",
    "detect_gaps",
    "detect_outliers",
    "quarantine_flagged",
    "reject_insufficient_data",
]
