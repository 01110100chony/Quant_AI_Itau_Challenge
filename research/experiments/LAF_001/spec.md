# LAF_001 — Liquidity Absorption Fragility

- **Experiment ID:** `LAF_001`
- **Spec version:** `v0.1-draft`
- **Status:** `DRAFT`
- **Created at:** `2026-08-15T01:40:48-03:00`
- **Freeze status:** This document is not a freeze and contains no authorization
  for empirical execution.

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
- **Information available at:** for future Stage A1 timing audit only, candidate
  daily fields are available after the official session close; the final
  point-in-time feature contract is `TBD — requires human decision`.
- **Decision timestamp:** after the close of the final XNYS session of each month.
- **Earliest possible economic execution:** open of the first following XNYS
  session. No execution or strategy is authorized.
- **Candidate universe:** fixed `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`.
- **Candidate target asset:** `SPY`.
- **Benchmark:** `TBD — requires human decision`.
- **Frequency/horizon:** candidate monthly decision timing; target horizon is
  `TBD — requires human decision`.
- **Candidate primary data source:** Yahoo Finance Chart API, only for a future
  structural audit.
- **Secondary provider:** `TBD — requires human decision`.
- **Candidate calendar:** XNYS via `exchange-calendars`.
- **Field contract:** raw OHLCV, Adj Close and corporate actions must remain
  separate.
- **Warm-up:** `2003-01-01`–`2003-12-31`, permitted only when a later human order
  authorizes Stage A1 empirical work.
- **Research sample:** `2004-01-01`–`2016-12-31`, permitted only when a later
  human order authorizes Stage A1 empirical work.
- **Validation sample:** `TBD — requires human decision`; CLOSED.
- **Final OOS:** `TBD — requires human decision`; CLOSED.
- **2017 onward:** CLOSED; must not be acquired, loaded, processed or displayed.
- **2026:** excluded in full.
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
- **Changes since previous specification:** first registered LAF_001 DRAFT.
- **Human approvals:** documentary Stage A1 preparation only, explicitly granted
  on 2026-08-15. Empirical Stage A1 remains unauthorized.
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

This DRAFT does not authorize market-data acquisition, loading, processing or
display. It does not authorize calculation of returns, `PI`, `LAF`, `RV`,
Corwin-Schultz or `TailLoss`; feature–target association; Stage B; Validation;
Final OOS; strategy; portfolio; or backtest.
