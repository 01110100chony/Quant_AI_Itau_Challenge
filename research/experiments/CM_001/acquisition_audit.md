# CM_001 — Acquisition audit

## Scope

Research boundary revised by human decision to `2010-01-01 <= Taiwan session <= 2018-12-31`. Validation and Final OOS were not requested, loaded, processed or displayed. No feature–target quantity was calculated.

## Root cause of the invalid first run

The Yahoo HTTP responses were structurally valid. The first acquisition converted JSON numbers to PowerShell objects and then used `Export-Csv` under a decimal-comma locale. Values such as decimal-point JSON numbers were persisted with commas. Python `to_numeric` expected decimal points and created thousands of `NaN`; those nulls did not come from the provider. The invalid snapshot is preserved with `snapshot_status = "INVALID"` and is excluded from all canonical paths.

| instrument | parser-created nulls | comma-decimal strings |
|---|---|---|
| 0050 | 11900 | 11900 |
| 0052 | 12750 | 12750 |
| QQQ | 14970 | 14970 |
| SPY | 14933 | 14933 |
| TAIEX | 14622 | 14622 |
| XSD | 14970 | 14970 |

## Corrected Yahoo raw-schema audit

The corrected flow persists immutable HTTP JSON first, validates schema/arrays, then parses. `chart.result` contains exactly one result; `quote` and `adjclose` are separate one-element lists; timestamps are Unix seconds; all quote/adjusted arrays have the same length as `timestamp`; JSON nulls are counted before DataFrame construction.

| Instrument | HTTP | Provider symbol | Interval | Timezone | Timestamps | All arrays aligned | Open nulls | Close nulls | Adj Close nulls | Raw schema gate |
|---|---|---|---|---|---|---|---|---|---|---|
| XSD | 200 | XSD | 1d | America/New_York | 3020 | True | 0 | 0 | 0 | VALID |
| QQQ | 200 | QQQ | 1d | America/New_York | 3020 | True | 0 | 0 | 0 | VALID |
| SPY | 200 | SPY | 1d | America/New_York | 3020 | True | 0 | 0 | 0 | VALID |
| 0052 | 200 | 0052.TW | 1d | Asia/Taipei | 2720 | True | 9 | 9 | 9 | VALID |
| TAIEX | 200 | ^TWII | 1d | Asia/Taipei | 2964 | True | 16 | 16 | 16 | VALID |
| 0050 | 200 | 0050.TW | 1d | Asia/Taipei | 2469 | True | 5 | 5 | 5 | VALID |

## Official TWSE schema audit

- `TAIEX/MI_5MINS_HIST`: monthly `Date, Opening Index, Highest Index, Lowest Index, Closing Index`; 2,970 complete sessions in the retained 2007–2018 acquisition audit and 2,223 sessions in revised Research.
- `afterTrading/STOCK_DAY`: available from `2010-01-04`; includes daily OHLC and a documented `"--"` sentinel. In revised Research, `0052` has 108 all-OHLC sentinel rows and `0050` has none.
- The official response has session dates but no timezone field. Timestamp construction therefore uses the separately documented TWSE regular hours and remains a calendar-policy item for human approval.

## Cross-provider QA

Large discrepancy means at least one comparable OHLC field differs by more than 0.5%; this is a data-integrity threshold, not an economic test.

| Instrument | matched_sessions | primary_only_sessions | reference_only_sessions | large_ohlc_discrepancy_sessions |
|---|---|---|---|---|
| 0052 | 2213 | 7 | 10 | 54 |
| TAIEX | 2213 | 7 | 10 | 2 |
| 0050 | 2213 | 7 | 10 | 1222 |

The Yahoo `0050` overlap contains a material scale discontinuity relative to TWSE official raw OHLC at `2014-01-02`. The official corporate-action audit found no Research-period split, so this is retained as a cross-provider scale defect rather than interpreted as a Research corporate action or silently corrected. No mixed raw Open/adjusted Close series was built.

## Stage A closure acquisition

On `2026-08-14`, a bounded closure acquisition added only Research-period official evidence: filtered TWSE `MI_INDEX` rows for a pre-specified 15-date `0052` sample, filtered `TWT49U` and `ETF/etfDiv` records for `0052`/`0050`, and filtered `TWTAWU` halt records for `0052`. Retrieval metadata records endpoint, date, instrument, period, raw path and parser. Any broader endpoint response was filtered in memory before persistence; current filing columns returned by `TWT49U` were discarded. No 2019+ market price was persisted, processed or visualized.

The closure evidence classifies the 108 official no-OHLC rows as 102 sessions with zero volume/value/transactions and 6 sessions with total activity below the 1,000-unit regular ETF trading unit. The 15-date second official cross-check agrees 15/15. Corporate actions are now cross-checked in two official endpoints: 6 `0052` and 11 `0050` cash distributions, with no Research split found. See the dedicated missing and corporate-action audits.
