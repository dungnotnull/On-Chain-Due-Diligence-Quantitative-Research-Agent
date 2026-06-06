"""Brain review CLI — display conflict/quarantine queues for adjudication."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from chainlens.knowledge.brain.store import BrainStore

console = Console()
app = typer.Typer(name="brain-review", help="Review conflict/quarantine queues")


@app.callback(invoke_without_command=True)
def run() -> None:
    """Show conflict and quarantine queues."""
    store = BrainStore()

    # Conflicts
    conflicts = store.get_conflict_queue()
    if conflicts:
        table = Table(title="Conflict Queue")
        table.add_column("Entry ID", style="red")
        table.add_column("Conflicts With", style="yellow")
        table.add_column("Reason")
        table.add_column("Status")
        for c in conflicts:
            table.add_row(
                c.entry_id,
                ", ".join(c.conflict_ids),
                c.reason,
                c.status,
            )
        console.print(table)
    else:
        console.print("[green]No conflicts in queue.[/green]")

    # Quarantine
    quarantine = store.get_quarantine()
    if quarantine:
        qtable = Table(title="Quarantine")
        qtable.add_column("Entry", style="yellow")
        qtable.add_column("Reason")
        qtable.add_column("Timestamp")
        for q in quarantine:
            entry_title = q.get("entry", {}).get("title", "unknown")
            reason = q.get("reason", "unknown")
            ts = q.get("timestamp", "")
            qtable.add_row(entry_title[:60], reason, str(ts)[:19])
        console.print(qtable)
    else:
        console.print("[green]Quarantine is empty.[/green]")
