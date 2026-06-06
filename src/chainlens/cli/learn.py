"""Learn mode CLI — explainable, example-driven tutoring."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from chainlens.agents.tutor import Tutor
from chainlens.storage.reports import write_report

console = Console()
app = typer.Typer(name="learn", help="Explainable example-driven tutoring")


@app.callback(invoke_without_command=True)
def run(
    topic: str = typer.Option(..., "--topic", "-t", help="Topic to explain"),
    level: str = typer.Option("beginner", "--level", "-l", help="User level (beginner/advanced)"),
) -> None:
    """Run learn mode — explain a topic with real cited examples."""
    valid_levels = ["beginner", "advanced"]
    if level not in valid_levels:
        console.print(f"[red]Level must be one of: {', '.join(valid_levels)}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Learn: '{topic}' at {level} level...[/cyan]")

    tutor = Tutor()
    report = tutor.explain_topic(topic, level)

    # Build content from curriculum
    from chainlens.agents.curriculum import get_curriculum
    curriculum = get_curriculum(topic, level)

    table = Table(title=f"Learn: {curriculum['title']}")
    table.add_column("Section", style="cyan")
    table.add_column("Content")
    table.add_column("Examples")

    for section in curriculum.get("sections", []):
        table.add_row(
            section["title"],
            section["content"][:80] + "..." if len(section["content"]) > 80 else section["content"],
            section.get("example", "—")[:60],
        )

    console.print(table)

    # Takeaways
    takeaways = curriculum.get("takeaways", [])
    if takeaways:
        console.print("\n[bold]Key Takeaways:[/bold]")
        for t in takeaways:
            console.print(f"  • {t}")

    # Knowledge context
    if report.knowledge_entries:
        console.print(f"\n[dim]Consulted {len(report.knowledge_entries)} knowledge entries[/dim]")

    path = write_report(report, "")
    console.print(f"\n[green]Learn note written to: {path}[/green]")
