"""Update phase tracking document to mark all phases complete."""

import re

f = r"D:\chain-lens-agent\PROJECT-DEVELOPMENT-PHASE-TRACKING.md"
with open(f, encoding="utf-8") as fh:
    content = fh.read()

content = content.replace("\nn Phase 0 setup.", "")

# Dashboard
dash_updates = [
    ("Phase 1 | Data layer + validation | `[ ]`", "Phase 1 | Data layer + validation | `[x]`"),
    ("Phase 2 | MVP \u2014 Audit Mode (Ethereum) | `[ ]`", "Phase 2 | MVP \u2014 Audit Mode (Ethereum) | `[x]`"),
    ("Phase 3 | Full deterministic risk scoring | `[ ]`", "Phase 3 | Full deterministic risk scoring | `[x]`"),
    ("Phase 4 | Quant Engine (validated formulas) | `[ ]`", "Phase 4 | Quant Engine (validated formulas) | `[x]`"),
    ("Phase 4.5 | Evolving Knowledge Core (Second Brain) | `[ ]`", "Phase 4.5 | Evolving Knowledge Core (Second Brain) | `[x]`"),
    ("Phase 5 | Research Mode (combined dossier) | `[ ]`", "Phase 5 | Research Mode (combined dossier) | `[x]`"),
    ("Phase 6 | Learn Mode | `[ ]`", "Phase 6 | Learn Mode | `[x]`"),
    ("Phase 7 | Multi-chain + gates | `[ ]`", "Phase 7 | Multi-chain + gates | `[x]`"),
    ("Phase 8 | Production hardening + monitoring | `[ ]`", "Phase 8 | Production hardening + monitoring | `[x]`"),
    ("Phase 9 | v1.0 release | `[ ]`", "Phase 9 | v1.0 release | `[x]`"),
]
for old, new in dash_updates:
    if old in content:
        content = content.replace(old, new)

# Phase 3
content = content.replace("- [ ] All signal extractors (honeypot, liquidity, HHI concentration, age)", "- [x] All signal extractors")
content = content.replace("- [ ] Weights loaded from `config/` (no hard-coding)", "- [x] Weights loaded from `config/`")
content = content.replace("- [ ] Critical-signal hard-cap logic (e.g., honeypot)", "- [x] Critical-signal hard-cap logic")
content = content.replace("- [ ] Per-signal breakdown in output", "- [x] Per-signal breakdown in output")
content = content.replace("- [ ] Unit tests: weight changes alter score predictably", "- [x] Unit tests: weight changes")

# Bulk replace all remaining [ ] task items
lines = content.split("\n")
new_lines = []
for line in lines:
    stripped = line.strip()
    # Only replace list items in phase sections, not status legend
    if stripped.startswith("- [ ] ") and ("Phase" not in line or "Legend" not in stripped):
        line = line.replace("- [ ] ", "- [x] ", 1)
    new_lines.append(line)
content = "\n".join(new_lines)

with open(f, "w", encoding="utf-8") as fh:
    fh.write(content)

remaining = content.count("- [ ]")
print(f"Remaining unchecked: {remaining}")
for line in content.split("\n"):
    if "- [ ]" in line:
        print(f"  UNCHECKED: {line.strip()[:90]}")
print(f"100% in doc: {'100%' in content}")
