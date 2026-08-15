# Cross-Market specification — CM_001 v1.0.1-frozen

## Quick Summary

- **Purpose:** especificação científica integralmente decidida para `CM_001` Stage B.
- **Read when:** implementing, executing or auditing CM_001.
- **Load next:** [`timing.md`](timing.md), [`data_contract.md`](data_contract.md), or [`validation_plan.md`](validation_plan.md).
- **Authority:** corrective content `v1.0.1-frozen`; H2c recorded exact H1c, and the one authorized Research execution returned `NO_GO`.
- **Scope:** Research `2010-01-01`–`2018-12-31`; Validation e Final OOS fechados.

## Contents

- [Thesis and variables](#thesis-and-variables)
- [Frozen data policies](#frozen-data-policies)
- [Timing and samples](#timing-and-samples)
- [Frozen models and inference](#frozen-models-and-inference)
- [Frozen falsification and diagnostics](#frozen-falsification-and-diagnostics)
- [Frozen gates](#frozen-gates)
- [Execution governance](#execution-governance)

## Thesis and variables

Pergunta: movimentos específicos de semicondutores formados durante a sessão americana contêm informação incremental sobre a tecnologia taiwanesa seguinte, além de tecnologia ampla e informação já presente em Taiwan?

- Leader: `XSD`; US controls: `QQQ`, `SPY`.
- Follower: `0052`; primary Taiwan benchmark: `TAIEX`; robustness benchmark: `0050`.
- Primary feature: `SemiSpecific`; control: `BroadTech`.
- Primary target: H2 / `IntradayRel`; secondary: H1 / `GapRel` and H3 / controlled `IntradayRel`.

For every eligible US regular session `s`:

```text
r_ID(asset,s) = log(raw Close(asset,s) / raw Open(asset,s))
SemiSpecific_s = r_ID(XSD,s) - r_ID(QQQ,s)
BroadTech_s = r_ID(QQQ,s) - r_ID(SPY,s)
```

For Taiwan session `j`, sum both components over the identical eligible set `S(j)`; do not normalize a multi-session window.

```text
GapRel_j = log(Open0052_j / Close0052_{j-1})
         - log(OpenTAIEX_j / CloseTAIEX_{j-1})

IntradayRel_j = log(Close0052_j / Open0052_j)
              - log(CloseTAIEX_j / OpenTAIEX_j)

PrevTWRel_j = log(Close0052_{j-1} / Close0052_{j-2})
            - log(CloseTAIEX_{j-1} / CloseTAIEX_{j-2})
```

Frozen `0050` robustness targets are literal substitutions of the benchmark leg:

```text
GapRel0050_j = log(Open0052_j / Close0052_{j-1})
             - log(Open0050_j / Close0050_{j-1})
IntradayRel0050_j = log(Close0052_j / Open0052_j)
                  - log(Close0050_j / Open0050_j)
PrevTWRel0050_j = log(Close0052_{j-1} / Close0052_{j-2})
                - log(Close0050_{j-1} / Close0050_{j-2})
```

## Frozen data policies

- Yahoo immutable Chart JSON supplies raw `Open`/`Close` for `XSD/QQQ/SPY`; TWSE official supplies `0052/0050/TAIEX`, official Taiwan sessions and corporate actions.
- Keep all 2,223 official Taiwan sessions in the ledger. When required OHLC is unavailable, exclude only the affected observation and never impute.
- Primary features, targets and controls use raw OHLC. `Adj Close` is audit/reference only. Never combine raw Open with adjusted Close.
- Primary H1 excludes the six confirmed `0052` event dates whose previous-close-to-open leg crosses an action. Primary H3 excludes the six following target sessions whose `PrevTWRel` close-to-close leg crosses an action. H2 retains the six event sessions unless a specific documented intraday issue exists; Stage A found none.
- `0050` robustness applies the same mechanical rule when a confirmed action in either `0052` or `0050` affects the relevant leg.
- US calendar is `exchange-calendars==4.13.2`, `XNYS`, `America/New_York`, with actual opens/closes, DST and early closes. Taiwan uses official TWSE session dates and regular `09:00`–`13:30 Asia/Taipei` hours. Preserve the 15 official TWSE dates omitted by `XTAI`; exclude the one `XTAI` extra date.

## Timing and samples

The observation is Taiwan session `j`. Its information window is the open interval `(previous Taiwan close, current Taiwan open)`. A US regular session is eligible only if its actual open and close both lie strictly inside. Empty windows remain in the ledger with `n_us_sessions=0`, are excluded from H1/H2/H3, and receive no zero/forward/back-filled feature.

- Research: `2010-01-01`–`2018-12-31`, inclusive.
- Validation: `2019-01-01`–`2022-12-31`, `CLOSED`.
- Final OOS: `2023-01-01`–`2025-12-31`, `CLOSED`.
- Calendar year 2026 is excluded from all samples.

Before any association is estimated, mechanical usable counts must equal H1 `1938`, H2 `2034`, H3 `1850`; divergence is a hard stop.

## Frozen models and inference

```text
H1: GapRel = alpha + beta * SemiSpecific + epsilon
H2: IntradayRel = alpha + beta * SemiSpecific + epsilon
H3: IntradayRel = alpha + beta * SemiSpecific
                  + gamma * BroadTech + delta * PrevTWRel + epsilon
```

- OLS with intercept, raw log-return units, no winsorization and no outlier removal.
- Newey-West/HAC covariance: Bartlett kernel, `maxlags=5`, small-sample correction on, t inference on.
- Directional test is one-sided `beta > 0`; also report bilateral 95% CI.
- Report `N`, beta, HAC SE, t, one-sided p, CI, adjusted R², and one-SD `SemiSpecific` effect in target basis points.

## Frozen falsification and diagnostics

- P1 for H2 and H3: circularly shift only `SemiSpecific`; `B=5000`, seed `7`, offsets sampled uniformly with replacement from `{21,...,N-21}`. H3 keeps target and other controls fixed. `p_perm=(1+count(beta_perm>=beta_observed))/(B+1)`.
- P2 for H2: construct the eligible-window table before any target filter, map every window to the next eligible window's `SemiSpecific`, then join H2 and form the common-complete sample. An eligible future window is never skipped because its own target is missing; an empty-US window is skipped. Refit the correctly aligned model on the identical sessions. Pass when future one-sided p is at least `0.10` and the correctly aligned standardized beta exceeds the future standardized beta.
- Stability blocks: `2010–2012`, `2013–2015`, `2016–2018`; pass support when H2 beta is positive in at least two blocks.
- Secondary only: H1/H2/H3 against `0050`; H2/H3 restricted to `n_us_sessions=1`; Spearman Rank IC and `IntradayRel` means by `SemiSpecific` quintile. These cannot rescue H2.

## Frozen gates

```text
CorePass = beta_H2 > 0 and p_H2_one_sided < 0.05
RobustnessPass = p_perm_H2 < 0.05 and positive H2 beta in at least 2/3 blocks
SpecificityPass = beta_H3 > 0 and p_H3_one_sided < 0.05 and p_perm_H3 < 0.05
TimingPass = P2 pass

GO = all four gates pass
CONDITIONAL_GO = CorePass and at least one support gate fails
NO_GO = CorePass fails
```

H1 and all secondary results are explicitly non-rescuing. No new assets, windows, variants, thresholds or post-result optimizations are authorized.

## Execution governance

Stage B may execute exactly once only after H1 freezes this scientific content and H2 records the exact H1 hash without changing scientific content. Any implementation/count/freeze conflict requires stop. Validation and Final OOS cannot be loaded. Their opening requires later, separate human authorization under the OOS policy.
