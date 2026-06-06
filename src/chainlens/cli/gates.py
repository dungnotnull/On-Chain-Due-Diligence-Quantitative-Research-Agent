"""Confirmation gate prompts for expensive or risky operations."""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Confirm

console = Console()


def confirm_multi_chain(target_chain: str, source_chain: str = "ethereum") -> bool:
    """Ask user to confirm running on a non-default chain."""
    if target_chain == source_chain:
        return True
    return Confirm.ask(
        f"[yellow]Run on {target_chain} instead of {source_chain}? "
        f"This may require different RPC/API keys.[/yellow]",
        default=False,
    )


def confirm_paid_api(
    api_name: str,
    estimated_cost: float = 0.0,
    cost_ceiling: float = 5.0,
) -> bool:
    """Ask user to confirm a call that may incur API costs."""
    if estimated_cost >= cost_ceiling:
        console.print(f"[red]Estimated cost ${estimated_cost:.2f} exceeds ceiling "
                       f"${cost_ceiling:.2f}. Aborting.[/red]")
        return False
    if estimated_cost > 0:
        return Confirm.ask(
            f"[yellow]Call {api_name} (est. ${estimated_cost:.2f})?[/yellow]",
            default=False,
        )
    return True


def confirm_large_window(window_days: int, threshold: int = 365) -> bool:
    """Ask user to confirm a large lookback window."""
    if window_days <= threshold:
        return True
    return Confirm.ask(
        f"[yellow]Large window ({window_days}d). This may take longer "
        f"and use more API calls. Continue?[/yellow]",
        default=False,
    )


def confirm_deep_run(estimated_calls: int, max_calls: int = 1000) -> bool:
    """Ask user to confirm a deep analysis run."""
    if estimated_calls > max_calls:
        console.print(f"[red]Estimated {estimated_calls} calls exceeds "
                       f"max {max_calls}. Aborting.[/red]")
        return False
    if estimated_calls > max_calls * 0.5:
        return Confirm.ask(
            f"[yellow]Deep run: ~{estimated_calls} API calls. Continue?[/yellow]",
            default=False,
        )
    return True
