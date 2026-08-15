# CM_001 — Stage A final data-policy evidence

## Scope

Closure evidence only. `CM_001` remains `DRAFT`; this document does not approve or freeze any policy and does not authorize Stage B. Validation and Final OOS were not loaded.

## Raw versus adjusted evidence

| source | instrument | raw_Open_available | raw_Close_available | Adj_Close_available | historical_adjustment_mechanism_known | dividends_included_in_Adj_Close | splits_included | Open_adjusted_consistently | provider_documentation_found | scale_discontinuities | policy_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Yahoo Chart API | XSD | True | True | True | True | True | True | False | True | none identified in structural session audit | Adj Close is separate; never pair it with raw Open |
| Yahoo Chart API | QQQ | True | True | True | True | True | True | False | True | none identified in structural session audit | Adj Close is separate; never pair it with raw Open |
| Yahoo Chart API | SPY | True | True | True | True | True | True | False | True | none identified in structural session audit | Adj Close is separate; never pair it with raw Open |
| Yahoo Chart API | 0052 | True | True | True | True | True | True | False | True | 0052 raw Open has nonpositive/missing records | Adj Close is separate; never pair it with raw Open |
| Yahoo Chart API | TAIEX | True | True | True | True | True | True | False | True | none identified in structural session audit | Adj Close is separate; never pair it with raw Open |
| Yahoo Chart API | 0050 | True | True | True | True | True | True | False | True | 2014-01-02 boundary in Yahoo 0050 raw history vs official TWSE (4x scale) | Adj Close is separate; never pair it with raw Open |
| TWSE official | 0052 | PARTIAL (2115/2223; 108 official no-regular-OHLC rows) | PARTIAL (2115/2223; 108 official no-regular-OHLC rows) | False | False | False | False | True | True | 108 official no-regular-OHLC rows, explicitly classified | official raw OHLC; actions maintained separately |
| TWSE official | 0050 | YES (2223/2223) | YES (2223/2223) | False | False | False | False | True | True | none in official Research raw scale | official raw OHLC; actions maintained separately |
| TWSE official | TAIEX | YES (2223/2223) | YES (2223/2223) | False | False | False | False | True | True | none in official Research raw scale | official raw OHLC; actions maintained separately |

Yahoo documents `Adj Close` as adjusted for applicable splits and dividend distributions, but supplies no adjusted Open. TWSE price endpoints provide raw OHLC and no adjusted close. The candidate raw-OHLC policy is therefore internally representable; an adjusted-Open/adjusted-Close intraday construction is not available from these snapshots.

The current research-component builders were inspected by AST-scoped source review: neither `build_us_components` nor `build_tw_components` references `adj_close`; they use raw Open and raw Close. `RAW OPEN + ADJUSTED CLOSE MIX = FALSE`.

The Taiwan reference comparison exposes a concrete scale hazard: Yahoo `0050` raw Close matches the official scale on 988 comparable sessions through 2013-12-31, then is approximately one quarter of official raw on 1220 sessions beginning 2014-01-02. This supports keeping Yahoo Taiwan prices as diagnostic only and TWSE raw as primary.

## Calendar/timezone final audit

| calendar | sessions | same_dates_as_XNYS | different_opens_vs_XNYS | different_closes_vs_XNYS |
| --- | --- | --- | --- | --- |
| XNYS | 2264 | True | 0 | 0 |
| XNAS | 2264 | True | 0 | 0 |
| ARCX | 2264 | True | 0 | 0 |

| instrument | provider_exchange | provider_timezone | valid_raw_sessions | raw_not_in_XNYS | XNYS_not_in_raw |
| --- | --- | --- | --- | --- | --- |
| XSD | NYSEArca | America/New_York | 2264 | 0 | 0 |
| QQQ | NasdaqGM | America/New_York | 2264 | 0 | 0 |
| SPY | NYSEArca | America/New_York | 2264 | 0 | 0 |

A. No incompatibility was found: XSD (`NYSEArca`), QQQ (`NasdaqGM`) and SPY (`NYSEArca`) each have 2,264 complete raw sessions exactly equal to XNYS dates.

B. In `exchange-calendars==4.13.2`, ARCX, XNAS and XNYS have identical dates, opens and closes throughout Research. XNYS contributes 19 actual early closes and DST-aware UTC timestamps.

C. XTAI omits 15 official TWSE sessions: `2010-02-06, 2012-02-04, 2012-03-03, 2012-12-22, 2013-02-23, 2013-09-14, 2014-12-27, 2016-01-30, 2016-06-04, 2016-09-10, 2017-02-18, 2017-06-03, 2017-09-30, 2018-03-31, 2018-12-22`. They are all Saturdays. Omitting any would delete an official target and merge adjacent information windows; the official-date mapper retains all 15, so the candidate policy is not affected by the library defect.

D. XTAI's sole extra date is `2011-05-02`. It has no official TAIEX row and is absent from the mapper.

E. TWSE official rules and history establish regular market hours `09:00–13:30 Asia/Taipei` throughout 2010–2018, including pre-2019 Saturday make-up sessions.

F. No relevant Taiwan session-level early close was found. TWSE's disaster rule is full-day closure before open or completion of the full regular session when an afternoon closure is announced after trading begins.

G. No Research session with extraordinary market hours was found. TWSE documents a possible security-level closing-auction postponement to 13:33 from 2012-02-20; it is not a market-session early close and cannot change `S(j)` because the next US open is hours later. This operational note should remain documented, but it creates no material mapper exception.

`CALENDAR_POLICY_EXCEPTION_REQUIRED: NO`.

## Final decision matrix

| Decision | Candidate | Evidence | Codex recommendation |
| --- | --- | --- | --- |
| A. MULTI-PROVIDER | Yahoo immutable JSON — XSD/QQQ/SPY; TWSE official — 0052/0050/TAIEX | US raw OHLC complete and exactly aligned to XNYS; Taiwan official OHLC/actions are canonical; immutable local artifacts | APPROVE |
| B. 0052 -- | retain ledger; exclude unavailable required OHLC; never impute | 102 no-trade + 6 odd-lot-only/no-regular-trade; 15/15 second official cross-check agrees; 0 unresolved | APPROVE |
| C. PRIMARY PRICE BASIS | raw OHLC primary; Adj Close audit/reference only | TWSE is raw-only; Yahoo has no adjusted Open; code audit confirms no raw-Open/Adj-Close mix; 0050 reference scale defect | APPROVE |
| D. CORPORATE ACTION POLICY | exclude confirmed H1/PrevTWRel crossings; retain H2 unless documented issue | 6 0052 events cross-checked by two official endpoints; exact affected sessions mapped; no Research splits | APPROVE |
| E. CALENDAR/TIMEZONE | XNYS actual sessions; official TWSE dates + 09:00–13:30 Asia/Taipei | XNYS/XNAS/ARCX identical; 15 XTAI omissions retained and one XTAI extra excluded; no material session-hour exception | APPROVE |
| F. RESEARCH SAMPLE | 2010-01-01–2018-12-31 | all generated date-bearing artifacts have max date 2018-12-28; no Validation/OOS loaded | APPROVE |

Recommendations are technical and non-binding. Human researchers must approve the policies and perform the specification freeze in a later explicit action.

## Boundary and provenance

`max Research date = 2018-12-28 <= 2018-12-31`; the final US Research session is 2018-12-31. All new market-data artifacts were acquisition-filtered before persistence. The broad `TWT49U` response returned current filing columns incidentally; those columns and unrelated instruments were discarded in memory and the occurrence is recorded in request metadata.

| source | url_or_endpoint | retrieval_date | instrument | period | raw_artifact_path | parser_version |
| --- | --- | --- | --- | --- | --- | --- |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/STOCK_DAY | 2026-08-14 | 0052/0050 | 2010-01-01..2018-12-31 | data/raw/cm_001/twse_official_audit_2007_2018/{instrument}_YYYYMM01.json | cross_market_stage_a_closure.load_twse_stock_day v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/TAIEX/MI_5MINS_HIST | 2026-08-14 | TAIEX | 2010-01-01..2018-12-31 | data/raw/cm_001/twse_official_audit_2007_2018/TAIEX_YYYYMM01.json | cross_market_stage_a_closure.load_twse_taiex_presence v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/MI_INDEX | 2026-08-14 | 0052 | 15 pre-specified Research dates | data/raw/cm_001/stage_a_closure_2010_2018/twse_mi_index_0052_YYYYMMDD.json | cross_market_stage_a_closure.load_missing_crosscheck v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/zh/exRight/TWT49U | 2026-08-14 | 0052/0050 | 2010-01-01..2018-12-31 | data/raw/cm_001/stage_a_closure_2010_2018/twse_ex_right_2010_2018.json | cross_market_stage_a_closure.load_corporate_action_master v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/zh/ETF/etfDiv | 2026-08-14 | 0052/0050 | 2010-01-01..2018-12-31 | data/raw/cm_001/stage_a_closure_2010_2018/twse_etf_div_{instrument}_2010_2018.json | cross_market_stage_a_closure.load_corporate_action_master v1 |
| Taiwan Stock Exchange | https://www.twse.com.tw/rwd/en/afterTrading/TWTAWU | 2026-08-14 | 0052 | 2011-10-03..2018-12-31 (endpoint coverage) | data/raw/cm_001/stage_a_closure_2010_2018/twse_halts_0052_20111003_20181231.json | JSON field audit v1 |
| Yahoo Finance Chart API | https://query1.finance.yahoo.com/v8/finance/chart/{symbol} | 2026-08-14 | XSD/QQQ/SPY; Taiwan reference only | parsed Research subset 2010-01-01..2018-12-31 | data/raw/cm_001/yahoo_chart_2007_2018_v2/{instrument}_response.json | cross_market_stage_a_closure.yahoo_presence v1 |
| exchange-calendars | local package calendars XNYS/XNAS/ARCX/XTAI | 2026-08-14 | market calendars | 2010-01-01..2018-12-31 | N/A — installed package schedule | exchange-calendars==4.13.2 |
| TWSE official documentation | https://www.twse.com.tw/en/products/system/trading.html; https://www.twse.com.tw/en/about/company/history.html; https://www.twse.com.tw/en/clearing/suspended.html | 2026-08-14 | Taiwan market | rules applicable to Research | N/A — official documentation pages, no price payload | manual structural documentation audit |
| Yahoo Finance Help | https://help.yahoo.com/kb/adjusted-close-sln28256.html | 2026-08-14 | provider field semantics | documentation | N/A — provider documentation page, no price payload | manual documentation audit |

## Stage A closure verdict

```text
PASS_READY_FOR_SPEC_FREEZE
```

This means the structural evidence is sufficient for a human data-policy decision and specification freeze. It is not a freeze, thesis result, Stage B authorization, Validation opening, or Final OOS opening.
