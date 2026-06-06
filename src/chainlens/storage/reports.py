"""Report writer — timestamped, append-only output files."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from chainlens.models import Report

OUTPUTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "outputs"


def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")


def report_path(mode: str, target: str) -> Path:
    """Generate a unique timestamped output path."""
    safe_target = target.replace(":", "_").replace("/", "_").replace("\\", "_")[:40]
    filename = f"{_timestamp()}_{safe_target}_{mode}.md"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUTS_DIR / filename


def format_citation(citation: object) -> str:
    """Format a citation object as a markdown footer line."""
    from chainlens.models import Citation

    if not isinstance(citation, Citation):
        return ""
    ref_ts = citation.retrieved_at.isoformat()
    return (
        f"> :link: *Source:* {citation.source} | *Ref:* `{citation.ref}`"
        f" | *Retrieved:* {ref_ts}"
    )


def write_report(report: Report, content: str) -> Path:
    """Write a timestamped, append-only report to outputs/."""
    path = report_path(report.meta.mode, report.meta.target)

    header = [
        f"# ChainLens Report — {report.meta.mode.upper()}",
        "",
        f"**Generated:** {report.meta.timestamp.isoformat()}",
        f"**Target:** {report.meta.target}",
        f"**Chain:** {report.meta.chain}",
        f"**Window:** {report.meta.window_days}d",
        f"**Brain version:** {report.meta.brain_version or 'N/A'}",
        "",
        "---",
        "",
    ]

    footer = [
        "",
        "---",
        f"*{report.disclaimer}*",
        "",
    ]

    full = "\n".join(header) + content.strip() + "\n".join(footer)
    path.write_text(full, encoding="utf-8")
    return path
