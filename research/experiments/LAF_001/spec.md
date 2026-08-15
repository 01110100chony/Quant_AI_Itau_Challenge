# LAF_001 — Liquidity Absorption Fragility

- **Experiment ID:** `LAF_001`
- **Spec version:** `v0.1-draft`
- **Status:** `DRAFT`
- **Created at:** `2026-08-15T01:40:48-03:00`
- **Freeze status:** This document is not a scientific freeze. Completed Stage
  A1/A1c structural audits do not authorize Stage A2 or predictive execution.

## Candidate research contract

- **Research question:** `TBD — requires human decision`; the working thesis is
  Liquidity Absorption Fragility.
- **Economic mechanism:** liquidity absorption fragility; the exact causal and
  empirical statement is `TBD — requires human decision`.
- **Null hypothesis:** `TBD — requires human decision`.
- **Alternative hypothesis:** `TBD — requires human decision`.
- **Expected direction:** `TBD — requires human decision`.
- **Feature X_t:** `TBD — requires human decision`; no `PI`, `LAF` or alternative
  proxy formula is approved in this DRAFT.
- **Target Y_t+h:** `TBD — requires human decision`; the candidate target asset is
  `SPY`, while the exact target price and definition remain unresolved.
- **Information available at:** Stage A1/A1c structurally observed candidate
  daily fields after the official session close; the final point-in-time
  feature contract is `TBD — requires human decision`.
- **Decision timestamp:** after the close of the final XNYS session of each month.
- **Earliest possible economic execution:** open of the first following XNYS
  session. No execution or strategy is authorized.
- **Candidate universe:** fixed `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`.
- **Candidate target asset:** `SPY`.
- **Benchmark:** `TBD — requires human decision`.
- **Frequency/horizon:** candidate monthly decision timing; target horizon is
  `TBD — requires human decision`.
- **Candidate primary data source:** Yahoo Finance Chart API, structurally
  audited in Stage A1/A1c but not approved as the final source.
- **Secondary provider:** `TBD — requires human decision`.
- **Candidate calendar:** XNYS via `exchange-calendars`.
- **Field contract:** raw OHLCV, Adj Close and corporate actions must remain
  separate.
- **Warm-up:** `2003-01-01`–`2003-12-31`; structurally inspected in Stage A1/A1c.
- **Research sample:** `2004-01-01`–`2016-12-31`; structurally inspected in
  Stage A1/A1c only.
- **Validation sample:** `TBD — requires human decision`; CLOSED.
- **Final OOS:** `TBD — requires human decision`; CLOSED.
- **2017 onward:** CLOSED for historical rows and corporate actions; no series
  from this period may be acquired, loaded, processed or displayed.
- **2026:** excluded from historical arrays. Dynamic current metadata found in
  the immutable raw response is quarantined by the Stage A1c whitelist and may
  not be emitted with values.
- **Primary metric:** `TBD — requires human decision`.
- **Secondary metrics:** `TBD — requires human decision`.
- **Controls:** `TBD — requires human decision`.
- **Placebos:** `TBD — requires human decision`.
- **Known confounders:** `TBD — requires human decision`.
- **Robustness-only tests:** `TBD — requires human decision`.
- **GO criteria:** `TBD — requires human decision`.
- **CONDITIONAL GO criteria:** `TBD — requires human decision`.
- **NO-GO criteria:** `TBD — requires human decision`.
- **Frozen parameters:** none; this is a DRAFT, not a freeze.
- **Changes since previous specification:** Stage A1 and the limited Stage A1c
  correction were completed without defining any unresolved scientific field.
- **Human approvals:** Stage A1 structural acquisition/audit and the limited
  Stage A1c metadata, provenance and 41-session IWM split-unit correction were
  explicitly authorized on 2026-08-15. Stage A2 remains unauthorized.
- **Git commit:** empty because this specification is not frozen.

## Material decisions still pending

Each item below is `TBD — requires human decision`:

- zero-return policy;
- missingness policy;
- MAD-zero policy;
- final normalization formula;
- Corwin-Schultz formula;
- exact RV definition;
- exact target price and target definition;
- secondary provider;
- Validation dates and access;
- Final OOS dates and access;
- statistical gates;
- portfolio rule;
- cash treatment;
- costs;
- slippage.

## Current hard stop

Stage A1/A1c are closed at structural feasibility. This DRAFT does not authorize
new acquisition or Stage A2 processing. It does not authorize calculation of
general returns, `PI`, `LAF`, `RV`, Corwin-Schultz or `TailLoss`; feature or
target construction; feature–target association; Stage B; Validation; Final
OOS; strategy; portfolio; or backtest.
