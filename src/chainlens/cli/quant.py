"""Quant mode CLI — formula-based quantitative metrics."""

from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime

import typer
from rich.console import Console
from rich.table import Table

from chainlens.quant.engine import QuantEngine
from chainlens.storage.reports import write_report

console = Console()
app = typer.Typer(name="quant", help="Formula-based quantitative metrics")


def _parse_window(window_str: str) -> int:
    """Parse '90d', '1y', '30d' etc. into days."""
    m = re.match(r"^(\d+)([dy]?)$", window_str)
    if not m:
        return 90
    num = int(m.group(1))
    unit = m.group(2)
    if unit == "y":
        return num * 365
    return num


@app.callback(invoke_without_command=True)
def run(
    token: str = typer.Option(..., "--token", "-t", help="Token symbol or address"),
    window: str = typer.Option("90d", "--window", "-w", help="Lookback window (e.g. 30d, 90d, 1y)"),
    chain: str = typer.Option("ethereum", "--chain", "-c", help="Blockchain"),
) -> None:
    """Run quant metrics on a token."""
    window_days = _parse_window(window)
    console.print(f"[cyan]Quant analysis: {token} over {window_days}d on {chain}...[/cyan]")

    engine = QuantEngine()

    try:
        metrics = asyncio.run(engine.run(token, window_days, chain))
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1) from e

    table = Table(title=f"Quant Metrics: {token} ({window})")
    table.add_column("Formula", style="cyan")
    table.add_column("Metric", style="yellow")
    table.add_column("Value", style="green")
    table.add_column("Window", style="dim")
    table.add_column("Samples", style="dim")

    metric_lines = ["## Quantitative Metrics\n"]
    for m in metrics:
        table.add_row(
            m.formula_id,
            m.name,
            str(m.value),
            f"{m.window_days}d",
            str(m.sample_size),
        )
        metric_lines.append(
            f"- **{m.name}** ({m.formula_id}): `{m.value}` | "
            f"window={m.window_days}d, samples={m.sample_size}, "
            f"source={m.source}, retrieved={m.retrieved_at.isoformat()}\n"
        )

    metric_lines.append(
        "\n> *All metrics are descriptive statistical estimates "
        "based on historical data. They do not predict future performance.*\n"
    )

    console.print(table)

    # Build report
    from chainlens.models import Report, ReportMeta

    meta = ReportMeta(
        timestamp=datetime.now(UTC),
        mode="quant",
        target=token,
        chain=chain,
        window_days=window_days,
    )
    report = Report(meta=meta, metrics=metrics)
    path = write_report(report, "\n".join(metric_lines))
    console.print(f"\n[green]Report written to: {path}[/green]")
