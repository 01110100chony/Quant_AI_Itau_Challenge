"""Mechanical data and session-mapping helpers for CM_001 Stage A only."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import numpy as np
import pandas as pd


ACQUISITION_AUDIT_START = date(2007, 1, 1)
RESEARCH_START = date(2010, 1, 1)
RESEARCH_END = date(2018, 12, 31)
US_ASSETS = ("XSD", "QQQ", "SPY")
TW_ASSETS = ("0052", "TAIEX", "0050")
PRICE_FIELDS = ("open", "high", "low", "close", "volume")


def load_provider_response(path: Path) -> dict[str, Any]:
    """Load an immutable provider JSON response without tabular conversion."""
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} top-level JSON value is not an object")
    return payload


def audit_yahoo_chart_response(
    payload: Mapping[str, Any], request: Mapping[str, Any]
) -> dict[str, Any]:
    """Audit Yahoo Chart schema and array integrity before creating a DataFrame."""
    issues: list[str] = []
    top_level_keys = sorted(str(key) for key in payload)
    chart = payload.get("chart")
    if not isinstance(chart, dict):
        return {
            "asset": request.get("asset", ""),
            "provider_symbol": request.get("provider_symbol", ""),
            "http_status": request.get("http_status"),
            "top_level_keys": top_level_keys,
            "schema_status": "INVALID",
            "snapshot_status": "INVALID",
            "issues": ["chart is missing or is not an object"],
        }

    result_container = chart.get("result")
    result_count = len(result_container) if isinstance(result_container, list) else 0
    error_key_present = "error" in chart
    error_value_is_null = error_key_present and chart.get("error") is None
    if not isinstance(result_container, list):
        issues.append("chart.result is missing or is not a list")
    elif result_count != 1:
        issues.append(f"chart.result count is {result_count}, expected 1")
    if not error_key_present:
        issues.append("chart.error key is missing")
    elif not error_value_is_null:
        issues.append("chart.error is non-null")

    result = result_container[0] if isinstance(result_container, list) and result_count == 1 else {}
    meta = result.get("meta") if isinstance(result, dict) else None
    timestamps = result.get("timestamp") if isinstance(result, dict) else None
    indicators = result.get("indicators") if isinstance(result, dict) else None
    if not isinstance(meta, dict):
        issues.append("result.meta is missing or is not an object")
        meta = {}
    if not isinstance(timestamps, list):
        issues.append("result.timestamp is missing or is not a list")
        timestamps = []
    if not isinstance(indicators, dict):
        issues.append("result.indicators is missing or is not an object")
        indicators = {}

    quote_container = indicators.get("quote")
    quote_is_list = isinstance(quote_container, list)
    quote_count = len(quote_container) if quote_is_list else 0
    if not quote_is_list:
        issues.append("indicators.quote is missing or is not a list")
    elif quote_count != 1:
        issues.append(f"indicators.quote count is {quote_count}, expected 1")
    quote = quote_container[0] if quote_is_list and quote_count == 1 else {}
    if not isinstance(quote, dict):
        issues.append("indicators.quote[0] is not an object")
        quote = {}

    adj_container = indicators.get("adjclose")
    adjclose_key_present = "adjclose" in indicators
    adjclose_is_list = isinstance(adj_container, list)
    adjclose_count = len(adj_container) if adjclose_is_list else 0
    adj = adj_container[0] if adjclose_is_list and adjclose_count == 1 else {}
    if adjclose_key_present and not adjclose_is_list:
        issues.append("indicators.adjclose exists but is not a list")
    elif adjclose_is_list and adjclose_count != 1:
        issues.append(f"indicators.adjclose count is {adjclose_count}, expected 1")
    if not isinstance(adj, dict):
        issues.append("indicators.adjclose[0] is not an object")
        adj = {}

    timestamp_count = len(timestamps)
    field_arrays: dict[str, list[Any]] = {}
    field_key_present: dict[str, bool] = {}
    for field in PRICE_FIELDS:
        field_key_present[field] = field in quote
        values = quote.get(field)
        if not isinstance(values, list):
            issues.append(f"quote.{field} is missing or is not a list")
            values = []
        field_arrays[field] = values
        if len(values) != timestamp_count:
            issues.append(
                f"len(quote.{field})={len(values)} != len(timestamp)={timestamp_count}"
            )

    adj_key_present = "adjclose" in adj
    adj_values = adj.get("adjclose")
    if not isinstance(adj_values, list):
        if adjclose_key_present:
            issues.append("adjclose[0].adjclose is missing or is not a list")
        adj_values = []
    if adj_values and len(adj_values) != timestamp_count:
        issues.append(
            f"len(adjclose)={len(adj_values)} != len(timestamp)={timestamp_count}"
        )

    epoch_unit = "unknown"
    non_null_timestamps = [value for value in timestamps if value is not None]
    if non_null_timestamps:
        magnitude = abs(float(non_null_timestamps[0]))
        if 1e8 <= magnitude < 1e11:
            epoch_unit = "seconds"
        elif 1e11 <= magnitude < 1e14:
            epoch_unit = "milliseconds"
        else:
            issues.append(f"timestamp magnitude does not identify seconds/milliseconds: {magnitude}")

    field_stats: dict[str, dict[str, Any]] = {}
    for field, values in (*field_arrays.items(), ("adjclose", adj_values)):
        null_count = sum(value is None for value in values)
        field_stats[field] = {
            "key_present": field_key_present.get(field, adj_key_present),
            "array_length": len(values),
            "null_count": null_count,
            "non_null_count": len(values) - null_count,
            "null_fraction": (null_count / len(values)) if values else None,
        }

    close_fraction = (
        field_stats["close"]["non_null_count"] / timestamp_count if timestamp_count else 0.0
    )
    if timestamp_count > 100 and close_fraction < 0.90:
        issues.append(
            f"valid close fraction {close_fraction:.6f} is below acquisition gate 0.90"
        )

    expected_timezone = request.get("expected_timezone")
    timezone_reported = meta.get("exchangeTimezoneName")
    if expected_timezone and timezone_reported != expected_timezone:
        issues.append(
            f"reported timezone {timezone_reported!r} != expected {expected_timezone!r}"
        )

    schema_status = "VALID" if not issues else "INVALID"
    return {
        "asset": request.get("asset", ""),
        "provider": request.get("provider", ""),
        "provider_symbol": request.get("provider_symbol", ""),
        "http_status": request.get("http_status"),
        "requested_interval": request.get("interval", ""),
        "requested_start": request.get("requested_start", ""),
        "requested_end_exclusive": request.get("requested_end_exclusive", ""),
        "top_level_keys": top_level_keys,
        "chart_keys": sorted(str(key) for key in chart),
        "result_count": result_count,
        "error_key_present": error_key_present,
        "error_value_is_null": error_value_is_null,
        "meta_keys": sorted(str(key) for key in meta),
        "timezone_reported": timezone_reported,
        "data_granularity": meta.get("dataGranularity"),
        "timestamp_count": timestamp_count,
        "timestamp_unit": epoch_unit,
        "quote_is_list": quote_is_list,
        "quote_count": quote_count,
        "quote_keys": sorted(str(key) for key in quote),
        "adjclose_key_present": adjclose_key_present,
        "adjclose_is_list": adjclose_is_list,
        "adjclose_count": adjclose_count,
        "events_key_present": isinstance(result, dict) and "events" in result,
        "event_types": sorted(str(key) for key in (result.get("events") or {}))
        if isinstance(result, dict) and isinstance(result.get("events"), dict)
        else [],
        "fields": field_stats,
        "schema_status": schema_status,
        "snapshot_status": schema_status,
        "issues": issues,
    }


def parse_yahoo_chart_response(
    payload: Mapping[str, Any], audit: Mapping[str, Any], exchange_timezone: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse one response only after its pre-DataFrame schema gate passes."""
    if audit.get("schema_status") != "VALID":
        raise ValueError(f"Refusing to parse invalid response: {audit.get('issues')}")
    result = payload["chart"]["result"][0]
    quote = result["indicators"]["quote"][0]
    adj_values = result["indicators"].get("adjclose", [{}])[0].get("adjclose")
    timestamp_count = len(result["timestamp"])
    if adj_values is None:
        adj_values = [None] * timestamp_count
    frame = pd.DataFrame(
        {
            "source_timestamp_utc": pd.to_datetime(
                result["timestamp"], unit="s", utc=True
            ),
            "open": quote["open"],
            "high": quote["high"],
            "low": quote["low"],
            "close": quote["close"],
            "adj_close": adj_values,
            "volume": quote["volume"],
        }
    )
    frame["session_date"] = frame["source_timestamp_utc"].dt.tz_convert(
        ZoneInfo(exchange_timezone)
    ).dt.date
    assert_acquisition_dates(frame["session_date"], label=str(audit.get("asset", "response")))

    action_rows: list[dict[str, Any]] = []
    events = result.get("events") or {}
    for event_type in ("dividends", "splits", "capitalGains"):
        container = events.get(event_type) or {}
        if not isinstance(container, dict):
            raise ValueError(f"events.{event_type} is not an object")
        for event in container.values():
            event_timestamp = pd.to_datetime(event["date"], unit="s", utc=True)
            event_date = event_timestamp.tz_convert(ZoneInfo(exchange_timezone)).date()
            assert_acquisition_dates(pd.Series([event_date]), label=f"{audit.get('asset')} actions")
            action_rows.append(
                {
                    "event_type": event_type,
                    "source_timestamp_utc": event_timestamp,
                    "event_date": event_date,
                    "amount": event.get("amount"),
                    "numerator": event.get("numerator"),
                    "denominator": event.get("denominator"),
                    "split_ratio": event.get("splitRatio"),
                }
            )
    actions = pd.DataFrame(
        action_rows,
        columns=[
            "event_type",
            "source_timestamp_utc",
            "event_date",
            "amount",
            "numerator",
            "denominator",
            "split_ratio",
        ],
    )
    return frame.sort_values("source_timestamp_utc").reset_index(drop=True), actions


def validate_parsed_ohlc(frame: pd.DataFrame) -> dict[str, int]:
    """Count structural OHLC defects without calculating returns."""
    required = {"source_timestamp_utc", "session_date", "open", "high", "low", "close"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"parsed OHLC missing columns: {sorted(missing)}")
    if frame["source_timestamp_utc"].dt.tz is None:
        raise ValueError("parsed timestamps are not timezone-aware")
    numeric = frame[["open", "high", "low", "close"]]
    complete = numeric.notna().all(axis=1)
    positive = numeric.gt(0)
    impossible = complete & (
        (frame["high"] < frame[["open", "close"]].max(axis=1))
        | (frame["low"] > frame[["open", "close"]].min(axis=1))
        | (frame["high"] < frame["low"])
    )
    return {
        "raw_rows": int(len(frame)),
        "valid_open_rows": int(frame["open"].notna().sum()),
        "valid_close_rows": int(frame["close"].notna().sum()),
        "missing_open": int(frame["open"].isna().sum()),
        "missing_close": int(frame["close"].isna().sum()),
        "nonpositive_open": int((frame["open"].notna() & ~positive["open"]).sum()),
        "nonpositive_high": int((frame["high"].notna() & ~positive["high"]).sum()),
        "nonpositive_low": int((frame["low"].notna() & ~positive["low"]).sum()),
        "nonpositive_close": int((frame["close"].notna() & ~positive["close"]).sum()),
        "impossible_ohlc": int(impossible.sum()),
        "duplicate_timestamps": int(frame["source_timestamp_utc"].duplicated().sum()),
        "duplicate_sessions": int(frame["session_date"].duplicated().sum()),
        "non_monotonic_timestamps": int(not frame["source_timestamp_utc"].is_monotonic_increasing),
    }


def parse_twse_taiex_responses(paths: list[Path]) -> pd.DataFrame:
    """Parse official monthly TAIEX OHLC responses inside the research boundary."""
    expected_fields = [
        "Date",
        "Opening Index",
        "Highest Index",
        "Lowest Index",
        "Closing Index",
    ]
    rows: list[dict[str, Any]] = []
    for path in sorted(paths):
        payload = load_provider_response(path)
        if payload.get("stat") != "OK":
            raise ValueError(f"{path} TWSE status is not OK: {payload.get('stat')}")
        if payload.get("fields") != expected_fields:
            raise ValueError(f"{path} unexpected TAIEX fields: {payload.get('fields')}")
        data = payload.get("data")
        if not isinstance(data, list):
            raise ValueError(f"{path} data is not a list")
        for values in data:
            if not isinstance(values, list) or len(values) != len(expected_fields):
                raise ValueError(f"{path} contains a row with invalid width")
            rows.append(dict(zip(expected_fields, values)))
    frame = pd.DataFrame(rows)
    frame["session_date"] = pd.to_datetime(frame.pop("Date"), format="%Y/%m/%d").dt.date
    rename = {
        "Opening Index": "open",
        "Highest Index": "high",
        "Lowest Index": "low",
        "Closing Index": "close",
    }
    frame = frame.rename(columns=rename)
    for field in ("open", "high", "low", "close"):
        frame[field] = pd.to_numeric(
            frame[field].astype(str).str.replace(",", "", regex=False), errors="raise"
        )
    frame["source_timestamp_utc"] = pd.to_datetime(
        frame["session_date"].astype(str) + " 09:00:00"
    ).dt.tz_localize(ZoneInfo("Asia/Taipei")).dt.tz_convert("UTC")
    assert_acquisition_dates(frame["session_date"], label="TWSE official TAIEX")
    if frame["session_date"].duplicated().any():
        raise ValueError("TWSE official TAIEX contains duplicate sessions")
    return frame.sort_values("session_date").reset_index(drop=True)


def parse_twse_stock_samples(paths: list[Path], instrument: str) -> tuple[pd.DataFrame, list[str]]:
    """Parse official TWSE stock/ETF OHLC samples and retain unavailable-period statuses."""
    expected = {
        "Date": "session_date",
        "Opening Price": "open",
        "Highest Price": "high",
        "Lowest Price": "low",
        "Closing Price": "close",
    }
    rows: list[dict[str, Any]] = []
    unavailable: list[str] = []
    for path in sorted(paths):
        payload = load_provider_response(path)
        if payload.get("stat") != "OK":
            unavailable.append(str(payload.get("stat")))
            continue
        fields = payload.get("fields")
        data = payload.get("data")
        if not isinstance(fields, list) or not all(field in fields for field in expected):
            raise ValueError(f"{path} missing official OHLC fields")
        if not isinstance(data, list):
            raise ValueError(f"{path} data is not a list")
        for values in data:
            if not isinstance(values, list) or len(values) != len(fields):
                raise ValueError(f"{path} contains a row with invalid width")
            record = dict(zip(fields, values))
            rows.append({target: record[source] for source, target in expected.items()})
    frame = pd.DataFrame(rows, columns=["session_date", "open", "high", "low", "close"])
    if frame.empty:
        return frame, unavailable
    frame["session_date"] = pd.to_datetime(frame["session_date"], format="%Y/%m/%d").dt.date
    for field in ("open", "high", "low", "close"):
        source = frame[field].astype(str).str.replace(",", "", regex=False)
        documented_missing = source.eq("--")
        converted = pd.to_numeric(source.mask(documented_missing), errors="coerce")
        unexpected = ~documented_missing & converted.isna()
        if unexpected.any():
            values = sorted(source.loc[unexpected].unique().tolist())
            raise ValueError(f"TWSE {instrument} unexpected {field} values: {values}")
        frame[field] = converted
    frame["source_timestamp_utc"] = pd.to_datetime(
        frame["session_date"].astype(str) + " 09:00:00"
    ).dt.tz_localize(ZoneInfo("Asia/Taipei")).dt.tz_convert("UTC")
    assert_research_dates(frame["session_date"], label=f"TWSE official {instrument}")
    if frame["session_date"].duplicated().any():
        raise ValueError(f"TWSE official {instrument} samples contain duplicate sessions")
    return frame.sort_values("session_date").reset_index(drop=True), sorted(set(unavailable))


def compare_provider_ohlc(
    primary: pd.DataFrame, reference: pd.DataFrame, *, relative_tolerance: float = 0.005
) -> dict[str, int]:
    """Compare dates and OHLC structure across providers for non-economic QA."""
    fields = ["open", "high", "low", "close"]
    left = primary.set_index("session_date")[fields].add_suffix("_primary")
    right = reference.set_index("session_date")[fields].add_suffix("_reference")
    joined = left.join(right, how="inner")
    large = pd.Series(False, index=joined.index)
    for field in fields:
        reference_values = joined[f"{field}_reference"]
        comparable = joined[[f"{field}_primary", f"{field}_reference"]].notna().all(axis=1)
        relative = (
            (joined[f"{field}_primary"] - reference_values).abs()
            / reference_values.abs()
        )
        large |= comparable & (relative > relative_tolerance)
    return {
        "matched_sessions": int(len(joined)),
        "primary_only_sessions": int(len(left.index.difference(right.index))),
        "reference_only_sessions": int(len(right.index.difference(left.index))),
        "large_ohlc_discrepancy_sessions": int(large.sum()),
    }


def schedule_from_twse_sessions(frame: pd.DataFrame) -> pd.DataFrame:
    """Build candidate Taiwan regular-session boundaries from official TWSE dates/hours."""
    dates = pd.Series(frame["session_date"].drop_duplicates().sort_values().tolist())
    local_open = pd.to_datetime(dates.astype(str) + " 09:00:00").dt.tz_localize(
        ZoneInfo("Asia/Taipei")
    )
    local_close = pd.to_datetime(dates.astype(str) + " 13:30:00").dt.tz_localize(
        ZoneInfo("Asia/Taipei")
    )
    return pd.DataFrame(
        {
            "session_date": dates,
            "session_open_utc": local_open.dt.tz_convert("UTC"),
            "session_close_utc": local_close.dt.tz_convert("UTC"),
            "session_duration_minutes": 270.0,
            "early_close": False,
        }
    )


def load_raw_ohlc(path: Path, exchange_timezone: str) -> pd.DataFrame:
    """Load one research-only raw snapshot and attach the local session date."""
    frame = pd.read_csv(path)
    required = {"source_timestamp_utc", "open", "high", "low", "close", "adj_close", "volume"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    frame["source_timestamp_utc"] = pd.to_datetime(frame["source_timestamp_utc"], utc=True)
    if frame["source_timestamp_utc"].dt.tz is None:
        raise ValueError(f"{path} timestamps are not timezone-aware")
    frame["session_date"] = frame["source_timestamp_utc"].dt.tz_convert(
        ZoneInfo(exchange_timezone)
    ).dt.date
    assert_acquisition_dates(frame["session_date"], label=str(path))
    if frame["session_date"].duplicated().any():
        raise ValueError(f"{path} contains duplicated local session dates")
    for column in ("open", "high", "low", "close", "adj_close", "volume"):
        source = frame[column]
        converted = pd.to_numeric(source, errors="coerce")
        newly_null = source.notna() & converted.isna()
        if newly_null.any():
            raise ValueError(
                f"{path} parser would create {int(newly_null.sum())} nulls in {column}"
            )
        frame[column] = converted
    return frame.sort_values("session_date").reset_index(drop=True)


def load_actions(path: Path, exchange_timezone: str) -> pd.DataFrame:
    """Load vendor corporate-action events without applying any adjustment."""
    if path.stat().st_size == 0:
        return pd.DataFrame(
            columns=["event_type", "source_timestamp_utc", "event_date", "amount", "numerator", "denominator", "split_ratio"]
        )
    frame = pd.read_csv(path)
    if frame.empty:
        frame["event_date"] = pd.Series(dtype="object")
        return frame
    frame["source_timestamp_utc"] = pd.to_datetime(frame["source_timestamp_utc"], utc=True)
    frame["event_date"] = frame["source_timestamp_utc"].dt.tz_convert(
        ZoneInfo(exchange_timezone)
    ).dt.date
    assert_research_dates(frame["event_date"], label=str(path))
    return frame.sort_values(["event_date", "event_type"]).reset_index(drop=True)


def assert_research_dates(values: pd.Series, *, label: str) -> None:
    """Reject any session outside the human-approved 2010-2018 research interval."""
    non_null = values.dropna()
    if non_null.empty:
        return
    if non_null.min() < RESEARCH_START or non_null.max() > RESEARCH_END:
        raise ValueError(f"{label} crosses the authorized research boundary")


def assert_acquisition_dates(values: pd.Series, *, label: str) -> None:
    """Bound legacy acquisition-audit evidence to 2007-2018 without promoting it."""
    non_null = values.dropna()
    if non_null.empty:
        return
    if non_null.min() < ACQUISITION_AUDIT_START or non_null.max() > RESEARCH_END:
        raise ValueError(f"{label} crosses the Stage A acquisition-audit boundary")


def calendar_schedule(name: str) -> pd.DataFrame:
    """Return a research-only exchange schedule with UTC-aware boundaries."""
    calendar = xcals.get_calendar(name)
    schedule = calendar.schedule.loc[str(RESEARCH_START) : str(RESEARCH_END)].copy()
    schedule = schedule.rename(columns={"open": "session_open_utc", "close": "session_close_utc"})
    schedule["session_date"] = schedule.index.date
    for column in ("session_open_utc", "session_close_utc"):
        if schedule[column].dt.tz is None:
            raise ValueError(f"{name} {column} is not timezone-aware")
    duration = schedule["session_close_utc"] - schedule["session_open_utc"]
    schedule["session_duration_minutes"] = duration.dt.total_seconds() / 60.0
    schedule["early_close"] = duration < duration.mode().iloc[0]
    return schedule.reset_index(drop=True)


def coverage_table(raw: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize requested coverage fields without exposing price values."""
    rows: list[dict[str, object]] = []
    for asset, frame in raw.items():
        valid = frame.loc[frame[["open", "close"]].notna().all(axis=1)]
        rows.append(
            {
                "asset": asset,
                "first_valid_date": valid["session_date"].min() if not valid.empty else None,
                "last_date_used": valid["session_date"].max() if not valid.empty else None,
                "sessions": int(len(frame)),
                "missing_open": int(frame["open"].isna().sum()),
                "missing_close": int(frame["close"].isna().sum()),
            }
        )
    return pd.DataFrame(rows)


def _join_asset(schedule: pd.DataFrame, frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    selected = frame.set_index("session_date")[["open", "close", "adj_close"]].rename(
        columns={column: f"{asset}_{column}" for column in ("open", "close", "adj_close")}
    )
    return schedule.join(selected, on="session_date")


def build_us_components(
    schedule: pd.DataFrame, raw: Mapping[str, pd.DataFrame]
) -> pd.DataFrame:
    """Prepare approved US intraday components without any target association."""
    result = schedule.copy()
    for asset in US_ASSETS:
        result = _join_asset(result, raw[asset], asset)
    complete_columns = [f"{asset}_{field}" for asset in US_ASSETS for field in ("open", "close")]
    positive = result[complete_columns].gt(0).all(axis=1)
    result["complete_us_session"] = result[complete_columns].notna().all(axis=1) & positive
    for asset in US_ASSETS:
        result[f"r_id_{asset}"] = np.nan
        mask = result["complete_us_session"]
        result.loc[mask, f"r_id_{asset}"] = np.log(
            result.loc[mask, f"{asset}_close"] / result.loc[mask, f"{asset}_open"]
        )
    result["semi_specific"] = result["r_id_XSD"] - result["r_id_QQQ"]
    result["broad_tech"] = result["r_id_QQQ"] - result["r_id_SPY"]
    return result


def build_tw_components(
    schedule: pd.DataFrame, raw: Mapping[str, pd.DataFrame]
) -> pd.DataFrame:
    """Prepare approved Taiwan target components without association tests."""
    result = schedule.copy()
    for asset in TW_ASSETS:
        result = _join_asset(result, raw[asset], asset)
    for asset in ("0052", "TAIEX"):
        valid_intraday = result[[f"{asset}_open", f"{asset}_close"]].gt(0).all(axis=1)
        previous_close = result[f"{asset}_close"].shift(1)
        valid_gap = (result[f"{asset}_open"] > 0) & (previous_close > 0)
        result[f"gap_{asset}"] = np.nan
        result.loc[valid_gap, f"gap_{asset}"] = np.log(
            result.loc[valid_gap, f"{asset}_open"] / previous_close.loc[valid_gap]
        )
        result[f"intraday_{asset}"] = np.nan
        result.loc[valid_intraday, f"intraday_{asset}"] = np.log(
            result.loc[valid_intraday, f"{asset}_close"]
            / result.loc[valid_intraday, f"{asset}_open"]
        )
    target_columns = ["gap_0052", "intraday_0052", "gap_TAIEX", "intraday_TAIEX"]
    result["missing_target_components"] = result[target_columns].isna().any(axis=1)
    return result


def map_taiwan_windows(tw: pd.DataFrame, us: pd.DataFrame) -> pd.DataFrame:
    """Map calendar sessions and distinguish true empty windows from missing data."""
    rows: list[dict[str, object]] = []
    previous_tw_close = tw["session_close_utc"].shift(1)
    for position, target in tw.iterrows():
        window_start = previous_tw_close.iloc[position]
        window_end = target["session_open_utc"]
        if pd.isna(window_start):
            eligible_calendar = us.iloc[0:0]
        else:
            eligible_calendar = us.loc[
                (us["session_open_utc"] > window_start)
                & (us["session_close_utc"] < window_end)
            ]
        eligible = eligible_calendar.loc[eligible_calendar["complete_us_session"]]
        n_calendar_sessions = int(len(eligible_calendar))
        n_sessions = int(len(eligible))
        if pd.isna(window_start):
            mapping_status = "NO_PREVIOUS_TW_SESSION"
        elif n_calendar_sessions == 0:
            mapping_status = "EMPTY_US_WINDOW"
        elif n_sessions != n_calendar_sessions:
            mapping_status = "DATA_MISSING"
        else:
            mapping_status = "VALID"
        row: dict[str, object] = {
                "target_session": target["session_date"],
                "previous_tw_close_utc": window_start,
                "current_tw_open_utc": window_end,
                "mapping_status": mapping_status,
                "n_us_calendar_sessions": n_calendar_sessions,
                "n_us_sessions": n_sessions,
                "us_session_dates": ";".join(str(value) for value in eligible["session_date"]),
                "us_open_timestamps_utc": ";".join(value.isoformat() for value in eligible["session_open_utc"]),
                "us_close_timestamps_utc": ";".join(value.isoformat() for value in eligible["session_close_utc"]),
                "feature_information_end_utc": (
                    eligible["session_close_utc"].max() if n_sessions else pd.NaT
                ),
                "us_early_close_sessions": int(eligible["early_close"].sum()),
            }
        if "semi_specific" in eligible.columns:
            row["semi_specific_sum"] = (
                float(eligible["semi_specific"].sum()) if n_sessions else np.nan
            )
        if "broad_tech" in eligible.columns:
            row["broad_tech_sum"] = (
                float(eligible["broad_tech"].sum()) if n_sessions else np.nan
            )
        rows.append(row)
    return pd.DataFrame(rows)


def mapping_integrity(mapping: pd.DataFrame) -> dict[str, int]:
    """Count mechanical mapping violations without inspecting economic relations."""
    duplicated_targets = int(mapping["target_session"].duplicated().sum())
    timestamp_violations = 0
    assignments: list[str] = []
    for row in mapping.itertuples(index=False):
        opens = [pd.Timestamp(value) for value in row.us_open_timestamps_utc.split(";") if value]
        closes = [pd.Timestamp(value) for value in row.us_close_timestamps_utc.split(";") if value]
        sessions = [value for value in row.us_session_dates.split(";") if value]
        assignments.extend(sessions)
        if len(opens) != len(closes) or len(opens) != row.n_us_sessions:
            timestamp_violations += 1
            continue
        if pd.isna(row.previous_tw_close_utc):
            timestamp_violations += int(row.n_us_sessions > 0)
            continue
        for open_timestamp, close_timestamp in zip(opens, closes):
            if not (
                row.previous_tw_close_utc < open_timestamp
                and open_timestamp < close_timestamp
                and close_timestamp < row.current_tw_open_utc
            ):
                timestamp_violations += 1
    duplicate_assignments = sum(count - 1 for count in Counter(assignments).values() if count > 1)
    return {
        "duplicated_taiwan_targets": duplicated_targets,
        "timestamp_violations": int(timestamp_violations),
        "ambiguous_mappings": int(duplicate_assignments),
    }


def distribution_us_sessions(mapping: pd.DataFrame) -> dict[str, int]:
    """Return the requested 0/1/2/3+ session-count distribution."""
    counts = mapping["n_us_sessions"]
    return {
        "0": int((counts == 0).sum()),
        "1": int((counts == 1).sum()),
        "2": int((counts == 2).sum()),
        "3+": int((counts >= 3).sum()),
    }


def read_metadata(path: Path) -> dict[str, object]:
    """Read static acquisition provenance for one asset."""
    return json.loads(path.read_text(encoding="utf-8-sig"))
