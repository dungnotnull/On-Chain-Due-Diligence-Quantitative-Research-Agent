"""Brain status CLI — show version, entry counts, last crawl."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from chainlens.knowledge.brain.store import BrainStore

console = Console()
app = typer.Typer(name="brain-status", help="Knowledge base status")


@app.callback(invoke_without_command=True)
def run() -> None:
    """Show brain version, entry counts, last crawl."""
    store = BrainStore()
    version = store.get_version()
    entries = store.load_entries()
    last_crawl = store.get_last_crawl()
    conflicts = store.get_conflict_queue()
    quarantine = store.get_quarantine()

    table = Table(title="Knowledge Base Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Brain version", str(version))
    table.add_row("Active entries", str(len(entries)))
    table.add_row("Pending conflicts", str(len([c for c in conflicts if c.status == "pending"])))
    table.add_row("Quarantined items", str(len(quarantine)))

    if last_crawl:
        table.add_row("Last crawl", str(last_crawl.started_at)[:19] if last_crawl.started_at else "N/A")
        table.add_row("Last accepted", str(last_crawl.entries_accepted))
    else:
        table.add_row("Last crawl", "Never")

    if entries:
        table.add_row("Latest entry", entries[-1].id if entries else "N/A")
        table.add_row("Topics", ", ".join(sorted({e.topic for e in entries})))

    console.print(table)
