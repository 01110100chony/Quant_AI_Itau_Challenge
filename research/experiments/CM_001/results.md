# CM_001 — Frozen Stage B Results

## Execution identity

- Specification: `v1.0.1-frozen`.
- Scientific freeze H1c: `417ffa85f954bd3ee87d11b35dbbef3b4da941e6`.
- Metadata freeze H2c / execution commit: `694edf0d745c044cbfa9c257c44719bc0cd9f4ea`.
- Research: `2010-01-01`–`2018-12-31`.
- Validation `2019–2022`: CLOSED and not loaded.
- Final OOS `2023–2025`: CLOSED and not loaded.
- Execution receipt: `COMPLETED`; this was the first and only Stage B execution.

Mechanical counts reconciled before association: H1 `1938`, H2 `2034`, H3 `1850`. Corrected P2 common-complete N was `2033`.

## Main models

OLS with intercept; Newey-West/HAC Bartlett `maxlags=5`, small-sample correction and t inference. The p-values below are the frozen one-sided tests for positive `SemiSpecific` beta.

| Model | N | beta | HAC SE | t | one-sided p | bilateral 95% CI | Adj. R² | 1-SD effect (bps) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H1 | 1938 | 0.022312 | 0.030884 | 0.7225 | 0.235047 | [-0.038256, 0.082881] | -0.000156 | 1.9379 |
| H2 PRIMARY | 2034 | 0.014480 | 0.040817 | 0.3548 | 0.361406 | [-0.065568, 0.094528] | -0.000378 | 1.2723 |
| H3 | 1850 | 0.025626 | 0.043519 | 0.5888 | 0.278020 | [-0.059727, 0.110978] | 0.005126 | 2.2327 |

H2 did not satisfy the frozen primary gate: its beta was positive but the one-sided HAC p-value was `0.361406`, not below `0.05`.

## P1 circular-shift placebo

| Model | B | seed | offset support | count beta_perm >= observed | p_perm |
|---|---:|---:|---|---:|---:|
| H2 | 5000 | 7 | 21–2013 | 1637 | 0.327534 |
| H3 | 5000 | 7 | 21–1829 | 1034 | 0.206959 |

Neither frozen permutation threshold passed.

## P2 future-information placebo

The lead was mapped from the next eligible information window before target filtering. The audit mapping contains 2,033 strict-future pairs, from target `2010-01-05` through `2018-12-27`; zero pairs used the same or an earlier date.

| Fit | N | beta | HAC SE | t | one-sided p | standardized beta | 1-SD effect (bps) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Correct alignment | 2033 | 0.014637 | 0.040820 | 0.3586 | 0.359975 | 0.010777 | 1.2863 |
| Future feature | 2033 | -0.024455 | 0.029825 | -0.8199 | 0.793823 | -0.017712 | -2.1142 |

`TimingPass = true`: future p was at least `0.10` and the correctly aligned standardized beta exceeded the future standardized beta.

## Stability blocks

| Block | N | beta | HAC SE | t | one-sided p | positive beta |
|---|---:|---:|---:|---:|---:|---|
| 2010–2012 | 697 | 0.017190 | 0.064181 | 0.2678 | 0.394453 | true |
| 2013–2015 | 673 | 0.097033 | 0.090940 | 1.0670 | 0.143177 | true |
| 2016–2018 | 664 | -0.080977 | 0.043396 | -1.8660 | 0.968758 | false |

The sign condition was positive in 2/3 blocks, but `RobustnessPass` still failed because P1 H2 did not pass.

## Secondary robustness

All p-values below are secondary/unadjusted and cannot alter the primary verdict.

| Model | N | beta | HAC SE | t | one-sided p | bilateral 95% CI | Adj. R² | 1-SD effect (bps) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H1 vs 0050 | 1929 | 0.026641 | 0.030006 | 0.8879 | 0.187364 | [-0.032206, 0.085487] | 0.000003 | 2.3125 |
| H2 vs 0050 | 2034 | 0.015592 | 0.040501 | 0.3850 | 0.350145 | [-0.063835, 0.095019] | -0.000359 | 1.3700 |
| H3 vs 0050 | 1842 | 0.021395 | 0.043525 | 0.4916 | 0.311545 | [-0.063969, 0.106760] | 0.005455 | 1.8616 |
| H2, n_us_sessions=1 | 1973 | -0.005364 | 0.041040 | -0.1307 | 0.551987 | [-0.085850, 0.075123] | -0.000493 | -0.4527 |
| H3, n_us_sessions=1 | 1797 | -0.006148 | 0.042912 | -0.1433 | 0.556951 | [-0.090311, 0.078015] | 0.004740 | -0.5193 |

Spearman Rank IC was `-0.013846` with two-sided unadjusted p `0.532577`. Mean `IntradayRel` by `SemiSpecific` quintile was: Q1 `0.0005628`, Q2 `-0.0000038`, Q3 `-0.0001030`, Q4 `0.0004214`, Q5 `0.0001866`; this diagnostic does not show monotonic ordering.

## Frozen gates and verdict

| Gate | Value | Evidence |
|---|---|---|
| CorePass | false | H2 one-sided p `0.361406 >= 0.05` |
| RobustnessPass | false | H2 permutation p `0.327534 >= 0.05` |
| SpecificityPass | false | H3 p and permutation p exceed `0.05` |
| TimingPass | true | corrected P2 satisfied both frozen conditions |

Frozen verdict: `NO_GO`, because `CorePass = false`. H1, P2 and all secondary diagnostics were not used to rescue the primary H2 result.

Machine-readable results, provenance, receipt, tables and figures are under [`stage_b/`](stage_b/) and [`stage_b_execution_receipt.json`](stage_b_execution_receipt.json).
