# LAF_001 — Future Stage A1 data/timing feasibility plan

> **Historical plan:** Stage A1 was later executed, and its original result was
> subsequently superseded for review by the independent Stage A1c corrective
> audit. This file is retained as the pre-execution plan; current state is in
> [`results.md`](results.md).

## Purpose

Define the outputs that a later, separately authorized empirical Stage A1 must
produce. This plan does not execute acquisition, parsing, calculation or
inspection.

## Authorized candidate boundary for a future order

- Instruments: `SPY`, `QQQ`, `IWM`, `DIA`, `MDY`.
- Warm-up: `2003-01-01`–`2003-12-31`.
- Research: `2004-01-01`–`2016-12-31`.
- Every date from `2017-01-01` onward: CLOSED; do not acquire, load, process or
  display.
- 2026: excluded in full.
- Candidate source: Yahoo Finance Chart API.
- Candidate calendar: XNYS via `exchange-calendars`.

## Required future outputs — not executed

1. Request metadata recording endpoint, symbol, requested bounds, collection
   timestamp, timezone and response status.
2. Immutable raw JSON response per request, kept separate from all processed
   artifacts.
3. SHA-256 for every request and raw-response artifact.
4. Coverage reconciliation against expected XNYS sessions, separated between
   warm-up and Research.
5. OHLC invariants, including finite/positive fields and mechanically valid
   high/low relationships.
6. Explicit counts of zero and missing volume without selecting a treatment
   policy.
7. Duplicate timestamp/session checks.
8. Source timezone and XNYS session-date audit, including month-end mapping.
9. Corporate-action inventory with raw OHLCV, Adj Close and actions preserved
   as separate fields/artifacts.
10. Complete-month audit without inventing a partial-month policy.
11. Mechanical row/session counts strictly inside warm-up and Research, with
    no rows from `2017-01-01` onward materialized.
12. At least one manual structural example and synthetic tests for the approved
    field, calendar and boundary invariants.

## Hard stop

Future Stage A1 must stop after data/timing feasibility outputs and before any
return, `PI`, `LAF`, `RV`, Corwin-Schultz, `TailLoss`, feature or target is
calculated. Any empirical execution requires a new explicit human order and all
still-pending policies must remain unresolved until separately approved.
