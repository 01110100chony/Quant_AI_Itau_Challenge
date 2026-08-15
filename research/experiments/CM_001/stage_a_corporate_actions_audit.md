# CM_001 — Stage A corporate actions audit

## Scope

Official-event audit for `0052` and secondary instrument `0050`, Research `2010-01-01`–`2018-12-31`. Events are identified from official records, never from price movements. No return or feature–target quantity was calculated.

## Canonical candidates and sources

Primary source: TWSE `TWT49U` ex-right/ex-dividend calculation results (available since 2003). Independent official cross-check: TWSE `ETF/etfDiv` distribution list. Both endpoints cover the whole Research interval. Broad upstream responses were filtered in acquisition memory to `0052`/`0050` and Research dates; current filing fields were discarded before persistence.

| instrument | event_date | event_type | source | source_authority | cash_distribution | split_ratio | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0050 | 2010-10-25 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 2.200000 |  | CROSS_CHECKED |
| 0050 | 2011-10-26 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.950000 |  | CROSS_CHECKED |
| 0050 | 2012-10-24 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.850000 |  | CROSS_CHECKED |
| 0050 | 2013-10-24 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.350000 |  | CROSS_CHECKED |
| 0050 | 2014-10-24 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.550000 |  | CROSS_CHECKED |
| 0050 | 2015-10-26 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 2.000000 |  | CROSS_CHECKED |
| 0050 | 2016-07-28 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 0.850000 |  | CROSS_CHECKED |
| 0050 | 2017-02-08 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.700000 |  | CROSS_CHECKED |
| 0050 | 2017-07-31 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 0.700000 |  | CROSS_CHECKED |
| 0050 | 2018-01-29 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 2.200000 |  | CROSS_CHECKED |
| 0050 | 2018-07-23 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 0.700000 |  | CROSS_CHECKED |
| 0052 | 2010-05-03 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.400000 |  | CROSS_CHECKED |
| 0052 | 2012-05-07 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 2.374000 |  | CROSS_CHECKED |
| 0052 | 2014-05-06 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 2.462000 |  | CROSS_CHECKED |
| 0052 | 2016-05-04 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 2.439000 |  | CROSS_CHECKED |
| 0052 | 2017-05-03 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.410000 |  | CROSS_CHECKED |
| 0052 | 2018-05-03 | CASH_DISTRIBUTION | TWSE TWT49U; TWSE ETF/etfDiv | TWSE_OFFICIAL_PRIMARY_AND_SECONDARY | 1.720000 |  | CROSS_CHECKED |

All 17 events (6 for `0052`, 11 for `0050`) agree between the two official endpoints on ex-date and cash amount. All are cash distributions. There are no `"**"` split/resumption marks in official `STOCK_DAY` for either instrument during Research, and the TWSE ETF split/reverse-split mechanism launched after this sample. Master status: `CROSS_CHECKED`; completeness is sufficiently defensible for the proposed Research policy.

Yahoo event history remains diagnostic only. It omitted the 2010 and 2012 `0052` distributions, placed the 2014 event on `2014-05-13` instead of the official `2014-05-06`, and reports some later cash amounts on a retrospectively changed scale. It is not the master.

## Affected H1 observations

| target_session | event_date | event_type | affected_leg |
| --- | --- | --- | --- |
| 2010-05-03 | 2010-05-03 | CASH_DISTRIBUTION | H1 |
| 2012-05-07 | 2012-05-07 | CASH_DISTRIBUTION | H1 |
| 2014-05-06 | 2014-05-06 | CASH_DISTRIBUTION | H1 |
| 2016-05-04 | 2016-05-04 | CASH_DISTRIBUTION | H1 |
| 2017-05-03 | 2017-05-03 | CASH_DISTRIBUTION | H1 |
| 2018-05-03 | 2018-05-03 | CASH_DISTRIBUTION | H1 |

These are the six `Close_{j-1} -> Open_j` crossings that the candidate policy would exclude. The policy remains unapproved.

## Affected PrevTWRel/H3 observations

| target_session | event_date | event_type | affected_leg |
| --- | --- | --- | --- |
| 2010-05-04 | 2010-05-03 | CASH_DISTRIBUTION | PrevTWRel/H3 |
| 2012-05-08 | 2012-05-07 | CASH_DISTRIBUTION | PrevTWRel/H3 |
| 2014-05-07 | 2014-05-06 | CASH_DISTRIBUTION | PrevTWRel/H3 |
| 2016-05-05 | 2016-05-04 | CASH_DISTRIBUTION | PrevTWRel/H3 |
| 2017-05-04 | 2017-05-03 | CASH_DISTRIBUTION | PrevTWRel/H3 |
| 2018-05-04 | 2018-05-03 | CASH_DISTRIBUTION | PrevTWRel/H3 |

These are the next official Taiwan sessions, whose `j-2 -> j-1` close-to-close control leg crosses the event.

## H2 interpretation cases

| target_session | event_date | event_type | affected_leg | automatic_exclusion |
| --- | --- | --- | --- | --- |
| 2010-05-03 | 2010-05-03 | CASH_DISTRIBUTION | H2 interpretation only | False |
| 2012-05-07 | 2012-05-07 | CASH_DISTRIBUTION | H2 interpretation only | False |
| 2014-05-06 | 2014-05-06 | CASH_DISTRIBUTION | H2 interpretation only | False |
| 2016-05-04 | 2016-05-04 | CASH_DISTRIBUTION | H2 interpretation only | False |
| 2017-05-03 | 2017-05-03 | CASH_DISTRIBUTION | H2 interpretation only | False |
| 2018-05-03 | 2018-05-03 | CASH_DISTRIBUTION | H2 interpretation only | False |

The event reset precedes the same-session regular Open, so raw `Open_j -> Close_j` does not cross the action. No automatic H2 exclusion was applied; the candidate policy would retain these six cases unless a specific documented issue appears.

## Unresolved items

No unresolved Research-period distribution or split candidate remains in the official master. Corporate-action treatment is still a human policy decision; this audit supplies the event list and mechanical impact only.

## Provenance

| source | url_or_endpoint | retrieval_date | raw_artifact_path | parser_version |
| --- | --- | --- | --- | --- |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/STOCK_DAY | 2026-08-14 | data/raw/cm_001/twse_official_audit_2007_2018/{instrument}_YYYYMM01.json | cross_market_stage_a_closure.load_twse_stock_day v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/zh/exRight/TWT49U | 2026-08-14 | data/raw/cm_001/stage_a_closure_2010_2018/twse_ex_right_2010_2018.json | cross_market_stage_a_closure.load_corporate_action_master v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/zh/ETF/etfDiv | 2026-08-14 | data/raw/cm_001/stage_a_closure_2010_2018/twse_etf_div_{instrument}_2010_2018.json | cross_market_stage_a_closure.load_corporate_action_master v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/TWTAWU | 2026-08-14 | data/raw/cm_001/stage_a_closure_2010_2018/twse_halts_0052_20111003_20181231.json | JSON field audit v1 |
