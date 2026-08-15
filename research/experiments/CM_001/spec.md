# CM_001 — Cross-Market Information Transmission

## Identity

- **Experiment ID:** CM_001
- **Spec version:** `v1.0.1-frozen`
- **Status:** `NO_GO`; corrected Stage B executed once
- **Research:** `2010-01-01`–`2018-12-31`
- **Validation:** `2019-01-01`–`2022-12-31`, CLOSED
- **Final OOS:** `2023-01-01`–`2025-12-31`, CLOSED
- **2026:** excluded
- **Canonical specification:** [`contexts/cross_market/specification.md`](../../../contexts/cross_market/specification.md)

The original scientific content was frozen at H1 `cc686c7a0c25b70de0bc31558d4d1bf6b64b3818`, with H2 `3cebbb0c54bea8b6023eb7e716de53d98402eeb9`. Both are preserved but superseded only for the pre-empirical P2 executable. Corrective H1c `417ffa85f954bd3ee87d11b35dbbef3b4da941e6` is registered by H2c `694edf0d745c044cbfa9c257c44719bc0cd9f4ea`; corrected Stage B executed once and returned `NO_GO`.

## Hypotheses and models

- H1: positive beta in `GapRel ~ 1 + SemiSpecific`.
- H2 primary: positive beta in `IntradayRel ~ 1 + SemiSpecific`.
- H3: positive beta in `IntradayRel ~ 1 + SemiSpecific + BroadTech + PrevTWRel`.

Use raw log Open/Close, OLS with intercept, HAC/Newey-West Bartlett `maxlags=5`, finite-sample correction, t inference, positive one-sided p and bilateral 95% CI. No winsorization/outlier removal. Sum multiple eligible US sessions without normalization.

## Frozen data and timing

- Yahoo immutable JSON: `XSD/QQQ/SPY`; TWSE official: `0052/0050/TAIEX`, Taiwan sessions and actions.
- Keep all 2,223 official Taiwan sessions; exclude observations requiring unavailable OHLC; never impute.
- Raw OHLC primary; adjusted close audit only; never raw Open plus adjusted Close.
- H1 excludes six confirmed `0052` event dates; H3 excludes six following sessions; H2 retains event dates absent a documented intraday issue. `0050` robustness applies the same leg rule to actions in either Taiwan ETF.
- US `XNYS`, `America/New_York`, exchange-calendars `4.13.2`, actual DST/early closes. Taiwan official dates, `09:00`–`13:30 Asia/Taipei`; preserve 15 official omissions from XTAI and reject its one extra date.
- Pre-association counts must be exactly H1 `1938`, H2 `2034`, H3 `1850`.

## Frozen falsification and gates

- P1 H2/H3: circular shift only `SemiSpecific`, `B=5000`, seed `7`, offsets `{21,...,N-21}` uniformly with replacement; p formula `(1+#>=observed)/(B+1)`.
- P2 H2: map the next eligible information-window feature before target filtering, then form common-complete rows; pass if future one-sided p `>=0.10` and correct standardized beta is larger.
- Blocks: 2010–2012, 2013–2015, 2016–2018; positive H2 beta in at least two.
- Secondary: `0050` H1/H2/H3; H2/H3 with `n_us_sessions=1`; Spearman Rank IC and target quintile means.
- `CorePass`: positive H2 beta and p `<0.05`.
- `RobustnessPass`: H2 permutation p `<0.05` and positive beta in at least 2/3 blocks.
- `SpecificityPass`: positive H3 beta, H3 p `<0.05`, H3 permutation p `<0.05`.
- `TimingPass`: P2 passes.
- GO if all pass; CONDITIONAL_GO if CorePass and any support gate fails; NO_GO if CorePass fails.

H1 and secondary results cannot rescue H2. Exact formulas and reporting fields are frozen in the canonical specification. New variants, optimization, strategy or holdout access are prohibited.

## Execution control

The implementation is [`src/cross_market_stage_b.py`](../../../src/cross_market_stage_b.py) with synthetic tests in [`tests/research/test_cross_market_stage_b.py`](../../../tests/research/test_cross_market_stage_b.py). The runner preflights mechanical counts without loading prices and executes Research exactly once after H2. Any divergence or failure requires stop and no automatic rerun.
