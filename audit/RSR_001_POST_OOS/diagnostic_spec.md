# RSR_001_POST_OOS_DIAGNOSTIC — frozen diagnostic specification

- **Diagnostic ID:** `RSR_001_POST_OOS_DIAGNOSTIC`
- **Classification:** `POST_OOS_EXPLORATORY`
- **Frozen at:** `2026-08-15T00:14:22.7905302-03:00`
- **Registry:** deliberately excluded from the canonical experiment registry
- **Required output label:**
  `POST_OOS_EXPLORATORY — NOT VALIDATION — CANNOT RESCUE RSR_001`

## Scientific status

The RSR_001 OOS has already been consumed. This diagnostic describes parameter
sensitivity after observing the result. It cannot validate a parameter, change
the frozen primary, replace `RSR_001 = NO_GO`, or produce `GO` or
`CONDITIONAL_GO`. Any favorable pattern is hypothesis generation for a future
prospective or independently frozen dataset.

## Fixed inputs and timing

- Frozen CSV only; no data download or refresh.
- Universe: XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY.
- Monthly feature at the final observed trading day of each signal month.
- Target: signal date exclusive through the final trading day of the complete
  following month, inclusive.
- Specification-compliant OOS only: 2019-03-29 through 2026-06-30, `n=88`,
  with final target ending 2026-07-31.
- Research: 2001-02-28 through 2018-10-31, `n=213`.
- Quarantine 2018-11-30 through 2019-02-28 is excluded from every metric.
- Top/Bottom fixed at 3; equal weights `+1/3` and `-1/3`.
- OOS blocks fixed at positions 1..30, 31..60, and 61..88. `array_split(88)`
  is prohibited.

## Closed grid

- Estimation window `W`: 126, 252, 504.
- Reversal window `S`: 10, 21, 42.
- Market proxy: SPY and equal-weight return of the nine sector ETFs.
- Cost: 5, 10, and 20 bps, applied only to economic metrics.
- Top/Bottom: 3, fixed.

This is exactly 18 signal specifications and 54 economic combinations. No
combination may be added after results are computed.

## Required statistics

For each signal specification, report research, seen OOS, and each of the three
fixed OOS blocks:

- mean and median Rank IC;
- IC hit rate;
- nominal P1 cross-sectional and P2 temporal one-sided permutation p-values,
  each with 5,000 draws, seed 7, and
  `p=(1 + count(null >= observed))/(N + 1)`;
- Holm-adjusted P1 and P2 within each 18-specification family and sample.

For each economic combination and the same samples, report:

- annualized gross log return, cost, and net log return;
- annualized volatility and Sharpe on monthly net log returns;
- frozen additive-log drawdown and conventional equity-curve drawdown;
- turnover;
- compounded annualized log-equivalent return and executable simple-return
  CAGR as secondary, non-substitute metrics.

## Surface interpretation

Report all rows, not only the best. Stability is descriptive across the three
fixed OOS blocks. Monotonicity is tested descriptively along ordered W and S
axes while holding the other signal dimensions fixed. Cost monotonicity is
mechanical and must not be presented as scientific support.

No result from this diagnostic changes the frozen primary or the corrected
verdict. The only permitted conclusion label is:

`POST_OOS_EXPLORATORY — NOT VALIDATION — CANNOT RESCUE RSR_001`.

