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
- [Previously closed experiment](#previously-closed-experiment)

## Promoted specification

No thesis is officially promoted or validated.

## Active candidate

There is no active Research candidate.

## Most recently closed experiment

`LAF_001 — Liquidity Absorption Fragility` completed its single frozen Research
execution at H1-LAF `cfbdff048ae8b0f7d9b8a1a804558bf59b656c1b`, authorized by
`842a87c2ca4ff7e65627f29d93726e9cae22c169`. All four prospective gates were
false and the literal verdict is `NO_GO`. It is not validated or promoted.

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
not used to alter the frozen design. The primary estimate was
`beta_LAF=0.01620172883243451`, with one-sided HAC p
`0.22659457277469747`. Validation and Final OOS remain closed.

## Previously closed experiment

`CM_001 — Cross-Market Information Transmission` completed its one authorized Research Stage B execution at corrective version `v1.0.1-frozen` with status `NO_GO`. `CorePass=false`; H1 and secondary diagnostics were not used to rescue H2. Original H1/H2 remain immutable, and H2c records corrective H1c `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`.

The immutable thesis uses `XSD` leader, `QQQ/SPY` controls, `0052` follower, `TAIEX` primary benchmark and `0050` robustness benchmark. H2 `SemiSpecific → IntradayRel` is primary; H1 `GapRel` and H3 controlled by `BroadTech` and `PrevTWRel` are secondary/non-rescuing. The full models, providers, raw-price policy, corporate-action exclusions, timing, HAC inference, P1/P2, blocks and gates are in the [`canonical specification`](../cross_market/specification.md).

Research 2010–2018 was inspected once. Validation 2019–2022 and Final OOS 2023–2025 remain CLOSED and were not loaded; 2026 is excluded. CM_001 stops at `NO_GO`, so no holdout opening is requested.

Specification freeze and any later Research verdict are not validation or promotion.
