# Cross-Market timing — CM_001 v1.0-frozen

## Quick Summary

- **Purpose:** frozen mapping and session-time contract.
- **Read when:** mapping US information to Taiwan target sessions.
- **Load next:** [`data_contract.md`](data_contract.md) and [`validation_plan.md`](validation_plan.md).
- **Authority:** scientific content frozen pending H1 provenance registration.

## Contents

- [Frozen calendars](#frozen-calendars)
- [Required invariants](#required-invariants)

For each official TWSE target session `j`, use the open interval:

```text
(previous_twse_close_j, current_twse_open_j)
```

A US session enters `S(j)` only when its actual regular open and close are both strictly inside that interval and raw Open/Close exist for `XSD`, `QQQ` and `SPY`. `SemiSpecific` and `BroadTech` use the identical `S(j)`. Multiple sessions are summed session by session; they are never normalized or converted to `Close_last/Open_first`.

Empty windows remain in the 2,223-session ledger with `n_us_sessions=0` but are absent from inferential samples. Missing data are never represented by a zero feature, forward-fill or backfill. The aggregated feature timestamp is the close of the last included US session and must precede Taiwan open.

## Frozen calendars

- US: `exchange-calendars==4.13.2`, calendar `XNYS`, timezone `America/New_York`, actual session opens/closes, DST-aware and actual early-close aware.
- Taiwan: official TWSE dates; regular session `09:00`–`13:30 Asia/Taipei`.
- Stage A found no Research-session difference among ARCX/XNAS/XNYS that changes mapping for `XSD/QQQ/SPY`.
- Retain 15 official TWSE sessions missing from `XTAI`; exclude `2018-02-20`, the single `XTAI` extra date not official in the TWSE ledger.
- Stage A found no relevant Taiwan early close or extraordinary Research session incompatible with `09:00`–`13:30`; no calendar-policy exception is required.

## Required invariants

- timezone-aware instants and strict `tw_close < us_open < us_close < tw_open`;
- unique, ordered official Taiwan sessions and no future US session mapping;
- actual US early closes and DST transitions;
- no extended-hours or incomplete US input;
- past-feature invariance when later dates are appended;
- Research target dates at most `2018-12-31`; Validation/OOS paths not loaded;
- pre-association primary counts H1 `1938`, H2 `2034`, H3 `1850`, otherwise stop.

The study is observational and defines no order, execution price, portfolio or strategy return.
