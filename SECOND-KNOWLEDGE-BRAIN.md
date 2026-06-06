# SECOND-KNOWLEDGE-BRAIN.md — ChainLens Evolving Knowledge Core

> **What this is:** ChainLens's persistent, versioned knowledge base. It accumulates *validated* research findings, attack patterns, and methodology improvements over time. The agent retrieves from this brain at reasoning time (RAG), so it grows more accurate as the library grows — **without retraining any model**.
>
> **Golden rule:** This brain gets *better*, not *bigger-and-noisier*. Every entry is quality-gated, sourced, dated, deduplicated, and conflict-checked. Low-quality or unverifiable knowledge is rejected, not stored.

---

## How the Brain Works (Mechanism)

ChainLens improves through a **gated knowledge loop**, not weight retraining:

```
Crawl → Filter (quality gate) → Extract → Dedup/Conflict-check
      → Human/auto confirm → Version & store → Index (vector)
      → Retrieved at reasoning time (RAG)
```

- **No model training in core.** Improvement = a richer, vetted evidence base.
- **Deterministic engines stay frozen.** New knowledge informs *interpretation and context*, never silently mutates audit rules or quant formulas. Rule/formula changes are explicit, versioned code changes — not auto-learned.
- **Every retrieval is cited** back to a specific brain entry → original source.

---

## Quality Gate (Mandatory Before Any Entry)

An item enters the brain **only if** it passes all checks:

- [ ] **Source credibility** — peer-reviewed (arXiv with citations, IEEE/ACM, top venues), reputable audit firms, or official protocol docs. No anonymous blogs as primary sources.
- [ ] **Relevance** — matches a tracked topic (smart-contract security, tokenomics, on-chain analytics, quant methodology).
- [ ] **Recency / supersession** — newer findings supersede older; superseded entries are marked, not deleted.
- [ ] **Deduplication** — not already represented (semantic similarity check).
- [ ] **Conflict check** — if it contradicts an existing entry, flag for human review; never silently overwrite.
- [ ] **Extractability** — a concrete, usable insight (pattern, metric, threshold, methodology), not vague commentary.
- [ ] **Provenance** — full citation + retrieval timestamp recorded.

Items failing any check go to **Quarantine** (below), not the live brain.

---

## Knowledge Entry Schema

Every entry follows this structure:

```jsonc
KnowledgeEntry {
  id,                      // KB-YYYYMMDD-####
  title,
  topic,                   // e.g., "smart-contract-security"
  summary,                 // 2-4 sentence usable insight
  insight_type,            // pattern | metric | threshold | methodology | finding
  applies_to,              // audit | quant | research | learn
  source { type, url, authors, venue, year },
  retrieved_at,
  confidence,              // high | medium | low
  status,                  // active | superseded | quarantined
  supersedes,              // optional KB id
  conflicts_with           // optional KB id (flagged for review)
}
```

---

## Topic Taxonomy (What We Track)

- **Smart-Contract Security** — new vulnerability classes, exploit patterns, audit techniques, formal-verification advances.
- **Tokenomics** — emission/vesting models, incentive design, failure modes.
- **On-Chain Analytics** — holder-distribution methods, MEV, flow analysis, wash-trading detection.
- **Quant Methodology** — robust volatility estimators, liquidity/slippage models, risk metrics validity in crypto.
- **Regulatory / Compliance Context** — disclosure standards (informational only).

---

## Knowledge Ledger (Append-Only)

> New validated entries are appended here, newest first. Each links to a vector-index record. **Never edit past entries in place** — supersede with a new dated entry.

### 2026-05-31 — Brain initialized
- **KB-20260531-0001** · *Brain bootstrap* · methodology · applies_to: all
  - Summary: Knowledge core established. Seed topics defined. Awaiting first crawl cycle.
  - Source: internal · Confidence: high · Status: active

<!-- Future entries appended below by the Knowledge-Updater agent -->

---

## Conflict & Review Queue

Entries that contradict existing knowledge land here for human/agent adjudication before going active.

| **Date** | **New Entry** | **Conflicts With** | **Resolution** | **Status** |
|----------|---------------|--------------------|----------------|------------|
| — | — | — | — | — |

---

## Quarantine (Rejected / Pending)

Items that failed the quality gate. Kept for traceability; **not** used in reasoning.

| **Date** | **Item** | **Reason Rejected** | **Source** |
|----------|----------|---------------------|------------|
| — | — | — | — |

---

## Versioning & Provenance

- **Brain version** increments on each accepted batch: `vMAJOR.MINOR` (e.g., v1.3 = 3rd batch since v1.0).
- **Current brain version:** v1.0 (initialized)
- **Last crawl cycle:** none yet
- **Active entries:** 1 · **Superseded:** 0 · **Quarantined:** 0

Every ChainLens report records *which brain version* informed it — so analyses are reproducible and auditable over time.

---

## How the Agent Uses This Brain

- **Audit Mode:** retrieves latest known exploit/vulnerability patterns to enrich (not replace) deterministic checks.
- **Quant Mode:** retrieves validated methodology notes (e.g., better volatility estimators) to *contextualize* metrics — formula changes still require explicit code review.
- **Research Mode:** cites the freshest relevant papers in dossiers.
- **Learn Mode:** teaches using the most current, vetted explanations.

> **Guardrail:** Retrieved knowledge **contextualizes and explains**; it never silently alters deterministic audit rules or quant formulas. Any change to core logic is an explicit, versioned engineering decision.
