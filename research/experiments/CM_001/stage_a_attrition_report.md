# CM_001 — Stage A mechanical attrition report

## Hard boundary

Presence/absence audit only. No `GapRel`, `IntradayRel`, `PrevTWRel`, feature value, return or feature–target relationship was calculated. Counts are based on 2,223 official TWSE session-ledger rows and the existing Stage A mapping structure.

## Stage waterfall

| Stage | count | excluded | reason |
| --- | --- | --- | --- |
| session ledger | 2223 | 0 | none |
| after empty-US-window rule | 2138 | 85 | no eligible US session |
| eligible US window | 2137 | 1 | first-session boundary has no previous Taiwan close |
| H1 raw-input availability | 1944 | 193 | required Open/previous Close presence only |
| H1 under candidate action policy | 1938 | 6 | confirmed corporate-action crossing; policy not approved |
| H2 raw-input availability | 2034 | 103 | required same-session Open/Close presence only |
| H3 raw-input availability | 1856 | 178 | BroadTech and PrevTWRel input presence only |
| H3 under candidate action policy | 1850 | 6 | confirmed corporate-action crossing; policy not approved |

`H1 raw-input availability = 1,944` and `H3 raw-input availability = 1,856` are policy-neutral. The proposed-but-unapproved corporate-action policy would reduce them to 1,938 and 1,850. `H2 = 2,034` is unchanged because the proposed rule does not automatically exclude same-session events.

## Mutually exclusive exclusion attribution

Reasons below are applied in displayed gate order so that counts reconcile without double counting. Independent raw incidence is 108 missing `0052` Opens and the same 108 missing `0052` Closes; some coincide with empty windows or consecutive missing sessions.

| hypothesis | reason | excluded |
| --- | --- | --- |
| H1 | first-session boundary | 1 |
| H1 | no eligible US session | 85 |
| H1 | missing 0052 Open after prior gates | 103 |
| H1 | missing 0052 previous Close after prior gates | 90 |
| H1 | missing TAIEX leg | 0 |
| H1 | corporate-action exclusion candidate | 6 |
| H1 | other mechanical reason | 0 |
| H2 | other: first-session boundary | 1 |
| H2 | no eligible US session | 85 |
| H2 | missing 0052 Open (and Close) after prior gates | 103 |
| H2 | missing 0052 Close only after prior gates | 0 |
| H2 | missing TAIEX Open/Close | 0 |
| H2 | other mechanical reason | 0 |
| H3 | all H2 requirements | 189 |
| H3 | missing BroadTech | 0 |
| H3 | missing PrevTWRel leg after H2 gates | 178 |
| H3 | corporate-action exclusion candidate | 6 |
| H3 | other mechanical reason | 0 |

Mechanical reconciliation:

- H1 under candidate policy: `2,223 - (1 + 85 + 103 + 90 + 0 + 6 + 0) = 1,938`.
- H2: `2,223 - (1 + 85 + 103 + 0 + 0 + 0) = 2,034`.
- H3 under candidate policy: `2,223 - (189 + 0 + 178 + 6 + 0) = 1,850`.

## Integrity

No missing `BroadTech` input exists within a calendar-eligible window: `XSD`, `QQQ`, and `SPY` each contain valid raw Open/Close on all 2,264 XNYS Research sessions. TAIEX Open/Close is present on all 2,223 official Taiwan sessions. The generated flags contain dates only and component-presence booleans.

## Provenance

| source | url_or_endpoint | retrieval_date | raw_artifact_path | parser_version |
| --- | --- | --- | --- | --- |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/STOCK_DAY | 2026-08-14 | data/raw/cm_001/twse_official_audit_2007_2018/{instrument}_YYYYMM01.json | cross_market_stage_a_closure.load_twse_stock_day v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/TAIEX/MI_5MINS_HIST | 2026-08-14 | data/raw/cm_001/twse_official_audit_2007_2018/TAIEX_YYYYMM01.json | cross_market_stage_a_closure.load_twse_taiex_presence v1 |
| Yahoo Finance Chart API | https://query1.finance.yahoo.com/v8/finance/chart/{symbol} | 2026-08-14 | data/raw/cm_001/yahoo_chart_2007_2018_v2/{instrument}_response.json | cross_market_stage_a_closure.yahoo_presence v1 |
| exchange-calendars | local package calendars XNYS/XNAS/ARCX/XTAI | 2026-08-14 | N/A — installed package schedule | exchange-calendars==4.13.2 |
