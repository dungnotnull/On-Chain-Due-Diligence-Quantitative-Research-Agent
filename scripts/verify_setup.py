#!/usr/bin/env python
"""Verify ChainLens Phase 0 setup — structure, imports, config, CLI binding."""

import importlib
import sys
from pathlib import Path

errors: list[str] = []


def check(condition: bool, msg: str) -> None:
    if not condition:
        errors.append(f"  X {msg}")
        print(f"  X {msg}")
    else:
        print(f"  + {msg}")


def main() -> int:
    print("\n=== ChainLens Phase 0 Verification ===\n")

    # --- 1. Directory structure ---
    print("[1] Directory structure")
    root = Path(__file__).resolve().parent.parent
    src = root / "src" / "chainlens"

    expected_dirs = [
        src,
        src / "agents",
        src / "collectors",
        src / "audit",
        src / "quant",
        src / "validation",
        src / "storage",
        src / "monitoring",
        src / "cli",
        src / "config",
        src / "knowledge",
        src / "knowledge" / "crawler",
        src / "knowledge" / "gatekeeper",
        src / "knowledge" / "extractor",
        src / "knowledge" / "indexer",
        src / "knowledge" / "brain",
        root / "outputs",
        root / "templates",
        root / "tests",
        root / ".github" / "workflows",
    ]

    for d in expected_dirs:
        check(d.is_dir(), f"Directory exists: {d.relative_to(root)}")

    # --- 2. File structure ---
    print("\n[2] File structure")
    expected_files = [
        root / "pyproject.toml",
        root / ".gitignore",
        root / "LICENSE",
        root / "README.md",
        root / ".env.example",
        root / ".github" / "workflows" / "ci.yml",
        root / "src" / "chainlens" / "__init__.py",
        root / "src" / "chainlens" / "models.py",
        root / "src" / "chainlens" / "config" / "settings.py",
        root / "src" / "chainlens" / "config" / "defaults.yaml",
        root / "src" / "chainlens" / "storage" / "reports.py",
        root / "src" / "chainlens" / "cli" / "main.py",
        root / "src" / "chainlens" / "cli" / "audit.py",
        root / "src" / "chainlens" / "cli" / "quant.py",
        root / "src" / "chainlens" / "cli" / "research.py",
        root / "src" / "chainlens" / "cli" / "learn.py",
        root / "src" / "chainlens" / "cli" / "validate.py",
        root / "src" / "chainlens" / "cli" / "brain_crawl.py",
        root / "src" / "chainlens" / "cli" / "brain_review.py",
        root / "src" / "chainlens" / "cli" / "brain_status.py",
    ]

    for f in expected_files:
        check(f.is_file(), f"File exists: {f.relative_to(root)}")

    # --- 3. Import check ---
    print("\n[3] Import check")
    src_path = str(root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    modules = [
        "chainlens",
        "chainlens.models",
        "chainlens.config.settings",
        "chainlens.storage.reports",
        "chainlens.cli.main",
        "chainlens.cli.audit",
        "chainlens.cli.quant",
        "chainlens.cli.research",
        "chainlens.cli.learn",
        "chainlens.cli.validate",
        "chainlens.cli.brain_crawl",
        "chainlens.cli.brain_review",
        "chainlens.cli.brain_status",
    ]

    for mod_name in modules:
        try:
            importlib.import_module(mod_name)
            check(True, f"Import: {mod_name}")
        except Exception as e:
            check(False, f"Import {mod_name}: {e}")

    # --- 4. Config loading ---
    print("\n[4] Config loading")
    try:
        from chainlens.config.settings import get_config

        cfg = get_config()
        check(cfg.n_min == 30, f"n_min_samples default = {cfg.n_min}")
        check(cfg.cost_ceiling_usd == 5.0, f"cost_ceiling_usd default = {cfg.cost_ceiling_usd}")
        check("ethereum" in cfg.chains, "Ethereum chain config present")
        check("bsc" in cfg.chains, "BSC chain config present")
        check(cfg.scoring.honeypot == 30.0, f"Honeypot weight = {cfg.scoring.honeypot}")
    except Exception as e:
        check(False, f"Config loading: {e}")

    # --- 5. Model construction ---
    print("\n[5] Data model construction")
    try:
        from datetime import datetime, timezone

        from chainlens.models import Citation, Finding, Metric, Report, ReportMeta

        citation = Citation(
            ref_type="contract",
            ref="0x1234",
            source="etherscan",
            retrieved_at=datetime.now(timezone.utc),
        )
        finding = Finding(
            signal="owner_privileges",
            severity="high",
            value=True,
            citation=citation,
        )
        metric = Metric(
            formula_id="VOL-001",
            name="annualized_volatility",
            value=0.85,
            window_days=90,
            sample_size=100,
            source="coingecko",
            retrieved_at=datetime.now(timezone.utc),
        )
        meta = ReportMeta(mode="audit", target="0x1234")
        report = Report(meta=meta, findings=[finding], metrics=[metric])

        check(len(report.findings) == 1, f"Report has {len(report.findings)} finding(s)")
        check(len(report.metrics) == 1, f"Report has {len(report.metrics)} metric(s)")
        check("financial" in report.disclaimer, "Disclaimer present")
    except Exception as e:
        check(False, f"Model construction: {e}")

    # --- 6. CLI binding check ---
    print("\n[6] CLI binding check")
    try:
        from chainlens.cli.main import app

        commands = [c for c in app.registered_commands]
        groups = [g for g in app.registered_groups]
        version_cmds = [c for c in commands if c.name == "version"]
        check(len(commands) >= 1, f"CLI has {len(commands)} command(s)")
        check(len(version_cmds) == 1, "Version command registered")
    except Exception as e:
        check(False, f"CLI binding: {e}")

    # --- 7. CLI smoke test ---
    print("\n[7] CLI smoke test")
    try:
        from typer.testing import CliRunner

        from chainlens.cli.main import app

        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        check(result.exit_code == 0, f"CLI 'version' returned {result.exit_code}")
        check("0.1.0" in result.stdout, f"CLI outputs version: {result.stdout.strip()}")
    except Exception as e:
        check(False, f"CLI smoke test: {e}")

    # --- Summary ---
    print(f"\n{'='*50}")
    if errors:
        print(f"FAILURE: {len(errors)} check(s) failed")
        for e in errors:
            print(f"   {e}")
        return 1
    else:
        print("ALL CHECKS PASSED -- Phase 0 setup is valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
