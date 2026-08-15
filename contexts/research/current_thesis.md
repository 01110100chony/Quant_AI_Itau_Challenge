# Current thesis

## Quick Summary

- **Purpose:** identify any active candidate without claiming validation and preserve
  the most recently closed experiment.
- **Read when:** implementing or describing the active research candidate.
- **Load next:** [`../../research/experiments/LAF_001/spec.md`](../../research/experiments/LAF_001/spec.md)
  and [`oos_policy.md`](oos_policy.md).
- **Authority:** `PROJECT_STATUS.md` controls current execution state.

## Contents

- [Promoted specification](#promoted-specification)
- [Active candidate](#active-candidate)
- [Most recently closed experiment](#most-recently-closed-experiment)

## Promoted specification

No thesis is officially promoted or validated.

## Active candidate

`LAF_001 — Liquidity Absorption Fragility` is the active Research candidate.
Its `v1.0-frozen` scientific content is human-approved and awaiting exact
H1-LAF registration plus a separate metadata authorization commit before the
single Research association execution. It is not predictively tested,
validated or promoted.

The fixed universe is `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`, with `SPY` as target.
Warm-up is 2003 and Research target months are 2004-01–2016-12. Validation
2017-01–2021-12 and Final OOS 2022-01–2025-12 are CLOSED; 2026 is excluded.
Only the five immutable Yahoo snapshots and XNYS are authorized.

The frozen construction uses prior-only 252-session robust normalization,
split-regime embargo, at least four ETFs for daily median aggregation, one
21-session monthly mean, contemporaneous SPY RV and next-month adjusted
entry-to-low TailLoss. Decision is after month-end close and informational
execution is the next month's first SPY open. OLS/HAC(3) and all gates are
frozen in the canonical specification.

Stage A1d ended without payload and has no scientific result. Positive-scale
invariance and target independence passed pre-association. The literal
missingness contract yields only 8 complete Research months, zero in the first
stability block and zero state-classified complete rows; these limitations were
not used to alter the frozen design. Validation and Final OOS remain closed.

## Most recently closed experiment

`CM_001 — Cross-Market Information Transmission` completed its one authorized Research Stage B execution at corrective version `v1.0.1-frozen` with status `NO_GO`. `CorePass=false`; H1 and secondary diagnostics were not used to rescue H2. Original H1/H2 remain immutable, and H2c records corrective H1c `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`.

The immutable thesis uses `XSD` leader, `QQQ/SPY` controls, `0052` follower, `TAIEX` primary benchmark and `0050` robustness benchmark. H2 `SemiSpecific → IntradayRel` is primary; H1 `GapRel` and H3 controlled by `BroadTech` and `PrevTWRel` are secondary/non-rescuing. The full models, providers, raw-price policy, corporate-action exclusions, timing, HAC inference, P1/P2, blocks and gates are in the [`canonical specification`](../cross_market/specification.md).

Research 2010–2018 was inspected once. Validation 2019–2022 and Final OOS 2023–2025 remain CLOSED and were not loaded; 2026 is excluded. CM_001 stops at `NO_GO`, so no holdout opening is requested.

Specification freeze and any later Research verdict are not validation or promotion.
