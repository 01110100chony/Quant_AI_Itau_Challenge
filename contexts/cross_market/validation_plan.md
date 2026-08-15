# Cross-Market validation plan — CM_001 v1.0.1-frozen

## Quick Summary

- **Purpose:** frozen Stage B models, falsification, diagnostics and gates.
- **Read when:** testing or interpreting the frozen Research execution.
- **Load next:** [`../research/oos_policy.md`](../research/oos_policy.md) before any later holdout request.
- **Authority:** scientific content frozen pending H1 provenance registration; this file never opens Validation/OOS.

## Contents

- [Stage separation](#stage-separation)
- [Primary models](#primary-models)
- [Falsification](#falsification)
- [Secondary diagnostics](#secondary-diagnostics)
- [Decision gates](#decision-gates)

## Stage separation

Stage A is structurally closed with `PASS_READY_FOR_SPEC_FREEZE`. Stage B is a one-time Research-only execution after H1/H2. Validation `2019-01-01`–`2022-12-31` and Final OOS `2023-01-01`–`2025-12-31` remain closed and cannot be acquired or loaded. Year 2026 is excluded.

Before association, availability flags must reconcile exactly to H1 `1938`, H2 `2034`, H3 `1850`; otherwise stop. Unit tests before H1 use synthetic fixtures only. A one-time execution receipt prevents silent reruns.

## Primary models

- H1: OLS `GapRel ~ 1 + SemiSpecific`.
- H2 primary: OLS `IntradayRel ~ 1 + SemiSpecific`.
- H3: OLS `IntradayRel ~ 1 + SemiSpecific + BroadTech + PrevTWRel`.
- Newey-West/HAC Bartlett `maxlags=5`, small-sample correction and t inference.
- Positive one-sided beta test plus bilateral 95% CI; no winsorization or outlier removal.
- Report N, beta, HAC SE, t, one-sided p, CI, adjusted R² and one-SD effect in target bps.

## Falsification

P1 circular shift for H2/H3 uses `B=5000`, seed `7`, offsets uniformly with replacement in `{21,...,N-21}`, shifts only `SemiSpecific`, and computes `(1 + # beta_perm >= beta_observed)/(B+1)`. H3 target, `BroadTech` and `PrevTWRel` remain fixed.

P2 H2 maps the next eligible Taiwan information-window `SemiSpecific` before any target-completeness filter. Missing target on that future window cannot change its identity; empty-US windows are skipped. It compares future and correctly aligned fits on the identical common-complete sessions and passes only if future one-sided p `>=0.10` and correct standardized beta exceeds future standardized beta.

Frozen H2 stability blocks are `2010–2012`, `2013–2015`, `2016–2018`; support requires positive beta in at least two.

## Secondary diagnostics

- H1/H2/H3 using literal `0050` relative targets.
- H2/H3 on `n_us_sessions=1`.
- Spearman Rank IC and target means by `SemiSpecific` quintile.

All are secondary and non-rescuing.

## Decision gates

```text
CorePass = beta_H2 > 0 and p_H2 < 0.05
RobustnessPass = p_perm_H2 < 0.05 and positive beta in >=2/3 blocks
SpecificityPass = beta_H3 > 0 and p_H3 < 0.05 and p_perm_H3 < 0.05
TimingPass = frozen P2 pass
GO = all pass
CONDITIONAL_GO = CorePass and any support gate fails
NO_GO = CorePass fails
```

H1 and secondary analyses cannot rescue the primary gate. After the one authorized Research execution, record the literal verdict and stop. No variant search, parameter change, Validation or Final OOS access is authorized.
