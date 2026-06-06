"""CLI entry point — mode router. Dispatches to all real engines."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from chainlens import __version__
from chainlens.cli.audit import run as audit_run
from chainlens.cli.learn import run as learn_run
from chainlens.cli.quant import run as quant_run
from chainlens.cli.research import run as research_run
from chainlens.cli.validate import run as validate_run
from chainlens.config.settings import get_config

console = Console()
app = typer.Typer(
    name="chainlens",
    help="Production-grade on-chain due-diligence and quantitative research agent",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


def _show_banner() -> None:
    config = get_config()
    console.print(
        Panel(
            f"[bold cyan]ChainLens v{__version__}[/bold cyan]\n"
            f"On-chain due-diligence & quantitative research agent\n"
            f"Env: {config.env}  |  Log level: {config.log_level}",
            title="ChainLens",
        )
    )


@app.callback(invoke_without_command=True)
def entry_point(ctx: typer.Context) -> None:
    """Run ChainLens interactive mode."""
    if ctx.invoked_subcommand is not None:
        return

    _show_banner()

    mode = Prompt.ask(
        "Select mode",
        choices=["audit", "quant", "research", "learn", "validate", "exit"],
        default="audit",
    )

    if mode == "exit":
        console.print("[yellow]Goodbye.[/yellow]")
        raise typer.Exit()

    target = Prompt.ask("Target (address, symbol, or topic)")
    chain = Prompt.ask("Chain", default=get_config().default_chain)

    console.print(f"[green]Launching {mode} mode for {target} on {chain}...[/green]")

    if mode == "audit":
        audit_run(address=target, chain=chain)
    elif mode == "quant":
        quant_run(token=target, window="90d", chain=chain)
    elif mode == "research":
        research_run(token=target, chain=chain, window="90d")
    elif mode == "learn":
        learn_run(topic=target, level="beginner")
    elif mode == "validate":
        validate_run(target=target, chain=chain)


@app.command("version")
def version_cmd() -> None:
    """Show version."""
    console.print(f"ChainLens v{__version__}")


if __name__ == "__main__":
    app()
