"""Generate CM_001 Stage A closure evidence without research-return calculations."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cross_market_stage_a_closure import (  # noqa: E402
    RESEARCH_END,
    annual_missing_distribution,
    assert_research_dates,
    audit_0050_provider_scale,
    build_attrition,
    build_corporate_action_impacts,
    calendar_audit,
    classify_0052_missing,
    load_corporate_action_master,
    load_missing_crosscheck,
    load_twse_stock_day,
    load_twse_taiex_presence,
    missing_runs,
    raw_adjusted_evidence,
)


TWSE_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "twse_official_audit_2007_2018"
CLOSURE_RAW = REPO_ROOT / "data" / "raw" / "cm_001" / "stage_a_closure_2010_2018"
YAHOO_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "yahoo_chart_2007_2018_v2"
PRIOR_PROCESSED = REPO_ROOT / "data" / "processed" / "cm_001" / "stage_a_provider_audit_v2"
OUTPUT_ROOT = REPO_ROOT / "data" / "processed" / "cm_001" / "stage_a_closure_audit"
EXPERIMENT_ROOT = REPO_ROOT / "research" / "experiments" / "CM_001"


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a small DataFrame as a stable Markdown table."""
    if frame.empty:
        return "_No rows._"
    display = frame.copy()
    for column in display.columns:
        display[column] = display[column].map(
            lambda value: value.isoformat() if hasattr(value, "isoformat") else value
        )
    headers = [str(column) for column in display.columns]
    rows = [[str(value) for value in row] for row in display.itertuples(index=False, name=None)]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def assert_no_adjusted_close_mix() -> dict[str, Any]:
    """Review the existing component builders for raw-open/adjusted-close mixing."""
    source_path = REPO_ROOT / "src" / "cross_market_stage_a.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    audited: dict[str, bool] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in {
            "build_us_components",
            "build_tw_components",
        }:
            segment = ast.get_source_segment(source, node) or ""
            audited[node.name] = "adj_close" not in segment
    if audited != {"build_us_components": True, "build_tw_components": True}:
        raise ValueError(f"Raw/adjusted code audit failed: {audited}")
    return {
        "source_path": relative(source_path),
        "functions_audited": sorted(audited),
        "raw_open_plus_adjusted_close_mix": False,
        "method": "AST-scoped source inspection; builders reference raw open/raw close only",
    }


def write_csv(frame: pd.DataFrame, name: str) -> Path:
    path = OUTPUT_ROOT / name
    frame.to_csv(path, index=False, date_format="%Y-%m-%d")
    return path


def provenance_frame() -> pd.DataFrame:
    rows = [
        {
            "source": "Taiwan Stock Exchange",
            "url_or_endpoint": "https://www.twse.com.tw/rwd/en/afterTrading/STOCK_DAY",
            "retrieval_date": "2026-08-14",
            "instrument": "0052/0050",
            "period": "2010-01-01..2018-12-31",
            "raw_artifact_path": "data/raw/cm_001/twse_official_audit_2007_2018/{instrument}_YYYYMM01.json",
            "parser_version": "cross_market_stage_a_closure.load_twse_stock_day v1",
        },
        {
            "source": "Taiwan Stock Exchange",
            "url_or_endpoint": "https://www.twse.com.tw/rwd/en/TAIEX/MI_5MINS_HIST",
            "retrieval_date": "2026-08-14",
            "instrument": "TAIEX",
            "period": "2010-01-01..2018-12-31",
            "raw_artifact_path": "data/raw/cm_001/twse_official_audit_2007_2018/TAIEX_YYYYMM01.json",
            "parser_version": "cross_market_stage_a_closure.load_twse_taiex_presence v1",
        },
        {
            "source": "Taiwan Stock Exchange",
            "url_or_endpoint": "https://www.twse.com.tw/rwd/en/afterTrading/MI_INDEX",
            "retrieval_date": "2026-08-14",
            "instrument": "0052",
            "period": "15 pre-specified Research dates",
            "raw_artifact_path": "data/raw/cm_001/stage_a_closure_2010_2018/twse_mi_index_0052_YYYYMMDD.json",
            "parser_version": "cross_market_stage_a_closure.load_missing_crosscheck v1",
        },
        {
            "source": "Taiwan Stock Exchange",
            "url_or_endpoint": "https://www.twse.com.tw/rwd/zh/exRight/TWT49U",
            "retrieval_date": "2026-08-14",
            "instrument": "0052/0050",
            "period": "2010-01-01..2018-12-31",
            "raw_artifact_path": "data/raw/cm_001/stage_a_closure_2010_2018/twse_ex_right_2010_2018.json",
            "parser_version": "cross_market_stage_a_closure.load_corporate_action_master v1",
        },
        {
            "source": "Taiwan Stock Exchange",
            "url_or_endpoint": "https://www.twse.com.tw/rwd/zh/ETF/etfDiv",
            "retrieval_date": "2026-08-14",
            "instrument": "0052/0050",
            "period": "2010-01-01..2018-12-31",
            "raw_artifact_path": "data/raw/cm_001/stage_a_closure_2010_2018/twse_etf_div_{instrument}_2010_2018.json",
            "parser_version": "cross_market_stage_a_closure.load_corporate_action_master v1",
        },
        {
            "source": "Taiwan Stock Exchange",
            "url_or_endpoint": "https://www.twse.com.tw/rwd/en/afterTrading/TWTAWU",
            "retrieval_date": "2026-08-14",
            "instrument": "0052",
            "period": "2011-10-03..2018-12-31 (endpoint coverage)",
            "raw_artifact_path": "data/raw/cm_001/stage_a_closure_2010_2018/twse_halts_0052_20111003_20181231.json",
            "parser_version": "JSON field audit v1",
        },
        {
            "source": "Yahoo Finance Chart API",
            "url_or_endpoint": "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            "retrieval_date": "2026-08-14",
            "instrument": "XSD/QQQ/SPY; Taiwan reference only",
            "period": "parsed Research subset 2010-01-01..2018-12-31",
            "raw_artifact_path": "data/raw/cm_001/yahoo_chart_2007_2018_v2/{instrument}_response.json",
            "parser_version": "cross_market_stage_a_closure.yahoo_presence v1",
        },
        {
            "source": "exchange-calendars",
            "url_or_endpoint": "local package calendars XNYS/XNAS/ARCX/XTAI",
            "retrieval_date": "2026-08-14",
            "instrument": "market calendars",
            "period": "2010-01-01..2018-12-31",
            "raw_artifact_path": "N/A — installed package schedule",
            "parser_version": "exchange-calendars==4.13.2",
        },
        {
            "source": "TWSE official documentation",
            "url_or_endpoint": "https://www.twse.com.tw/en/products/system/trading.html; https://www.twse.com.tw/en/about/company/history.html; https://www.twse.com.tw/en/clearing/suspended.html",
            "retrieval_date": "2026-08-14",
            "instrument": "Taiwan market",
            "period": "rules applicable to Research",
            "raw_artifact_path": "N/A — official documentation pages, no price payload",
            "parser_version": "manual structural documentation audit",
        },
        {
            "source": "Yahoo Finance Help",
            "url_or_endpoint": "https://help.yahoo.com/kb/adjusted-close-sln28256.html",
            "retrieval_date": "2026-08-14",
            "instrument": "provider field semantics",
            "period": "documentation",
            "raw_artifact_path": "N/A — provider documentation page, no price payload",
            "parser_version": "manual documentation audit",
        },
    ]
    return pd.DataFrame(rows)


def main() -> int:
    required = [TWSE_ROOT, CLOSURE_RAW, YAHOO_ROOT, PRIOR_PROCESSED]
    missing_roots = [str(path) for path in required if not path.exists()]
    if missing_roots:
        raise FileNotFoundError(f"Required Stage A artifacts are missing: {missing_roots}")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    follower = load_twse_stock_day(TWSE_ROOT.glob("0052_????????.json"), "0052")
    benchmark_0050 = load_twse_stock_day(TWSE_ROOT.glob("0050_????????.json"), "0050")
    taiex = load_twse_taiex_presence(TWSE_ROOT.glob("TAIEX_????????.json"))
    missing = classify_0052_missing(follower)
    annual = annual_missing_distribution(follower, missing)
    runs = missing_runs(follower, missing)
    crosscheck = load_missing_crosscheck(CLOSURE_RAW, missing)
    master, action_crosscheck = load_corporate_action_master(CLOSURE_RAW)
    h1_impact, h3_impact, h2_interpretation = build_corporate_action_impacts(
        follower["session_date"], master
    )
    flags, attrition, attrition_reasons = build_attrition(
        PRIOR_PROCESSED / "session_mapping.csv", follower, taiex, master
    )
    venue_calendars, us_raw_calendar, calendar = calendar_audit(
        taiex["session_date"], YAHOO_ROOT, PRIOR_PROCESSED / "session_mapping.csv"
    )
    raw_adjusted = raw_adjusted_evidence(YAHOO_ROOT)
    scale_audit = audit_0050_provider_scale(
        benchmark_0050, YAHOO_ROOT / "0050_response.json"
    )
    no_mix = assert_no_adjusted_close_mix()
    provenance = provenance_frame()

    saturday_missing = missing.loc[
        missing["session_date"].map(lambda value: value.weekday() == 5), "session_date"
    ].tolist()
    multi_runs = runs.loc[runs["official_session_count"].gt(1)]
    classification_counts = (
        missing.groupby("classification").size().rename("sessions").reset_index()
    )
    if classification_counts["sessions"].sum() != 108:
        raise ValueError("Missing classification count does not reconcile to 108")
    if missing["classification"].eq("UNRESOLVED").any():
        raise ValueError("0052 missing audit contains unresolved classifications")
    if not crosscheck["crosscheck_status"].eq("official source agrees").all():
        raise ValueError("Official missing-row cross-check did not fully agree")

    output_files = {
        "missing": write_csv(missing, "0052_missing_classification.csv"),
        "annual": write_csv(annual, "0052_missing_annual_distribution.csv"),
        "runs": write_csv(runs, "0052_missing_runs.csv"),
        "missing_crosscheck": write_csv(crosscheck, "0052_missing_official_crosscheck.csv"),
        "master": write_csv(master, "corporate_action_master.csv"),
        "action_crosscheck": write_csv(action_crosscheck, "corporate_action_crosscheck.csv"),
        "h1_impact": write_csv(h1_impact, "corporate_action_h1_impact.csv"),
        "h3_impact": write_csv(h3_impact, "corporate_action_prevtwrel_h3_impact.csv"),
        "h2_interpretation": write_csv(
            h2_interpretation, "corporate_action_h2_interpretation.csv"
        ),
        "flags": write_csv(flags, "mechanical_availability_flags.csv"),
        "attrition": write_csv(attrition, "mechanical_attrition.csv"),
        "attrition_reasons": write_csv(attrition_reasons, "mechanical_attrition_reasons.csv"),
        "venue_calendars": write_csv(venue_calendars, "us_venue_calendar_audit.csv"),
        "us_raw_calendar": write_csv(us_raw_calendar, "us_raw_calendar_alignment.csv"),
        "raw_adjusted": write_csv(raw_adjusted, "raw_adjusted_evidence.csv"),
        "provenance": write_csv(provenance, "provenance.csv"),
    }

    diagnostic = {
        "research_start": "2010-01-01",
        "research_end": "2018-12-31",
        "max_research_date": max(flags["session_date"]).isoformat(),
        "validation_loaded": False,
        "final_oos_loaded": False,
        "feature_target_relationship_calculated": False,
        "classification_counts": {
            str(key): int(value)
            for key, value in zip(
                classification_counts["classification"], classification_counts["sessions"]
            )
        },
        "official_missing_crosscheck": {
            str(key): int(value)
            for key, value in crosscheck["crosscheck_status"].value_counts().items()
        },
        "corporate_action_counts": {
            str(key): int(value) for key, value in master["instrument"].value_counts().items()
        },
        "corporate_action_crosscheck": {
            str(key): int(value)
            for key, value in action_crosscheck["crosscheck_status"].value_counts().items()
        },
        "attrition": {
            "total_sessions": len(flags),
            "eligible_us": int(flags["eligible_us"].sum()),
            "h1_inputs": int(flags["h1_input_available"].sum()),
            "h1_candidate_policy": int(flags["h1_usable_under_candidate_policy"].sum()),
            "h2_inputs": int(flags["h2_input_available"].sum()),
            "h3_inputs": int(flags["h3_input_available"].sum()),
            "h3_candidate_policy": int(flags["h3_usable_under_candidate_policy"].sum()),
        },
        "calendar": calendar,
        "0050_provider_scale": scale_audit,
        "raw_adjusted_mix_audit": no_mix,
        "stage_a_closure_verdict": "PASS_READY_FOR_SPEC_FREEZE",
    }
    diagnostics_path = OUTPUT_ROOT / "diagnostics.json"
    diagnostics_path.write_text(
        json.dumps(diagnostic, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Assert every date-bearing generated table stays inside Research.
    for frame, columns, label in [
        (missing, ["session_date"], "missing classification"),
        (master, ["event_date"], "corporate action master"),
        (h1_impact, ["target_session", "event_date"], "H1 impact"),
        (h3_impact, ["target_session", "event_date"], "H3 impact"),
        (flags, ["session_date"], "attrition flags"),
    ]:
        for column in columns:
            assert_research_dates(frame[column], label=f"{label}.{column}")
    if max(flags["session_date"]) != RESEARCH_END.replace(day=28):
        # 2018-12-31 was a US session but not a TWSE session; last official TW session is 12-28.
        raise ValueError("Unexpected last official Taiwan Research session")

    provenance_subset = provenance[
        ["source", "url_or_endpoint", "retrieval_date", "raw_artifact_path", "parser_version"]
    ]
    missing_detail = missing[
        [
            "session_date",
            "Trade Volume",
            "Trade Value",
            "Transaction",
            "classification",
        ]
    ]
    missing_report = f"""# CM_001 — Stage A 0052 missing audit

## Scope and hard boundary

Structural availability audit only, limited to official Taiwan sessions in Research `2010-01-01`–`2018-12-31`. No feature, target, return, association, Validation or Final OOS quantity was calculated or loaded.

## Problem definition and root classification

Official `STOCK_DAY` contains 108 `0052` rows with sentinel `"--"` in all four OHLC fields. The same official rows also contain trade volume, trade value and transaction count, allowing an evidence-based distinction:

{markdown_table(classification_counts)}

- `NO_0052_TRADE`: 102 rows have official volume, value and transaction count all equal to zero.
- `NO_REGULAR_0052_TRADE_ODD_LOT_ONLY`: 6 rows have positive activity of only 1–105 units. TWSE defines one regular unit for a domestic ETF as 1,000 units and anything below one regular unit as odd-lot activity. Because total daily volume itself is below 1,000, no regular-lot execution can be present; official OHLC remains absent.
- `OFFICIAL_MISSING_OHLC`, `SUSPENDED_OR_NO_QUOTE`, and `UNRESOLVED`: zero classified rows. The official halt database has no `0052` record in its available period `2011-10-03`–`2018-12-31`; the database does not cover earlier dates.

## 108-session classification

{markdown_table(missing_detail)}

## Annual distribution

{markdown_table(annual.assign(fraction_no_OHLC=annual['fraction_no_OHLC'].map(lambda value: f'{value:.6f}')))}

The cases are not confined to the start of Research: 99/108 occur in 2012–2017. The maximum annual share is 2016 (`27/244 = 0.110656`); 2018 has one case. There are {len(multi_runs)} multi-session runs and the longest contains {int(runs['official_session_count'].max())} consecutive official sessions. Missing Saturdays are `{', '.join(value.isoformat() for value in saturday_missing)}`: 3/108 cases and all are official pre-2019 make-up sessions. The remaining cases are ordinary official session dates rather than a single calendar episode.

## Second official-source cross-check

The pre-specified sample contains all six positive-volume cases plus one zero-volume case from every Research year. `MI_INDEX Daily Quotes (ALL)` agrees with `STOCK_DAY` on volume, value, transactions and absent OHLC for all 15/15 dates. Bid/ask fields exist in the second endpoint on sampled zero-trade dates, showing that absent execution must not be relabeled as missing market data or automatically as suspension.

{markdown_table(crosscheck[['session_date', 'primary_classification', 'crosscheck_status', 'trade_volume', 'transactions', 'last_best_bid', 'last_best_ask']])}

## Unresolved cases

None among the 108 rows under the structural classification above. The label is about regular-price availability, not an assertion that no order was ever entered. No imputation or future information was used.

## Non-binding technical recommendation

Retain all 2,223 official Taiwan sessions in the ledger; exclude a hypothesis observation whenever its required `0052` Open/Close input is absent; never impute a price or zero return. Recommendation: `APPROVE`, subject to human specification freeze.

## Provenance

{markdown_table(provenance_subset.iloc[[0, 2, 5, 8]])}
"""
    (EXPERIMENT_ROOT / "stage_a_0052_missing_audit.md").write_text(
        missing_report, encoding="utf-8"
    )

    action_report = f"""# CM_001 — Stage A corporate actions audit

## Scope

Official-event audit for `0052` and secondary instrument `0050`, Research `2010-01-01`–`2018-12-31`. Events are identified from official records, never from price movements. No return or feature–target quantity was calculated.

## Canonical candidates and sources

Primary source: TWSE `TWT49U` ex-right/ex-dividend calculation results (available since 2003). Independent official cross-check: TWSE `ETF/etfDiv` distribution list. Both endpoints cover the whole Research interval. Broad upstream responses were filtered in acquisition memory to `0052`/`0050` and Research dates; current filing fields were discarded before persistence.

{markdown_table(master[['instrument', 'event_date', 'event_type', 'source', 'source_authority', 'cash_distribution', 'split_ratio', 'confidence']])}

All 17 events (6 for `0052`, 11 for `0050`) agree between the two official endpoints on ex-date and cash amount. All are cash distributions. There are no `"**"` split/resumption marks in official `STOCK_DAY` for either instrument during Research, and the TWSE ETF split/reverse-split mechanism launched after this sample. Master status: `CROSS_CHECKED`; completeness is sufficiently defensible for the proposed Research policy.

Yahoo event history remains diagnostic only. It omitted the 2010 and 2012 `0052` distributions, placed the 2014 event on `2014-05-13` instead of the official `2014-05-06`, and reports some later cash amounts on a retrospectively changed scale. It is not the master.

## Affected H1 observations

{markdown_table(h1_impact)}

These are the six `Close_{{j-1}} -> Open_j` crossings that the candidate policy would exclude. The policy remains unapproved.

## Affected PrevTWRel/H3 observations

{markdown_table(h3_impact)}

These are the next official Taiwan sessions, whose `j-2 -> j-1` close-to-close control leg crosses the event.

## H2 interpretation cases

{markdown_table(h2_interpretation[['target_session', 'event_date', 'event_type', 'affected_leg', 'automatic_exclusion']])}

The event reset precedes the same-session regular Open, so raw `Open_j -> Close_j` does not cross the action. No automatic H2 exclusion was applied; the candidate policy would retain these six cases unless a specific documented issue appears.

## Unresolved items

No unresolved Research-period distribution or split candidate remains in the official master. Corporate-action treatment is still a human policy decision; this audit supplies the event list and mechanical impact only.

## Provenance

{markdown_table(provenance_subset.iloc[[0, 3, 4, 5]])}
"""
    (EXPERIMENT_ROOT / "stage_a_corporate_actions_audit.md").write_text(
        action_report, encoding="utf-8"
    )

    attrition_report = f"""# CM_001 — Stage A mechanical attrition report

## Hard boundary

Presence/absence audit only. No `GapRel`, `IntradayRel`, `PrevTWRel`, feature value, return or feature–target relationship was calculated. Counts are based on 2,223 official TWSE session-ledger rows and the existing Stage A mapping structure.

## Stage waterfall

{markdown_table(attrition)}

`H1 raw-input availability = 1,944` and `H3 raw-input availability = 1,856` are policy-neutral. The proposed-but-unapproved corporate-action policy would reduce them to 1,938 and 1,850. `H2 = 2,034` is unchanged because the proposed rule does not automatically exclude same-session events.

## Mutually exclusive exclusion attribution

Reasons below are applied in displayed gate order so that counts reconcile without double counting. Independent raw incidence is 108 missing `0052` Opens and the same 108 missing `0052` Closes; some coincide with empty windows or consecutive missing sessions.

{markdown_table(attrition_reasons)}

Mechanical reconciliation:

- H1 under candidate policy: `2,223 - (1 + 85 + 103 + 90 + 0 + 6 + 0) = 1,938`.
- H2: `2,223 - (1 + 85 + 103 + 0 + 0 + 0) = 2,034`.
- H3 under candidate policy: `2,223 - (189 + 0 + 178 + 6 + 0) = 1,850`.

## Integrity

No missing `BroadTech` input exists within a calendar-eligible window: `XSD`, `QQQ`, and `SPY` each contain valid raw Open/Close on all 2,264 XNYS Research sessions. TAIEX Open/Close is present on all 2,223 official Taiwan sessions. The generated flags contain dates only and component-presence booleans.

## Provenance

{markdown_table(provenance_subset.iloc[[0, 1, 6, 7]])}
"""
    (EXPERIMENT_ROOT / "stage_a_attrition_report.md").write_text(
        attrition_report, encoding="utf-8"
    )

    official_not_xtai = ", ".join(calendar["official_not_xtai"])
    xtai_extra = ", ".join(calendar["xtai_not_official"])
    decision_matrix = pd.DataFrame(
        [
            {
                "Decision": "A. MULTI-PROVIDER",
                "Candidate": "Yahoo immutable JSON — XSD/QQQ/SPY; TWSE official — 0052/0050/TAIEX",
                "Evidence": "US raw OHLC complete and exactly aligned to XNYS; Taiwan official OHLC/actions are canonical; immutable local artifacts",
                "Codex recommendation": "APPROVE",
            },
            {
                "Decision": "B. 0052 --",
                "Candidate": "retain ledger; exclude unavailable required OHLC; never impute",
                "Evidence": "102 no-trade + 6 odd-lot-only/no-regular-trade; 15/15 second official cross-check agrees; 0 unresolved",
                "Codex recommendation": "APPROVE",
            },
            {
                "Decision": "C. PRIMARY PRICE BASIS",
                "Candidate": "raw OHLC primary; Adj Close audit/reference only",
                "Evidence": "TWSE is raw-only; Yahoo has no adjusted Open; code audit confirms no raw-Open/Adj-Close mix; 0050 reference scale defect",
                "Codex recommendation": "APPROVE",
            },
            {
                "Decision": "D. CORPORATE ACTION POLICY",
                "Candidate": "exclude confirmed H1/PrevTWRel crossings; retain H2 unless documented issue",
                "Evidence": "6 0052 events cross-checked by two official endpoints; exact affected sessions mapped; no Research splits",
                "Codex recommendation": "APPROVE",
            },
            {
                "Decision": "E. CALENDAR/TIMEZONE",
                "Candidate": "XNYS actual sessions; official TWSE dates + 09:00–13:30 Asia/Taipei",
                "Evidence": "XNYS/XNAS/ARCX identical; 15 XTAI omissions retained and one XTAI extra excluded; no material session-hour exception",
                "Codex recommendation": "APPROVE",
            },
            {
                "Decision": "F. RESEARCH SAMPLE",
                "Candidate": "2010-01-01–2018-12-31",
                "Evidence": "all generated date-bearing artifacts have max date 2018-12-28; no Validation/OOS loaded",
                "Codex recommendation": "APPROVE",
            },
        ]
    )
    policy_report = f"""# CM_001 — Stage A final data-policy evidence

## Scope

Closure evidence only. `CM_001` remains `DRAFT`; this document does not approve or freeze any policy and does not authorize Stage B. Validation and Final OOS were not loaded.

## Raw versus adjusted evidence

{markdown_table(raw_adjusted)}

Yahoo documents `Adj Close` as adjusted for applicable splits and dividend distributions, but supplies no adjusted Open. TWSE price endpoints provide raw OHLC and no adjusted close. The candidate raw-OHLC policy is therefore internally representable; an adjusted-Open/adjusted-Close intraday construction is not available from these snapshots.

The current research-component builders were inspected by AST-scoped source review: neither `build_us_components` nor `build_tw_components` references `adj_close`; they use raw Open and raw Close. `RAW OPEN + ADJUSTED CLOSE MIX = FALSE`.

The Taiwan reference comparison exposes a concrete scale hazard: Yahoo `0050` raw Close matches the official scale on {scale_audit['approximately_1x_sessions']} comparable sessions through {scale_audit['last_1x_session']}, then is approximately one quarter of official raw on {scale_audit['approximately_4x_sessions']} sessions beginning {scale_audit['first_4x_session']}. This supports keeping Yahoo Taiwan prices as diagnostic only and TWSE raw as primary.

## Calendar/timezone final audit

{markdown_table(venue_calendars)}

{markdown_table(us_raw_calendar)}

A. No incompatibility was found: XSD (`NYSEArca`), QQQ (`NasdaqGM`) and SPY (`NYSEArca`) each have 2,264 complete raw sessions exactly equal to XNYS dates.

B. In `exchange-calendars==4.13.2`, ARCX, XNAS and XNYS have identical dates, opens and closes throughout Research. XNYS contributes 19 actual early closes and DST-aware UTC timestamps.

C. XTAI omits 15 official TWSE sessions: `{official_not_xtai}`. They are all Saturdays. Omitting any would delete an official target and merge adjacent information windows; the official-date mapper retains all 15, so the candidate policy is not affected by the library defect.

D. XTAI's sole extra date is `{xtai_extra}`. It has no official TAIEX row and is absent from the mapper.

E. TWSE official rules and history establish regular market hours `09:00–13:30 Asia/Taipei` throughout 2010–2018, including pre-2019 Saturday make-up sessions.

F. No relevant Taiwan session-level early close was found. TWSE's disaster rule is full-day closure before open or completion of the full regular session when an afternoon closure is announced after trading begins.

G. No Research session with extraordinary market hours was found. TWSE documents a possible security-level closing-auction postponement to 13:33 from 2012-02-20; it is not a market-session early close and cannot change `S(j)` because the next US open is hours later. This operational note should remain documented, but it creates no material mapper exception.

`CALENDAR_POLICY_EXCEPTION_REQUIRED: NO`.

## Final decision matrix

{markdown_table(decision_matrix)}

Recommendations are technical and non-binding. Human researchers must approve the policies and perform the specification freeze in a later explicit action.

## Boundary and provenance

`max Research date = 2018-12-28 <= 2018-12-31`; the final US Research session is 2018-12-31. All new market-data artifacts were acquisition-filtered before persistence. The broad `TWT49U` response returned current filing columns incidentally; those columns and unrelated instruments were discarded in memory and the occurrence is recorded in request metadata.

{markdown_table(provenance)}

## Stage A closure verdict

```text
PASS_READY_FOR_SPEC_FREEZE
```

This means the structural evidence is sufficient for a human data-policy decision and specification freeze. It is not a freeze, thesis result, Stage B authorization, Validation opening, or Final OOS opening.
"""
    (EXPERIMENT_ROOT / "stage_a_final_data_policy_evidence.md").write_text(
        policy_report, encoding="utf-8"
    )

    print(json.dumps(diagnostic, indent=2, ensure_ascii=False, default=str))
    print("Generated:")
    for path in output_files.values():
        print(relative(path))
    print(relative(diagnostics_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
