# CLAUDE.md

This file provides guidance to Claude Code (and compatible AI coding agents) when working with this repository.

## Project Summary

**ChainLens** is a production-grade on-chain due-diligence and quantitative research agent for blockchain, tokens, and smart contracts. It is built for **real traders, researchers, and analysts** — not demos.

It combines two rigorously separated engines:
1. **Deterministic Audit Engine** — rule-based smart-contract risk analysis over verified source + on-chain state. No ML, fully explainable.
2. **Quantitative Metrics Engine** — closed-form financial math (volatility, returns, drawdown, Sharpe, liquidity depth, holder concentration) over historical and on-chain data. Formula-based, no model training.

Every output is **evidence-cited** (tx hash, contract address, source line, or data source + timestamp) and labeled as either a **deterministic fact** or a **statistical estimate**.

The pipeline: **Ingest → Validate → Analyze (Audit + Quant) → Explain → Report.**

## Core Principles

- **No prediction, no advice.** ChainLens audits the present and quantifies the past. It does NOT forecast price or issue trading signals. Mandatory disclaimer on every report.
- **Fact vs. estimate separation.** Deterministic findings and statistical metrics are never mixed without explicit labeling.
- **Data integrity first.** Bad data is worse than no data. All inputs are validated, timestamped, and source-tagged before analysis.
- **Verifiability.** Prefer verified source (Etherscan/Sourcify) and raw RPC/explorer data over third-party narratives.
- **Reproducibility.** Same inputs → same outputs. Quant calculations are deterministic and unit-tested against known references.
- **Budget & latency aware.** Cache aggressively; enforce per-run cost ceiling and response-time targets.

## Architecture Overview

```
src/
  agents/          # Orchestrator + sub-agents (audit, quant, research, tutor)
  collectors/      # RPC client, explorer APIs, source fetcher, market-data (OHLCV)
  knowledge/
    crawler/         # Fetch recent papers (arXiv, Scholar, audit reports)
    gatekeeper/      # Quality gate: credibility, dedup, conflict, recency
    extractor/       # Turn sources into KnowledgeEntry objects
    indexer/         # Vector index for retrieval (RAG)
    brain.md         # symlink/sync to SECOND-KNOWLEDGE-BRAIN.md
  audit/           # Deterministic contract risk heuristics
  quant/           # Financial-math metrics (volatility, returns, drawdown, etc.)
  validation/      # Data-integrity checks, schema validation, outlier detection
  knowledge/       # Glossary, pattern library (rug-pull/honeypot signatures)
  storage/         # Cache, dedup, time-series store, report writers
  monitoring/      # Logging, metrics, data-freshness & API-health checks
  cli/             # Interactive flow & modes (audit | quant | research | learn)
  config/          # Env, chain RPCs, scoring weights, quant params
outputs/           # Timestamped .md reports (YYYY-MM-DD_HHMMSS_<target>.md)
templates/         # Report templates per mode
tests/             # Unit + reference tests (quant validated vs known values)
```

## Key Commands

```bash
# Install
npm install            # or: pip install -e .

# Run interactive flow
npm run start          # asks for mode + target + chain + lookback window

# Mode-specific entry points
npm run audit -- --address 0x... --chain ethereum
npm run quant -- --token "<symbol or address>" --window 90d
npm run research -- --token "<symbol or address>"
npm run learn -- --topic "ERC-20 approvals"

# Quality gates
npm test               # includes quant reference tests
npm run lint
npm run validate-data  # dry-run data-integrity checks
```

## Operating Modes (Enforce Distinct Flows)

1. **Audit Mode** — Deterministic contract risk: ownership, mint authority, honeypot, liquidity locks, blacklist/pausable. Output a Risk Score + cited evidence.
2. **Quant Mode** — Closed-form metrics over OHLCV + on-chain data: volatility, returns, drawdown, Sharpe, liquidity depth, holder concentration (HHI/Gini). Output metrics + interpretation, NO forecast.
3. **Research Mode** — Combines Audit + Quant + tokenomics + protocol comparison into a full dossier.
4. **Learn Mode** — Explains concepts/contracts/metrics step by step with real cited examples.

## Coding Conventions

- All external calls route through `collectors/` with retry + backoff + cache.
- All inputs pass through `validation/` before reaching `audit/` or `quant/`.
- Scoring weights, quant params, and chain configs live in `config/` — never hard-code.
- Outputs are **append-only**, timestamped, never overwritten.
- Every claim attaches a **citation object** `{ type, ref, source, retrieved_at }`.
- Every quant figure attaches `{ value, window, sample_size, formula_id }`.
- Functions are small, typed, and unit-tested.

## Quant Engine Rules (Mandatory)

- Use **only closed-form, documented formulas** (see PROJECT-detail §6). No ML training in core.
- Every metric must declare its **lookback window, sample size, and data source**.
- Reject calculations with **insufficient samples** (configurable minimum); never silently extrapolate.
- Use **log returns** for compounding-correct math.
- Annualize volatility/Sharpe explicitly with a stated periods-per-year constant.
- Validate each formula in `tests/` against a **known reference value**.
- Flag and quarantine **outliers / data gaps**; never compute over corrupted series.

## Evolving Knowledge Core (Second Brain)

ChainLens continuously improves via a **gated knowledge loop**, NOT model retraining. A `Knowledge-Updater` sub-agent crawls recent research, quality-gates it, and appends validated entries to `SECOND-KNOWLEDGE-BRAIN.md` + a vector index. The agent retrieves this knowledge at reasoning time (RAG).


### Knowledge Rules (Mandatory)
- **No core mutation by knowledge.** Deterministic audit rules and quant formulas are frozen code. Retrieved knowledge only *contextualizes and explains*; it never auto-edits rules/formulas. Such changes are explicit, versioned PRs.
- **Quality gate before storage.** Every entry must pass credibility, relevance, recency, dedup, conflict, extractability, and provenance checks (see SECOND-KNOWLEDGE-BRAIN.md). Failures → Quarantine.
- **Conflict → human review.** Contradictory findings go to the Review Queue, never silently overwrite.
- **Versioned & cited.** Each accepted batch bumps the brain version. Every report records the brain version it used and cites specific entries.
- **Append-only ledger.** Never edit past entries in place — supersede with a new dated entry.

### Commands
```bash
npm run brain:crawl     # run a gated knowledge crawl cycle (confirmation-gated)
npm run brain:review    # show conflict/quarantine queues for adjudication
npm run brain:status    # brain version, entry counts, last crawl
```

## Guardrails (Mandatory — Real-Money Context)

- **Never** predict price, give trading signals, or financial advice.
- Always append: *"Educational/informational only — not financial advice. Quantitative metrics describe historical/current data and do not predict future performance."*
- Crawl cycles are **confirmation-gated** (cost + quality). Never auto-ingest unvetted sources into the live brain.
- Never say a token is "safe" — use "lower observed risk based on signals."
- Never present a statistical estimate as a deterministic fact (or vice versa).
- Abort gracefully on stale data, failed validation, or budget breach — with a clear reason.
- Summarize external text; do not reproduce large copyrighted content verbatim.

## Do Not

- Do not skip data validation before analysis.
- Do not output any metric without window + sample size + source.
- Do not commit API keys, private keys, or `.env`.
- Do not overwrite `outputs/`.
- Do not introduce ML forecasting into the core audit/quant engines without an explicit, separately-gated experimental module.
