# CM_001 — Stage A 0052 missing audit

## Scope and hard boundary

Structural availability audit only, limited to official Taiwan sessions in Research `2010-01-01`–`2018-12-31`. No feature, target, return, association, Validation or Final OOS quantity was calculated or loaded.

## Problem definition and root classification

Official `STOCK_DAY` contains 108 `0052` rows with sentinel `"--"` in all four OHLC fields. The same official rows also contain trade volume, trade value and transaction count, allowing an evidence-based distinction:

| classification | sessions |
| --- | --- |
| NO_0052_TRADE | 102 |
| NO_REGULAR_0052_TRADE_ODD_LOT_ONLY | 6 |

- `NO_0052_TRADE`: 102 rows have official volume, value and transaction count all equal to zero.
- `NO_REGULAR_0052_TRADE_ODD_LOT_ONLY`: 6 rows have positive activity of only 1–105 units. TWSE defines one regular unit for a domestic ETF as 1,000 units and anything below one regular unit as odd-lot activity. Because total daily volume itself is below 1,000, no regular-lot execution can be present; official OHLC remains absent.
- `OFFICIAL_MISSING_OHLC`, `SUSPENDED_OR_NO_QUOTE`, and `UNRESOLVED`: zero classified rows. The official halt database has no `0052` record in its available period `2011-10-03`–`2018-12-31`; the database does not cover earlier dates.

## 108-session classification

| session_date | Trade Volume | Trade Value | Transaction | classification |
| --- | --- | --- | --- | --- |
| 2010-02-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2010-03-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2010-06-10 | 0 | 0 | 0 | NO_0052_TRADE |
| 2010-06-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2010-07-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2010-08-30 | 0 | 0 | 0 | NO_0052_TRADE |
| 2011-03-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2011-12-30 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-01-04 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-05-14 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-05-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-06-14 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-06-20 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-07-31 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-08-01 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-09-03 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-09-28 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-10-30 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-11-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-12-06 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-12-10 | 0 | 0 | 0 | NO_0052_TRADE |
| 2012-12-20 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-03-20 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-03-21 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-03-28 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-05-31 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-06-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-06-28 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-07-02 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-08-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-08-15 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-09-06 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-09-14 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-10-01 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-10-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-10-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-11-06 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-11-11 | 0 | 0 | 0 | NO_0052_TRADE |
| 2013-11-18 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-01-06 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-01-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-06-03 | 50 | 1,794 | 1 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY |
| 2014-06-20 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-08-14 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-08-20 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-08-21 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-08-28 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-09-12 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-09-18 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-09-19 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-09-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-10-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-10-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-10-29 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-10-30 | 0 | 0 | 0 | NO_0052_TRADE |
| 2014-11-21 | 0 | 0 | 0 | NO_0052_TRADE |
| 2015-05-04 | 0 | 0 | 0 | NO_0052_TRADE |
| 2015-06-18 | 0 | 0 | 0 | NO_0052_TRADE |
| 2015-09-18 | 0 | 0 | 0 | NO_0052_TRADE |
| 2015-10-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2015-10-29 | 0 | 0 | 0 | NO_0052_TRADE |
| 2015-12-31 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-01-14 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-01-21 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-02-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-03-04 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-03-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-05-12 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-05-16 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-05-31 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-06-03 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-06-04 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-06-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-07-20 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-07-22 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-08-19 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-08-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-09-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-09-26 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-09-30 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-10-06 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-10-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-11-01 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-11-21 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-11-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-11-30 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-12-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-12-26 | 0 | 0 | 0 | NO_0052_TRADE |
| 2016-12-29 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-01-03 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-01-16 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-02-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-02-20 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-04-05 | 105 | 4,830 | 2 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY |
| 2017-06-01 | 75 | 3,472 | 1 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY |
| 2017-06-03 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-07-20 | 1 | 49 | 1 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY |
| 2017-08-04 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-08-14 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-08-24 | 1 | 44 | 1 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY |
| 2017-09-28 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-09-29 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-10-02 | 98 | 4,953 | 1 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY |
| 2017-10-05 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-11-01 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-11-09 | 0 | 0 | 0 | NO_0052_TRADE |
| 2017-11-24 | 0 | 0 | 0 | NO_0052_TRADE |
| 2018-01-12 | 0 | 0 | 0 | NO_0052_TRADE |

## Annual distribution

| year | official_TW_sessions | 0052_no_OHLC_sessions | fraction_no_OHLC |
| --- | --- | --- | --- |
| 2010 | 251 | 6 | 0.023904 |
| 2011 | 247 | 2 | 0.008097 |
| 2012 | 250 | 14 | 0.056000 |
| 2013 | 246 | 17 | 0.069106 |
| 2014 | 248 | 17 | 0.068548 |
| 2015 | 244 | 6 | 0.024590 |
| 2016 | 244 | 27 | 0.110656 |
| 2017 | 246 | 18 | 0.073171 |
| 2018 | 247 | 1 | 0.004049 |

The cases are not confined to the start of Research: 99/108 occur in 2012–2017. The maximum annual share is 2016 (`27/244 = 0.110656`); 2018 has one case. There are 7 multi-session runs and the longest contains 3 consecutive official sessions. Missing Saturdays are `2013-09-14, 2016-06-04, 2017-06-03`: 3/108 cases and all are official pre-2019 make-up sessions. The remaining cases are ordinary official session dates rather than a single calendar episode.

## Second official-source cross-check

The pre-specified sample contains all six positive-volume cases plus one zero-volume case from every Research year. `MI_INDEX Daily Quotes (ALL)` agrees with `STOCK_DAY` on volume, value, transactions and absent OHLC for all 15/15 dates. Bid/ask fields exist in the second endpoint on sampled zero-trade dates, showing that absent execution must not be relabeled as missing market data or automatically as suspension.

| session_date | primary_classification | crosscheck_status | trade_volume | transactions | last_best_bid | last_best_ask |
| --- | --- | --- | --- | --- | --- | --- |
| 2010-02-24 | NO_0052_TRADE | official source agrees | 0 | 0 | 33.50 | 33.98 |
| 2011-03-09 | NO_0052_TRADE | official source agrees | 0 | 0 | 36.00 | 36.90 |
| 2012-01-04 | NO_0052_TRADE | official source agrees | 0 | 0 | 29.55 | 30.00 |
| 2013-03-20 | NO_0052_TRADE | official source agrees | 0 | 0 | 32.50 | 32.95 |
| 2014-01-06 | NO_0052_TRADE | official source agrees | 0 | 0 | 34.25 | 34.41 |
| 2014-06-03 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY | official source agrees | 50 | 1 | 39.15 | 39.30 |
| 2015-05-04 | NO_0052_TRADE | official source agrees | 0 | 0 | 42.12 | 42.41 |
| 2016-01-14 | NO_0052_TRADE | official source agrees | 0 | 0 | 34.83 | 35.14 |
| 2017-01-03 | NO_0052_TRADE | official source agrees | 0 | 0 | 42.84 | 43.00 |
| 2017-04-05 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY | official source agrees | 105 | 2 | 45.38 | 45.76 |
| 2017-06-01 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY | official source agrees | 75 | 1 | 46.41 | 46.50 |
| 2017-07-20 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY | official source agrees | 1 | 1 | 49.74 | 49.78 |
| 2017-08-24 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY | official source agrees | 1 | 1 | 49.75 | 50.15 |
| 2017-10-02 | NO_REGULAR_0052_TRADE_ODD_LOT_ONLY | official source agrees | 98 | 1 | 51.25 | 51.60 |
| 2018-01-12 | NO_0052_TRADE | official source agrees | 0 | 0 | 54.20 | 54.70 |

## Unresolved cases

None among the 108 rows under the structural classification above. The label is about regular-price availability, not an assertion that no order was ever entered. No imputation or future information was used.

## Non-binding technical recommendation

Retain all 2,223 official Taiwan sessions in the ledger; exclude a hypothesis observation whenever its required `0052` Open/Close input is absent; never impute a price or zero return. Recommendation: `APPROVE`, subject to human specification freeze.

## Provenance

| source | url_or_endpoint | retrieval_date | raw_artifact_path | parser_version |
| --- | --- | --- | --- | --- |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/STOCK_DAY | 2026-08-14 | data/raw/cm_001/twse_official_audit_2007_2018/{instrument}_YYYYMM01.json | cross_market_stage_a_closure.load_twse_stock_day v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/MI_INDEX | 2026-08-14 | data/raw/cm_001/stage_a_closure_2010_2018/twse_mi_index_0052_YYYYMMDD.json | cross_market_stage_a_closure.load_missing_crosscheck v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/TWTAWU | 2026-08-14 | data/raw/cm_001/stage_a_closure_2010_2018/twse_halts_0052_20111003_20181231.json | JSON field audit v1 |
| TWSE official documentation | https://www.twse.com.tw/en/products/system/trading.html; https://www.twse.com.tw/en/about/company/history.html; https://www.twse.com.tw/en/clearing/suspended.html | 2026-08-14 | N/A — official documentation pages, no price payload | manual structural documentation audit |
