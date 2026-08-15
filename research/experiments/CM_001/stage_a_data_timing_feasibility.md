# CM_001 — Stage A integrity report

## Hard stop

This report contains only acquisition, OHLC, calendar and timestamp diagnostics for revised Research `2010-01-01`–`2018-12-31`. It contains no H1/H2/H3, correlation, covariance, regression, beta, t-statistic, p-value, IC, conditional mean, hit rate, quintile, Sharpe, strategy return, backtest or feature–target visualization. Validation and Final OOS remain closed.

## Coverage and OHLC integrity

| Instrument | Provider | Requested start | First valid session | Last valid Research session | Raw rows | Valid Open rows | Valid Close rows | Missing Open | Missing Close | Duplicate sessions | Corporate-action coverage | Timezone status | Acquisition status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| XSD | Yahoo Chart API | 2010-01-01 | 2010-01-04 | 2018-12-31 | 2264 | 2264 | 2264 | 0 | 0 | 0 | adjusted-close semantics documented; not action master | provider metadata matched | VALID |
| QQQ | Yahoo Chart API | 2010-01-01 | 2010-01-04 | 2018-12-31 | 2264 | 2264 | 2264 | 0 | 0 | 0 | adjusted-close semantics documented; not action master | provider metadata matched | VALID |
| SPY | Yahoo Chart API | 2010-01-01 | 2010-01-04 | 2018-12-31 | 2264 | 2264 | 2264 | 0 | 0 | 0 | adjusted-close semantics documented; not action master | provider metadata matched | VALID |
| 0052 | TWSE STOCK_DAY | 2010-01-01 | 2010-01-04 | 2018-12-28 | 2223 | 2115 | 2115 | 108 | 108 | 0 | 6 official distributions; 2-endpoint cross-check | calendar-defined; provider date only | PARTIAL |
| TAIEX | TWSE MI_5MINS_HIST | 2010-01-01 | 2010-01-04 | 2018-12-28 | 2223 | 2223 | 2223 | 0 | 0 | 0 | N/A for index | calendar-defined; provider date only | VALID |
| 0050 | TWSE STOCK_DAY | 2010-01-01 | 2010-01-04 | 2018-12-28 | 2223 | 2223 | 2223 | 0 | 0 | 0 | 11 official distributions; 2-endpoint cross-check | calendar-defined; provider date only | VALID |

All retained positive OHLC rows satisfy `High >= max(Open, Close)`, `Low <= min(Open, Close)`, `High >= Low`; duplicate timestamp/session and non-monotonic timestamp counts are zero. `0052`'s 108 `"--"` rows are explicitly missing and never imputed.

## Corporate actions

The closure audit replaced the incomplete Yahoo diagnostic with the official TWSE `TWT49U` master and independently cross-checked every event against official `ETF/etfDiv` records. It identifies 6 `0052` and 11 `0050` cash distributions in Research; dates and amounts agree for 17/17 events. No Research split or `"**"` split/resumption mark was found. The canonical candidate, exact event list and affected-leg map are in [`stage_a_corporate_actions_audit.md`](stage_a_corporate_actions_audit.md). Raw OHLC, adjusted close and events remain separate; the proposed policy has not been approved or applied silently.

## Calendar status

| package | version | us_calendar | us_timezone | us_sessions | us_early_closes | taiwan_candidate | taiwan_sessions | xtai_missing_official_sessions | xtai_extra_sessions |
|---|---|---|---|---|---|---|---|---|---|
| exchange-calendars | 4.13.2 | XNYS (XNAS/ARCX aliases resolve to the same calendar) | America/New_York | 2264 | 19 | official TWSE TAIEX session dates + official 09:00-13:30 Asia/Taipei regular hours | 2223 | 15 | 1 |

The US calendar includes actual early closes and DST-aware UTC timestamps. Official TWSE Research session dates include 15 sessions missing from the `XTAI` library candidate (principally historical Saturday make-up sessions); `XTAI` includes 1 date absent from official TAIEX. The mapper therefore uses official TWSE dates/hours for this audit, while final calendar policy remains subject to human approval.

## Session mapping

Taiwan target sessions: **2223**.

| n_us_sessions | Taiwan windows |
|---|---|
| 0 | 86 |
| 1 | 2072 |
| 2 | 43 |
| 3+ | 22 |

| mapping_status | Taiwan windows |
|---|---|
| VALID | 2137 |
| EMPTY_US_WINDOW | 85 |
| NO_PREVIOUS_TW_SESSION | 1 |

| duplicated_taiwan_targets | timestamp_violations | ambiguous_mappings | future_data_violations | missing_feature_source_sessions | missing_target_component_sessions |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 209 |

`EMPTY_US_WINDOW` is assigned only when the calendar has no eligible US session. If an eligible US calendar session lacked validated `XSD/QQQ/SPY` OHLC, status would be `DATA_MISSING`; these states are never conflated.

## Manual calendar-selected cases

| category | target_session | previous_tw_close_utc | us_open_timestamps_utc | us_close_timestamps_utc | current_tw_open_utc | mapping_status | n_us_sessions |
|---|---|---|---|---|---|---|---|
| Normal session | 2010-01-05 | 2010-01-04 05:30:00+00:00 | 2010-01-04T14:30:00+00:00 | 2010-01-04T21:00:00+00:00 | 2010-01-05 01:00:00+00:00 | VALID | 1 |
| Additional normal session | 2010-01-06 | 2010-01-05 05:30:00+00:00 | 2010-01-05T14:30:00+00:00 | 2010-01-05T21:00:00+00:00 | 2010-01-06 01:00:00+00:00 | VALID | 1 |
| Weekend | 2010-01-11 | 2010-01-08 05:30:00+00:00 | 2010-01-08T14:30:00+00:00 | 2010-01-08T21:00:00+00:00 | 2010-01-11 01:00:00+00:00 | VALID | 1 |
| US holiday / zero-US window | 2010-01-19 | 2010-01-18 05:30:00+00:00 |  |  | 2010-01-19 01:00:00+00:00 | EMPTY_US_WINDOW | 0 |
| Taiwan Saturday session | 2010-02-06 | 2010-02-05 05:30:00+00:00 | 2010-02-05T14:30:00+00:00 | 2010-02-05T21:00:00+00:00 | 2010-02-06 01:00:00+00:00 | VALID | 1 |
| Taiwan Lunar New Year gap | 2010-02-22 | 2010-02-10 05:30:00+00:00 | 2010-02-10T14:30:00+00:00;2010-02-11T14:30:00+00:00;2010-02-12T14:30:00+00:00;2010-02-16T14:30:00+00:00;2010-02-17T14:30:00+00:00;2010-02-18T14:30:00+00:00;2010-02-19T14:30:00+00:00 | 2010-02-10T21:00:00+00:00;2010-02-11T21:00:00+00:00;2010-02-12T21:00:00+00:00;2010-02-16T21:00:00+00:00;2010-02-17T21:00:00+00:00;2010-02-18T21:00:00+00:00;2010-02-19T21:00:00+00:00 | 2010-02-22 01:00:00+00:00 | VALID | 7 |
| US DST start | 2010-03-16 | 2010-03-15 05:30:00+00:00 | 2010-03-15T13:30:00+00:00 | 2010-03-15T20:00:00+00:00 | 2010-03-16 01:00:00+00:00 | VALID | 1 |
| Multiple-US-session window | 2010-06-17 | 2010-06-15 05:30:00+00:00 | 2010-06-15T13:30:00+00:00;2010-06-16T13:30:00+00:00 | 2010-06-15T20:00:00+00:00;2010-06-16T20:00:00+00:00 | 2010-06-17 01:00:00+00:00 | VALID | 2 |
| US DST end | 2010-11-09 | 2010-11-08 05:30:00+00:00 | 2010-11-08T14:30:00+00:00 | 2010-11-08T21:00:00+00:00 | 2010-11-09 01:00:00+00:00 | VALID | 1 |
| US early close | 2010-11-29 | 2010-11-26 05:30:00+00:00 | 2010-11-26T14:30:00+00:00 | 2010-11-26T18:00:00+00:00 | 2010-11-29 01:00:00+00:00 | VALID | 1 |

## Stage A verdict

```text
PASS_READY_FOR_SPEC_FREEZE
```

The structural evidence is sufficient for a human data-policy decision and specification freeze. The verdict is not a freeze, does not approve the proposed policies, and does not authorize Stage B. See the missing audit, corporate-action audit, attrition report and final data-policy matrix.
