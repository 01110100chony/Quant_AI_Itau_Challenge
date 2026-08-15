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

`LAF_001 — Liquidity Absorption Fragility` is the active DRAFT candidate. It is
not promoted, scientifically frozen, predictively tested or validated. Human
authorization covered the completed Stage A1 structural audit and the limited
Stage A1c boundary/provenance correction; it does not cover Stage A2.

The fixed candidate universe is `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`, with `SPY`
as candidate target asset. Warm-up is limited to 2003 and Research to
2004–2016. Every date from `2017-01-01` onward remains CLOSED and 2026 is
excluded from historical arrays. The immutable raw response nevertheless
contained dynamic 2026 metadata, which the original artifact emitted and
Stage A1c disclosed and excluded from corrective canonical outputs. Yahoo
Finance Chart API and XNYS remain candidate inputs only. The structural audit
is feasibility evidence, not a predictive or economic result.

The decision timestamp is after the close of the last monthly session. Any
eventual economic execution could occur only at the next session open. Feature,
target, normalization, missingness, statistical gates and portfolio choices
remain unresolved unless the DRAFT specification records otherwise as `TBD —
requires human decision`.

Stage A1c verified zero historical rows and zero corporate actions dated 2017
or later and all five raw hashes unchanged. Its 41-session IWM event audit was
consistent with local continuity but did not prove Volume-unit semantics.
`SAFE_TO_RUN_LAF_STAGE_A2 = NO`; human review and a separate order remain
required.

## Most recently closed experiment

`CM_001 — Cross-Market Information Transmission` completed its one authorized Research Stage B execution at corrective version `v1.0.1-frozen` with status `NO_GO`. `CorePass=false`; H1 and secondary diagnostics were not used to rescue H2. Original H1/H2 remain immutable, and H2c records corrective H1c `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`.

The immutable thesis uses `XSD` leader, `QQQ/SPY` controls, `0052` follower, `TAIEX` primary benchmark and `0050` robustness benchmark. H2 `SemiSpecific → IntradayRel` is primary; H1 `GapRel` and H3 controlled by `BroadTech` and `PrevTWRel` are secondary/non-rescuing. The full models, providers, raw-price policy, corporate-action exclusions, timing, HAC inference, P1/P2, blocks and gates are in the [`canonical specification`](../cross_market/specification.md).

Research 2010–2018 was inspected once. Validation 2019–2022 and Final OOS 2023–2025 remain CLOSED and were not loaded; 2026 is excluded. CM_001 stops at `NO_GO`, so no holdout opening is requested.

Specification freeze and any later Research verdict are not validation or promotion.
