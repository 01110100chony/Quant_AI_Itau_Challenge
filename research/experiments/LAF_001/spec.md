# LAF_001 — Liquidity Absorption Fragility

- **Experiment ID:** `LAF_001`
- **Spec version:** `v1.0-frozen`
- **Status:** content frozen; exact H1-LAF is registered in the separate execution-authorization commit.
- **Human approval:** explicit final Research order of 2026-08-15.
- **Promotion status:** Research candidate only; not validated or promoted.

## Research question and mechanism

Does aggregate liquidity-absorption fragility observable at the close of month
`t` contain incremental information, beyond contemporaneous volatility, about
SPY entry-to-trough loss in month `t+1`?

The proposed mechanism is that unusually large absolute adjusted-price moves
relative to the provider-consistent monetary-volume proxy indicate thin
aggregate absorption. Persistent cross-ETF fragility at month-end may precede
larger next-month downside excursions. This Research test is falsification-first
and is not a portfolio backtest.

- **H0:** conditional on contemporaneous SPY realized volatility,
  `beta_LAF <= 0`.
- **H1:** conditional on contemporaneous SPY realized volatility,
  `beta_LAF > 0`.
- **Expected direction:** positive `beta_LAF`.

## Frozen samples and access

- Universe: exactly `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`.
- Target asset: `SPY`.
- Warm-up: calendar year 2003.
- Research target months: `2004-01` through `2016-12`.
- Validation: `2017-01` through `2021-12`; `CLOSED`, not loaded.
- Final OOS: `2022-01` through `2025-12`; `CLOSED`, not loaded.
- 2026: excluded.
- A Research observation is eligible only when feature, execution and target
  are formed without any historical row from 2017 onward.
- Source: the five immutable Yahoo Chart API raws from retrieval
  `20260815T055848814Z`, hash-checked before parsing with the Stage A1c parser.
- Calendar: XNYS through `exchange-calendars`.

## Frozen daily construction

For ETF `i` and XNYS session `d`:

```text
r_i,d  = ln(AdjClose_i,d / AdjClose_i,d-1)
MV_i,d = Close_i,d * Volume_i,d
PI_i,d = abs(r_i,d) / MV_i,d
x_i,d  = ln(PI_i,d), only when PI_i,d > 0 and MV_i,d > 0
```

`MV` is called a provider-consistent monetary-volume proxy. The literal
historical Volume unit is not claimed to have been independently proven. No
epsilon, repair, fill, backfill or future shift is allowed. An ETF-day is
missing when the stated positivity conditions fail.

For every ETF, normalization uses exactly the prior 252 session observations,
excluding the current session:

```text
median_i,d = median(x_i,d-252 ... x_i,d-1)
MAD_i,d    = median(abs(x - median_i,d))
z_i,d      = (x_i,d - median_i,d) / (1.4826 * MAD_i,d)
```

All 252 prior values must be observed and `MAD > 0`; otherwise `z_i,d` is
missing. Full-sample normalization is prohibited.

## Frozen split-regime embargo

The Stage A1c corporate-action table contains one known split: IWM on
`2005-06-09`. For every audited split, that ETF is excluded from the daily
aggregate on the split session and on each later session whose prior 252-session
normalization window still contains a pre-split session. It is eligible again
only when the complete prior window belongs to the post-split regime.

The daily aggregate is defined only when at least four ETFs are eligible:

```text
A_d = median_i(z_i,d)
```

Before any target association, positive scale changes of `0.5` and `2.0` to
pre-split Close and/or Volume must leave `A_d` and monthly `LAF` unchanged
outside the embargo within absolute tolerance `1e-12`. Failure is a hard stop.

## Frozen monthly feature and control

For month `t`, use exactly the last 21 common XNYS sessions ending on its final
session:

```text
LAF_t = arithmetic mean(A_d)
RV_t  = sqrt(sum(r_SPY,d^2))
```

All 21 daily values must exist. No monthly median, maximum, percentile, EWMA or
alternative lookback is authorized.

- Feature timestamp: official close of the final common session in month `t`.
- Decision: after that close.
- Execution timestamp: first tradable SPY open in target month `t+1`.

## Frozen target

For SPY session `d`:

```text
factor_d  = AdjClose_d / Close_d
AdjOpen_d = Open_d * factor_d
AdjLow_d  = Low_d * factor_d
```

For target month `t+1`:

```text
P_entry      = AdjOpen on the first session of the month
TailLoss_t+1 = max(0, -min_d(ln(AdjLow_d / P_entry)))
```

Target-only changes must leave every feature exactly unchanged.

## Frozen Research models

Primary and only full model:

```text
TailLoss_t+1 = alpha + beta_LAF * LAF_t + beta_RV * RV_t + epsilon_t+1
```

Single control model:

```text
TailLoss_t+1 = alpha + beta_RV * RV_t + epsilon_t+1
```

- OLS with intercept;
- Bartlett Newey-West HAC with `maxlags=3`;
- small-sample correction active;
- Student-t inference;
- complete cases;
- unilateral primary p-value for `beta_LAF > 0`;
- no post-result variant.

## Frozen prospective gates

`CorePass` requires `beta_LAF > 0` and unilateral HAC p-value `< 0.10`. The
10% level is a prospective Research screen, not final proof.

`IncrementalPass` requires adjusted R-squared of the full model to exceed that
of RV-only.

`StabilityPass` requires positive `beta_LAF` separately in target months
`2004-2010` and `2011-2016`, with no isolated significance requirement. A block
without enough complete cases to estimate the frozen model cannot pass.

`StatePass` uses an expanding Q80 of LAF calculated from prior months only,
excluding the current month, after at least 36 prior LAF observations. It
requires at least 8 high states (`LAF > prior Q80`), at least 24 normal states,
and higher mean TailLoss in high states. Insufficient counts cannot pass.

```text
GO = CorePass AND IncrementalPass AND StabilityPass AND StatePass

CONDITIONAL_GO = CorePass AND IncrementalPass
                 AND exactly one of StabilityPass/StatePass is false

NO_GO = every other result
```

Secondary diagnostics cannot rescue `CorePass`.

## Pre-association mechanical disclosure

The frozen missingness rule yields 8 primary complete months out of the
156-month Research target grid. There are zero complete cases in 2004–2010,
8 in 2011–2016 and zero complete cases with a prior-only state classification.
These are construction counts, not feature-target association results. No rule
was relaxed after observing them; mechanically non-estimable/count-deficient
gates remain false if execution proceeds.

## Hard stops

Validation, Final OOS, strategy, portfolio and backtest remain prohibited.
No provider, universe, sample, lookback, aggregation, target, threshold, model,
HAC option or gate may change after H1-LAF. A negative Research result must be
recorded literally and cannot trigger parameter search.
