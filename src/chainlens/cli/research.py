"""Research mode CLI — combined audit + quant + knowledge dossier."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from chainlens.agents.orchestrator import Orchestrator
from chainlens.storage.reports import write_report

console = Console()
app = typer.Typer(name="research", help="Combined audit + quant dossier")


@app.callback(invoke_without_command=True)
def run(
    token: str = typer.Option(..., "--token", "-t", help="Token symbol or address"),
    chain: str = typer.Option("ethereum", "--chain", "-c", help="Blockchain"),
    window: str = typer.Option("90d", "--window", "-w", help="Lookback window"),
) -> None:
    """Run a full research dossier combining audit, quant, and knowledge."""
    window_days = 90
    if window.endswith("d"):
        window_days = int(window[:-1])
    elif window.endswith("y"):
        window_days = int(window[:-1]) * 365
    else:
        window_days = int(window)

    console.print(f"[cyan]Research dossier: {token} on {chain} ({window_days}d)[/cyan]")

    orch = Orchestrator()
    report = orch.run_research(token, chain, window_days)

    # Display summary
    table = Table(title=f"Research Dossier: {token}")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")

    table.add_row("Audit findings", str(len(report.findings)),
                  f"Risk score: {report.risk_score.score if report.risk_score else 'N/A'}")
    table.add_row("Quant metrics", str(len(report.metrics)),
                  f"Window: {report.meta.window_days}d" if report.metrics else "N/A")
    table.add_row("Knowledge entries", str(len(report.knowledge_entries)),
                  ", ".join(report.knowledge_entries[:3]) if report.knowledge_entries else "None")
    table.add_row("Brain version", report.meta.brain_version or "N/A", "")

    console.print(table)

    # Build markdown
    lines = ["## Executive Summary\n"]
    if report.risk_score:
        lines.append(f"**Risk Score:** {report.risk_score.score}/100\n")
    lines.append(f"**Target:** {token} on {chain}\n")
    lines.append(f"**Window:** {window_days} days\n")

    lines.append("## Audit Findings\n")
    for f in report.findings:
        lines.append(f"- **{f.signal}** ({f.severity}): `{f.value}`\n")

    lines.append("## Quantitative Metrics\n")
    for m in report.metrics:
        lines.append(f"- **{m.name}** ({m.formula_id}): `{m.value}` | samples={m.sample_size}\n")

    if report.knowledge_entries:
        lines.append("## Knowledge Context\n")
        for kid in report.knowledge_entries:
            lines.append(f"- Entry: {kid}\n")

    lines.append("\n*This dossier combines deterministic findings with statistical estimates. "
                  "Not financial advice.*\n")

    path = write_report(report, "\n".join(lines))
    console.print(f"\n[green]Dossier written to: {path}[/green]")
