"""Audit mode CLI — deterministic smart-contract risk analysis."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import typer
from rich.console import Console
from rich.table import Table

from chainlens.audit.engine import AuditEngine
from chainlens.storage.reports import format_citation, write_report
from chainlens.validation.schema import validate_address

console = Console()
app = typer.Typer(name="audit", help="Deterministic smart-contract risk analysis")


@app.callback(invoke_without_command=True)
def run(
    address: str = typer.Option(..., "--address", "-a", help="Contract address"),
    chain: str = typer.Option("ethereum", "--chain", "-c", help="Blockchain"),
) -> None:
    """Run a deterministic audit on a smart contract."""
    try:
        addr = validate_address(address)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e

    console.print(f"[cyan]Auditing {addr} on {chain}...[/cyan]")

    engine = AuditEngine()
    findings, risk_score = asyncio.run(engine.run(addr, chain))

    report = engine.build_report(findings, risk_score, addr, chain)
    report.meta.timestamp = datetime.now(UTC)

    # Display results
    table = Table(title=f"Audit Results: {addr}")
    table.add_column("Signal", style="cyan")
    table.add_column("Severity", style="yellow")
    table.add_column("Value")
    table.add_column("Type")

    for f in findings:
        table.add_row(
            f.signal,
            f.severity,
            str(f.value),
            f.type.value,
        )

    if risk_score:
        table.add_row(
            "[bold]Risk Score[/bold]",
            "[bold]---[/bold]",
            f"[bold]{risk_score.score}/100[/bold]",
            "[bold]composite[/bold]",
        )

    console.print(table)

    # Build markdown content
    lines = ["## Findings\n"]
    for f in findings:
        citation = format_citation(f.citation)
        lines.append(f"- **{f.signal}** ({f.severity}, {f.type.value}): `{f.value}`")
        lines.append(f"  {citation}\n")

    if risk_score:
        lines.append("## Risk Score\n")
        lines.append(f"**Score:** {risk_score.score}/100\n")
        lines.append("### Per-Signal Breakdown\n")
        for sig, val in risk_score.breakdown.items():
            lines.append(f"- {sig}: {val}")
        if risk_score.hard_caps:
            lines.append(f"\n**Hard-caps triggered by:** {', '.join(risk_score.hard_caps)}\n")
    else:
        lines.append("## Risk Score\n")
        lines.append("Scoring not configured — run with scoring weights to compute risk score.\n")

    path = write_report(report, "\n".join(lines))
    console.print(f"\n[green]Report written to: {path}[/green]")
