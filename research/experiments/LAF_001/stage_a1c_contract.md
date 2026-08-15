# LAF_001 — Stage A1c corrective audit contract

## Authority and scope

This contract records the explicit human authorization of 2026-08-15 for the
limited `LAF_001 Stage A1c` correction. It is not Stage A2 and does not change
the thesis, universe, periods, candidate provider, calendar or closed-sample
policy.

The correction may reuse only the five immutable raw payloads from retrieval
`20260815T055848814Z`. It may remediate the metadata-boundary incident, make
code provenance exact and perform the pre-specified event-only IWM split-unit
audit. No network request is permitted.

## Fixed provenance

- Raw acquisition H0: `01cc8408a83024663cc7cb7d434f82292072a945`.
- Original results: `f549a1a8d8e4b06028100b22a450fa0e5c46473b`.
- Corrective code H0-A1c: the commit containing this contract, implementation
  and synthetic tests. The runner must record its real `HEAD` after that commit
  exists.
- Parser: `laf-stage-a1-v1.0.1`.
- Corrective destination:
  `data/processed/laf_001/stage_a1c/20260815T055848814Z/`.
- The original processed snapshot remains immutable.

## Registered raw-response hashes

| Symbol | SHA-256 |
|---|---|
| SPY | `306c43087e3a33048d29b47746250cfeaca6a0ec69532084d3e12e7cb2393153` |
| QQQ | `1d747eb4f1fc4b7f22e1cfdae40ad4932a9301324c666e101e3bebcd41a9e479` |
| IWM | `ee972d8c9d5ad737370df7f30d4954e8065316218ae08d64430f28b9f3feb0b3` |
| DIA | `30f7b0370a61be244cd0425602c7c4821dbc4ddef9d3598e267f6aaf8e6fbe53` |
| MDY | `5dba651a9fa9100ef740eaa27f4a8221b63371a8a44b22b1bf29113a46a41fc5` |

## Canonical metadata policy

`provider_metadata.csv` may contain exactly these columns:

`symbol`, `currency`, `exchangeName`, `fullExchangeName`, `instrumentType`,
`exchangeTimezoneName`, `timezone`, `gmtoffset`, `dataGranularity`,
`firstTradeDate`, `priceHint`, `hasPrePostMarketData`, `validRanges`.

Every other raw metadata field is excluded from canonical artifacts and
recorded by name only in `metadata_boundary_audit.csv` as
`OUT_OF_SCOPE_DYNAMIC`, with `emitted=false`. No value from those fields may be
copied to that audit or to aggregate JSON.

## Fixed split-unit audit

The only newly authorized price-volume calculation is for IWM on exactly the
20 XNYS sessions immediately before `2005-06-09`, the event session and the 20
immediately following XNYS sessions. The price field is named only `provider
Close`; no claim that it is an unadjusted-price semantic is permitted.

For `reported_volume`, `provider_close_x_reported_volume` and
`adj_close_div_provider_close`, the audit records pre/post medians, the
post/pre ratio and the following inclusive classification:

- `0.75`–`1.33`: `CONSISTENT_WITH_LOCAL_CONTINUITY_NOT_PROOF`;
- `1.60`–`2.40`: `CONSISTENT_WITH_FACTOR_TWO_DISCONTINUITY_NOT_PROOF`;
- otherwise: `INCONCLUSIVE`.

Without provider documentation or an independent source, the semantic status
must remain
`VOLUME_UNIT_SEMANTICS = UNRESOLVED_REQUIRES_HUMAN_SOURCE_DECISION`.

## Hard stops

No general return, PI, log(PI), LAF, RV, Corwin-Schultz, TailLoss, feature,
target, association, strategy or backtest may be calculated. No row or
corporate action from 2017 onward may be loaded. Validation and Final OOS stay
closed. Stage A2 remains unauthorized and no corrective result may authorize
it automatically.
