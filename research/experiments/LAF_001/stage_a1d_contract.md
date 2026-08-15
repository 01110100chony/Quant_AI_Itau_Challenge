# LAF_001 — Stage A1d independent source-unit audit contract

## Authority and scope

This contract records the explicit human authorization of 2026-08-15 for the
limited `LAF_001 Stage A1d` audit. It is not Stage A2. It does not calculate a
return, PI, log(PI), LAF, RV, Corwin-Schultz, TailLoss, feature, target or
association, and it does not open Validation or Final OOS.

Stage A1c was human-accepted at code commit
`176bb12b2413edb866cdcc38e86a497021cebd6c` and results commit
`d8b7efa803bf2d042b20d3624da7cac65014086a`. Stage A1d uses only the existing
41-line Yahoo split audit at
`data/processed/laf_001/stage_a1c/20260815T055848814Z/split_unit_audit.csv`.
No new Yahoo request is allowed.

## Frozen secondary-provider request

- Provider: `Tiingo EOD`.
- Role: sample audit; not the primary source.
- Symbol: `IWM` only.
- `startDate=2005-05-11`.
- `endDate=2005-07-08`.
- Frequency: daily.
- Endpoint without token:
  `https://api.tiingo.com/tiingo/daily/IWM/prices`.
- Authentication exclusively through header
  `Authorization: Token ${TIINGO_API_TOKEN}`.
- Utilized fields: `date`, `close`, `volume`, `splitFactor`.
- Every other response field: `PRIVATE_NOT_USED_NOT_EMITTED`.
- Private raw destination:
  `data/private/laf_001/stage_a1d/<retrieval_id>/`.

The acquisition is one logical request. A second and final attempt is allowed
only after transport error, timeout, HTTP 429 or HTTP 5xx. Schema/content
failure and every other HTTP status stop without retry. Every attempt receipt
is private. The credential is never placed in a URL, file, receipt, log or
versioned artifact.

## Date and coverage contract

The response must contain exactly the 41 existing Stage A1c XNYS session
dates, with no missing, extra or duplicate date. The provider `date` is
normalized to a `session_date` label and is not interpreted as an availability
timestamp. Historical timezone semantics use the IANA zone
`America/New_York`; fixed `EDT` or `gmtoffset` conversion is prohibited.

## Frozen split and unit mapping

For dates before `2005-06-09`, `F_d=2`; for the event and later dates,
`F_d=1`:

- `tiingo_split_close = tiingo_close / F_d`;
- `tiingo_split_volume = tiingo_volume * F_d`;
- `tiingo_raw_dollar_volume = tiingo_close * tiingo_volume`;
- `yahoo_dollar_volume = yahoo_provider_close * yahoo_reported_volume`.

Exactly one non-unit `splitFactor` must occur on `2005-06-09`. The convention
is pre-registered before data: a reported factor of `2` maps directly to the
economic factor `2`; a reported factor of `0.5` is reciprocated mechanically
to economic factor `2`; any other non-unit factor fails. The observed
convention is recorded categorically and is not selected after inspecting
comparisons.

MAPE is frozen as
`mean(abs(Yahoo - TiingoComparable) / abs(TiingoComparable))`. Every unit and
dollar-volume ratio is frozen as `Yahoo / TiingoComparable`. Price and volume
`event+post` MAPEs use the event plus 20 following sessions. Dollar-volume
post MAPE and the session-count conditions use the 20 sessions strictly after
the event.

## Pre-registered gates

### CoveragePass

- 41/41 dates;
- zero missing, extra or duplicate dates.

### SplitEventPass

- exactly one non-unit event on `2005-06-09`;
- normalized economic factor equals 2.

### PriceUnitPass

- pre-event MAPE against `tiingo_split_close` at most 2%;
- event+post MAPE against `tiingo_close` at most 2%.

### VolumeUnitPass

- pre-event MAPE against `tiingo_split_volume` at most 5%;
- event+post MAPE against `tiingo_volume` at most 5%;
- median Yahoo/Tiingo raw Volume pre-event in `[1.80, 2.20]`;
- median Yahoo/Tiingo split-Volume pre-event in `[0.95, 1.05]`;
- median Yahoo/Tiingo raw Volume post-event in `[0.95, 1.05]`;
- at least 18/20 pre-event and 18/20 post-event sessions within 10% relative
  error.

### DollarVolumePass

- pre-event and post-event MAPE at most 5%;
- at least 18/20 pre-event and 18/20 post-event sessions with Yahoo/Tiingo
  dollar-volume ratio in `[0.90, 1.10]`.

No threshold, window, source or convention may change after acquisition.

## Literal interpretation and stop

If all five gates pass:

- `YAHOO_PRICE_UNIT = SPLIT_ADJUSTED_BASIS_CONFIRMED_FOR_IWM_2005_SAMPLE`;
- `YAHOO_VOLUME_UNIT = RECIPROCALLY_SPLIT_ADJUSTED_BASIS_CONFIRMED_FOR_IWM_2005_SAMPLE`;
- `YAHOO_CLOSE_X_VOLUME = CONSISTENT_WITH_AS_TRADED_DOLLAR_VOLUME_FOR_OBSERVED_SPLIT_SAMPLE`;
- `VOLUME_UNIT_SEMANTICS = RESOLVED_FOR_ALL_OBSERVED_SPLITS_IN_RESEARCH_DATA`;
- `SAFE_TO_RUN_LAF_STAGE_A2 = NO`;
- `READY_FOR_HUMAN_STAGE_A2_FREEZE_DECISION = YES`.

If any gate fails, `VOLUME_UNIT_SEMANTICS = UNRESOLVED` and
`SAFE_TO_RUN_LAF_STAGE_A2 = NO`. No alternative source, window or tolerance
may be sought to rescue failure. Stage A2 always requires a later human order.
