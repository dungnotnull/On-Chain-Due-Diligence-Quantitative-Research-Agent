# PROJECT-detail.md — ChainLens

## 1. Vision

ChainLens is a **production-grade on-chain due-diligence and quantitative research agent** for real traders, market researchers, and serious learners. It refuses the two traps that sink most crypto AI tools — **price prediction** (unreliable) and **black-box advice** (legally and ethically risky).

Instead, it does two things exceptionally well, with proof:
- **Audits the present:** deterministic smart-contract risk analysis.
- **Quantifies the past/now:** rigorous, formula-based financial metrics.

Its signature: **every statement is evidence-cited and explicitly labeled as either a deterministic fact or a statistical estimate.**

---

## 2. Why This Architecture (The "What's It Based On" Answer)

This section directly addresses the core design question: *what does the analysis rely on?*

| **Engine** | **Basis** | **Needs ML/training?** | **Needs dataset?** | **Output type** |
|------------|-----------|------------------------|--------------------|-----------------|
| Audit | Deterministic rules over verified code + chain state | ❌ No | ❌ No (reads live) | Deterministic fact |
| Quant | Closed-form financial math over OHLCV + on-chain data | ❌ No | ✅ Yes (historical price/on-chain) | Statistical estimate |

**Deliberately excluded from core:** ML price forecasting and automated trading strategies. Crypto markets are near-efficient and adversarial; out-of-sample forecasting is unreliable and carries legal exposure. If ever explored, it lives in a **separate, clearly-labeled experimental module** — never in the trusted core.

This separation is *the* feature: traders get **trustworthy, reproducible, explainable** analysis they can act on with full understanding of its limits.

---

## 3. Goals & Non-Goals

### Goals
- Deterministic, cited **smart-contract risk audits**.
- Rigorous, formula-based **quantitative metrics** with stated windows & samples.
- **Data-integrity layer** ensuring no analysis runs on corrupted/stale data.
- Combined **research dossiers** and an **explainable tutor**.
- Production reliability: caching, monitoring, validation, reproducibility.

### Non-Goals
- No price forecasting, trading signals, or financial advice (core).
- No fund custody or transaction execution.
- No guarantee of safety — risk inference only.

---

## 4. Target Users & Value

| **User** | **Primary Mode** | **Value Delivered** |
|----------|------------------|---------------------|
| Trader / investor | Audit + Quant | Pre-trade risk audit + objective volatility/liquidity/drawdown metrics |
| Market researcher | Research | Full dossier: risk + tokenomics + quant + comparisons |
| Researcher / student | Learn | Explainable, example-driven mastery |
| Quant-curious builder | Quant + Learn | Transparent, validated metric formulas |

---

## 5. Operating Modes & Flow

### Step 0 — Intake
Ask for: **mode**, **target** (symbol/address/topic), **chain** (default Ethereum), **lookback window** (for Quant, e.g., 30d/90d/1y), **depth/limit**.

### Mode A — Audit (Deterministic)
1. Resolve target → contract address(es).
2. Fetch verified source (Etherscan/Sourcify) + on-chain state.
3. Run risk heuristics (ownership, mint authority, honeypot, liquidity, blacklist/pausable, verification, age).
4. Compute **Risk Score** with per-signal breakdown + citations.
5. Output `outputs/..._audit.md`.

### Mode B — Quant (Formula-Based)
1. Fetch & **validate** historical OHLCV + on-chain series.
2. Reject if sample size < configured minimum or data gaps detected.
3. Compute metrics (§6) with declared window + sample + source.
4. Provide **descriptive interpretation only** (e.g., "volatility is high relative to window"), never a forecast.
5. Output `outputs/..._quant.md`.

### Mode C — Research (Combined)
1. Run Audit + Quant.
2. Add tokenomics, holder distribution, comparable protocols.
3. Produce a structured dossier.
4. Output `outputs/..._research.md`.

### Mode D — Learn
1. Explain a concept/contract/metric step by step.
2. Anchor to real cited examples; adapt to user level.
3. Output `outputs/..._learn.md`.

### Confirmation Gate
Before multi-chain expansion, paid-API deep runs, or large lookback windows, request user approval.

---

## 6. Quantitative Metrics Engine (Financial Math)

All metrics are **closed-form, documented, and unit-tested against reference values**. Each carries a `formula_id`, window, sample size, and source. No training, no extrapolation.

### 6.1 Returns

Log returns (compounding-correct):

$$r_t = \ln\frac{P_t}{P_{t-1}}$$

### 6.2 Volatility (annualized)

$$\sigma = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(r_i - \bar{r})^2}, \qquad \sigma_{ann} = \sigma \sqrt{N}$$

where $$N$$ is periods per year (stated explicitly, e.g., 365 for daily crypto).

### 6.3 Sharpe Ratio (risk-adjusted, descriptive)

$$S = \frac{\bar{r} - r_f}{\sigma}$$

Reported as a historical descriptor, not a recommendation.

### 6.4 Maximum Drawdown

$$MDD = \min_t \left( \frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau} \right)$$

### 6.5 Holder Concentration

Herfindahl–Hirschman Index over top holders:

$$HHI = \sum_{i=1}^{k} s_i^2$$

where $$s_i$$ is wallet $$i$$'s share of supply. Optionally a Gini coefficient for distribution inequality.

## 6.6 Evolving Knowledge Core (The Self-Improvement Engine)

ChainLens's key long-term advantage: it **gets more accurate over time** by accumulating a *curated, versioned* knowledge base — not by retraining models. This is honest, reproducible self-improvement.

### How improvement actually happens

| **Mechanism** | **ChainLens (correct)** | **Naive "self-learning" (avoided)** |
|---------------|-------------------------|--------------------------------------|
| What changes | Vetted knowledge library grows | Model weights drift |
| Quality control | Hard quality gate per entry | None → noise compounds |
| Reproducibility | Brain version recorded per report | Lost |
| Core logic | Frozen; changes are explicit PRs | Silently mutates |
| Trust | Every claim cited to a source | Opaque |

### The Gated Knowledge Loop

```
Crawl recent research → Quality gate → Extract insight
  → Dedup + conflict check → (Human/auto confirm)
  → Version & store in SECOND-KNOWLEDGE-BRAIN.md → Vector index
  → Retrieved at reasoning time (RAG), always cited
```

### Sources Crawled
- arXiv (cs.CR, q-fin), IEEE/ACM, top security/finance venues.
- Reputable audit-firm disclosures and post-mortems.
- Official protocol documentation and standards (EIPs).

### Quality Gate (summary)
Credibility · Relevance · Recency/supersession · Deduplication · Conflict-check · Extractability · Provenance. Failures are quarantined, not stored. (Full spec in `SECOND-KNOWLEDGE-BRAIN.md`.)

### Strict Separation (Critical)
- **Deterministic engines stay frozen.** New knowledge enriches *interpretation, context, and explanations* — it never silently rewrites audit rules or quant formulas.
- **Core changes are explicit.** If research suggests a better volatility estimator or a new exploit check, it becomes a **reviewed, versioned code change**, validated by reference tests — never an automatic mutation.

### Why this is the system's moat
A static analyzer ages. ChainLens compounds: each crawl cycle adds vetted, current intelligence (new attack vectors, better methodologies, fresh tokenomics failure modes). Because it's *gated and versioned*, it improves monotonically — and every analysis remains fully auditable.


### 6.7 Liquidity Depth

Reported from pool reserves / order-book depth where available, with source + timestamp. Includes a simple slippage estimate for a stated trade size.

### 6.8 Value-at-Risk (historical, descriptive)

$$VaR_{\alpha} = -\text{quantile}_{\alpha}(\{r_t\})$$

Reported as a historical descriptive statistic only.

> **Rule:** Every metric output must state its **window, sample size, data source, and retrieval timestamp**, and is labeled a **statistical estimate** — never a prediction.

---

## 7. Risk Scoring Model (Deterministic)

Explainable score (0–100, **higher = higher risk**) over hand-set, config-driven weights.

| **Signal** | **Red-flag meaning** | **Weight idea** |
|------------|----------------------|-----------------|
| Owner/admin privileges | Can mint, pause, blacklist | High |
| Mint authority active | Supply inflation | High |
| Honeypot patterns | Can buy, can't sell | Critical (hard-cap) |
| Liquidity not locked | Rug-pull potential | High |
| Holder concentration (HHI) | Few wallets dominate | Medium |
| Unverified source | Unauditable | Medium |
| Contract age / activity | New, low history | Low |

$$Risk = 100 \times \frac{\sum_{i} w_i \cdot s_i}{\sum_{i} w_i}$$

Critical signals (e.g., honeypot) can hard-cap the score upward regardless of others.

---

## 8. Data Integrity & Reliability (Production)

Because real traders depend on this, data quality is a first-class concern.

- **Validation:** schema checks, type checks, range checks before any analysis.
- **Freshness:** every datum tagged with `retrieved_at`; stale data triggers refresh or abort.
- **Gap/outlier handling:** detect missing candles and anomalous spikes; quarantine, never silently fill.
- **Minimum sample enforcement:** reject quant runs below configured `n_min`.
- **Source priority:** verified on-chain > reputable explorer > aggregated market API, with provenance recorded.
- **Reproducibility:** cached snapshots allow re-running an identical report later.

---

## 9. System Architecture

```
┌─────────────┐    ┌──────────────┐    ┌────────────┐
│   CLI /     │───▶│  Orchestrator │───▶│ Collectors │
│ Mode Intake │    │   (Agents)    │    │RPC/Explorer│
└─────────────┘    └──────┬───────┘    │   /OHLCV   │
                          │            └─────┬──────┘
                   ┌──────▼──────┐           │
                   │ Validation  │◀──────────┘
                   │  (gatekeep) │
                   └──────┬──────┘
              ┌───────────┴───────────┐
       ┌──────▼──────┐         ┌──────▼──────┐
       │ Audit Engine│         │ Quant Engine│
       │(determinist)│         │ (formulas)  │
       └──────┬──────┘         └──────┬──────┘
              └───────────┬───────────┘
                   ┌──────▼──────┐    ┌────────────┐
                   │ Report/Tutor│    │ Monitoring │
                   └─────────────┘    └────────────┘
```

---

## 10. Tech Stack (Suggested)

| **Layer** | **Choice** | **Why** |
|-----------|-----------|---------|
| Language | Python | Best for quant (NumPy/pandas) + web3 |
| Quant math | NumPy / pandas | Validated, vectorized closed-form math |
| Agent framework | LangGraph / custom orchestrator | Stateful multi-step flows |
| Chain access | web3.py + explorer APIs | On-chain state + verified source |
| Source verification | Etherscan API / Sourcify | Audit real code |
| Market data | Exchange / aggregator OHLCV APIs | Historical price series |
| Storage | SQLite/Parquet + filesystem MD | Time-series cache + reports |
| Monitoring | structured logging + health checks | Production reliability |
| LLM | Claude | Reasoning, interpretation, tutoring |

---

## 11. Data Model (Core Entities)

```jsonc
Contract {
  address, chain, verified, source_summary,
  functions[], admin_privileges[], mint_authority,
  pausable, blacklist, age, last_activity
}

PriceSeries {
  symbol, source, interval, candles[], retrieved_at,
  sample_size, gaps_detected, outliers_flagged
}

Metric {
  formula_id, name, value, window, sample_size,
  source, retrieved_at, type: "estimate"
}

Finding {
  signal, severity, value, type: "fact",
  citation{ ref_type, ref, source, retrieved_at }
}

Report {
  timestamp, mode, target, risk_score, metrics[],
  findings[], data_quality, disclaimer
}
```

---

## 12. Outputs

Timestamped, append-only, in `outputs/`:

- `*_audit.md` — deterministic risk + cited findings.
- `*_quant.md` — metrics with window/sample/source + interpretation.
- `*_research.md` — combined dossier.
- `*_learn.md` — explainable study note.

Every report includes a **data-quality summary** and the mandatory disclaimer:
*"Educational/informational only — not financial advice. Quantitative metrics describe historical/current data and do not predict future performance."*

---

## 13. Risks & Mitigations

| **Risk** | **Mitigation** |
|----------|----------------|
| Misread as prediction/advice | Hard guardrail + explicit fact/estimate labels + disclaimer |
| Corrupted/stale data → wrong metric | Validation layer, freshness tags, min-sample rejection |
| Hallucinated conclusions | Mandatory citations; deterministic audit core |
| Quant formula errors | Reference-value unit tests for every formula |
| API limits / cost / latency | Caching, backoff, budget ceiling, response-time targets |
| Unverified contracts | Flag "unauditable," lower confidence |
| False sense of safety | Never "safe"; "lower observed risk" |
| Scope creep into ML forecasting | Core forbids it; experimental module is separate + gated |
| Knowledge base degrading (noise) | Hard quality gate, dedup, conflict review, quarantine |
| Knowledge silently altering results | Frozen core; knowledge only contextualizes; explicit PRs for logic changes |
| Stale/superseded findings | Supersession marking + recency check; brain version per report |

---

## 14. Roadmap

1. **MVP** — Audit Mode (Ethereum) + data validation + cited report.
2. **v0.2** — Full deterministic risk scoring + holder HHI.
3. **v0.3** — Quant Engine (returns, volatility, drawdown, Sharpe, VaR) + validation tests.
4. **v0.4** — Research Mode (combined dossier) + liquidity depth/slippage.
5. **v0.5** — Learn Mode + multi-chain + confirmation gates.
6.5. **v0.5b** — Knowledge Core: crawler + quality gate + extractor + vector index + `SECOND-KNOWLEDGE-BRAIN.md` integration.
6. **v0.6** — Monitoring, freshness checks, budget/latency controls.
7. **v1.0** — Production-hardened CLI, full docs, reproducibility, release.
