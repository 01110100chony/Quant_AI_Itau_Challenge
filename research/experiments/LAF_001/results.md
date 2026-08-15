# LAF_001 — Results

## Stage A1 structural data feasibility

Stage A1 was executed under the explicit human authorization dated
`2026-08-15`. The immutable retrieval is `20260815T055848814Z`, and its
pre-data implementation commit is H0-A1
`01cc8408a83024663cc7cb7d434f82292072a945`.

Literal structural verdict:

`PASS_READY_FOR_STAGE_A2_DECISIONS`

All five authorized symbols (`SPY`, `QQQ`, `IWM`, `DIA`, `MDY`) contained
3,525 daily observations from the first XNYS session on `2003-01-02` through
the last XNYS session on `2016-12-30`. Required OHLCV and Adj Close arrays
were present and separately preserved in the raw JSON. The audit found no
missing or extra XNYS sessions, duplicate timestamps, non-monotonic timestamps,
null/zero/negative OHLCV values or OHLC invariant violations.

The provider returned 390 corporate actions: 389 dividends and one IWM stock
split dated `2005-06-09`. The event-only mechanical neighborhood classified
the IWM raw price series as already scale-continuous around that split. No
provider value was repaired, adjusted, filled or imputed.

The first derived calendar audit was discarded as invalid because
`exchange-calendars` had been instantiated with its moving default window,
which began only on `2006-08-15`. The implementation was corrected to request
the already-authorized fixed XNYS interval explicitly, a regression test was
added, and the derived audit was regenerated from the same immutable raw
payloads. No request was repeated and no raw byte or hash changed.

This is a data/timing feasibility result only. No general return series,
`PI`, `log(PI)`, `LAF`, `RV`, Corwin-Schultz, `TailLoss`, feature, target,
association, prediction, strategy or backtest was calculated.

`LAF_001` remains `v0.1-draft`: not frozen, not promoted and not validated.
