"""Brain crawl CLI — run a knowledge crawl cycle through gatekeeper + extractor."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from chainlens.knowledge.brain.models import CrawlResult
from chainlens.knowledge.brain.store import BrainStore
from chainlens.knowledge.crawler.engine import CrawlEngine
from chainlens.knowledge.extractor.engine import Extractor
from chainlens.knowledge.gatekeeper.engine import GateKeeper

console = Console()
app = typer.Typer(name="brain-crawl", help="Run a knowledge crawl cycle")


@app.callback(invoke_without_command=True)
def run(
    max_results: int = typer.Option(5, "--max", "-m", help="Max results per source"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Crawl, gate, and extract new knowledge entries."""
    if not confirm:
        console.print("[yellow]This makes external API calls (arXiv). Use --yes to confirm.[/yellow]")
        raise typer.Exit(0)

    console.print("[cyan]Starting knowledge crawl cycle...[/cyan]")

    store = BrainStore()
    engine = CrawlEngine()
    gatekeeper = GateKeeper()
    extractor = Extractor()

    # Fix: remove 'topics' argument and use default
    raw_sources = asyncio.run(engine.run(max_results=max_results))
    console.print(f"[dim]Scanned {len(raw_sources)} raw sources[/dim]")

    existing = store.load_entries()
    passed, quarantined, conflicts = gatekeeper.gate(raw_sources, existing)

    for item in conflicts:
        store.add_conflict(item)
    for src in quarantined:
        store.add_to_quarantine(src, "Failed quality gate")

    accepted = 0
    for src in passed:
        entry = extractor.extract(src)
        store.append_entry(entry)
        accepted += 1

    store.bump_version()

    result = CrawlResult(
        entries_scanned=len(raw_sources),
        entries_accepted=accepted,
        entries_rejected=len(quarantined),
        conflicts_found=len(conflicts),
        quarantined=len(quarantined),
    )
    store.record_crawl(result)
    store.sync_with_markdown()

    table = Table(title="Crawl Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Sources scanned", str(result.entries_scanned))
    table.add_row("Accepted", str(result.entries_accepted))
    table.add_row("Rejected", str(result.entries_rejected))
    table.add_row("Conflicts", str(result.conflicts_found))
    table.add_row("Brain version", str(store.get_version()))

    console.print(table)
