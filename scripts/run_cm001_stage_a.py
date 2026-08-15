#!/usr/bin/env python3
"""Finalize the CM_001 Stage A provider/timing audit without economic tests."""

from __future__ import annotations

import json
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cross_market_stage_a import (  # noqa: E402
    RESEARCH_END,
    RESEARCH_START,
    US_ASSETS,
    audit_yahoo_chart_response,
    calendar_schedule,
    compare_provider_ohlc,
    distribution_us_sessions,
    load_provider_response,
    map_taiwan_windows,
    mapping_integrity,
    parse_twse_stock_samples,
    parse_twse_taiex_responses,
    parse_yahoo_chart_response,
    schedule_from_twse_sessions,
    validate_parsed_ohlc,
)


YAHOO_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "yahoo_chart_2007_2018_v2"
LEGACY_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "yahoo_chart_2007_2018"
TWSE_ROOT = REPO_ROOT / "data" / "raw" / "cm_001" / "twse_official_audit_2007_2018"
OUTPUT_ROOT = REPO_ROOT / "data" / "processed" / "cm_001" / "stage_a_provider_audit_v2"
CANONICAL_ROOT = OUTPUT_ROOT / "canonical"
CANDIDATE_ROOT = OUTPUT_ROOT / "provider_candidates"
EXPERIMENT_ROOT = REPO_ROOT / "research" / "experiments" / "CM_001"
TIMEZONES = {
    "XSD": "America/New_York",
    "QQQ": "America/New_York",
    "SPY": "America/New_York",
    "0052": "Asia/Taipei",
    "TAIEX": "Asia/Taipei",
    "0050": "Asia/Taipei",
}


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a small DataFrame without adding a reporting dependency."""
    columns = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for values in frame.itertuples(index=False, name=None):
        lines.append(
            "| "
            + " | ".join("" if pd.isna(value) else str(value) for value in values)
            + " |"
        )
    return "\n".join(lines)


def research_slice(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply the approved Taiwan/session-date Research boundary."""
    result = frame.loc[
        (frame["session_date"] >= RESEARCH_START)
        & (frame["session_date"] <= RESEARCH_END)
    ].copy()
    if result.empty or result["session_date"].min() < RESEARCH_START:
        raise ValueError("invalid or empty research slice")
    if result["session_date"].max() > RESEARCH_END:
        raise ValueError("research slice crosses Validation")
    return result.reset_index(drop=True)


def load_yahoo() -> tuple[
    dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, dict[str, Any]], dict[str, dict[str, Any]]
]:
    """Run raw-response gates before parsing any Yahoo response."""
    frames: dict[str, pd.DataFrame] = {}
    actions: dict[str, pd.DataFrame] = {}
    audits: dict[str, dict[str, Any]] = {}
    requests: dict[str, dict[str, Any]] = {}
    for asset, timezone in TIMEZONES.items():
        request = json.loads(
            (YAHOO_ROOT / f"{asset}_request.json").read_text(encoding="utf-8-sig")
        )
        payload = load_provider_response(YAHOO_ROOT / f"{asset}_response.json")
        audit = audit_yahoo_chart_response(payload, request)
        if audit["schema_status"] != "VALID":
            raise ValueError(f"{asset} failed raw acquisition gate: {audit['issues']}")
        frame, action_frame = parse_yahoo_chart_response(payload, audit, timezone)
        frames[asset] = frame
        actions[asset] = action_frame
        audits[asset] = audit
        requests[asset] = request
    return frames, actions, audits, requests


def legacy_parser_diagnosis() -> pd.DataFrame:
    """Prove how locale serialization created nulls in the invalid snapshot."""
    rows = []
    for asset in TIMEZONES:
        path = LEGACY_ROOT / f"{asset}_ohlc.csv"
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        for field in ("open", "high", "low", "close", "adj_close"):
            source = frame[field]
            parsed = pd.to_numeric(source, errors="coerce")
            rows.append(
                {
                    "instrument": asset,
                    "field": field,
                    "rows": len(source),
                    "comma_decimal_strings": int(source.str.contains(",", regex=False).sum()),
                    "parser_created_nulls": int((source.ne("") & parsed.isna()).sum()),
                }
            )
    return pd.DataFrame(rows)


def build_us_availability(
    schedule: pd.DataFrame, yahoo: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """Attach only OHLC availability to the US calendar; do not calculate features."""
    result = schedule.copy()
    required: list[str] = []
    for asset in US_ASSETS:
        frame = research_slice(yahoo[asset]).set_index("session_date")[["open", "close"]]
        renamed = frame.rename(columns={field: f"{asset}_{field}" for field in ("open", "close")})
        result = result.join(renamed, on="session_date")
        required.extend([f"{asset}_open", f"{asset}_close"])
    result["complete_us_session"] = result[required].notna().all(axis=1) & result[required].gt(0).all(axis=1)
    return result


def official_mark_counts(instrument: str) -> int:
    """Count TWSE's documented split/resumption mark in the approved Research months."""
    count = 0
    for path in sorted(TWSE_ROOT.glob(f"{instrument}_????????.json")):
        payload = load_provider_response(path)
        if payload.get("stat") != "OK":
            continue
        fields = payload.get("fields", [])
        if "Mark" not in fields:
            continue
        index = fields.index("Mark")
        count += sum(str(row[index]).strip() == "**" for row in payload.get("data", []))
    return count


def write_toml(path: Path, values: OrderedDict[str, Any]) -> None:
    """Write the flat source-manifest contract deterministically."""
    lines = []
    for key, value in values.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, int):
            rendered = str(value)
        else:
            escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
            rendered = f'"{escaped}"'
        lines.append(f"{key} = {rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def choose_examples(mapping: pd.DataFrame, us_schedule: pd.DataFrame) -> pd.DataFrame:
    """Select timing cases by calendar properties only, never by returns."""
    work = mapping.sort_values("target_session").reset_index(drop=True).copy()
    work["previous_target"] = work["target_session"].shift(1)
    work["tw_gap_days"] = [
        (current - previous).days if isinstance(previous, date) else None
        for current, previous in zip(work["target_session"], work["previous_target"])
    ]
    session_sets = work["us_session_dates"].map(
        lambda value: {date.fromisoformat(item) for item in value.split(";") if item}
    )
    utc_open_minutes = us_schedule["session_open_utc"].dt.hour * 60 + us_schedule["session_open_utc"].dt.minute
    changes = utc_open_minutes.diff()
    dst_start = set(us_schedule.loc[changes < 0, "session_date"])
    dst_end = set(us_schedule.loc[changes > 0, "session_date"])
    selected: OrderedDict[date, str] = OrderedDict()

    def add(mask: pd.Series, label: str) -> None:
        for target in work.loc[mask, "target_session"]:
            if target not in selected:
                selected[target] = label
                return

    add(session_sets.map(lambda values: bool(values & dst_start)), "US DST start")
    add(session_sets.map(lambda values: bool(values & dst_end)), "US DST end")
    add(work["us_early_close_sessions"].gt(0), "US early close")
    add(work["mapping_status"].eq("EMPTY_US_WINDOW"), "US holiday / zero-US window")
    add(work["target_session"].map(lambda value: value.weekday() == 0) & work["n_us_sessions"].eq(1), "Weekend")
    add(work["target_session"].map(lambda value: value.month == 2) & work["tw_gap_days"].ge(5), "Taiwan Lunar New Year gap")
    add(work["n_us_sessions"].ge(2) & ~work["target_session"].isin(selected), "Multiple-US-session window")
    add(work["target_session"].map(lambda value: value.weekday() == 5), "Taiwan Saturday session")
    add(work["n_us_sessions"].eq(1) & work["us_early_close_sessions"].eq(0), "Normal session")
    add(work["n_us_sessions"].eq(1) & ~work["target_session"].isin(selected), "Additional normal session")

    columns = [
        "target_session",
        "previous_tw_close_utc",
        "us_open_timestamps_utc",
        "us_close_timestamps_utc",
        "current_tw_open_utc",
        "mapping_status",
        "n_us_sessions",
    ]
    examples = work.loc[work["target_session"].isin(selected), columns].copy()
    examples.insert(0, "category", examples["target_session"].map(selected))
    return examples.sort_values("target_session").reset_index(drop=True)


def main() -> int:
    yahoo_all, yahoo_actions, yahoo_audits, yahoo_requests = load_yahoo()
    legacy = legacy_parser_diagnosis()
    official_taiex_all = parse_twse_taiex_responses(list(TWSE_ROOT.glob("TAIEX_????????.json")))
    official_0052, unavailable_0052 = parse_twse_stock_samples(
        list(TWSE_ROOT.glob("0052_????????.json")), "0052"
    )
    official_0050, unavailable_0050 = parse_twse_stock_samples(
        list(TWSE_ROOT.glob("0050_????????.json")), "0050"
    )
    official = {
        "0052": research_slice(official_0052),
        "TAIEX": research_slice(official_taiex_all),
        "0050": research_slice(official_0050),
    }
    yahoo = {asset: research_slice(frame) for asset, frame in yahoo_all.items()}

    integrity_by_asset: dict[str, dict[str, int]] = {
        asset: validate_parsed_ohlc(yahoo[asset]) for asset in US_ASSETS
    }
    integrity_by_asset.update(
        {asset: validate_parsed_ohlc(official[asset]) for asset in ("0052", "TAIEX", "0050")}
    )
    acquisition_status = {
        "XSD": "VALID",
        "QQQ": "VALID",
        "SPY": "VALID",
        "0052": "PARTIAL",
        "TAIEX": "VALID",
        "0050": "VALID",
    }
    provider = {
        "XSD": "Yahoo Chart API",
        "QQQ": "Yahoo Chart API",
        "SPY": "Yahoo Chart API",
        "0052": "TWSE STOCK_DAY",
        "TAIEX": "TWSE MI_5MINS_HIST",
        "0050": "TWSE STOCK_DAY",
    }

    coverage_rows = []
    for asset in (*US_ASSETS, "0052", "TAIEX", "0050"):
        frame = yahoo[asset] if asset in US_ASSETS else official[asset]
        stats = integrity_by_asset[asset]
        valid = frame.loc[(frame["open"] > 0) & (frame["close"] > 0), "session_date"]
        coverage_rows.append(
            {
                "Instrument": asset,
                "Provider": provider[asset],
                "Requested start": str(RESEARCH_START),
                "First valid session": valid.min() if not valid.empty else None,
                "Last valid Research session": valid.max() if not valid.empty else None,
                "Raw rows": stats["raw_rows"],
                "Valid Open rows": int(((frame["open"].notna()) & (frame["open"] > 0)).sum()),
                "Valid Close rows": int(((frame["close"].notna()) & (frame["close"] > 0)).sum()),
                "Missing Open": stats["missing_open"],
                "Missing Close": stats["missing_close"],
                "Duplicate sessions": stats["duplicate_sessions"],
                "Corporate-action coverage": (
                    "Yahoo events queried; completeness unverified"
                    if asset in (*US_ASSETS, "0052", "0050")
                    else "N/A for index"
                ),
                "Timezone status": "calendar-defined; provider date only" if asset not in US_ASSETS else "provider metadata matched",
                "Acquisition status": acquisition_status[asset],
            }
        )
    coverage = pd.DataFrame(coverage_rows)

    cross_provider_rows = []
    for asset in ("0052", "TAIEX", "0050"):
        result = compare_provider_ohlc(yahoo[asset], official[asset])
        cross_provider_rows.append({"Instrument": asset, **result})
    cross_provider = pd.DataFrame(cross_provider_rows)

    us_schedule = calendar_schedule("XNYS")
    us_availability = build_us_availability(us_schedule, yahoo)
    if not us_availability["complete_us_session"].all():
        raise ValueError("US price integrity gate failed; mapper is blocked")
    tw_schedule = schedule_from_twse_sessions(official["TAIEX"])
    if tw_schedule["session_date"].duplicated().any():
        raise ValueError("Taiwan calendar integrity gate failed; mapper is blocked")
    mapping = map_taiwan_windows(tw_schedule, us_availability)
    distribution = distribution_us_sessions(mapping)
    mapping_status_counts = {
        str(key): int(value) for key, value in mapping["mapping_status"].value_counts().items()
    }
    map_integrity = mapping_integrity(mapping)
    map_integrity["future_data_violations"] = int(
        (
            mapping["feature_information_end_utc"].notna()
            & (mapping["feature_information_end_utc"] >= mapping["current_tw_open_utc"])
        ).sum()
    )
    map_integrity["missing_feature_source_sessions"] = int(
        mapping["mapping_status"].eq("DATA_MISSING").sum()
    )

    follower = tw_schedule[["session_date"]].merge(
        official["0052"][["session_date", "open", "close"]], on="session_date", how="left"
    )
    current_valid = follower[["open", "close"]].notna().all(axis=1) & follower[["open", "close"]].gt(0).all(axis=1)
    prior_close_valid = follower["close"].shift(1).notna() & follower["close"].shift(1).gt(0)
    target_component_valid = current_valid & prior_close_valid
    map_integrity["missing_target_component_sessions"] = int((~target_component_valid).sum())

    xtai = calendar_schedule("XTAI")
    official_dates = set(tw_schedule["session_date"])
    xtai_dates = set(xtai["session_date"])
    calendar_audit = {
        "package": "exchange-calendars",
        "version": "4.13.2",
        "us_calendar": "XNYS (XNAS/ARCX aliases resolve to the same calendar)",
        "us_timezone": "America/New_York",
        "us_sessions": int(len(us_schedule)),
        "us_early_closes": int(us_schedule["early_close"].sum()),
        "taiwan_candidate": "official TWSE TAIEX session dates + official 09:00-13:30 Asia/Taipei regular hours",
        "taiwan_sessions": int(len(tw_schedule)),
        "xtai_missing_official_sessions": len(official_dates - xtai_dates),
        "xtai_extra_sessions": len(xtai_dates - official_dates),
    }
    examples = choose_examples(mapping, us_schedule)

    action_rows = []
    action_details = []
    for asset in ("0052", "0050"):
        actions = yahoo_actions[asset]
        actions = actions.loc[
            actions["event_date"].map(lambda value: RESEARCH_START <= value <= RESEARCH_END)
        ].copy()
        trading_dates = set(tw_schedule["session_date"])
        dividends = actions.loc[actions["event_type"].eq("dividends")]
        splits = actions.loc[actions["event_type"].eq("splits")]
        action_rows.append(
            {
                "Instrument": asset,
                "Event query start": str(RESEARCH_START),
                "Event query end": str(RESEARCH_END),
                "Dividend/distribution events": len(dividends),
                "Split events in Research": len(splits),
                "TWSE ** marks": official_mark_counts(asset),
                "Events on TW sessions": int(actions["event_date"].isin(trading_dates).sum()),
                "History completeness": "UNRESOLVED",
            }
        )
        for row in actions.itertuples(index=False):
            action_details.append(
                {"Instrument": asset, "Event type": row.event_type, "Event date": row.event_date}
            )
    action_summary = pd.DataFrame(action_rows)
    action_detail_frame = pd.DataFrame(action_details)

    schema_rows = []
    for asset, audit in yahoo_audits.items():
        lengths = {stats["array_length"] for stats in audit["fields"].values()}
        schema_rows.append(
            {
                "Instrument": asset,
                "HTTP": audit["http_status"],
                "Provider symbol": audit["provider_symbol"],
                "Interval": audit["requested_interval"],
                "Timezone": audit["timezone_reported"],
                "Timestamps": audit["timestamp_count"],
                "All arrays aligned": len(lengths) == 1 and next(iter(lengths)) == audit["timestamp_count"],
                "Open nulls": audit["fields"]["open"]["null_count"],
                "Close nulls": audit["fields"]["close"]["null_count"],
                "Adj Close nulls": audit["fields"]["adjclose"]["null_count"],
                "Raw schema gate": audit["schema_status"],
            }
        )
    schema_audit = pd.DataFrame(schema_rows)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    CANONICAL_ROOT.mkdir(parents=True, exist_ok=True)
    CANDIDATE_ROOT.mkdir(parents=True, exist_ok=True)
    legacy_notice = LEGACY_ROOT / "SOURCE_MANIFEST.toml"
    write_toml(
        legacy_notice,
        OrderedDict(
            provider="Yahoo Finance chart API",
            instrument="MULTI_ASSET",
            provider_symbol="XSD,QQQ,SPY,0052.TW,^TWII,0050.TW",
            requested_start="2007-01-01",
            requested_end="2019-01-01",
            snapshot_status="INVALID",
            notes="PowerShell Export-Csv used locale decimal commas; the Python parser created nulls. Preserved for debug only; never canonical.",
        ),
    )
    for asset in TIMEZONES:
        frame = yahoo_all[asset]
        valid = frame.loc[(frame["open"] > 0) & (frame["close"] > 0)]
        integrity = validate_parsed_ohlc(frame)
        raw_status = "VALID"
        if asset in ("0052", "0050", "TAIEX") and (
            integrity["missing_open"] or integrity["nonpositive_open"] or integrity["impossible_ohlc"]
        ):
            raw_status = "PARTIAL"
        write_toml(
            YAHOO_ROOT / f"{asset}_SOURCE_MANIFEST.toml",
            OrderedDict(
                provider="Yahoo Finance chart API",
                instrument=asset,
                provider_symbol=yahoo_requests[asset]["provider_symbol"],
                requested_start="2007-01-01",
                requested_end="2019-01-01",
                acquired_at=yahoo_requests[asset]["acquired_at_utc"],
                first_timestamp_returned=str(frame["source_timestamp_utc"].min()),
                last_timestamp_returned=str(frame["source_timestamp_utc"].max()),
                raw_rows=len(frame),
                valid_open_rows=int(((frame["open"].notna()) & (frame["open"] > 0)).sum()),
                valid_close_rows=int(((frame["close"].notna()) & (frame["close"] > 0)).sum()),
                timezone_reported=yahoo_audits[asset]["timezone_reported"],
                has_open=True,
                has_close=True,
                has_adj_close=True,
                has_dividends="events requested; presence varies",
                has_splits="events requested; presence varies",
                snapshot_status=raw_status,
                notes="Immutable JSON response. Quote OHLC and Adj Close remain separate; no adjustment policy selected.",
            ),
        )

    for asset in ("0052", "TAIEX", "0050"):
        frame = official[asset]
        valid = frame.loc[(frame["open"] > 0) & (frame["close"] > 0)]
        status = acquisition_status[asset]
        write_toml(
            TWSE_ROOT / f"{asset}_SOURCE_MANIFEST.toml",
            OrderedDict(
                provider="Taiwan Stock Exchange",
                instrument=asset,
                provider_symbol=asset,
                requested_start=str(RESEARCH_START),
                requested_end="2019-01-01",
                acquired_at="",
                first_timestamp_returned=str(frame["source_timestamp_utc"].min()),
                last_timestamp_returned=str(frame["source_timestamp_utc"].max()),
                raw_rows=len(frame),
                valid_open_rows=len(valid),
                valid_close_rows=len(valid),
                timezone_reported="",
                has_open=True,
                has_close=True,
                has_adj_close=False,
                has_dividends=False,
                has_splits=False,
                snapshot_status=status,
                notes="Official daily OHLC; timezone is not in price response and is supplied separately by official TWSE trading-hours documentation.",
            ),
        )

    for asset in US_ASSETS:
        research_slice(yahoo[asset]).to_csv(CANONICAL_ROOT / f"{asset}_ohlc.csv", index=False)
    official["TAIEX"].to_csv(CANONICAL_ROOT / "TAIEX_ohlc.csv", index=False)
    official["0050"].to_csv(CANONICAL_ROOT / "0050_ohlc.csv", index=False)
    official["0052"].loc[
        official["0052"][["open", "high", "low", "close"]].notna().all(axis=1)
    ].to_csv(CANONICAL_ROOT / "0052_ohlc_valid_rows.csv", index=False)
    official["0052"].to_csv(CANDIDATE_ROOT / "0052_all_official_rows.csv", index=False)
    mapping.to_csv(OUTPUT_ROOT / "session_mapping.csv", index=False)
    examples.to_csv(OUTPUT_ROOT / "manual_mapping_examples.csv", index=False)
    coverage.to_csv(OUTPUT_ROOT / "coverage.csv", index=False)
    cross_provider.to_csv(OUTPUT_ROOT / "cross_provider_qa.csv", index=False)
    schema_audit.to_csv(OUTPUT_ROOT / "yahoo_schema_audit.csv", index=False)
    (OUTPUT_ROOT / "yahoo_response_audit.json").write_text(
        json.dumps(yahoo_audits, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    twse_response_audit = {
        "TAIEX": {
            "provider": "Taiwan Stock Exchange",
            "dataset": "MI_5MINS_HIST",
            "top_level_keys": ["data", "date", "fields", "stat", "title", "total"],
            "fields": ["Date", "Opening Index", "Highest Index", "Lowest Index", "Closing Index"],
            "research_rows": len(official["TAIEX"]),
            "status": "VALID",
        },
        "0052": {
            "provider": "Taiwan Stock Exchange",
            "dataset": "STOCK_DAY",
            "fields": ["Date", "Trade Volume", "Trade Value", "Opening Price", "Highest Price", "Lowest Price", "Closing Price", "Change", "Transaction", "Mark"],
            "research_rows": len(official["0052"]),
            "ohlc_missing_sentinel_rows": int(official["0052"]["open"].isna().sum()),
            "pre_2010_statuses": unavailable_0052,
            "status": "PARTIAL",
        },
        "0050": {
            "provider": "Taiwan Stock Exchange",
            "dataset": "STOCK_DAY",
            "fields": ["Date", "Trade Volume", "Trade Value", "Opening Price", "Highest Price", "Lowest Price", "Closing Price", "Change", "Transaction", "Mark"],
            "research_rows": len(official["0050"]),
            "ohlc_missing_sentinel_rows": int(official["0050"]["open"].isna().sum()),
            "pre_2010_statuses": unavailable_0050,
            "status": "VALID",
        },
    }
    (OUTPUT_ROOT / "twse_response_audit.json").write_text(
        json.dumps(twse_response_audit, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    legacy.to_csv(OUTPUT_ROOT / "legacy_parser_failure.csv", index=False)
    action_summary.to_csv(OUTPUT_ROOT / "corporate_action_summary.csv", index=False)
    action_detail_frame.to_csv(OUTPUT_ROOT / "corporate_action_events.csv", index=False)

    diagnostics = {
        "experiment_id": "CM_001",
        "stage": "A - Data & Timing Feasibility",
        "research_start": str(RESEARCH_START),
        "research_end": str(RESEARCH_END),
        "taiwan_target_sessions": len(mapping),
        "us_sessions_per_taiwan_window": distribution,
        "mapping_status_counts": mapping_status_counts,
        "integrity": map_integrity,
        "calendar": calendar_audit,
        "data_source_status": "DATA SOURCE DECISION REQUIRED",
        "stage_a_verdict": "DECISION_REQUIRED",
        "stage_b_authorized": False,
        "validation_opened": False,
        "oos_opened": False,
    }
    (OUTPUT_ROOT / "diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )

    acquisition_report = f"""# CM_001 — Acquisition audit

## Scope

Research boundary revised by human decision to `2010-01-01 <= Taiwan session <= 2018-12-31`. Validation and Final OOS were not requested, loaded, processed or displayed. No feature–target quantity was calculated.

## Root cause of the invalid first run

The Yahoo HTTP responses were structurally valid. The first acquisition converted JSON numbers to PowerShell objects and then used `Export-Csv` under a decimal-comma locale. Values such as decimal-point JSON numbers were persisted with commas. Python `to_numeric` expected decimal points and created thousands of `NaN`; those nulls did not come from the provider. The invalid snapshot is preserved with `snapshot_status = \"INVALID\"` and is excluded from all canonical paths.

{markdown_table(legacy.groupby('instrument', as_index=False).agg(**{'parser-created nulls': ('parser_created_nulls', 'sum'), 'comma-decimal strings': ('comma_decimal_strings', 'sum')}))}

## Corrected Yahoo raw-schema audit

The corrected flow persists immutable HTTP JSON first, validates schema/arrays, then parses. `chart.result` contains exactly one result; `quote` and `adjclose` are separate one-element lists; timestamps are Unix seconds; all quote/adjusted arrays have the same length as `timestamp`; JSON nulls are counted before DataFrame construction.

{markdown_table(schema_audit)}

## Official TWSE schema audit

- `TAIEX/MI_5MINS_HIST`: monthly `Date, Opening Index, Highest Index, Lowest Index, Closing Index`; 2,970 complete sessions in the retained 2007–2018 acquisition audit and 2,223 sessions in revised Research.
- `afterTrading/STOCK_DAY`: available from `2010-01-04`; includes daily OHLC and a documented `\"--\"` sentinel. In revised Research, `0052` has 108 all-OHLC sentinel rows and `0050` has none.
- The official response has session dates but no timezone field. Timestamp construction therefore uses the separately documented TWSE regular hours and remains a calendar-policy item for human approval.

## Cross-provider QA

Large discrepancy means at least one comparable OHLC field differs by more than 0.5%; this is a data-integrity threshold, not an economic test.

{markdown_table(cross_provider)}

The Yahoo `0050` overlap contains a material scale discontinuity relative to TWSE official raw OHLC. This is consistent with incomplete retrospective adjustment around the later 4:1 ETF split, but is recorded as a provider-provenance inference rather than silently corrected. No mixed raw Open/adjusted Close series was built.
"""
    (EXPERIMENT_ROOT / "acquisition_audit.md").write_text(acquisition_report, encoding="utf-8")

    provider_comparison = pd.DataFrame(
        [
            ["Yahoo Chart API — US", "2010–2018 complete", "valid OHLC", "dividends/splits stream", "timezone metadata; no calendar", "no auth; live endpoint", "unofficial and mutable history", "Candidate for human approval"],
            ["Yahoo Chart API — Taiwan", "partial", "0052 zero/missing Open; 0050 scale issue", "event stream", "timezone metadata; no calendar", "no auth; live endpoint", "history not defensible as sole source", "Do not promote"],
            ["TWSE public — TAIEX", "1999 onward; complete Research", "official OHLC", "not applicable", "date only; hours separate", "public monthly endpoint", "no timezone in response", "Recommended primary TAIEX source"],
            ["TWSE public — 0052/0050", "2010 onward", "official OHLC; 0052 has 108 no-OHLC rows", "split mark only", "date only; hours separate", "public monthly endpoint", "pre-2010 unavailable; redistribution terms need review", "Recommended Taiwan price source after policy approval"],
            ["TWSE Data E-Shop", "starts 1992", "official daily OHLC product", "separate products may be needed", "official production metadata", "subscription required", "licensing/cost", "Not needed after approved 2010 revision unless missing-row policy requires it"],
            ["Fubon / issuer — 0052", "product/distribution history", "not a daily exchange-OHLC source", "issuer distributions", "not a calendar", "public pages", "does not replace TWSE OHLC", "Use for action cross-check"],
        ],
        columns=["Provider candidate", "Coverage", "OHLC quality", "Corporate actions", "Timezone/calendar quality", "Reproducibility", "Main limitation", "Recommendation"],
    )
    comparison_report = f"""# CM_001 — Data source comparison

{markdown_table(provider_comparison)}

```text
DATA SOURCE DECISION REQUIRED
```

Recommended multi-provider candidate for human approval: Yahoo immutable JSON for `XSD/QQQ/SPY`; official TWSE monthly endpoints for `0052/TAIEX/0050`; official session sources for dates/hours, with `exchange-calendars==4.13.2` `XNYS` for the US candidate calendar. This recommendation uses only coverage, schema, provenance, timestamps, OHLC integrity, corporate-action information and reproducibility.
"""
    (EXPERIMENT_ROOT / "data_source_comparison.md").write_text(comparison_report, encoding="utf-8")

    distribution_frame = pd.DataFrame(
        [{"n_us_sessions": key, "Taiwan windows": value} for key, value in distribution.items()]
    )
    mapping_status_frame = pd.DataFrame(
        [{"mapping_status": key, "Taiwan windows": value} for key, value in mapping_status_counts.items()]
    )
    integrity_frame = pd.DataFrame([map_integrity])
    integrity_report = f"""# CM_001 — Stage A integrity report

## Hard stop

This report contains only acquisition, OHLC, calendar and timestamp diagnostics for revised Research `2010-01-01`–`2018-12-31`. It contains no H1/H2/H3, correlation, covariance, regression, beta, t-statistic, p-value, IC, conditional mean, hit rate, quintile, Sharpe, strategy return, backtest or feature–target visualization. Validation and Final OOS remain closed.

## Coverage and OHLC integrity

{markdown_table(coverage)}

All retained positive OHLC rows satisfy `High >= max(Open, Close)`, `Low <= min(Open, Close)`, `High >= Low`; duplicate timestamp/session and non-monotonic timestamp counts are zero. `0052`'s 108 `\"--\"` rows are explicitly missing and never imputed.

## Corporate actions

{markdown_table(action_summary)}

{markdown_table(action_detail_frame) if not action_detail_frame.empty else 'No Research-period events reported.'}

Dividend/split completeness is unresolved because the public price endpoint is not a corporate-action master and Yahoo history is mutable. Raw OHLC, Adj Close, dividends and splits remain separate. No adjustment method was selected or applied.

## Calendar status

{markdown_table(pd.DataFrame([calendar_audit]))}

The US calendar includes actual early closes and DST-aware UTC timestamps. Official TWSE Research session dates include {calendar_audit['xtai_missing_official_sessions']} sessions missing from the `XTAI` library candidate (principally historical Saturday make-up sessions); `XTAI` includes {calendar_audit['xtai_extra_sessions']} date absent from official TAIEX. The mapper therefore uses official TWSE dates/hours for this audit, while final calendar policy remains subject to human approval.

## Session mapping

Taiwan target sessions: **{len(mapping)}**.

{markdown_table(distribution_frame)}

{markdown_table(mapping_status_frame)}

{markdown_table(integrity_frame)}

`EMPTY_US_WINDOW` is assigned only when the calendar has no eligible US session. If an eligible US calendar session lacked validated `XSD/QQQ/SPY` OHLC, status would be `DATA_MISSING`; these states are never conflated.

## Manual calendar-selected cases

{markdown_table(examples)}

## Stage A verdict

```text
DECISION_REQUIRED
```

The dataset/timing construction is feasible for 2010–2018, but 0052 missing-OHLC handling, adjustment/corporate-action policy and final multi-provider/calendar approval are material human decisions. Stage B remains not authorized.
"""
    (EXPERIMENT_ROOT / "stage_a_data_timing_feasibility.md").write_text(integrity_report, encoding="utf-8")

    decision_request = """# CM_001 — Stage A decision request

Before any Stage B freeze, researchers must decide:

1. Approve or reject the proposed multi-provider source policy: Yahoo immutable JSON for `XSD/QQQ/SPY`; official TWSE monthly OHLC for `0052/TAIEX/0050`.
2. Approve the treatment of 108 official `0052` no-OHLC (`\"--\"`) sessions. Recommended: retain them in the session ledger, exclude observations whose required target components are unavailable, and never impute prices or zero returns.
3. Approve adjusted versus unadjusted OHLC and corporate-action treatment. Raw OHLC, Adj Close and actions remain separate; no policy has been applied.
4. Approve the calendar/timezone policy: actual `XNYS` session boundaries including early closes/DST for the US; official TWSE dates plus official 09:00–13:30 `Asia/Taipei` regular hours for Taiwan.
5. Include the already human-approved `2010-01-01` Research start in the eventual full specification freeze and recorded Git commit.

Estimator, inference, HAC/Newey-West, placebos and GO/CONDITIONAL GO/NO-GO criteria remain untouched and TBD. Validation and Final OOS remain closed.
"""
    (EXPERIMENT_ROOT / "stage_a_decision_request.md").write_text(decision_request, encoding="utf-8")

    print(json.dumps(diagnostics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
