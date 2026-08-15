# LAF_001 — Decision record

## Human Research decision

On 2026-08-15 the researchers approved the complete `v1.0-frozen` LAF_001
Research specification: Yahoo inputs, five-ETF universe, 2003 warm-up,
2004-2016 Research target months, closed Validation/Final OOS, point-in-time
252-session robust normalization, split embargo, unique 21-session aggregation,
SPY TailLoss target, RV control, OLS/HAC(3), prospective gates and literal
GO/CONDITIONAL_GO/NO_GO rule.

The scientific-content commit H1-LAF is
`cfbdff048ae8b0f7d9b8a1a804558bf59b656c1b`. This exact hash is now registered
by the separate metadata/provenance commit authorized in the same human order.
The one frozen Research association execution is authorized. No result has
been observed at this point.

## A1d closure

H0-A1d remains
`74e53946e9e2fbd07dce15e77d527fd5cd0d1f38`. Two private transport-failure
receipts are preserved. No Tiingo payload or scientific gate was observed and
no retry remains authorized.

```text
A1D_STATUS = INCONCLUSIVE_TRANSPORT_NO_PAYLOAD
A1D_SCIENTIFIC_RESULT = NONE
A1D_RETRY_AUTHORIZED = NO
```

The independent audit is no longer required for Research because the approved
estimator is invariant to positive constant Close/Volume scales within each
split regime and excludes transition-crossing windows. The remaining proxy
limitation is recorded in [`construct_volume_erratum.md`](construct_volume_erratum.md).

## Pre-association disposition

All five Yahoo hashes remain unchanged; 3,525 XNYS rows per symbol end on
`2016-12-30`; no historical row from 2017 onward was loaded. Scale-invariance
and target-independence checks passed.

The literal missingness rule produces 8 primary complete Research months, zero
in 2004–2010 and 8 in 2011–2016. No complete row has the required prior-only
state classification. These mechanical facts were observed without fitting a
feature-target association and were not used to relax any rule. An
unestimable stability block and insufficient state counts cannot pass their
respective frozen gates.

## Frozen Research disposition

The authorization commit is
`842a87c2ca4ff7e65627f29d93726e9cae22c169`. The single Research association
was executed once and produced `CorePass=false`, `IncrementalPass=false`,
`StabilityPass=false` and `StatePass=false`; the literal verdict is `NO_GO`.
No variant or secondary diagnostic was used to rescue the result.

Validation, Final OOS, strategy, portfolio and backtest remain prohibited.

SAFE_TO_RUN_VALIDATION = NO
READY_FOR_HUMAN_VALIDATION_DECISION = NO
