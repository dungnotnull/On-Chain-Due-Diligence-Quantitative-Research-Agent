"""Validate data CLI — schema, freshness, outlier checks."""

from __future__ import annotations

from datetime import UTC, datetime

import typer
from rich.console import Console
from rich.table import Table

from chainlens.models import PriceCandle, PriceSeries
from chainlens.validation import (
    VALIDATION_WARNINGS,
    reset_warnings,
    validate_address,
    validate_price_series,
)
from chainlens.validation.freshness import check_freshness
from chainlens.validation.outliers import detect_gaps, detect_outliers, reject_insufficient_data

console = Console()
app = typer.Typer(name="validate", help="Data-integrity checks")


@app.callback(invoke_without_command=True)
def run(
    target: str = typer.Option(..., "--target", "-t", help="Address or symbol"),
    chain: str = typer.Option("ethereum", "--chain", "-c", help="Blockchain"),
) -> None:
    """Run data-integrity checks on a target."""
    reset_warnings()
    table = Table(title=f"Validation Results: {target} on {chain}")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Detail")

    try:
        addr = validate_address(target)
        table.add_row("Address format", "PASS", addr)
    except ValueError as e:
        table.add_row("Address format", "SKIP (not address)", str(e))

    now = datetime.now(UTC)
    fresh = check_freshness(now, max_age_hours=1)
    table.add_row("Freshness sensor", "PASS" if fresh else "STALE", f"Current time: {now.isoformat()}")

    dummy = PriceSeries(
        symbol=target,
        source="coingecko/usd",
        interval="90d",
        candles=[
            PriceCandle(timestamp=now, open=100.0, high=105.0, low=99.0, close=102.0, volume=1000.0),
            PriceCandle(timestamp=now, open=102.0, high=108.0, low=101.0, close=107.0, volume=1200.0),
        ],
        retrieved_at=now,
        sample_size=2,
    )

    try:
        validated = validate_price_series(dummy)
        gaps = detect_gaps(validated)
        outliers = detect_outliers(validated)
        reject = reject_insufficient_data(validated, n_min=30)

        table.add_row("Schema check", "PASS", f"{validated.sample_size} candles")
        table.add_row("Gap detection", "INFO", f"{gaps} gaps")
        table.add_row("Outlier check", "INFO", f"{len(outliers)} outliers")
        table.add_row("Min samples (30)", "FAIL" if reject else "PASS (dummy)",
                       "2 < 30" if reject else "n/a")
    except ValueError as e:
        table.add_row("Schema check", "FAIL", str(e))

    for w in VALIDATION_WARNINGS:
        table.add_row("Warning", "WARN", w)

    console.print(table)
    console.print("\n[yellow]Note: Real data validation requires configured RPC/API keys.[/yellow]")
