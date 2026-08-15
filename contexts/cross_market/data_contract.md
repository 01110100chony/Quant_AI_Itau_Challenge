# Cross-Market data contract — CM_001 v1.0-frozen

## Quick Summary

- **Purpose:** frozen provider, field, adjustment and provenance contract.
- **Read when:** acquiring, parsing or constructing CM_001 data.
- **Load next:** [`timing.md`](timing.md) and [`validation_plan.md`](validation_plan.md).
- **Authority:** scientific content frozen pending H1 provenance registration.

## Contents

- [Missing and corporate actions](#missing-and-corporate-actions)
- [Provenance and boundaries](#provenance-and-boundaries)

| Instrument | Role | Frozen provider | Primary fields |
|---|---|---|---|
| `XSD` | leader | Yahoo immutable Chart JSON | raw regular Open/Close |
| `QQQ` | US control | Yahoo immutable Chart JSON | raw regular Open/Close |
| `SPY` | US control | Yahoo immutable Chart JSON | raw regular Open/Close |
| `0052` | follower | TWSE official | raw Open/Close |
| `TAIEX` | primary Taiwan benchmark | TWSE official | raw Open/Close |
| `0050` | robustness benchmark | TWSE official | raw Open/Close |

`Adj Close` is retained only as audit/reference for the Yahoo instruments. Primary construction never mixes raw Open with adjusted Close. TWSE raw price fields are the primary Taiwan basis. Confirmed official corporate actions come from the TWSE ex-right/ex-dividend master cross-checked against a second TWSE endpoint.

## Missing and corporate actions

All 2,223 official Taiwan sessions are retained in the ledger. The 108 sessions with no regular `0052` OHLC are structural no-regular-trade cases (102 no trade, six odd-lot-only) and are excluded only when a required component is absent; never impute.

- H1/TAIEX: exclude the six confirmed `0052` action dates.
- H3/TAIEX: exclude the six following sessions whose `PrevTWRel` leg crosses those actions.
- H2/TAIEX: retain same-session Open–Close on those event dates; no documented intraday exception was found.
- `0050` robustness: apply the same leg-specific rule for confirmed actions in either `0052` or `0050`.

## Provenance and boundaries

Every input/output must record source or endpoint, retrieval date, instrument, period, raw artifact, parser/version and SHA-256 where applicable. Acquisition is separate from transformation and immutable raw responses are preserved. The Stage B loader may read only canonical Research artifacts with dates `2010-01-01`–`2018-12-31`; it asserts the upper bound and does not access Validation or Final OOS.

The exact formulas, inference, tests and gates are in [`specification.md`](specification.md). New providers, assets or inferred observations are prohibited without a new human decision and version.
